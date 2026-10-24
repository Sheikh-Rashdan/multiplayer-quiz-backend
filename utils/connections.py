import asyncio
from collections.abc import Callable
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect, WebSocketException, status
from starlette.websockets import WebSocketDisconnected

import storage.room as storage
from database.db import SessionLocal


class WebSocketConnections:
    def __init__(self):
        self.connections: dict[str, RoomConnection] = {}

    async def connect(
        self,
        room_id: str | None,
        websocket: WebSocket,
        user_id: int | None,
        is_host: bool,
        quiz_started: bool,
        duplicate_user_id: bool,
    ) -> None:
        await websocket.accept()

        if room_id is None:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="room does not exist",
            )
        if quiz_started:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="quiz already in progress",
            )
        if duplicate_user_id:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="user already in room",
            )

        if is_host:
            self.connections[room_id] = RoomConnection(user_id)

        room_connection: RoomConnection | None = self.connections.get(room_id)
        if room_connection is None:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION, reason="host not connected"
            )

        if not is_host:
            player_ids = perform_database_operation(
                operation=storage.add_player, room_id=room_id, player_id=user_id
            )

            response = {"type": "player_joined", "player_ids": player_ids}
            await websocket_connections.multicast(response, room_id, user_id)

        room_connection.websockets[websocket] = user_id

    async def disconnect(self, room_id: str, websocket: WebSocket) -> None:
        room_connection: RoomConnection | None = self.connections.get(room_id)
        if room_connection is not None and websocket in room_connection.websockets:
            user_id = room_connection.websockets.pop(websocket)

            player_ids = perform_database_operation(
                operation=storage.remove_player, room_id=room_id, player_id=user_id
            )

            if player_ids is not None:
                response = {"type": "player_left", "player_ids": player_ids}
                await websocket_connections.multicast(response, room_id, user_id)

            if room_connection.host_id == user_id:
                await self.disconnect_all(room_id)
                return

            if len(room_connection.websockets) == 0:
                del self.connections[room_id]

            return player_ids

    async def disconnect_all(self, room_id: str):
        room_connection: RoomConnection | None = self.connections.get(room_id)
        if room_connection is not None:
            for websocket in room_connection.websockets.copy():
                await websocket.close(
                    code=status.WS_1001_GOING_AWAY, reason="host disconnected"
                )
                room_connection.websockets.pop(websocket)

        del self.connections[room_id]

        perform_database_operation(operation=storage.delete_room, room_id=room_id)

    async def broadcast(self, data: dict, user_id: int | None = None) -> None:
        for room_id, room_connection in self.connections.items():
            for websocket in room_connection.websockets.copy():
                try:
                    await websocket.send_json(data)
                except WebSocketDisconnect, WebSocketDisconnected:
                    await self.disconnect(room_id, websocket)

    async def multicast(
        self, data: dict, room_id: int, user_id: int | None = None
    ) -> None:
        room_connection: RoomConnection | None = self.connections.get(room_id)
        if room_connection is None:
            return

        for websocket in room_connection.websockets.copy():
            try:
                await websocket.send_json(data)
            except WebSocketDisconnect, WebSocketDisconnected:
                await self.disconnect(room_id, websocket)

    def get_lock(self, room_id: int) -> asyncio.Lock:
        room_connection: RoomConnection | None = self.connections.get(room_id)
        if room_connection is None:
            raise ValueError(f"invalid room_id {room_id}")
        return room_connection.lock


class RoomConnection:
    def __init__(self, host_id):
        self.host_id: int = host_id
        self.websockets: dict[WebSocket, int] = {}
        self.lock = asyncio.Lock()


websocket_connections = WebSocketConnections()


def handle_websocket_message(websocket: WebSocket, message: dict) -> None:

    message_type: str = message.get("type")
    if message_type is None:
        return {"send_to": "this", "type": "error", "error": "missing type"}

    match message_type:
        case "update":
            return {"send_to": "this", "type": "update", "room": None}
        case "next_question":
            return {
                "send_to": "room",
                "type": "next_question",
                "question_index": None,
            }
        case "start_quiz":
            return {
                "send_to": "room",
                "type": "start_quiz",
                "status": "ongoing",
            }
        case "end_session":
            return {"send_to": "room", "type": "end_session"}
        case "confirm_answer":
            question_index: int | None = message.get("question_index")
            answer_index: int | None = message.get("answer_index")

            parameters = (question_index, answer_index)
            failure = any(parameter is None for parameter in parameters)

            if failure:
                return {
                    "send_to": "this",
                    "type": "error",
                    "error": "message must include question_index and answer_index",
                }
            return {
                "send_to": "this",
                "type": "confirm_answer",
                "question_index": question_index,
                "answer_index": answer_index,
            }

    return {"send_to": "this", "type": "error", "error": "invalid type"}


def perform_database_operation(operation: Callable, **params) -> Any:
    with SessionLocal() as db:
        return operation(db, **params)
