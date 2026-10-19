from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Quiz


def get_quizzes(db: Session, limit: int, offset: int) -> list[Quiz]:
    statement = select(Quiz).limit(limit).offset(offset)
    return db.scalars(statement).all()


def get_quiz(db: Session, quiz_id: int) -> Quiz | None:
    statement = select(Quiz).where(Quiz.id == quiz_id)
    return db.scalar(statement)


def post_quiz(db: Session, create_dict: dict[str, Any]) -> Quiz:
    quiz = Quiz(**create_dict)

    db.add(quiz)
    try:
        db.commit()
        db.refresh(quiz)
    except:
        db.rollback()
        raise

    return quiz


def delete_quiz(db: Session, quiz: Quiz) -> None:
    db.delete(quiz)

    try:
        db.commit()
    except:
        db.rollback()
        raise


def patch_quiz(db: Session, quiz: Quiz, patch_dict: dict[str, Any]) -> Quiz:
    for attribute, value in patch_dict.items():
        setattr(quiz, attribute, value)

    try:
        db.commit()
        db.refresh(quiz)
    except:
        db.rollback()
        raise

    return quiz
