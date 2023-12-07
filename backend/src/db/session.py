from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
from ..core.config import Configuration


db_url = Configuration.SQLALCHEMY_DATABASE_URI.unicode_string()
Engine = create_engine(db_url, pool_pre_ping=True, pool_size=5, max_overflow=5,
                       pool_recycle=120, pool_timeout=30)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)


def get_db() -> Generator:
    connection = None
    try:
        connection = SessionLocal()
        yield connection
    finally:
        if connection is not None:
            connection.close()
