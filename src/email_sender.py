"""
Email sender using the Resend SDK.

Sends HTML emails via Resend's API using the free-tier
onboarding@resend.dev sender address.
"""

import resend

from src.config import RESEND_API_KEY, SENDER_EMAIL, RECIPIENT_EMAIL


def send_email(subject: str, html_body: str) -> dict:
    """
    Send an HTML email via Resend.

    Args:
        subject: Email subject line.
        html_body: Full HTML content of the email.

    Returns:
        Resend API response dict containing the email ID.

    Raises:
        Exception: If required config is missing or the API call fails.
    """
    # ── Validate configuration ───────────────────────────────────────────
    if not RESEND_API_KEY:
        raise ValueError("RESEND_API_KEY is not set. Check your environment variables.")
    if not RECIPIENT_EMAIL:
        raise ValueError("RECIPIENT_EMAIL is not set. Check your environment variables.")

    # ── Send the email ───────────────────────────────────────────────────
    resend.api_key = RESEND_API_KEY

    params: resend.Emails.SendParams = {
        "from": SENDER_EMAIL,
        "to": [RECIPIENT_EMAIL],
        "subject": subject,
        "html": html_body,
    }

    response = resend.Emails.send(params)
    email_id = response.get("id", "N/A") if isinstance(response, dict) else "N/A"
    print(f"   ✅ Email sent! (ID: {email_id})")

    return response
