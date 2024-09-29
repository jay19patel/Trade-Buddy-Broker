from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from starlette.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List
from app.Core.config import setting

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


async def email_send_access_token(emails: List[str], access_token: str) -> JSONResponse:
    try:
        url_for_authentication = f"{setting.HOST_URL}auth/verify_email/verification/{access_token}"
        html = f"""
        <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Email Verification for Trade Buddy</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                        <td style="padding: 20px 0; text-align: center; background-color: #ffffff;">
                            <table role="presentation" width="100%" max-width="600px" cellspacing="0" cellpadding="0" border="0" style="margin: auto;">
                                <tr>
                                    <td style="padding: 40px 30px; background-color: #ffffff;">
                                        <h1 style="color: #333333; font-size: 24px; margin-bottom: 20px;">Email Verification for Trade Buddy</h1>
                                        <p style="color: #666666; font-size: 16px; margin-bottom: 30px;">
                                            Thank you for signing up! Please click the button below to verify your email address and complete your registration.
                                        </p>
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto;">
                                            <tr>
                                                <td style="border-radius: 4px; background-color: #007bff;">
                                                    <a href="{url_for_authentication}" target="_blank" style="border: solid 1px #007bff; border-radius: 4px; color: #ffffff; display: inline-block; font-size: 16px; font-weight: bold; padding: 12px 24px; text-align: center; text-decoration: none;">Verify Email</a>
                                                </td>
                                            </tr>
                                        </table>
                                        <p style="color: #666666; font-size: 14px; margin-top: 30px;">
                                            If you didn't create an account, you can safely ignore this email.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
        """
        message = MessageSchema(
            subject="Trade Buddy by Jay Patel",
            recipients=emails,
            body=html,
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        print(f"EMAIL Send success to {emails}")
    except Exception as e:
        print("Something went wrong", e)

