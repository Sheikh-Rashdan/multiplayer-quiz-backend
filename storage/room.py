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
