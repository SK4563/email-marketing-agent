import os
from dotenv import load_dotenv

load_dotenv()

# Project Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# API Keys and External Services
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY", "")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN", "")

# Database Configuraion
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///marketing_agent.db")

# Email Provider Settings
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "mailgun").lower()  # Options: mailgun, smtp
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@yourdomain.com")

# Agent Settings
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Application Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")