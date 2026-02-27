import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.gmail_address = settings.GMAIL_ADDRESS
        self.gmail_password = settings.GMAIL_APP_PASSWORD

    def send_email(self, to_email: str, subject: str, html_content: str):
        """
        Sends an email using standard Python smtplib and a Gmail App Password,
        costing $0 and requiring no domain registration.
        """
        if not self.gmail_address or not self.gmail_password:
            logger.info(f"[MOCK] Sending Email via SMTP to {to_email}: Subject={subject}")
            return "mock_smtp_id_123"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"SheetAgent <{self.gmail_address}>"
        msg["To"] = to_email

        # Attach the HexaCore stylized HTML template
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

        try:
            # Connect to Gmail's SMTP server securely over SSL
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.gmail_address, self.gmail_password)
                server.sendmail(self.gmail_address, to_email, msg.as_string())
                
            logger.info(f"Email sent securely to {to_email} via Gmail SMTP")
            return "smtp_success_id"
            
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {str(e)}")
            raise e

email_service = EmailService()
