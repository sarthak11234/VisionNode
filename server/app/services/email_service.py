import logging
import resend
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        if settings.RESEND_API_KEY:
            resend.api_key = settings.RESEND_API_KEY
        else:
            logger.warning("Resend API key not found. EmailService will operate in mock mode.")

    def send_email(self, to_email: str, subject: str, html_content: str):
        """
        Sends an email using Resend.
        """
        if not settings.RESEND_API_KEY:
            logger.info(f"[MOCK] Sending Email to {to_email}: Subject={subject}")
            return "mock_email_id_123"

        try:
            params = {
                "from": "SheetAgent <notifications@visionnode.ai>", # Placeholder domain
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }

            email = resend.Emails.send(params)
            logger.info(f"Email sent! ID: {email['id']}")
            return email['id']
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise e

email_service = EmailService()
