from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


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
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:postgres@localhost/BookRecommendation'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()