from functools import lru_cache

from dotenv import find_dotenv
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    app_name: str = "Book Recommender API"
    # debug: bool = False
    database_url: PostgresDsn = "postgresql://postgres:postgres@localhost:5432/BookRecommendation"
    model_config = SettingsConfigDict(env_file=find_dotenv(".env"), env_file_encoding='utf-8')


# @lru_cache
def get_config():
    try:
        config = AppConfig()
        return config
    except Exception as e:
        print(e)
        raise e

