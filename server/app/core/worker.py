from celery import Celery
from app.core.config import settings

# Initialize Celery app
celery_app = Celery(
    "sheetagent_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Optional config for Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
import asyncio

@celery_app.task(name="execute_agent_rule")
def execute_agent_rule(row_id: str, rule_id: str):
    """
    Background task to evaluate an agent rule against a specific row.
    This task spins up the LangGraph orchestration.
    """
    import logging
    from app.agents.workflow import agent_app
    from app.core.database import SessionLocal
    from app.models.row import Row
    from app.models.agent_rule import AgentRule
    from app.models.agent_log import AgentLog
    
    logger = logging.getLogger(__name__)
    logger.info(f"Executing agent rule {rule_id} for row {row_id}")
    
    # We must run DB queries synchronously in the Celery worker, 
    # but our DAOs are async, so we use asyncio.run
    async def run_workflow():
        async with SessionLocal() as db:
            row = await db.get(Row, row_id)
            rule = await db.get(AgentRule, rule_id)
            
            if not row or not rule:
                logger.error("Row or Rule not found")
                return {"status": "failed", "error": "Not Found"}
                
            # Initialize the LangGraph state
            state = {
                "rule_id": str(rule.id),
                "row_id": str(row.id),
                "row_data": row.data,
                "action_type": rule.action_type,
                "trigger_column": rule.trigger_column,
                "trigger_value": rule.trigger_value,
            }
            
            # Execute LangGraph workflow
            result_state = await agent_app.ainvoke(state)
            
            # Log the outcome
            log = AgentLog(
                rule_id=rule.id,
                row_id=row.id,
                status=result_state.get("status", "unknown"),
                message=result_state.get("error_message") or str(result_state.get("action_result", "")),
            )
            db.add(log)
            await db.commit()
            return result_state

    return asyncio.run(run_workflow())


