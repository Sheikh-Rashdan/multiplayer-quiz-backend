from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import User


def post_user(db: Session, create_dict: dict[str, Any]) -> User:
    user: User = User(**create_dict)

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except:
        db.rollback()
        raise

    return user


def get_user_with_username(db: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return db.scalar(statement)


def get_user_with_id(db: Session, user_id: int) -> User | None:
    statement = select(User).where(User.id == user_id)
    return db.scalar(statement)
