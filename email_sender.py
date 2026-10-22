"""
Sends the Reporter's email via Resend (https://resend.com), a free
transactional email API with a simple REST interface.

If RESEND_API_KEY isn't set, runs in dry-run mode: prints the email instead
of sending it, so the whole pipeline is testable with zero external
accounts.
"""
import os

import requests

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "price-tracker@yourdomain.com")


def send_email(to_email: str, subject: str, body_text: str):
    if not RESEND_API_KEY:
        print(f"[DRY RUN] Would email {to_email}\nSubject: {subject}\n\n{body_text}\n{'-' * 40}")
        return {"dry_run": True}

    resp = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
        json={"from": FROM_EMAIL, "to": [to_email], "subject": subject, "text": body_text},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
