from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Question, Quiz


def get_questions(db: Session, quiz: Quiz, limit: int, offset: int) -> list[Question]:
    statement = (
        select(Question).where(Question.quiz_id == quiz.id).limit(limit).offset(offset)
    )
    return db.scalars(statement).all()


def get_question(db: Session, question_id: int) -> Question | None:
    statement = select(Question).where(Question.id == question_id)
    return db.scalar(statement)


def post_question(db: Session, create_dict: dict[str, Any]) -> Question:
    question = Question(**create_dict)

    db.add(question)
    try:
        db.commit()
        db.refresh(question)
    except:
        db.rollback()
        raise

    return question


def delete_question(db: Session, question: Question) -> None:
    db.delete(question)

    try:
        db.commit()
    except:
        db.rollback()
        raise


def patch_question(
    db: Session, question: Question, patch_dict: dict[str, Any]
) -> Question:
    for attribute, value in patch_dict.items():
        setattr(question, attribute, value)

    try:
        db.commit()
        db.refresh(question)
    except:
        db.rollback()
        raise

    return question
