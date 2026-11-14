import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from abc import ABC, abstractmethod
from typing import Optional, Dict

from config import (
    EMAIL_PROVIDER,
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SENDER_EMAIL,
    MAILGUN_API_KEY,
    MAILGUN_DOMAIN,
)

class EmailProvider(ABC):
    """Abstract base class for email provider implementations."""

    @abstractmethod
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
        """
        Sends an email.
        
        :param to_email: Recipient email address.
        :param subject: Email subject line.
        :param html_body: HTML content of the email.
        :param text_body: Plain text content of the email (optional fallback).
        :return: True if sent successfully, False otherwise.
        """
        pass

class SMTPEmailProvider(EmailProvider):
    """Implementation for sending emails via standard SMTP."""

    def send_email(self, to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email

        if not text_body:
            text_body = "Please use an HTML capable email client to view this message."

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
            return True
        except Exception:
            return False

class MailgunEmailProvider(EmailProvider):
    """Implementation for sending emails via Mailgun API."""

    def send_email(self, to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
        api_url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
        
        data = {
            "from": SENDER_EMAIL,
            "to": to_email,
            "subject": subject,
            "html": html_body,
        }
        
        if text_body:
            data["text"] = text_body

        try:
            response = requests.post(
                api_url,
                auth=("api", MAILGUN_API_KEY),
                data=data
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

def get_email_provider() -> EmailProvider:
    """
    Factory function to retrieve the configured email provider.
    
    :return: An instance of a concrete EmailProvider class.
    """
    if EMAIL_PROVIDER == "mailgun":
        return MailgunEmailProvider()
    elif EMAIL_PROVIDER == "smtp":
        return SMTPEmailProvider()
    else:
        raise ValueError(f"Unsupported Email Provider configured: {EMAIL_PROVIDER}")

if __name__ == "__main__":
    # Small self-test/example if run directly
    print(f"Configured Provider: {EMAIL_PROVIDER}")
    
    try:
        provider = get_email_provider()
        print(f"Provider class: {provider.__class__.__name__}")
        
        # Uncomment below to actually attempt sending (requires valid config)
        # success = provider.send_email(
        #     to_email="test@example.com",
        #     subject="Test Email",
        #     html_body="<h1>Hello</h1><p>This is a test.</p>"
        # )
        # print(f"Send status: {success}")
        
    except Exception as e:
        print(f"Configuration Error: {e}")
