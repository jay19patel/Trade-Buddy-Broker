from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from starlette.responses import JSONResponse
from pydantic import EmailStr
from typing import List
import os

conf = ConnectionConfig(
    MAIL_USERNAME="developer.jay19@gmail.com",
    MAIL_PASSWORD="gtlgweqwhtizargb",
    MAIL_FROM="developer.jay19@gmail.com",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def email_send_for_ticket_replay(emails: List[str],data:dict) -> JSONResponse:
    try:
        support_website = ""
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Trade Buddy Ticket Reply</title>
            <style>
                @media (prefers-color-scheme: dark) {{
                    body {{ background-color: #1a1a1a; color: #e0e0e0; }}
                    .container{{ background-color: #333; box-shadow: 0 0 10px rgba(255, 255, 255, 0.1); }}
                    .ticket-label {{ background-color: #2a2a2a; }}
                    .ticket-value {{ background-color: #222; }}
                    a {{ color: #bb86fc; }}
                }}
            </style>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f0f0f0; color: #333;">
            <div class="container" style="max-width: 600px; margin: 20px auto; padding: 20px; background-color: #ffffff; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); border-radius: 8px;">
                <h2 style="color: #00aaff; text-align: center; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #00aaff;">Trade Buddy Ticket Reply</h2>
                
                <div style="margin-bottom: 20px; border: 2px solid #ccc; border-radius: 8px; overflow: hidden;">
                    <div style="display: flex; flex-wrap: wrap; border-bottom: 1px solid #ccc;">
                        <div style="flex: 1 0 30%; padding: 10px; background-color: #e0e0e0; font-weight: bold;">Ticket ID:</div>
                        <div style="flex: 1 0 70%; padding: 10px; background-color: #f5f5f5;">{data.get("ticket_id", "").replace('"', '')}</div>
                    </div>
                    <div style="display: flex; flex-wrap: wrap; border-bottom: 1px solid #ccc;">
                        <div style="flex: 1 0 30%; padding: 10px; background-color: #e0e0e0; font-weight: bold;">Subject:</div>
                        <div style="flex: 1 0 70%; padding: 10px; background-color: #f5f5f5;">{data.get("ticket_subject", "").replace('"', '')}</div>
                    </div>
                    <div style="display: flex; flex-wrap: wrap;">
                        <div style="flex: 1 0 30%; padding: 10px; background-color: #e0e0e0; font-weight: bold;">Message:</div>
                        <div style="flex: 1 0 70%; padding: 10px; background-color: #f5f5f5;">{data.get("ticket_message", "").replace('"', '')}</div>
                    </div>
                </div>
                
                <div style="border: 2px solid #ccc; border-radius: 8px; padding: 15px; background-color: #e0e0e0; margin-bottom: 20px;">
                    <div style="font-weight: bold; margin-bottom: 10px; color: #00aaff;">Dear Trade Buddy User</div>
                    <p>{data.get("ticket_reply", "").replace('"', '')}</p>
                    <p>Thank you for contacting our support team.</p>
                </div>

                <div style="text-align: center; font-size: 14px; border-top: 1px solid #ccc; padding-top: 10px;">
                    <span>Sent by: Jay Patel</span> |
                    <span>Contact: 7069668308</span> |
                    <span>Email: developer.jay19@gmail.com</span> |
                    <span>For more information, visit our <a href="{support_website}" style="color: #00aaff; text-decoration: none;">Support Center</a></span>
                </div>
            </div>
        </body>
        </html>
        """
        message = MessageSchema(
            subject=f"Trade Buddy by Jay Patel for your Issue ID #{data.get("ticket_id")}",
            recipients=emails,
            body=html,
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message)
        print(f"EMAIL sent successfully to {emails}")
    except Exception as e:
        print("Something went wrong", e)
