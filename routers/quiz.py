from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import storage.quiz as storage
from database.db import get_db
from database.models import Quiz
from models.quiz import QuizCreate, QuizModel, QuizPatch

quiz_router = APIRouter(prefix="/quiz", tags=["quiz"])


def validate_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz: Quiz | None = storage.get_quiz(db, quiz_id)

    if quiz is None:
        raise HTTPException(status_code=404, detail=f"quiz_id {quiz_id} does not exist")

    return quiz


@quiz_router.get("", response_model=list[QuizModel])
def get_quizzes(
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1),
    offset: int = Query(default=0, ge=0),
):
    return storage.get_quizzes(db, limit, offset)


@quiz_router.get("/{quiz_id}", response_model=QuizModel)
def get_quiz(quiz: Quiz = Depends(validate_quiz)):
    return quiz


@quiz_router.post("", status_code=201, response_model=QuizModel)
def post_quiz(quiz_create: QuizCreate, db: Session = Depends(get_db)):
    return storage.post_quiz(db, quiz_create.model_dump())
