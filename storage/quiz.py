from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Quiz


def get_quizzes(db: Session, limit: int, offset: int) -> list[Quiz]:
    statement = select(Quiz).limit(limit).offset(offset)
    return db.scalars(statement).all()
