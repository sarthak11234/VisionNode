import logging
from twilio.rest import Client
from app.core.config import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        else:
            logger.warning("Twilio credentials not found. WhatsAppService will operate in mock mode.")

    def send_template_message(self, to_number: str, template_id: str, variables: list[str]):
        """
        Sends a WhatsApp message using a pre-approved Twilio Content Template.
        Note: requires Twilio Content API setup.
        """
        if not self.client:
            logger.info(f"[MOCK] Sending WhatsApp template {template_id} to {to_number} with vars {variables}")
            return "mock_sid_123"

        try:
            # Format: 'whatsapp:+123456789'
            formatted_to = f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number
            formatted_from = f"whatsapp:{settings.TWILIO_WHATSAPP_FROM}" if not settings.TWILIO_WHATSAPP_FROM.startswith("whatsapp:") else settings.TWILIO_WHATSAPP_FROM

            message = self.client.messages.create(
                from_=formatted_from,
                to=formatted_to,
                # Twilio Content API approach
                content_sid=template_id,
                content_variables=str(variables) # Simplified for now
            )
            logger.info(f"WhatsApp message sent! SID: {message.sid}")
            return message.sid
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            raise e

    def send_freeform_message(self, to_number: str, body: str):
        """
        Sends a freeform message (only works within 24hr window).
        """
        if not self.client:
            logger.info(f"[MOCK] Sending WhatsApp message to {to_number}: {body}")
            return "mock_sid_456"

        try:
            formatted_to = f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number
            formatted_from = f"whatsapp:{settings.TWILIO_WHATSAPP_FROM}" if not settings.TWILIO_WHATSAPP_FROM.startswith("whatsapp:") else settings.TWILIO_WHATSAPP_FROM

            message = self.client.messages.create(
                from_=formatted_from,
                to=formatted_to,
                body=body
            )
            return message.sid
        except Exception as e:
            logger.error(f"Failed to send freeform WhatsApp message: {str(e)}")
            raise e

whatsapp_service = WhatsAppService()
