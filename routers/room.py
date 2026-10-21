import asyncio
import secrets
from string import ascii_uppercase

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

import storage.room as storage
from database.db import get_db
from database.models import Quiz, Room, User
from models.room import RoomCreate, RoomModel
from routers.quiz import validate_quiz, validate_quiz_belongs_to_user
from routers.user import get_current_user
from websocket_handler.connections import (
    handle_websocket_message,
    perform_database_operation,
    websocket_connections,
)

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
    websocket: WebSocket,
    room: Room = Depends(validate_optional_room),
    user: User = Depends(get_current_user),
):
    room_exists = room is not None
    room_id = room.id if room_exists else None
    user_id = user.id
    is_host = (room.host_id == user_id) if room_exists else False
    quiz_started = room.status == "ongoing" if room_exists else False
    duplicate_user_id = (user_id in room.player_ids) if room_exists else False

    await websocket_connections.connect(
        room_id, websocket, user_id, is_host, quiz_started, duplicate_user_id
    )
    if room is None:
        return

    lock: asyncio.Lock = websocket_connections.get_lock(room_id)

    try:
        while True:
            message: dict = await websocket.receive_json()
            response = await run_in_threadpool(
                handle_websocket_message, websocket=websocket, message=message
            )

            response_type: str = response.get("type")
            if response_type is None:
                raise ValueError("response must have a type")

            host_control_error = {
                "send_to": "this",
                "type": "error",
                "error": "only host can control the room",
            }

            match response_type:
                case "update":
                    async with lock:
                        room = await run_in_threadpool(
                            perform_database_operation,
                            operation=storage.get_room,
                            room_id=room_id,
                        )
                    response["room"] = room.to_json()
                case "next_question":
                    if is_host:
                        async with lock:
                            question_index = await run_in_threadpool(
                                perform_database_operation,
                                operation=storage.next_question,
                                room_id=room_id,
                            )
                        if question_index is None:
                            response = {
                                "send_to": "this",
                                "type": "error",
                                "error": "quiz is not ongoing",
                            }
                        elif question_index >= 0:
                            response["question_index"] = question_index
                        else:
                            response = {
                                "send_to": "room",
                                "type": "end_quiz",
                                "status": "finished",
                            }
                    else:
                        response = host_control_error
                case "start_quiz":
                    if is_host:
                        async with lock:
                            status = await run_in_threadpool(
                                perform_database_operation,
                                operation=storage.start_quiz,
                                room_id=room_id,
                            )
                        if status == None:
                            response = {
                                "send_to": "this",
                                "type": "error",
                                "error": "failed to start quiz",
                            }
                    else:
                        response = host_control_error

            send_to = response.pop("send_to")
            match send_to:
                case "this":
                    await websocket.send_json(response)
                case "room":
                    await websocket_connections.multicast(response, room.id, user_id)

    except WebSocketDisconnect:
        await websocket_connections.disconnect(room.id, websocket, user_id)
