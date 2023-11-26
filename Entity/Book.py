from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Book(Base):
    __tablename__ = 'Books'

    book_id = Column(Integer, primary_key=True)
    isbn = Column(Integer)
    isbn13 = Column(Integer)
    link = Column(String)
    url = Column(String)
    country_code = Column(String)
    language_code = Column(String)
    average_rating = Column(Float)
    description = Column(Text)
    work_id = Column(Integer)
    title = Column(String)
    title_without_series = Column(String)
    similar_books = relationship("SimilarBook", backref="book")

