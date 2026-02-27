"""
Celery Application Configuration.

We use Celery as our async task queue to offload heavy agent processing
(LangGraph + LLM calls + External API requests) from the main FastAPI thread.
This ensures the web server stays perfectly responsive under load.

Redis is used as both the message broker (queue) and the result backend.
"""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "sheetagent",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.agent_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # A task might take seconds to minutes if making LLM calls
    task_time_limit=300, 
    task_soft_time_limit=270,
)
