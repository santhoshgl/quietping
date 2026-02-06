import os
import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime
from zoneinfo import ZoneInfo


API_URL = os.environ.get("API_URL")
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
TO_EMAIL = os.environ.get("TO_EMAIL")


def fetch_updates():
    """
    Fetch top 5 updates from the API.
    Returns a list of clean text strings.
    """
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()

    payload = resp.json()

    # Expected shape: { data: [ { attributes: { update: [...] } } ] }
    data = payload.get("data", [])
    if not data:
        return []

    attributes = data[0].get("attributes", {})
    updates = attributes.get("update", [])

    top_five = []
    for item in updates[:5]:
        text = item.get("data", "").strip()
        if text:
            top_five.append(text)

    return top_five


def send_email(updates):
    """
    Send updates via Gmail SMTP to multiple recipients.
    """
    if not updates:
        print("No updates found — skipping email")
        return

    recipients = [e.strip() for e in TO_EMAIL.split(",") if e.strip()]

    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    timestamp = now.strftime("%d %b %Y · %I:%M %p IST")

    subject = f"quietping — latest updates ({timestamp})"

    body = "\n\n".join(
        f"{i + 1}. {update}"
        for i, update in enumerate(updates)
    )

    msg = EmailMessage()
    msg["From"] = GMAIL_USER
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg, to_addrs=recipients)

    print(f"Email sent to {len(recipients)} recipient(s)")


if __name__ == "__main__":
    updates = fetch_updates()
    send_email(updates)
