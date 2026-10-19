from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import storage.quiz as storage
from database.db import get_db
from database.models import Quiz, User
from models.quiz import QuizCreate, QuizModel, QuizPatch
from routers.user import get_current_user

quiz_router = APIRouter(prefix="/quizzes", tags=["quiz"])


def validate_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz: Quiz | None = storage.get_quiz(db, quiz_id)

    if quiz is None:
        raise HTTPException(status_code=404, detail=f"quiz_id {quiz_id} does not exist")

    return quiz


def validate_quiz_belongs_to_user(quiz: Quiz, user: User):
    if quiz.author_id != user.id:
        raise HTTPException(
            status_code=403,
            detail=f"quiz_id {quiz.id} does not belong to user_id {user.id}",
        )


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
def post_quiz(
    quiz_create: QuizCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    create_dict = quiz_create.model_dump()
    create_dict["author_id"] = user.id
    return storage.post_quiz(db, create_dict)


@quiz_router.delete("/{quiz_id}", status_code=204)
def delete_quiz(
    quiz: Quiz = Depends(validate_quiz),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    validate_quiz_belongs_to_user(quiz, user)
    return storage.delete_quiz(db, quiz)


@quiz_router.patch("/{quiz_id}", response_model=QuizModel)
def patch_quiz(
    quiz_patch: QuizPatch,
    quiz: Quiz = Depends(validate_quiz),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    validate_quiz_belongs_to_user(quiz, user)
    return storage.patch_quiz(db, quiz, quiz_patch.model_dump(exclude_unset=True))
