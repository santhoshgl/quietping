import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

API_URL = os.environ["API_URL"]

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
TO_EMAIL = os.environ.get("TO_EMAIL", GMAIL_USER)

def fetch_updates():
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()

    payload = resp.json()

    # payload is a dict: { data: [...], meta: {...} }
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
    body = "\n\n".join(
    f"{i+1}. {update}"
    for i, update in enumerate(updates)
)

    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = TO_EMAIL
    msg["Subject"] = "quietping — latest updates"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        s.send_message(msg)

if __name__ == "__main__":
    updates = fetch_updates()
    send_email(updates)
    print("quietping sent")
