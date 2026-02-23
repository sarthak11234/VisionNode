"""
Celery Task Definitions for Agent Orchestration.

These tasks run in background worker processes, away from the FastAPI event loop.
Because they are synchronous Celery processes running async LangGraph and DB operations,
we instantiate their own asyncio event loop per task.
"""

import asyncio
from typing import Any
import uuid

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import async_session
from app.models.agent_rule import AgentRule
from app.models.row import Row
from app.models.agent_log import AgentLog
from app.agents.workflow import agent_app
from app.agents.state import AgentState


@celery_app.task(name="app.tasks.agent_tasks.process_agent_rule")
def process_agent_rule(rule_id_str: str, row_id_str: str) -> dict[str, Any]:
    """
    Background job triggered when a row is edited and an agent rule matches.
    """
    return asyncio.run(_process_agent_rule_async(rule_id_str, row_id_str))


async def _process_agent_rule_async(rule_id_str: str, row_id_str: str) -> dict[str, Any]:
    rule_id = uuid.UUID(rule_id_str)
    row_id = uuid.UUID(row_id_str)

    # 1. Provide context block for DB session
    async with async_session() as db:
        # Load Rule
        rule_res = await db.execute(select(AgentRule).where(AgentRule.id == rule_id))
        rule = rule_res.scalar_one_or_none()
        
        # Load Row
        row_res = await db.execute(select(Row).where(Row.id == row_id))
        row = row_res.scalar_one_or_none()
        
        if not rule or not row:
            return {"status": "skipped", "reason": "Rule or row deleted"}
            
        # Optional: Check if already succeeded to ensure idempotency
        # log_check = await db.execute(
        #     select(AgentLog).where(
        #         AgentLog.rule_id == rule_id, 
        #         AgentLog.row_id == row_id,
        #         AgentLog.status == "success"
        #     )
        # )
        # if log_check.scalar_one_or_none():
        #     return {"status": "skipped", "reason": "Already executed successfully"}
            
        # 2. Build initial LangGraph State
        initial_state: AgentState = {
            "rule_id": str(rule.id),
            "row_id": str(row.id),
            "row_data": row.data,
            "action_type": rule.action_type,
            "trigger_column": rule.trigger_column,
            "trigger_value": rule.trigger_value,
            "action_result": None,
            "status": None,
            "error_message": None
        }

        # 3. Execute LangGraph Workflow
        print(f"[{rule.action_type.upper()}] Starting workflow for Rule {str(rule.id)[:8]} on Row {str(row.id)[:8]}")
        # agent_app.ainvoke returns the final state dict
        final_state = await agent_app.ainvoke(initial_state)

        # 4. Log the result to the database
        log_entry = AgentLog(
            rule_id=rule.id,
            row_id=row.id,
            status=final_state.get("status", "unknown"),
            message=final_state.get("error_message") or str(final_state.get("action_result") or "Action executed successfully")
        )
        db.add(log_entry)
        await db.commit()
        
        return {
            "status": final_state.get("status"),
            "log_id": str(log_entry.id)
        }
