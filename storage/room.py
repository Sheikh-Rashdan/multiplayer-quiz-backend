from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Room


def get_room(db: Session, room_id: str) -> Room | None:
    statement = select(Room).where(Room.id == room_id)
    return db.scalar(statement)


def post_room(db: Session, create_dict: dict[str, Any]) -> Room:
    room = Room(**create_dict)

    db.add(room)

    try:
        db.commit()
        db.refresh(room)
    except:
        db.rollback()
        raise

    return room


def add_player(db: Session, room_id: int, player_id: int) -> Room:
    room = get_room(db, room_id)
    room.player_ids = list(set(room.player_ids + [player_id]))

    try:
        db.commit()
        db.refresh(room)
    except:
        db.rollback()
        raise

    return room


def next_question(db: Session, room_id: int) -> int:
    room = get_room(db, room_id)
    max_question_index = len(room.quiz.questions)

    if room.question_index >= max_question_index:
        room.question_index = -1
    else:
        room.question_index += 1

    try:
        db.commit()
        db.refresh(room)
    except:
        db.rollback()
        raise

    return room.question_index


def start_quiz(db: Session, room_id: int) -> str:
    room = get_room(db, room_id)

    if room.status != "waiting" or len(room.player_ids) == 0:
        return None

    room.status = "ongoing"

    try:
        db.commit()
        db.refresh(room)
    except:
        db.rollback()
        raise

    return room.status
