from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from .Base import Base


class SimilarBook(Base):
    __tablename__ = 'similar_books'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.book_id'))
    similar_book_id = Column(Integer, ForeignKey('books.book_id'))
