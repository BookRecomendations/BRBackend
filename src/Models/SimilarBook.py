from sqlalchemy import Column, Integer, ForeignKey

from src.database import Base


# from .Base import Base


class SimilarBook(Base):
    __tablename__ = 'similar_books'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.book_id'))
    similar_book_id = Column(Integer, ForeignKey('books.book_id'))
