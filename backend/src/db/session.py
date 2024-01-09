from typing import Generator

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, create_engine

from ..core.config import Configuration

db_url = Configuration.SQLALCHEMY_DATABASE_URI.unicode_string()
engine = create_engine(db_url, pool_pre_ping=True, pool_size=5, max_overflow=5,
                       pool_recycle=120, pool_timeout=30)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db() -> Generator:
    session = None
    try:
        # connection = SessionLocal()
        # yield connection
        with Session(engine) as session:
            yield session
    finally:
        if session is not None:
            session.close()
