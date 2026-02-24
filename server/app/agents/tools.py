"""
Agent Communication Tools (Dummy Implementation).

Phase 4 sets up the architecture. In Phase 5, these will be replaced with
actual integration code for Twilio and Resend.
"""

import asyncio
from typing import Any
from app.agents.state import AgentState

from app.services.whatsapp_service import whatsapp_service
from app.core.constants import WHATSAPP_TEMPLATES, ACTION_TYPE_WHATSAPP, ACTION_TYPE_GROUP

async def send_whatsapp_tool(state: AgentState) -> dict[str, Any]:
    """
    Sends a WhatsApp template message using the real WhatsAppService.
    """
    # 1. Extract data from state
    row_data = state["row_data"]
    phone = row_data.get("phone") or row_data.get("Phone") or row_data.get("mobile")
    
    if not phone:
        print("[TOOL] WhatsApp Failed: No phone number found in row data")
        return {"status": "error", "error": "No phone number found"}
    
    # 2. Identify template (default to 'status_update' or look in rule/action_config)
    # For now, we simulate picking a template based on the trigger
    template_id = WHATSAPP_TEMPLATES.get("status_update")
    
    # Build variables (e.g., [Name, Status])
    name = row_data.get("name") or row_data.get("Name") or "User"
    status = state.get("trigger_value", "updated")
    variables = [name, status]

    try:
        # 3. Call Service
        # Note: WhatsAppService.send_template_message is synchronous, 
        # but we are in an async tool called by LangGraph (which is run inside asyncio.run in Celery).
        # We can run it in a threadpool to avoid blocking if needed, but for now simple call is fine.
        message_sid = whatsapp_service.send_template_message(
            to_number=phone,
            template_id=template_id,
            variables=variables
        )
        
        return {
            "status": "success",
            "provider": "twilio",
            "message_sid": message_sid,
            "to": phone,
            "template": template_id
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def create_whatsapp_group_tool(state: AgentState) -> dict[str, Any]:
    """
    Agent tool to 'create a group'. 
    Fallback: Sends a WhatsApp message with a group invite link.
    """
    row_data = state["row_data"]
    phone = row_data.get("phone") or row_data.get("Phone")
    
    if not phone:
        return {"status": "error", "error": "No phone number found"}

    # Mock Group Invite Link
    group_link = "https://chat.whatsapp.com/mock-invite-link"
    name = row_data.get("name") or row_data.get("Name") or "User"
    
    body = f"Hi {name}! You have been invited to join the group. Click here: {group_link}"

    try:
        message_sid = whatsapp_service.send_freeform_message(to_number=phone, body=body)
        return {
            "status": "success",
            "action": "group_invite_sent",
            "message_sid": message_sid,
            "group_link": group_link
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def send_email_tool(state: AgentState) -> dict[str, Any]:
    """
    Sends an email using the real EmailService and HexaCore templates.
    """
    row_data = state["row_data"]
    email = row_data.get("email") or row_data.get("Email")
    
    if not email:
        return {"status": "error", "error": "No email address found"}

    name = row_data.get("name") or row_data.get("Name") or "User"
    status = state.get("trigger_value", "updated")
    sheet_name = "Your Spreadsheet" # Could be fetched from sheet_id in state

    try:
        html_content = get_status_update_email(name, status, sheet_name)
        message_id = email_service.send_email(
            to_email=email,
            subject=f"Sheet Update: {status}",
            html_content=html_content
        )
        
        return {
            "status": "success",
            "provider": "resend",
            "message_id": message_id,
            "to": email
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

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
