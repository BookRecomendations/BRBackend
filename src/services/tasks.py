import logging
import time
from typing import Optional, Any

import numpy as np
import requests
import torch
from bs4 import BeautifulSoup
from celery import shared_task
from langdetect import detect
from requests import HTTPError
from sqlalchemy.orm import Session
from transformers import pipeline

import config_ini
from src import celery
from src.schemas.book import NewBook, Book, UserBook, ScrapedInfo
from src.services.bookcrud import BookCRUD

from src.utils.app_exceptions import AppException
from src.utils.service_result import ServiceResult

log = logging.getLogger(config_ini.LOGGING_CONF)


@celery.app.task(bind=True)
def scrape_book_data(self, book_id: int) -> Optional[ScrapedInfo] | dict[str, Any]:
    url = f"https://www.goodreads.com/book/show/{book_id}"

    response = requests.get(url)
    response.raise_for_status()

    # get description of the book
    self.update_state(state='PROGRESS', meta={'current': 'Getting data'})
    time.sleep(5)
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

    return_dict = ScrapedInfo(book_id=book_id, description=description, url=url, image_url=image_url).model_dump()
    return return_dict
    # if self:
    #     return ScrapedInfo(book_id=book_id, description=description, url=url, image_url=image_url).model_dump()
    # else:
    #     return ScrapedInfo(book_id=book_id, description=description, url=url, image_url=image_url).model_dump()


def lang_detect(text: str) -> str | float:
    try:
        return detect(text)
    except Exception as e:
        return np.NaN


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


@celery.app.task(bind=True)
def proces_new_book(self, book: NewBook, session: Session) -> ServiceResult:
    # STATUS: POBRANIE DANYCH Z GOODREADS
    # pobierz dane z goodreads

    try:
        self.update_state(state='PROGRESS', meta={'current': 'Getting data'})
        book_info = scrape_book_data(book.book_id)
    except HTTPError as e:
        return ServiceResult(AppException.BookAddNewRequestError({"book_id": book.book_id, "error": str(e)}))

    if book_info is None:
        return ServiceResult(AppException.BookAddNewNoDescription({"book_id": book.book_id}))
    # jeżeli nie ma opisu to zwróć informację o braku książki
    if not book_info.description:
        return ServiceResult(AppException.BookAddNewNoDescription({"book_id": book.book_id}))
    # jeżeli jest opis sprawdź, czy jest wystarczająco długi
    if len(book_info.description) < self.min_description_length:
        return ServiceResult(AppException.BookAddNewDescriptionTooShort({"book_id": book.book_id}))

    # sprawdź, czy język jest angielski i zwróć informację o nieodpowiednim języku
    self.update_state(state='PROGRESS', meta={'current': 'Checking language'})
    language = lang_detect(book_info.description)
    if language != 'en':
        return ServiceResult(
            AppException.BookAddNewDescriptionNotInEnglish({"book_id": book.book_id, "error": "Language not English"}))

    # sprawdź, czy opis nie jest za długi
    if len(book_info.description.split()) > 512:
        self.update_state(state='PROGRESS', meta={'current': 'Summarizing description'})
        book_info.description = summary_text(book_info.description)

    full_book = Book(
        book_id=book_info.book_id,
        isbn=book.isbn,
        isbn13=book.isbn13,
        link=book_info.image_url,
        url=book_info.url,
        language_code=language,
        description=book_info.description,
        average_rating=book.average_rating,
        title=book.title,
    )
    # dodaj do bazy
    self.update_state(state='PROGRESS', meta={'current': 'Adding book to database'})
    # BookCRUD(session).add_book(full_book)
    # oblicz embedding i dodaj do bazy faiss
    # book_service.get_embedding_and_add_to_faiss(full_book)

    user_book = UserBook(
        book_id=full_book.book_id,
        url=full_book.url,
        title=full_book.title,
        image_url=full_book.link,
        description=full_book.description,
        average_rating=full_book.average_rating,
        user_rating=book.my_rating,
    )

    return ServiceResult(user_book)
