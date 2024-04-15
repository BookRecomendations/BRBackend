import logging
import time
from io import StringIO
from typing import List, Optional

import numpy as np
import requests
import torch
from bs4 import BeautifulSoup
from fastapi import UploadFile
import asyncio

from requests import HTTPError
from transformers import pipeline

import config_ini

from src.models import Book
import pandas as pd
from langdetect import detect

from src.schemas.book import NewBook, ScrapedInfo, UserBook, BookImportResult, BookTask, Status, TaskStatus
from .bookcrud import BookCRUD
from .main import AppCRUD, AppService
from .. import celery
from ..utils.app_exceptions import AppException
from ..utils.book_utils import process_book_row
from ..utils.service_result import ServiceResult

from src.services.tasks import proces_new_book, scrape_book_data

log = logging.getLogger(config_ini.LOGGING_CONF)


class BookService(AppService):

    def __init__(self, session):
        super().__init__(session)
        # TODO: Move to config, check what is the best value
        self.min_description_length = 70
        self.max_description_pseudo_token_length = 512

    def get_book(self, book_id: int):
        book: Book = BookCRUD(self.db).get_book_by_book_id(book_id=book_id)
        return ServiceResult(book)

    def add_book(self, book: NewBook):
        task_id = self.get_new_book(book)
        return ServiceResult(task_id)

    async def get_task_status(self, task_id: str):
        # Check if the task is finished
        task = celery.app.AsyncResult(task_id)

        # print(task.state)
        # print(task.result)
        # print(task.info.get('current', ''))
        if task.ready():
            return ServiceResult(TaskStatus(status=task.state, message=task.result).model_dump())
        else:
            if task.state == 'PENDING':
                return ServiceResult(TaskStatus(status=task.state, message="Task is pending").model_dump())
            else:
                return ServiceResult(TaskStatus(status=task.state, message=task.info.get('current', '')).model_dump())
        # if task.ready():
        #     return {
        #         "status": task.state,
        #         "result": task.result
        #     }
        # else:
        #     if task.state == 'PENDING':
        #         return {
        #             "status": task.state,
        #             "result": "Task is pending"
        #         }
        #     else:
        #         return {
        #             "status": task.state,
        #             "result": task.info.get('current', '')
        #         }

    async def read_books_from_goodreads_csv(self, file: UploadFile):
        contents = await file.read()
        df = self.validate_and_read_csv(contents)

        books: List[NewBook] = [process_book_row(row) for _, row in df.iterrows()]
        await file.close()
        book_crud = BookCRUD(self.db)

        return_books: List[UserBook] = []

        for book in books:
            db_book = book_crud.get_book_by_book_id(book.book_id)
            if not db_book:
                continue

            updates = {}

            # If book exists but lacks description or image_url, scrape for them.
            if not db_book.description or not db_book.image_url:
                scraped_info = self.scrape_book_data(book.book_id)
                if not db_book.description and scraped_info and scraped_info.description:
                    updates['description'] = scraped_info.description
                if not db_book.image_url and scraped_info and scraped_info.image_url:
                    updates['image_url'] = scraped_info.image_url

            if updates:
                book_crud.update_book(book.book_id, **updates)
                log.debug(f"Updated book {db_book} in the database with scraped information.")

            # Create UserBook object from the updated db_book information
            user_book = UserBook(
                book_id=db_book.book_id,
                url=db_book.url,
                title=db_book.title,
                image_url=db_book.image_url,
                description=db_book.description,
                average_rating=book.average_rating,
                user_rating=book.my_rating
            )

            return_books.append(user_book)

        return ServiceResult(return_books)

    async def process_goodreads_library_csv(self, file: UploadFile) -> ServiceResult:
        contents = await file.read()
        df = self.validate_and_read_csv(contents)
        await file.close()

        book_crud = BookCRUD(self.db)

        books: List[BookImportResult] = []

        for _, row in df.iterrows():
            task = None
            book = process_book_row(row)
            db_book = book_crud.get_book_by_book_id(book.book_id)
            # If book exists in the database
            if db_book:
                # If book has every information filled
                if db_book.description and db_book.image_url and db_book.url:
                    # If average_rating is different, update it
                    if db_book.average_rating != book.average_rating:
                        book_crud.update_book(book.book_id, average_rating=book.average_rating)
                # If book lacks description or image_url, scrape for them
                else:
                    task = scrape_book_data.delay(book.book_id)
            # If book does not exist in the database, scrape for description and image_url
            else:
                # task = proces_new_book.delay(book, self.db)
                task = scrape_book_data.delay(book.book_id)

            if task:
                book_task = BookTask(task_id=task.id,
                                     book_id=book.book_id,
                                     title=book.title,
                                     average_rating=book.average_rating,
                                     user_rating=book.my_rating)
                books.append(BookImportResult(status=Status.running, book_task=book_task))
            else:
                user_book = UserBook(
                    book_id=db_book.book_id,
                    url=db_book.url,
                    title=book.title,
                    image_url=db_book.image_url,
                    description=db_book.description,
                    average_rating=book.average_rating,
                    user_rating=book.my_rating
                )
                books.append(BookImportResult(status=Status.ready, book=user_book))

        return ServiceResult(books)

    @staticmethod
    def validate_and_read_csv(contents: bytes) -> pd.DataFrame:
        df = pd.read_csv(StringIO(contents.decode('utf-8')), sep=',', quotechar='"')
        print(df)
        expected_columns = ['Book Id', 'Title', 'My Rating', 'Average Rating', 'Author', 'ISBN', 'ISBN13']
        if not all(col in df.columns for col in expected_columns):
            raise ValueError("The CSV file does not have the expected columns.")
        return df

    @staticmethod
    def scrape_book_data(book_id: int) -> Optional[ScrapedInfo]:

        url = f"https://www.goodreads.com/book/show/{book_id}"

        response = requests.get(url)
        response.raise_for_status()

        # get description of the book
        soup = BeautifulSoup(response.text, 'html.parser')
        description_div = soup.find('div', class_='DetailsLayoutRightParagraph')
        description = None
        if description_div:
            description = description_div.text.strip()
            log.debug(f"Scraped description for ID {book_id} from {url}")
            # If description is too short, set it to None
            if len(description) < 10:
                description = None
        else:
            log.warning(f"No description found for ID {book_id} at {url}")

        # get image of the book
        image_div = soup.find('img', class_='ResponsiveImage')
        image_url = None
        if image_div:
            image_url = image_div['src']
            log.debug(f"Scraped image for ID {book_id} from {url}")
        else:
            log.warning(f"No image found for ID {book_id} at {url}")

        return ScrapedInfo(book_id=book_id, description=description, url=url, image_url=image_url)

    @staticmethod
    def summary_text(txt: str):

        max_length = 512
        min_length = 256
        log.info("Starting summarization process.")

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logging.info(f"Using device: {device}")

        summarizer = pipeline(
            "summarization",
            "pszemraj/long-t5-tglobal-base-16384-book-summary",
            device=device.index,
        )

        try:
            summarized_text = summarizer(txt, max_length=max_length, min_length=min_length)[0]["summary_text"]
            return summarized_text
        except Exception as e:
            logging.error(f"Error summarizing description: {e}")
            return txt

    def get_new_book(self, book: NewBook) -> str:
        task = proces_new_book.delay(book, self.db)
        return task.id

    def get_embedding_and_add_to_faiss(self, book: Book):
        pass
