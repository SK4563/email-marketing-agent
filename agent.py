import json
from html import escape
from typing import Any, Dict, Optional

from openai import OpenAI

from config import LLM_MODEL, OPENAI_API_KEY, TEMPERATURE
from integrations.email_provider import EmailProvider


class MarketingAgent:
    """
    Main logic for the AI agent handling email content generation and execution
    specifically for cost estimation and quantity takeoff services.
    """

    def __init__(self, email_provider: EmailProvider):
        self.email_provider = email_provider
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

    def _normalize_lead_data(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(lead_data)
        normalized["email"] = normalized.get("email") or normalized.get("email_address") or ""
        normalized["full_name"] = normalized.get("full_name") or normalized.get("name") or "Unknown Lead"
        normalized["company_name"] = normalized.get("company_name") or normalized.get("company") or ""
        normalized["project_type"] = normalized.get("project_type") or normalized.get("project") or ""
        return normalized

    def generate_email_content(self, lead_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Uses LLM to generate personalized email subject and HTML body.

        :param lead_data: Dictionary containing lead information (e.g., name, company, project type).
        :return: Dict with 'subject' and 'html_body' if generation successful, None otherwise.
        """
        lead_data = self._normalize_lead_data(lead_data)
        if self.client is None:
            return self._generate_template_content(lead_data)

        prompt = f"""
        Generate a professional direct outreach email for a business offering cost estimation and quantity takeoff services.
        Target Lead Data: {json.dumps(lead_data)}
        Service focus: Accurate construction cost estimates, detailed material quantity takeoffs, fast turnaround.
        Tone: Professional, persuasive, helpful.

        Output must be strictly valid JSON with keys: 'subject' and 'html_body'.
        Do not include markdown inside the output string.
        """

        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                temperature=TEMPERATURE,
                messages=[
                    {"role": "system", "content": "You are an expert marketing copywriter for construction services."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                return None

            data = json.loads(content)
            return {
                "subject": data.get("subject", "Expert Construction Estimation Services"),
                "html_body": data.get("html_body", "<p>Error generating content.</p>"),
            }
        except Exception:
            # In production, integrate logging here
            return None

    def _generate_template_content(self, lead_data: Dict[str, Any]) -> Dict[str, str]:
        name = lead_data["full_name"]
        if name == "Unknown Lead":
            name = "there"

        project = str(lead_data["project_type"]).strip()
        company = str(lead_data["company_name"]).strip()
        subject = (
            f"Construction estimating support for {project}"
            if project
            else "Construction estimating support"
        )

        greeting = escape(str(name))
        project_line = (
            f"<p>If you have an upcoming {escape(project)} project, "
            "we can help prepare the estimate and takeoff.</p>"
            if project
            else ""
        )
        company_line = (
            f"<p>We would be glad to discuss estimating support for {escape(company)}.</p>"
            if company
            else ""
        )
        return {
            "subject": subject,
            "html_body": (
                f"<p>Hi {greeting},</p>"
                "<p>We provide construction cost estimates and detailed material "
                "quantity takeoffs to help teams plan upcoming work.</p>"
                f"{project_line}{company_line}"
                "<p>Would you be open to a brief conversation about an upcoming project?</p>"
                "<p>Best,<br>Construction Estimation Team</p>"
            ),
        }

    def engage_lead(self, lead_data: Dict[str, Any]) -> bool:
        """
        Generates content and sends the email to a specific lead.

        :param lead_data: Dictionary containing lead information, must include 'email'.
        :return: True if process succeeded, False otherwise.
        """
        normalized_lead = self._normalize_lead_data(lead_data)
        to_email = normalized_lead.get("email")
        if not to_email:
            return False

        content = self.generate_email_content(normalized_lead)
        if not content:
            return False

        return self.email_provider.send_email(
            to_email=to_email,
            subject=content["subject"],
            html_body=content["html_body"],
        )