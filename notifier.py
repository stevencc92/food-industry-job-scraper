"""
notifier.py — Sends an email digest of new job matches.
Uses Gmail SMTP with credentials stored in .env — never hardcoded.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
import os

# Load the credentials from .env
load_dotenv()

SCRAPER_EMAIL = os.getenv("SCRAPER_EMAIL")
SCRAPER_PASSWORD = os.getenv("SCRAPER_PASSWORD")
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")


def build_email_body(new_jobs):
    """
    Builds a plain-text email with two sections:
    - Food & Hospitality (primary targets)
    - Analytics & BI (broader roles)
    """
    date_str = datetime.now().strftime("%B %d, %Y")
    lines = []

    lines.append(f"Job Scraper Digest — {date_str}")
    lines.append(f"{len(new_jobs)} new job(s) found\n")

    # Split into categories
    food_jobs = [j for j in new_jobs if j.get("category") == "food"]
    analytics_jobs = [j for j in new_jobs if j.get("category") == "analytics"]
    other_jobs = [j for j in new_jobs if j.get("category") not in ("food", "analytics")]

    def format_section(title, jobs):
        if not jobs:
            return []
        section = []
        section.append("=" * 40)
        section.append(title)
        section.append("=" * 40)

        # Group by company
        by_company = {}
        for job in jobs:
            company = job["company"]
            if company not in by_company:
                by_company[company] = []
            by_company[company].append(job)

        for company, company_jobs in by_company.items():
            section.append(f"\n{company}")
            section.append("-" * len(company))
            for job in company_jobs:
                section.append(f"  {job['title']}")
                section.append(f"  Location: {job['location']}")
                section.append(f"  {job['url']}")
                section.append("")
        return section

    lines += format_section("FOOD & HOSPITALITY", food_jobs)
    lines += format_section("ANALYTICS & BI", analytics_jobs)
    lines += format_section("OTHER", other_jobs)

    lines.append("=" * 40)
    lines.append("Sent by your job scraper.")

    return "\n".join(lines)


def send_notification(new_jobs):
    """
    Sends the digest email if there are new jobs to report.
    Skips sending if the list is empty.
    """
    if not new_jobs:
        print("[notifier] No new jobs — skipping email.")
        return

    # Check credentials are loaded
    if not all([SCRAPER_EMAIL, SCRAPER_PASSWORD, NOTIFY_EMAIL]):
        print("[notifier] Missing credentials in .env — skipping email.")
        return

    subject = f"Job Scraper — {len(new_jobs)} new job(s) found"
    body = build_email_body(new_jobs)

    # Build the email
    msg = MIMEMultipart()
    msg["From"] = SCRAPER_EMAIL
    msg["To"] = NOTIFY_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Send it via Gmail's SMTP server
    try:
        print("[notifier] Connecting to Gmail...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SCRAPER_EMAIL, SCRAPER_PASSWORD)
            server.sendmail(SCRAPER_EMAIL, NOTIFY_EMAIL, msg.as_string())
        print(f"[notifier] Email sent to {NOTIFY_EMAIL}")

    except smtplib.SMTPAuthenticationError:
        print("[notifier] Authentication failed — check your app password in .env")
    except Exception as e:
        print(f"[notifier] Failed to send email — {e}")