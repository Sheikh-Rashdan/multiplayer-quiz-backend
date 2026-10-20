import secrets
from string import ascii_uppercase

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy.orm import Session

import storage.room as storage
from database.db import get_db
from database.models import Quiz, Room, User
from models.room import RoomCreate, RoomModel
from routers.quiz import validate_quiz, validate_quiz_belongs_to_user
from routers.user import get_current_user
from websocket_handler.connections import websocket_connections

room_router = APIRouter(prefix="/rooms", tags=["room"])


def validate_optional_room(room_id: str, db: Session = Depends(get_db)) -> Room | None:
    return storage.get_room(db, room_id)


def validate_room(room_id: str, db: Session = Depends(get_db)) -> Room:
    room: Room | None = validate_optional_room(room_id, db)

    if room is None:
        raise HTTPException(status_code=404, detail="room not found")

    return room


@room_router.get("/{room_id}", response_model=RoomModel)
def get_room(room: Room = Depends(validate_room)):
    return room


@room_router.post("", status_code=201, response_model=RoomModel)
def post_room(
    room_create: RoomCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quiz: Quiz = validate_quiz(room_create.quiz_id, db)
    validate_quiz_belongs_to_user(quiz, user)

    create_dict = room_create.model_dump()
    create_dict["host_id"] = user.id

    code = generate_unique_code(db)
    create_dict["id"] = code
    return storage.post_room(db, create_dict)


def generate_unique_code(db: Session):
    while True:
        code = ""
        for _ in range(5):
            code += secrets.choice(ascii_uppercase)

        room: Room | None = validate_optional_room(code, db)
        if room is None:
            return code


@room_router.websocket("/{room_id}")
async def websocket_connection(
    websocket: WebSocket, room: Room = Depends(validate_optional_room)
):
    await websocket_connections.connect(room and room.id, websocket)
    if room is None:
        return

    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        websocket_connections.disconnect(room.id, websocket)
        print(f"{websocket.client} disconnected")
