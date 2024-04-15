from enum import Enum
from typing import Optional

from pydantic import BaseModel


class BaseBook(BaseModel):
    book_id: int


class Book(BaseBook):
    isbn: str
    isbn13: str
    link: str
    url: str
    country_code: str
    language_code: str
    average_rating: float
    description: str
    work_id: int
    title: str
    title_without_series: str
    similar_books: list[int] = []

    class Config:
        from_attributes = True


class NewBook(BaseBook):
    title: str
    author: str
    isbn: Optional[str] = None
    isbn13: Optional[str] = None
    my_rating: Optional[int] = None
    average_rating: Optional[float] = None


class ScrapedInfo(BaseBook):
    description: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None


class UserBook(BaseBook):
    url: str
    title: str
    image_url: str
    description: str
    average_rating: float
    user_rating: int


class BookTask(BaseBook):
    task_id: str
    title: str
    average_rating: float
    user_rating: int


class Status(Enum):
    ready = "ready"
    running = "running"
    error = "error"


class BookImportResult(BaseModel):
    status: Status
    book_task: Optional[BookTask] = None
    book: Optional[UserBook] = None


class TaskStatus(BaseModel):
    status: str
    message: str | dict

# class LibraryImportResult(BaseModel):
#     books: list[BookImportResult]
