import os
import time
import logging
from dotenv import load_dotenv

from messaging.google_handler import GoogleHandler
from messaging.whatsapp_bot import WhatsAppBot
from messaging.mail_sender import MailSender

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing VisionNode Messaging Module...")
    load_dotenv()
    
    # 1. Initialization
    CREDENTIALS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'visionnode-creds.json'))
    SPREADSHEET_ID = os.environ.get("GOOGLE_SPREADSHEET_ID", "1jHXw5PGeFdnWx2ZOZ43VjWdOalHs5AR2QDznv3D1PHE")
    SHEET_RANGE = "Sheet1!A:E" # Assuming Name, Phone, Email, Message, Status
    
    GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
    GMAIL_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
    
    SESSION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sessions', 'whatsapp_user_data'))
    if not os.path.exists(SESSION_DIR):
        os.makedirs(SESSION_DIR)

    # 2. Setup Handlers
    try:
        google = GoogleHandler(credentials_path=CREDENTIALS_FILE, spreadsheet_id=SPREADSHEET_ID)
    except Exception as e:
        logger.error(f"Setup Error: {e}")
        return

    mailer = MailSender(gmail_address=GMAIL_ADDRESS, gmail_app_password=GMAIL_PASSWORD)
    wa_bot = WhatsAppBot(session_dir=SESSION_DIR)
    
    # 3. Start WhatsApp Session
    wa_bot.start_session(visible=True) 

    # 4. Processing Loop
    try:
        logger.info("Checking Google Sheets for pending messages...")
        pending_rows = google.fetch_pending_rows(sheet_range=SHEET_RANGE)

        
        for row in pending_rows:
            row_idx = row['_row_index']
            name = row.get('Name', 'User')
            phone = row.get('Phone', '').strip()
            email = row.get('Email', '').strip()
            message_body = row.get('Message', f"Hello {name}, this is an automated message from VisionNode!")
            
            logger.info(f"Processing row {row_idx} for {name}...")
            
            # Send WhatsApp
            wa_sent = False
            if phone:
                wa_sent = wa_bot.send_message(phone_number=phone, message=message_body)
                
            # Send Email
            email_sent = False
            if email:
                email_sent = mailer.send_email(
                    to_email=email, 
                    subject="VisionNode Update", 
                    html_content=f"<p>{message_body.replace(chr(10), '<br>')}</p>"
                )
            
            # Update Sheets for Idempotency
            if wa_sent or email_sent:
                # Assuming 'Status' is in Column E
                google.update_row_status(sheet_name="Sheet1", row_index=row_idx, status_letter_column="E", new_status="Sent")
            else:
                logger.warning(f"Could not send messages for row {row_idx}. Missing contact info or error occurred.")

    finally:
        logger.info("Closing WhatsApp Bot session...")
        wa_bot.close()

if __name__ == "__main__":
    main()
