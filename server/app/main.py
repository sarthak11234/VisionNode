"""
SheetAgent — FastAPI Application Entry Point

This is the root of the backend. All routers are registered here.
CORS is configured to allow the Next.js frontend to communicate.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title="SheetAgent API",
    description="Agentic spreadsheet platform backend",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS — Cross-Origin Resource Sharing
# ---------------------------------------------------------------------------
# Why: The Next.js frontend (localhost:3000) and FastAPI backend (localhost:8000)
# run on different ports. Browsers block cross-origin requests by default.
# CORS headers tell the browser "it's okay, this origin is allowed."
#
# Alternative: Serve both from the same origin via a reverse proxy (nginx).
#   Pros: No CORS needed. Cons: More complex dev setup.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Simple health check endpoint to verify the server is running."""
    return {"status": "ok", "service": "sheetagent-api"}
