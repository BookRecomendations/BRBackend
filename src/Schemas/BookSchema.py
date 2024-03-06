from pydantic import BaseModel


class Book(BaseModel):
    book_id: int
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
        orm_mode = True
