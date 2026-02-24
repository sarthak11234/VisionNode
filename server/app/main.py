"""
SheetAgent — FastAPI Application Entry Point

This is the root of the backend. All routers are registered here.
CORS is configured to allow the Next.js frontend to communicate.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import workspaces, sheets, rows, agent_rules, ws, webhooks

app = FastAPI(
    title="SheetAgent API",
    description="Agentic spreadsheet platform backend",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS — Cross-Origin Resource Sharing
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers — All API endpoints under /api/v1
# ---------------------------------------------------------------------------
API_PREFIX = "/api/v1"

app.include_router(workspaces.router, prefix=API_PREFIX)
app.include_router(sheets.router, prefix=API_PREFIX)
app.include_router(rows.router, prefix=API_PREFIX)
app.include_router(agent_rules.router, prefix=API_PREFIX)
app.include_router(webhooks.router, prefix=API_PREFIX)  # Webhooks prefix /api/v1/webhooks
app.include_router(ws.router)  # WebSocket — no prefix (ws://host/ws/sheet/{id})


@app.get("/health")
async def health_check():
    """Simple health check endpoint to verify the server is running."""
    return {"status": "ok", "service": "sheetagent-api"}
