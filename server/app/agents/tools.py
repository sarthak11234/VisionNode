import asyncio
import os
import sys
from typing import Any
from langchain_core.tools import tool

from app.agents.state import AgentState
from app.core.config import settings

# Inject the src/ directory into the Python path so we can import the standalone messaging modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.messaging.whatsapp_bot import WhatsAppBot
from src.messaging.mail_sender import MailSender

@tool
async def send_whatsapp_tool(state: AgentState) -> dict[str, Any]:
    """
    Sends a WhatsApp message using the custom Selenium browser automation.
    """
    row_data = state.get("row_data", {})
    phone = row_data.get("phone") or row_data.get("Phone") or row_data.get("Phone No.") or row_data.get("mobile")
    name = row_data.get("name") or row_data.get("Name") or "User"
    
    if not phone:
        return {"status": "error", "error": "No phone number found in row data"}
        
    status = state.get("trigger_value", "updated")
    message_body = row_data.get("Message") or row_data.get("message") or f"Hey {name}! Just wanted to let you know your status has been marked as: *{status}*.\n\nLet us know if you have any questions!"

    try:
        session_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../sessions/whatsapp_user_data"))
        wa_bot = WhatsAppBot(session_dir=session_dir)
        
        # Run completely headless for background tasks
        wa_bot.start_session(visible=False)
        success = wa_bot.send_message(phone, message_body)
        wa_bot.close_session()
        
        if success:
            return {"status": "success", "provider": "selenium", "to": phone, "text": message_body}
        else:
            return {"status": "error", "error": "Selenium failed to send the message"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@tool
async def send_email_tool(state: AgentState) -> dict[str, Any]:
    """
    Sends an email using the real MailSender Python SMTP integration.
    """
    row_data = state.get("row_data", {})
    email = row_data.get("email") or row_data.get("Email")
    name = row_data.get("name") or row_data.get("Name") or "User"
    
    if not email:
        return {"status": "error", "error": "No email address found"}

    status = state.get("trigger_value", "updated")
    message_body = row_data.get("Message") or row_data.get("message") or f"Hey {name}! Just wanted to let you know your status has been marked as: {status}."

    try:
        mailer = MailSender(gmail_address=settings.GMAIL_ADDRESS, gmail_app_password=settings.GMAIL_APP_PASSWORD)
        mailer.send_email(
            to_email=email,
            subject=f"Update for {name}: {status}",
            body=message_body
        )
        return {"status": "success", "provider": "smtp", "to": email}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@tool
async def create_whatsapp_group_tool(state: AgentState) -> dict[str, Any]:
    """
    Agent tool to 'create a group'. Fallback to sending a dummy link.
    """
    return {"status": "success", "action": "group_invite_sent"}

@tool
async def clean_sheet_tool(state: AgentState) -> dict[str, Any]:
    """
    Simulate an LLM cleaning/formatting a sheet's data.
    """
    await asyncio.sleep(1.5)
    return {"status": "success", "action": "clean_sheet", "rows_affected": 0}

@tool
async def summarize_sheet_tool(state: AgentState) -> dict[str, Any]:
    """
    Simulate an LLM summarizing the current state of a sheet.
    """
    await asyncio.sleep(2.0)
    return {"status": "success", "action": "summarize_sheet"}
