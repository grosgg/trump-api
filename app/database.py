"""Database module"""
from urllib.parse import urlparse

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.logger import logger

from app.models import User


def get_postgres_info(url: str):
    """Extract PostgreSQL connection info from URL"""
    parsed = urlparse(url)

    # Convert async URL to sync for database creation
    sync_url = url.replace('+asyncpg', '+psycopg')

    db_name = parsed.path.lstrip('/')
    server_url = f"postgresql+psycopg://{parsed.netloc}/postgres"

    return {
        'db_name': db_name,
        'server_url': server_url,
        'sync_url': sync_url,
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'username': parsed.username,
        'password': parsed.password
    }


def create_postgres_database():
    """Create PostgreSQL database if it doesn't exist"""
    db_info = get_postgres_info(settings.DB_URL)

    try:
        # Try connecting to the target database
        test_engine = create_engine(db_info['sync_url'])
        with test_engine.connect():
            logger.info(
                f"PostgreSQL database '{db_info['db_name']}' already exists")
        test_engine.dispose()
        return

    except (OperationalError, ProgrammingError):
        # Database doesn't exist, create it
        logger.info(
            f"PostgreSQL database '{db_info['db_name']}' doesn't exist. Creating...")

        try:
            # Connect to postgres default database
            temp_engine = create_engine(
                db_info['server_url'],
                isolation_level="AUTOCOMMIT"  # Required for CREATE DATABASE
            )

            with temp_engine.connect() as conn:
                # Check if database exists first
                result = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                    {"dbname": db_info['db_name']}
                )

                if result.fetchone() is None:
                    # Create the database
                    conn.execute(
                        text(f'CREATE DATABASE "{db_info["db_name"]}"'))
                    logger.info(
                        f"PostgreSQL database '{db_info['db_name']}' created successfully!")
                else:
                    logger.info(
                        f"PostgreSQL database '{db_info['db_name']}' already exists")

            temp_engine.dispose()

        except Exception as e:
            logger.error(f"Failed to create PostgreSQL database: {e}")
            raise


# Create the database first
create_postgres_database()

engine = create_async_engine(settings.DB_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    """Async database session dependency"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User)
