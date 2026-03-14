
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///hainan.db")


def get_engine(url: str | None = None):
    """Return a SQLAlchemy Engine for the given URL.

    If no URL is provided, the value from the environment variable
    `DATABASE_URL` is used. If that is not set, a local SQLite file is used.
    """

    url = url or DATABASE_URL
    return create_engine(url, future=True)


def get_session(engine=None):
    """Return a SQLAlchemy session bound to the given engine."""

    engine = engine or get_engine()
    return sessionmaker(bind=engine, future=True)()
