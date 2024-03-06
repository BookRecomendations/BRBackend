from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from src.database import engine, SessionLocal, Base

from src.Models import Book
from src.Services import BookService
from src.Schemas import BookSchema

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/items/")
def create_item(name: str, db: AsyncSession = Depends(get_db)):
    # new_item = ExampleModel(name=name)
    # db.add(new_item)
    # await db.commit()
    # return {"id": new_item.id, "name": new_item.name}
    pass


@app.get("/books")
def get_books(db: Session = Depends(get_db)):
    return BookService.get_books(db, 10)


