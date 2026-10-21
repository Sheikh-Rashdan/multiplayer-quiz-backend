import asyncio
from collections.abc import Callable
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect, WebSocketException, status

from database.db import SessionLocal


class WebSocketConnections:
    def __init__(self):
        self.connections: dict[str, RoomConnection] = {}

    async def connect(
        self, room_id: str | None, websocket: WebSocket, host_id: int | None = None
    ) -> None:
        await websocket.accept()

        if room_id is None:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="room_id does not exist",
            )

        if host_id is not None:
            self.connections[room_id] = RoomConnection(host_id)

        room_connection: RoomConnection | None = self.connections.get(room_id)
        if room_connection is None:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION, reason="host not connected"
            )
        room_connection.websockets.append(websocket)

    async def disconnect(
        self, room_id: str, websocket: WebSocket, user_id: int | None = None
    ) -> None:
        room_connection: RoomConnection | None = self.connections.get(room_id)
        if room_connection is not None and websocket in room_connection.websockets:
            room_connection.websockets.remove(websocket)

            if room_connection.host_id == user_id:
                await self.disconnect_all(room_id)
            elif len(room_connection.websockets) == 0:
                del self.connections[room_id]

    async def disconnect_all(self, room_id: str):
        room_connection: RoomConnection | None = self.connections.get(room_id)
        if room_connection is not None:
            for websocket in room_connection.websockets.copy():
                await websocket.close(
                    code=status.WS_1001_GOING_AWAY, reason="host disconnected"
                )
                room_connection.websockets.remove(websocket)

        del self.connections[room_id]

    async def broadcast(self, data: dict, user_id: int | None = None) -> None:
        for room_id, room_connection in self.connections.items():
            for websocket in room_connection.websockets.copy():
                try:
                    await websocket.send_json(data)
                except WebSocketDisconnect:
                    await self.disconnect(room_id, websocket, user_id)

    async def multicast(
        self, data: dict, room_id: int, user_id: int | None = None
    ) -> None:
        room_connection: RoomConnection | None = self.connections.get(room_id)
        if room_connection is None:
            return

        for websocket in room_connection.websockets.copy():
            try:
                await websocket.send_json(data)
            except WebSocketDisconnect:
                await self.disconnect(room_id, websocket, user_id)

    def get_lock(self, room_id: int) -> asyncio.Lock:
        room_connection: RoomConnection | None = self.connections.get(room_id)
        if room_connection is None:
            raise ValueError(f"Invalid room_id {room_id}")
        return room_connection.lock


class RoomConnection:
    def __init__(self, host_id):
        self.host_id: int = host_id
        self.websockets: list[WebSocket] = []
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
        case "hello":
            return {
                "send_to": "room",
                "type": "hello",
                "status": f"{websocket.client.host} says hi!",
            }

    return {"send_to": "this", "type": "error", "error": "invalid type"}


def perform_database_operation(operation: Callable, **params) -> Any:
    with SessionLocal() as db:
        return operation(db, **params)
