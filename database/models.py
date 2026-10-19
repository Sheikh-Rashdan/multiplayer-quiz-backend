from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.sqlite import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str | None] = mapped_column(String, nullable=True)

    questions: Mapped[list[Question]] = relationship(
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
