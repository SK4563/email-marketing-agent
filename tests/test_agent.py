import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.agent import MarketingAgent
from integrations.email_provider import EmailProvider


class FakeProvider(EmailProvider):
    def __init__(self):
        self.calls = []

    def send_email(self, to_email, subject, html_body, text_body=None):
        self.calls.append({
            "to_email": to_email,
            "subject": subject,
            "html_body": html_body,
            "text_body": text_body,
        })
        return True


class MarketingAgentTests(unittest.TestCase):
    def test_generate_email_content_uses_local_template_without_api_key(self):
        provider = FakeProvider()
        with patch("core.agent.OPENAI_API_KEY", ""), patch("core.agent.OpenAI") as mock_openai:
            agent = MarketingAgent(provider)
            result = agent.generate_email_content({
                "full_name": "Jane Smith",
                "company_name": "Acme & Sons",
                "project_type": "R&D expansion",
            })

        mock_openai.assert_not_called()
        self.assertEqual(result["subject"], "Construction estimating support for R&D expansion")
        self.assertIn("Hi Jane Smith", result["html_body"])
        self.assertIn("R&amp;D expansion", result["html_body"])
        self.assertIn("Acme &amp; Sons", result["html_body"])

    def test_generate_email_content_accepts_alias_fields_and_returns_html_body(self):
        fake_response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content='{"subject": "Project Estimate Help", "html_body": "<p>Hello</p>"}')
                )
            ]
        )

        with patch("core.agent.OPENAI_API_KEY", "test-key"), patch("core.agent.OpenAI") as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value = fake_response
            provider = FakeProvider()
            agent = MarketingAgent(provider)

            result = agent.generate_email_content({
                "name": "Jane Smith",
                "email_address": "jane@example.com",
                "company": "Acme Construction",
                "project": "Residential build-out",
            })

        self.assertEqual(result["subject"], "Project Estimate Help")
        self.assertEqual(result["html_body"], "<p>Hello</p>")

    def test_engage_lead_uses_normalized_email_and_sends_email(self):
        fake_response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content='{"subject": "Fast Takeoff", "html_body": "<p>Hi</p>"}')
                )
            ]
        )

        with patch("core.agent.OPENAI_API_KEY", "test-key"), patch("core.agent.OpenAI") as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value = fake_response
            provider = FakeProvider()
            agent = MarketingAgent(provider)
            sent = agent.engage_lead({"email": "lead@example.com", "company_name": "North Ridge"})

        self.assertTrue(sent)
        self.assertEqual(provider.calls[0]["to_email"], "lead@example.com")
        self.assertEqual(provider.calls[0]["subject"], "Fast Takeoff")
        self.assertEqual(provider.calls[0]["html_body"], "<p>Hi</p>")


if __name__ == "__main__":
    unittest.main()
