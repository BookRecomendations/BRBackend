from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship

from .Base import Base


class Book(Base):
    __tablename__ = 'books'

    book_id = Column(Integer, primary_key=True)
    isbn = Column(String)
    isbn13 = Column(String)
    link = Column(String)
    url = Column(String)
    country_code = Column(String)
    language_code = Column(String)
    average_rating = Column(Float)
    description = Column(Text)
    work_id = Column(Integer)
    title = Column(String)
    title_without_series = Column(String)
    similar_books = relationship(
        "SimilarBook",
        foreign_keys="[SimilarBook.book_id]",
        backref="book"
    )


