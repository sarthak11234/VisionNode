from fastapi import APIRouter, Request, Form, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.agent_log import AgentLog
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/whatsapp/status")
async def whatsapp_status(
    SmsStatus: str = Form(...),
    MessageSid: str = Form(...),
    To: str = Form(...),
    ErrorCode: str | None = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Twilio calls this when the message status changes.
    """
    logger.info(f"WhatsApp Status Update: SID={MessageSid}, Status={SmsStatus}")
    
    # 1. Map Twilio status to AgentLog status
    status_map = {
        "delivered": "success",
        "read": "success",
        "failed": "failed",
        "undelivered": "failed",
        "sent": "success"
    }
    new_status = status_map.get(SmsStatus, "pending")

    # 2. Update DB
    result = await db.execute(
        select(AgentLog).where(AgentLog.provider_message_id == MessageSid)
    )
    log_entry = result.scalar_one_or_none()
    
    if log_entry:
        log_entry.status = new_status
        if ErrorCode:
            log_entry.message = f"Twilio Error: {ErrorCode}"
        await db.commit()
    
    return {"status": "success"}

@router.post("/whatsapp/incoming")
async def whatsapp_incoming(
    Body: str = Form(...),
    From: str = Form(...),
    MessageSid: str = Form(...)
):
    """
    Twilio calls this when a user sends a message TO our WhatsApp number.
    """
    logger.info(f"Incoming WhatsApp from {From}: {Body}")
    return {"status": "success"}

@router.post("/resend")
async def resend_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Resend calls this for delivery/bounce/complaint events.
    """
    payload = await request.json()
    event_type = payload.get("type")
    data = payload.get("data", {})
    email_id = data.get("email_id")
    
    logger.info(f"Resend Webhook Event: {event_type} for Email ID {email_id}")
    
    # 1. Map Resend events to AgentLog status
    status_map = {
        "email.delivered": "success",
        "email.bounced": "failed",
        "email.complained": "failed",
        "email.delivery_delayed": "pending"
    }
    
    if event_type in status_map:
        result = await db.execute(
            select(AgentLog).where(AgentLog.provider_message_id == email_id)
        )
        log_entry = result.scalar_one_or_none()
        
        if log_entry:
            log_entry.status = status_map[event_type]
            await db.commit()
    
    return {"status": "success"}
