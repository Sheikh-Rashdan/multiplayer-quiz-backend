from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.sqlite import JSONB, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from utils.room_code import get_unique_room_code


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    quizzes: Mapped[list[Quiz]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    rooms: Mapped[list[Room]] = relationship(
        back_populates="host", cascade="all, delete-orphan"
    )


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, insert_default=get_unique_room_code
    )
    host_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String, nullable=False, default="waiting")
    player_ids: Mapped[list[int]] = mapped_column(
        JSONB, nullable=False, insert_default=list
    )
    question_index: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, insert_default=datetime.now
    )

    host: Mapped[User] = relationship(back_populates="rooms")
    quiz: Mapped[Quiz] = relationship(back_populates="rooms")


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    author: Mapped[User] = relationship(back_populates="quizzes")

    questions: Mapped[list[Question]] = relationship(
        back_populates="quiz", cascade="all, delete-orphan"
    )
    rooms: Mapped[list[Room]] = relationship(
        back_populates="quiz", cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    options: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    answer_index: Mapped[int] = mapped_column(nullable=False)

    quiz_id: Mapped[Quiz] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    quiz: Mapped[Quiz] = relationship(back_populates="questions")
