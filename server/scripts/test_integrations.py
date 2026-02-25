import asyncio
import os
import sys

# Add the server directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.whatsapp_service import whatsapp_service
from app.services.email_service import email_service
from app.core.config import settings

async def main():
    print("========================================")
    print("Integration Verification Script")
    print("========================================")

    # 1. Test WhatsApp via WAHA
    print("\n[1] Testing WhatsApp (WAHA)...")
    test_phone = input("Enter a phone number to send a test WhatsApp message to (e.g., +1234567890): ").strip()
    if test_phone:
        try:
            print(f"Sending WAHA POST request to {settings.WAHA_BASE_URL}...")
            # Note: This has a Jitter-delay so it will pause for a few seconds.
            msg_id = whatsapp_service.send_freeform_message(
                to_number=test_phone,
                body="Hello from SheetAgent! 🚀 This is a test message from your 100% free WAHA integration."
            )
            print(f"✅ WhatsApp Success! Message ID: {msg_id}")
        except Exception as e:
            print(f"❌ WhatsApp Failed: {e}")
            print(f"   -> Make sure you ran 'docker compose up -d waha' and scanned the QR code at http://localhost:3001")
    else:
        print("Skipping WhatsApp check.")

    # 2. Test Email via SMTP
    print("\n[2] Testing Email (Gmail SMTP)...")
    test_email = input("Enter an email address to send a test email to: ").strip()
    if test_email:
        if not settings.GMAIL_ADDRESS or not settings.GMAIL_APP_PASSWORD:
            print("❌ Email Failed: GMAIL_ADDRESS or GMAIL_APP_PASSWORD is missing in your .env file.")
        else:
            try:
                print("Sending securely via smtp.gmail.com:465...")
                html_body = "<h2>SheetAgent Test</h2><p>This is a test email sent using standard Python smtplib and a Gmail App Password.</p>"
                res = email_service.send_email(
                    to_email=test_email,
                    subject="Test Email from SheetAgent",
                    html_content=html_body
                )
                if res.startswith("mock_"):
                    print("⚠️ Email service ran in MOCK mode (credentials missing).")
                else:
                    print(f"✅ Email Success!")
            except Exception as e:
                print(f"❌ Email Failed: {e}")
                print("   -> Did you generate a Gmail App Password correctly? Standard Gmail passwords do not work if 2FA is active.")
    else:
        print("Skipping Email check.")

    print("\nVerification finished.")

if __name__ == "__main__":
    asyncio.run(main())
