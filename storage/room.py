from typing import Any

from sqlalchemy import delete, select
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


def delete_room(db: Session, room_id: int) -> None:
    statement = delete(Room).where(Room.id == room_id)
    db.execute(statement)

    try:
        db.commit()
    except:
        db.rollback()
        raise


def add_player(db: Session, room_id: int, player_id: int) -> list[int]:
    room = get_room(db, room_id)
    room.player_ids = list(set(room.player_ids + [player_id]))

    try:
        db.commit()
        db.refresh(room)
    except:
        db.rollback()
        raise

    return room.player_ids


def remove_player(db: Session, room_id: int, player_id: int) -> list[int]:
    room = get_room(db, room_id)

    if player_id not in room.player_ids:
        return room.player_ids

    player_ids_copy = room.player_ids.copy()
    player_ids_copy.remove(player_id)
    room.player_ids = player_ids_copy

    try:
        db.commit()
        db.refresh(room)
    except:
        db.rollback()
        raise

    return room.player_ids


def next_question(db: Session, room_id: int) -> int:
    room = get_room(db, room_id)
    max_question_index = len(room.quiz.questions)

    if room.status != "ongoing":
        return None

    if room.question_index >= max_question_index:
        room.question_index = -1
        room.status = "finished"
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
