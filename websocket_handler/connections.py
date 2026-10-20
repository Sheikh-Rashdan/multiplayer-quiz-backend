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


websocket_connections = WebSocketConnections()
