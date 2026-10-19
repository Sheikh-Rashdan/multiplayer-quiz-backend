from collections.abc import Generator
from os import getenv

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from database.models import Base

load_dotenv()
DATABASE_URL = getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError(".env does not contain DATABASE_URL")

engine: Engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session]:
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
