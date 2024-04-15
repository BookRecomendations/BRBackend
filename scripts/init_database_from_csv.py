import gzip
import os

from src.database import SessionLocal
import csv

from src.models import Book


def add_book_to_session(session, book_data):
    book: Book = Book(
        id=int(book_data[1]),
        book_id=int(book_data[2]),
        title=book_data[3],
        language_code=book_data[4],
        url=book_data[7],
        description=book_data[9],
    )
    session.add(book)


def main():
    DIR = ''
    with gzip.open(os.path.join(DIR, 'goodreads_cleaned_books_summarized.csv.gz'), 'rt', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        with SessionLocal() as session:
            try:
                count = 0
                for row in csv_reader:
                    # skip the first row (header)
                    if count == 0:
                        count += 1
                        continue
                    add_book_to_session(session, row)
                    count += 1
                    if count % 100 == 0:
                        session.commit()
                        session.close()
                        session = SessionLocal()
                        print(f"Processed {count} rows")
                session.commit()
            except Exception as e:
                print(e)
                session.rollback()
            finally:
                session.close()


if __name__ == "__main__":
    main()
