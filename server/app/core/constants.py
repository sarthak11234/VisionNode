"""
Centralized constants for the SheetAgent platform.
"""

# WhatsApp Twilio Content SIDs (Placeholders)
# In production, these would be the IDs from the Twilio Content Editor.
WHATSAPP_TEMPLATES = {
    "welcome": "HX1234567890abcdef1234567890abcdef",
    "event_invite": "HXabcdef1234567890abcdef1234567890",
    "status_update": "HX0987654321fedcba0987654321fedcba",
}

# Agent Action Types
ACTION_TYPE_WHATSAPP = "send_whatsapp"
ACTION_TYPE_EMAIL = "send_email"
ACTION_TYPE_GROUP = "create_whatsapp_group"
