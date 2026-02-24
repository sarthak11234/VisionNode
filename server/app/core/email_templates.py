"""
HexaCore Dark Theme Email Templates.
These templates follow the design.txt aesthetic:
Background: #0B0B0B, Accent: #0905FE, Text: #B0B0B0
"""

def get_base_template(content_html: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                background-color: #0B0B0B;
                color: #B0B0B0;
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 40px;
            }}
            .card {{
                background: rgba(26, 26, 46, 0.8);
                border: 1px solid #0905FE;
                border-radius: 12px;
                padding: 30px;
                max-width: 600px;
                margin: 0 auto;
                box-shadow: 0 4px 15px rgba(9, 5, 254, 0.2);
            }}
            .header {{
                font-family: 'Montserrat', sans-serif;
                color: #FFFFFF;
                font-size: 24px;
                margin-bottom: 20px;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            .button {{
                display: inline-block;
                background-color: #0905FE;
                color: #FFFFFF;
                padding: 12px 24px;
                border-radius: 6px;
                text-decoration: none;
                margin-top: 20px;
                font-weight: bold;
                text-align: center;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 12px;
                color: #4A63C6;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">SheetAgent Notification</div>
            {content_html}
            <div class="footer">
                &copy; 2026 SheetAgent — HexaCore Intelligence Systems
            </div>
        </div>
    </body>
    </html>
    """

def get_status_update_email(name: str, status: str, sheet_name: str) -> str:
    content = f"""
    <p>Hello <strong>{name}</strong>,</p>
    <p>Your status in <strong>{sheet_name}</strong> has been updated to:</p>
    <h2 style="color: #00FFC2;">{status}</h2>
    <p>The AI Agent has processed this change and notified all relevant stakeholders.</p>
    <a href="#" class="button">View Sheet</a>
    """
    return get_base_template(content)

def get_event_invite_email(name: str, event_name: str, invite_link: str) -> str:
    content = f"""
    <p>Hi {name}!</p>
    <p>You have been invited to join <strong>{event_name}</strong>.</p>
    <p>Click the button below to accept your invitation and join the workspace.</p>
    <a href="{invite_link}" class="button">Accept Invitation</a>
    """
    return get_base_template(content)
