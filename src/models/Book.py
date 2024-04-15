from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship

from src.database import Base


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer)
    isbn = Column(String)
    isbn13 = Column(String)
    link = Column(String)
    url = Column(String)
    image_url = Column(String)
    country_code = Column(String)
    language_code = Column(String)
    average_rating = Column(Float)
    description = Column(Text)
    work_id = Column(Integer)
    title = Column(String)
    title_without_series = Column(String)

    def __repr__(self):
        return f"<Book(book_id={self.book_id}, title={self.title})>"

    def __str__(self):
        return f"Book(book_id={self.book_id}, title={self.title})"

    def __eq__(self, other: 'Book'):
        return self.book_id == other.book_id
