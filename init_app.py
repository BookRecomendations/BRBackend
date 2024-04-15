import timeit

from sqlalchemy.orm import Session

from src.models import Book
from src.recommenders.BertModel import BertModel
from src.services.IndexDatabase import IndexDatabase
from src.database import SessionLocal
from scipy.spatial.distance import cosine

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db = SessionLocal()

index = IndexDatabase(metric="angular", vector_size=768, name="test")

# db = get_db()

books = db.query(Book).order_by(Book.book_id).limit(1000).all()

model = BertModel()
# print(books[0].description)
# embeddings = []
# print("Building embeddings")
# for book in books:
#     embeddings = model.get_embedding(book.description)
#     index.add_item(book.book_id, embeddings)
# print("Building index")
# index.build()
# index.save(".", replace=True)
# print("Index built and saved")
index.load("test.ann")
start = timeit.default_timer()
nearest_books = index.get_nns_by_item(1, 100)
print(nearest_books)
end = timeit.default_timer()

book_0 = model.get_embedding(books[0].description)

for book in nearest_books:
    # calculate cosine similarity
    simlarity = 1 - cosine(book_0, index.get_item_vector(book))
    print(f"Book {book} has similarity {simlarity}")


print(f"Time: {end - start}")

