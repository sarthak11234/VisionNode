"""
WebSocket Connection Manager — tracks active connections per sheet.

ALGORITHM: Room-based pub/sub (in-memory)
  Each sheet_id is a "room". When a client connects to /ws/sheet/{id},
  they join that room. When any row in that sheet changes, we broadcast
  to everyone in the room.

  Data structure: dict[UUID, list[WebSocket]]
    Key   = sheet_id
    Value = list of active WebSocket connections

WHY IN-MEMORY (not Redis pub/sub)?
  For a single-server setup, an in-memory dict is the simplest and
  fastest approach — zero latency, no external dependency.

  LIMITATION: Only works on ONE server instance. If you scale to
  multiple FastAPI workers/pods, connections on server A won't see
  broadcasts from server B.

  UPGRADE PATH (when scaling):
    1. Redis Pub/Sub  — publish events to a Redis channel, each server
       subscribes and forwards to its local WebSocket clients. Adds ~1ms
       latency. Most common production pattern.
    2. Supabase Realtime — managed WebSocket service built on PostgreSQL
       LISTEN/NOTIFY. Zero code but vendor lock-in.
    3. NATS / RabbitMQ — heavier but supports more complex routing patterns.

  We start simple and upgrade to Redis pub/sub when we add Celery workers
  (they already depend on Redis).
"""

import uuid
from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections grouped by sheet_id."""

    def __init__(self) -> None:
        # dict[sheet_id] → list of connected WebSocket clients
        self._rooms: dict[uuid.UUID, list[WebSocket]] = {}

    async def connect(self, sheet_id: uuid.UUID, websocket: WebSocket) -> None:
        """Accept a WebSocket and add it to the sheet's room."""
        await websocket.accept()
        if sheet_id not in self._rooms:
            self._rooms[sheet_id] = []
        self._rooms[sheet_id].append(websocket)

    def disconnect(self, sheet_id: uuid.UUID, websocket: WebSocket) -> None:
        """Remove a WebSocket from the sheet's room."""
        if sheet_id in self._rooms:
            self._rooms[sheet_id].remove(websocket)
            # Clean up empty rooms to avoid memory leaks
            if not self._rooms[sheet_id]:
                del self._rooms[sheet_id]

    async def broadcast(self, sheet_id: uuid.UUID, message: dict) -> None:
        """Send a JSON message to all clients connected to a sheet.

        If a client has disconnected unexpectedly, we catch the error
        and remove them (stale connection cleanup).
        """
        if sheet_id not in self._rooms:
            return

        stale: list[WebSocket] = []
        for ws in self._rooms[sheet_id]:
            try:
                await ws.send_json(message)
            except Exception:
                stale.append(ws)

        # Remove stale connections
        for ws in stale:
            self.disconnect(sheet_id, ws)

    def active_count(self, sheet_id: uuid.UUID) -> int:
        """Number of active connections for a sheet."""
        return len(self._rooms.get(sheet_id, []))

    def total_connections(self) -> int:
        """Total active connections across all sheets."""
        return sum(len(conns) for conns in self._rooms.values())


# Singleton instance — shared across the app
manager = ConnectionManager()
