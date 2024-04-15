import logging
from typing import List

from sqlalchemy import select

import config_ini
from src import Book
from src.services.main import AppCRUD

log = logging.getLogger(config_ini.LOGGING_CONF)


class BookCRUD(AppCRUD):
    def get_book_by_book_id(self, book_id: int) -> Book | None:
        stmt = select(Book).where(Book.book_id == book_id)
        result = self.db.execute(stmt).first()
        if result:
            return result[0]
        else:
            return None

    def get_book_by_id(self, book_id: int) -> Book | None:
        stmt = select(Book).where(Book.id == book_id)
        result = self.db.execute(stmt).first()
        if result:
            return result[0]
        else:
            return None

    def add_book(self, book: Book):
        self.db.add(book)
        self.db.commit()
        log.debug(f"Added book {book} to the database")
        return book

    def add_books(self, books: List[Book]):
        self.db.add_all(books)
        self.db.commit()
        for book in books:
            log.debug(f"Added book {book} to the database")

    def update_book(self, book_id: int, **kwargs) -> Book | None:
        """Update an existing book's attributes."""
        book = self.get_book_by_book_id(book_id)
        if book:
            for key, value in kwargs.items():
                if hasattr(book, key):
                    setattr(book, key, value)
                else:
                    log.warning(f"Book does not have attribute {key}")
                    raise AttributeError(f"Book does not have attribute {key}")
            self.db.commit()
            log.debug(f"Updated book {book} in the database")
            return book
        else:
            log.debug(f"Book with ID {book_id} not found.")
            return None
