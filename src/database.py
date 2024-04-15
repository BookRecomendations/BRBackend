from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from src.config.app_config import get_config

# ASYNC_SQLALCHEMY_DATABASE_URL = 'postgresql+asyncpg://postgres:postgres@localhost/BookRecommendation'
#
# async_engine = create_async_engine(
#     ASYNC_SQLALCHEMY_DATABASE_URL
# )
# AsyncSessionLocal = sessionmaker(
#     bind=async_engine,
#     class_=AsyncSession,
#     expire_on_commit=False
# )

config = get_config()

engine = create_engine(
    config.database_url.unicode_string(),
)
# engine = create_async_engine(config.database_url.unicode_string(), echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# SessionLocal = sessionmaker(
#     expire_on_commit=False,
#     class_=AsyncSession,
#     bind=engine,
# )

Base = declarative_base()


# async def create_session() -> AsyncSession:
#     async with SessionLocal() as session:
#         yield session

def create_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
