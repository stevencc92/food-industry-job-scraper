"""
notifier.py — Sends an email digest of new job matches.
Uses Gmail SMTP with credentials stored in .env — never hardcoded.
Email is organized into priority tiers so high-value matches are always at the top.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

SCRAPER_EMAIL = os.getenv("SCRAPER_EMAIL")
SCRAPER_PASSWORD = os.getenv("SCRAPER_PASSWORD")
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")

LOCAL_KEYWORDS = [
    "san jose", "santa clara", "sunnyvale", "mountain view",
    "palo alto", "san francisco", "sf", "bay area", "campbell",
    "cupertino", "milpitas", "fremont", "oakland", "berkeley",
    "redwood city", "menlo park", "foster city", "south bay"
]

REMOTE_KEYWORDS = ["remote", "anywhere", "distributed", "work from home", "wfh"]

INTERNSHIP_KEYWORDS = [
    "intern", "internship", "co-op", "coop", "student"
]


def tag_location(location_str):
    if not location_str:
        return "Other"
    loc = location_str.lower()
    if any(k in loc for k in REMOTE_KEYWORDS):
        return "Remote"
    if any(k in loc for k in LOCAL_KEYWORDS):
        return "Local"
    return "Other"


def is_internship(title):
    title_lower = title.lower()
    return any(k in title_lower for k in INTERNSHIP_KEYWORDS)


def tier_job(job):
    """
    Returns a tier number 1-4 based on location and internship status.
    Lower = higher priority.
    """
    loc = tag_location(job.get("location", ""))
    intern = is_internship(job.get("title", ""))

    if intern and loc in ("Local", "Remote"):
        return 1  # Local or Remote Internship — apply now
    if intern:
        return 2  # Internship but other location — worth a look
    if loc in ("Local", "Remote"):
        return 3  # Local or Remote full-time
    return 4      # Everything else


TIER_LABELS = {
    1: "TIER 1 — Internships (Local & Remote)",
    2: "TIER 2 — Internships (Other Locations)",
    3: "TIER 3 — Full-Time (Local & Remote)",
    4: "TIER 4 — Full-Time (Other Locations)",
}


def build_email_body(new_jobs):
    date_str = datetime.now().strftime("%B %d, %Y")
    lines = []

    lines.append(f"Job Scraper Digest — {date_str}")
    lines.append(f"{len(new_jobs)} new job(s) found")
    lines.append("")

    # Sort jobs into tiers
    tiers = {1: [], 2: [], 3: [], 4: []}
    for job in new_jobs:
        tiers[tier_job(job)].append(job)

    # Print tier summary
    lines.append("SUMMARY")
    lines.append("-" * 30)
    for tier_num, label in TIER_LABELS.items():
        count = len(tiers[tier_num])
        if count:
            lines.append(f"  {label}: {count} job(s)")
    lines.append("")

    # Print each tier
    for tier_num, label in TIER_LABELS.items():
        jobs = tiers[tier_num]
        if not jobs:
            continue

        lines.append("=" * 40)
        lines.append(label)
        lines.append("=" * 40)

        # Group by company within tier
        by_company = {}
        for job in jobs:
            company = job["company"]
            if company not in by_company:
                by_company[company] = []
            by_company[company].append(job)

        for company, company_jobs in by_company.items():
            lines.append(f"\n{company}")
            lines.append("-" * len(company))
            for job in company_jobs:
                loc_tag = tag_location(job.get("location", ""))
                lines.append(f"  [{loc_tag}] {job['title']}")
                lines.append(f"  {job.get('location', 'Not listed')}")
                lines.append(f"  {job['url']}")
                lines.append("")

    lines.append("=" * 40)
    lines.append("Sent by your job scraper.")

    return "\n".join(lines)


def send_notification(new_jobs):
    if not new_jobs:
        print("[notifier] No new jobs — skipping email.")
        return

    if not all([SCRAPER_EMAIL, SCRAPER_PASSWORD, NOTIFY_EMAIL]):
        print("[notifier] Missing credentials in .env — skipping email.")
        return

    # Count tier 1 for subject line
    tier1_count = sum(1 for j in new_jobs if tier_job(j) == 1)
    tier1_str = f" ★ {tier1_count} internship(s) to review" if tier1_count else ""

    subject = f"Job Scraper — {len(new_jobs)} new job(s){tier1_str}"
    body = build_email_body(new_jobs)

    msg = MIMEMultipart()
    msg["From"] = SCRAPER_EMAIL
    msg["To"] = NOTIFY_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

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