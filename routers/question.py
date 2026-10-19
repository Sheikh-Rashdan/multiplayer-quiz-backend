from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import storage.question as storage
from database.db import get_db
from database.models import Question, Quiz, User
from models.question import QuestionCreate, QuestionModel, QuestionPatch
from routers.quiz import validate_quiz, validate_quiz_belongs_to_user
from routers.user import get_current_user

question_router = APIRouter(prefix="/quizzes/{quiz_id}/questions", tags=["question"])


def validate_question(question_id: int, db: Session = Depends(get_db)):
    question: Question | None = storage.get_question(db, question_id)

    if question is None:
        raise HTTPException(
            status_code=404, detail=f"question_id {question_id} does not exist"
        )

    return question


def validate_question_belongs_to_quiz(question: Question, quiz: Quiz):
    if question.quiz_id != quiz.id:
        raise HTTPException(
            status_code=403,
            detail=f"question_id {question.id} does not belong to quiz_id {quiz.id}",
        )


def validate_index_within_bounds(answer_index: int, options: list[str]):
    if answer_index >= len(options):
        raise HTTPException(
            status_code=422,
            detail=f"answer_index [{answer_index}] must be within the range - 0 to {len(options) - 1}",
        )


@question_router.get("", response_model=list[QuestionModel])
def get_questions(
    db: Session = Depends(get_db),
    quiz: Quiz = Depends(validate_quiz),
    limit: int = Query(default=100, ge=1),
    offset: int = Query(default=0, ge=0),
):
    return storage.get_questions(db, quiz, limit, offset)


@question_router.get("/{question_id}", response_model=QuestionModel)
def get_question(
    quiz: Quiz = Depends(validate_quiz), question: Question = Depends(validate_question)
):
    validate_question_belongs_to_quiz(question, quiz)
    return question


@question_router.post("", status_code=201, response_model=QuestionModel)
def post_question(
    question_create: QuestionCreate,
    quiz: Quiz = Depends(validate_quiz),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    validate_quiz_belongs_to_user(quiz, user)
    validate_index_within_bounds(question_create.answer_index, question_create.options)

    create_dict = question_create.model_dump()
    create_dict["quiz_id"] = quiz.id
    return storage.post_question(db, create_dict)


@question_router.delete("/{question_id}", status_code=204)
def delete_question(
    question: Question = Depends(validate_question),
    quiz: Quiz = Depends(validate_quiz),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    validate_quiz_belongs_to_user(quiz, user)
    validate_question_belongs_to_quiz(question, quiz)
    return storage.delete_question(db, question)


@question_router.patch("/{question_id}", response_model=QuestionModel)
def patch_question(
    question_patch: QuestionPatch,
    question: Question = Depends(validate_question),
    quiz: Quiz = Depends(validate_quiz),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    validate_quiz_belongs_to_user(quiz, user)
    validate_question_belongs_to_quiz(question, quiz)

    answer_index = question_patch.answer_index
    if answer_index is None:
        answer_index = question.answer_index
    options = question_patch.options
    if options is None:
        options = question.options

    validate_index_within_bounds(answer_index, options)

    return storage.patch_question(
        db, question, question_patch.model_dump(exclude_unset=True)
    )
