from src.schemas.book import NewBook


def process_book_row(row) -> NewBook | None:
    book_id: int = int(row['Book Id'])
    title: str = row['Title']
    author: str = row['Author']
    isbn: str = row['ISBN'][3:-2]
    isbn13: str = row['ISBN13'][3:-2]
    my_rating: float = float(row['My Rating'])
    average_rating: float = float(row['Average Rating'])

    return NewBook(
        book_id=book_id,
        title=title,
        author=author,
        isbn=isbn,
        isbn13=isbn13,
        my_rating=my_rating,
        average_rating=average_rating,
    )