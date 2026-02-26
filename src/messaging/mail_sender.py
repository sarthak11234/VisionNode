import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class MailSender:
    def __init__(self, gmail_address: str, gmail_app_password: str):
        self.gmail_address = gmail_address
        self.gmail_password = gmail_app_password

    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Sends an email using standard Python smtplib and a Gmail App Password.
        """
        if not self.gmail_address or not self.gmail_password:
            logger.error("Missing Gmail credentials.")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"VisionNode <{self.gmail_address}>"
        msg["To"] = to_email

        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.gmail_address, self.gmail_password)
                server.sendmail(self.gmail_address, to_email, msg.as_string())
                
            logger.info(f"Email successfully sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
