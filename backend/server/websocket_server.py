"""
WebSocket Telemetry Streaming Manager
Author: Uday Kiran Jammula
"""

import logging
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("nexus.websocket")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"[WS] Client connected. Total active clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"[WS] Client disconnected. Remaining clients: {len(self.active_connections)}")

    async def broadcast_json(self, data: dict):
        if not self.active_connections:
            return

        dead_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.warning(f"[WS] Failed to send frame to client: {e}")
                dead_connections.add(connection)

        for dead in dead_connections:
            self.disconnect(dead)

ws_manager = ConnectionManager()
