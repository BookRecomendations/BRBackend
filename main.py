from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

app = FastAPI()

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/dbname"

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/items/")
async def create_item(name: str, db: AsyncSession = Depends(get_db)):
    # new_item = ExampleModel(name=name)
    # db.add(new_item)
    # await db.commit()
    # return {"id": new_item.id, "name": new_item.name}
    pass
