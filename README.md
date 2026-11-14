# Email Marketing Agent

A Python demo for generating construction estimating outreach emails and sending them through Mailgun or SMTP.

## Requirements

- Python 3.10 or later
- Credentials for an email provider to send messages
- An OpenAI API key is optional. Without one, the agent creates email copy from a local template.

## Setup on Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with the credentials for your chosen email provider. Keep `.env` private; it is excluded from Git.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

## Run the campaign

Replace the demonstration contacts in `main.py` with recipients you are authorized to contact. Configure and verify your sender with Mailgun or SMTP before running:

```powershell
python main.py
```

The campaign sends email through the configured provider. Test with one recipient before using a larger list.
