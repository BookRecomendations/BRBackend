import gzip
import json
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from Models.Base import Base  # upewnij się, że Base jest zaimportowane poprawnie
from Models.Book import Book
from Models.SimilarBook import SimilarBook

# Konfiguracja połączenia z bazą danych
DATABASE_URL = 'postgresql+asyncpg://postgres:postgres@localhost/BookRecommendation'
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Inicjalizacja bazy danych (opcjonalnie)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Funkcja do dodawania książek do sesji
async def add_book_to_session(session, book_data):
    book: Book = Book(
        book_id=int(book_data.get('book_id')),
        isbn=book_data.get('isbn'),
        isbn13=book_data.get('isbn13'),
        link=book_data.get('link'),
        url=book_data.get('url'),
        country_code=book_data.get('country_code'),
        language_code=book_data.get('language_code'),
        average_rating=float(book_data.get('average_rating', 0)),
        description=book_data.get('description'),
        work_id=int(book_data.get('work_id')),
        title=book_data.get('title'),
        title_without_series=book_data.get('title_without_series')
    )
    session.add(book)
    # await session.flush()  # To make sure book_id is generated

    # similar_books_ids = book_data.get('similar_books', [])
    # for sb_id in similar_books_ids:
    #     # Convert the similar book id from string to integer before creating the SimilarBook object
    #     try:
    #         sb_id_int = int(sb_id)
    #         similar_book = SimilarBook(book_id=book.book_id, similar_book_id=sb_id_int)
    #         session.add(similar_book)
    #     except ValueError:
    #         # Handle the case where the string cannot be converted to an integer
    #         print(f"Warning: '{sb_id}' is not a valid integer for a similar_book_id.")

async def main():
    DIR = './Data'
    await init_db()  # Wywołanie opcjonalne jeśli baza jest już zainicjowana
    print("Adding books to the database...")
    async with AsyncSessionLocal() as session:
        with gzip.open(os.path.join(DIR, 'goodreads_books.json.gz')) as fin:
            lines = 2_360_655
            try:
                count = 0
                print(f"Adding {lines} books to the database...")
                for line in fin:
                    book_data = json.loads(line)
                    await add_book_to_session(session, book_data)

                    count += 1
                    if count % 100 == 0:
                        await session.commit()
                        await session.close()
                        session = AsyncSessionLocal()
                        print(f"Added {count}/{lines} books to the database.")

                await session.commit()
            except Exception as e:
                print(e)
                await session.rollback()
            finally:
                await session.close()

# Uruchomienie asynchronicznego głównego procesu
asyncio.run(main())
