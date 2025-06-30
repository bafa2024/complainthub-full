import logging
import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .config.settings import settings
from .db.base_class import Base
from typing import Generator

logger = logging.getLogger(__name__)

# Database configuration with error handling
try:
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
    logger.info(f"Database URL configured: {SQLALCHEMY_DATABASE_URL.split('@')[1] if '@' in SQLALCHEMY_DATABASE_URL else 'local'}")
except Exception as e:
    logger.error(f"Failed to get database URL from settings: {e}")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./voicebot.db"  # Fallback to SQLite

try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,  # Enable connection health checks
        pool_recycle=300,    # Recycle connections every 5 minutes
        echo=False           # Set to True for SQL query logging
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    # Create a fallback SQLite engine
    try:
        engine = create_engine("sqlite:///./voicebot.db")
        logger.info("Fallback SQLite engine created")
    except Exception as fallback_error:
        logger.error(f"Failed to create fallback engine: {fallback_error}")
        raise

try:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database session factory created successfully")
except Exception as e:
    logger.error(f"Failed to create session factory: {e}")
    raise

def get_db() -> Generator:
    """Database dependency with comprehensive error handling"""
    db = None
    try:
        db = SessionLocal()
        logger.debug("Database session created")
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        if db:
            db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error in database session: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        if db:
            db.rollback()
        raise
    finally:
        try:
            if db:
                db.close()
                logger.debug("Database session closed")
        except Exception as e:
            logger.error(f"Error closing database session: {e}")

def test_database_connection():
    """Test database connection and return status"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection test successful")
        return {"status": "connected", "message": "Database is accessible"}
    except SQLAlchemyError as e:
        logger.error(f"Database connection test failed: {e}")
        return {"status": "error", "message": f"Database connection failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error testing database connection: {e}")
        return {"status": "error", "message": f"Unexpected error: {str(e)}"} 