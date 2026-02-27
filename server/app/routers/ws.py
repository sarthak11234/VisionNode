"""
WebSocket Router — real-time sheet updates.

PROTOCOL:
  Client connects to: ws://localhost:8000/ws/sheet/{sheet_id}
  Server sends JSON events whenever rows change:
    {"event": "row_updated", "row": {...}}
    {"event": "row_created", "row": {...}}
    {"event": "row_deleted", "row_id": "..."}

  The client keeps the connection open and listens for events.
  No client-to-server messages are needed right now (one-way push).

WHY WEBSOCKETS (not SSE or polling)?
  - SSE (Server-Sent Events): Simpler, HTTP-based, one-way. Would work here
    since we only push. But WebSockets give us bidirectional capability for
    future features (collaborative editing, cursor presence).
  - Polling: Simplest but wastes bandwidth — client asks "anything new?"
    every N seconds. Terrible for real-time UX.
  - WebSockets: Persistent TCP connection, ~50 bytes overhead per message.
    Ideal for sub-100ms latency updates.
"""

import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.ws_manager import manager

router = APIRouter()


@router.websocket("/ws/sheet/{sheet_id}")
async def sheet_websocket(websocket: WebSocket, sheet_id: uuid.UUID):
    """WebSocket endpoint for real-time sheet updates.

    Clients connect here to receive live row change events.
    The connection stays open until the client disconnects.
    """
    await manager.connect(sheet_id, websocket)
    try:
        # Keep the connection alive by waiting for incoming messages.
        # We don't process them — this just prevents the connection
        # from closing. FastAPI/Starlette requires an active receive loop.
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(sheet_id, websocket)
