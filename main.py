import logging
import sys
from typing import Any, Dict, List

from config import EMAIL_PROVIDER
from core.agent import MarketingAgent
from integrations.email_provider import get_email_provider
from utils.helpers import get_timestamp, validate_email

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Mock database of leads for demonstration
SAMPLE_LEADS_DB: List[Dict[str, Any]] = [
    {
        "full_name": "John Doe",
        "email_address": "john.doe@example.com",
        "company_name": "Example Construction Co.",
        "project_type": "Commercial Mid-rise",
    },
    {
        "full_name": "Jane Smith",
        "email_address": "jane.smith@example.org",
        "company_name": "Example Residential Development",
        "project_type": "Luxury Single Family Homes",
    },
    {
        "full_name": "Invalid Lead",
        "email_address": "invalid-email-format",
        "company_name": "Bad Data Corp.",
        "project_type": "Renovation",
    },
]


def run_marketing_campaign() -> None:
    """
    Initializes components and executes the marketing campaign for sample leads.
    """
    logger.info(f"Starting marketing campaign run at {get_timestamp()}")

    try:
        email_service = get_email_provider()
    except (ImportError, ValueError) as exc:
        logger.error(f"Failed to initialize email provider '{EMAIL_PROVIDER}': {exc}")
        return

    agent = MarketingAgent(email_provider=email_service)

    processed_count = 0
    failure_count = 0

    for lead in SAMPLE_LEADS_DB:
        lead_name = lead.get("full_name", "Unknown Lead")
        lead_email = lead.get("email_address") or lead.get("email") or ""

        logger.info(f"Processing lead: {lead_name} ({lead_email})")

        if not validate_email(lead_email):
            logger.warning(f"Skipping lead {lead_name}: Invalid email format '{lead_email}'.")
            failure_count += 1
            continue

        try:
            email_content = agent.generate_email_content(lead)

            if not email_content or "subject" not in email_content or "html_body" not in email_content:
                logger.error(f"Failed to generate valid content for lead {lead_name}.")
                failure_count += 1
                continue

            send_success = email_service.send_email(
                to_email=lead_email,
                subject=email_content["subject"],
                html_body=email_content["html_body"],
            )

            if send_success:
                logger.info(f"Successfully sent marketing email to {lead_name}.")
                processed_count += 1
            else:
                logger.error(f"Email provider failed to send email to {lead_name}.")
                failure_count += 1

        except Exception as exc:
            logger.exception(f"Unexpected error processing lead {lead_name}: {exc}")
            failure_count += 1

    logger.info(f"Campaign run complete. Processed: {processed_count}, Failures: {failure_count}.")


if __name__ == "__main__":
    run_marketing_campaign()