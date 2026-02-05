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
    r = requests.get(API_URL, timeout=20)
    r.raise_for_status()
    data = r.json()["data"][:5]
    return [item["attributes"]["update"].strip() for item in data]

def send_email(updates):
    body = "\n\n".join(f"{i+1}. {u}" for i, u in enumerate(updates))

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
