from fastapi import WebSocket, WebSocketDisconnect, WebSocketException, status


class WebSocketConnections:
    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = {}

    async def connect(self, room_id: str | None, websocket: WebSocket):
        await websocket.accept()

        if room_id is None:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="room_id does not exist",
            )

        self.connections.setdefault(room_id, [])
        self.connections[room_id].append(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket):
        room_connections: list[WebSocket] = self.connections.get(room_id)
        if room_connections is not None and websocket in room_connections:
            room_connections.remove(websocket)
            if len(room_connections) == 0:
                del self.connections[room_id]

    async def broadcast(self, data):
        for room_id, room_connections in self.connections.items():
            for websocket in room_connections.copy():
                try:
                    await websocket.send_json(data)
                except WebSocketDisconnect:
                    self.disconnect(room_id, websocket)

    async def multicast(self, data, room_id):
        room_connections: list[WebSocket] = self.connections.get(room_id)
        if room_connections is None:
            return

        for websocket in room_connections.copy():
            try:
                await websocket.send_json(data)
            except WebSocketDisconnect:
                self.disconnect(room_id, websocket)


class RoomConnection:
    def __init__(self, host_id):
        self.host_id: int = host_id
        self.websockets: list[WebSocket] = []
        self.lock = asyncio.Lock()


websocket_connections = WebSocketConnections()


def handle_websocket_message(websocket: WebSocket, message: dict) -> None:

    message_type: str = message.get("type")
    if message_type is None:
        return

    match message_type:
        case "status":
            return {"send_to": "this", "type": "status", "status": "online"}
        case "hello":
            return {
                "send_to": "room",
                "type": "hello",
                "status": f"{websocket.client.host} says hi!",
            }
