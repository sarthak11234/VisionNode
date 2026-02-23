"""
Agent Communication Tools (Dummy Implementation).

Phase 4 sets up the architecture. In Phase 5, these will be replaced with
actual integration code for Twilio and Resend.
"""

import asyncio
from typing import Any
from app.agents.state import AgentState

async def send_email_tool(state: AgentState) -> dict[str, Any]:
    """
    Simulate sending an email.
    """
    # Simulate network latency
    await asyncio.sleep(1.0)
    
    email = state["row_data"].get("email", "unknown@example.com")
    print(f"[TOOL] Sending Email to {email} based on rule {state['rule_id']}")
    
    # Fake success
    return {
        "provider": "resend",
        "message_id": "eml_123456789",
        "to": email
    }

async def send_whatsapp_tool(state: AgentState) -> dict[str, Any]:
    """
    Simulate sending a WhatsApp message.
    """
    # Simulate network latency
    await asyncio.sleep(1.0)
    
    phone = state["row_data"].get("phone", "unknown number")
    print(f"[TOOL] Sending WhatsApp to {phone} based on rule {state['rule_id']}")
    
    # Fake success
    return {
        "provider": "twilio",
        "message_sid": "SM123456789abc",
        "to": phone
    }

async def clean_sheet_tool(state: AgentState) -> dict[str, Any]:
    """
    Simulate an LLM cleaning/formatting a sheet's data.
    """
    await asyncio.sleep(1.5)
    print(f"[TOOL] LLM Cleaning Sheet {state.get('sheet_id')}")
    
    return {
        "status": "success",
        "action": "clean_sheet",
        "rows_affected": 0,
        "llm_summary": "Normalized 0 phone numbers and capitalized 0 names."
    }

async def summarize_sheet_tool(state: AgentState) -> dict[str, Any]:
    """
    Simulate an LLM summarizing the current state of a sheet.
    """
    await asyncio.sleep(2.0)
    print(f"[TOOL] LLM Summarizing Sheet {state.get('sheet_id')}")
    
    return {
        "status": "success",
        "action": "summarize_sheet",
        "summary": "This sheet contains 0 records. The overall completion rate is 100%."
    }
