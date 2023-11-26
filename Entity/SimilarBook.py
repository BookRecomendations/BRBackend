from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class SimilarBook(Base):
    __tablename__ = 'similar_books'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('Books.book_id'))
    similar_book_id = Column(Integer, ForeignKey('Books.book_id'))
