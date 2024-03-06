from sqlalchemy.orm import Session

from ..Models import Book


def get_books(db: Session, limit: int):
    return db.query(Book).limit(limit).all()
