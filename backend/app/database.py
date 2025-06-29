from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings # Imports the 'settings' instance
from app.db.base_class import Base
from typing import Generator

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()