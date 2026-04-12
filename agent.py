"""
agent.py — Job Application Agent
Processes unprocessed jobs from SQLite, evaluates fit via Claude API,
and generates cover letters and resume notes as .txt files.

Usage:
    python3 agent.py

Output:
    output/jobs/job_{id}_{Company}_{Title}_cover_letter.txt
    output/jobs/job_{id}_{Company}_{Title}_resume_notes.txt
    output/jobs/index.txt  (appended each run)

Requirements:
    - ANTHROPIC_API_KEY in .env
    - resume.txt in project root (plain text version of your resume)
    - pip install anthropic python-dotenv
"""

import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

DB_PATH = "data/jobs.db"
RESUME_PATH = "resume.txt"
OUTPUT_DIR = "output/jobs"
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1000


# ─────────────────────────────────────────────
# FILENAME HELPERS
# ─────────────────────────────────────────────

def slugify(text, max_length=35):
    """Convert a string to a safe, readable filename slug."""
    text = text.strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "_", text)
    text = text.strip("_-")
    return text[:max_length]


def build_filename(job_id, company, title, suffix):
    """
    Builds a descriptive filename.
    Example: job_7550844_Toast_Data_Analyst_Intern_cover_letter.txt
    """
    company_slug = slugify(company)
    title_slug = slugify(title)
    return f"job_{job_id}_{company_slug}_{title_slug}_{suffix}.txt"


# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_unprocessed_jobs(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, company, title, url, location, source, date_found, description
        FROM jobs
        WHERE processed = 0 OR processed IS NULL
    """)
    return [dict(row) for row in cursor.fetchall()]


def mark_processed(conn, job_id):
    conn.execute("UPDATE jobs SET processed = 1 WHERE id = ?", (job_id,))
    conn.commit()


# ─────────────────────────────────────────────
# RESUME
# ─────────────────────────────────────────────

def load_resume():
    if not os.path.exists(RESUME_PATH):
        raise FileNotFoundError(
            f"Resume not found at '{RESUME_PATH}'. "
            "Add a plain text version of your resume before running the agent."
        )
    with open(RESUME_PATH, "r") as f:
        return f.read().strip()


# ─────────────────────────────────────────────
# PROMPT
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are a job application assistant helping a candidate apply for data analyst roles.

The candidate is:
- A Chef de Partie at a medical center in San Jose, transitioning into data analytics
- A third-year CS student (Data Analytics concentration) at SNHU
- Planning to relocate to Sacramento in approximately four months
- Portfolio: a food industry job scraper (Python, SQLite, multi-platform ATS integration), a hospital food services audit identifying gaps in HCAHPS data usage, and a healthcare food waste analysis using synthetic datasets
- Background spans culinary operations, healthcare food services, supply chain, and team coordination

Fit scoring criteria:
GREEN (apply): internship, data analyst, business intelligence, junior/entry-level, remote or hybrid, Sacramento region, hospitality/food/healthcare context
STRETCH (worth considering): onsite Sacramento, adjacent titles (reporting analyst, operations analyst), other industries if clearly analytical
SKIP: senior/lead/manager, 3+ years required with no internship language, onsite outside Sacramento

Respond ONLY in the following format with no preamble:

FIT: [GREEN | STRETCH | SKIP]
REASONING: [1-2 sentences explaining the score]

COVER LETTER:
[Full cover letter draft, 3-4 paragraphs, addressed to Hiring Manager. Connect the candidate's culinary/healthcare operations background to the analytical role. Reference specific details from the job description where possible. Tone: professional but warm, confident without overselling.]

RESUME NOTES:
[3-5 bullet suggestions for resume bullets or talking points specific to this job. Focus on quantifiable impact, domain relevance, and transferable skills. Do not reformat or rewrite the resume — bullets only.]

If FIT is SKIP, respond ONLY with:
FIT: SKIP
REASONING: [1-2 sentences]
No cover letter or resume notes needed."""


def build_user_prompt(job, resume_text):
    description = job.get("description") or "No description available."
    return f"""Job to evaluate:

Company: {job['company']}
Title: {job['title']}
Location: {job['location']}
URL: {job['url']}
Source ATS: {job['source']}
Date Found: {job['date_found']}

Job Description:
{description}

---

Candidate Resume:
{resume_text}"""


# ─────────────────────────────────────────────
# API
# ─────────────────────────────────────────────

def evaluate_job(client, job, resume_text):
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": build_user_prompt(job, resume_text)}
        ]
    )
    return response.content[0].text.strip()


# ─────────────────────────────────────────────
# PARSING
# ─────────────────────────────────────────────

def parse_response(response_text):
    result = {
        "fit": None,
        "reasoning": None,
        "cover_letter": None,
        "resume_notes": None,
    }

    lines = response_text.splitlines()
    current_section = None
    buffer = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("FIT:"):
            result["fit"] = stripped.replace("FIT:", "").strip()

        elif stripped.startswith("REASONING:"):
            result["reasoning"] = stripped.replace("REASONING:", "").strip()

        elif stripped == "COVER LETTER:":
            if current_section and buffer:
                result[current_section] = "\n".join(buffer).strip()
            current_section = "cover_letter"
            buffer = []

        elif stripped == "RESUME NOTES:":
            if current_section and buffer:
                result[current_section] = "\n".join(buffer).strip()
            current_section = "resume_notes"
            buffer = []

        else:
            if current_section:
                buffer.append(line)

    if current_section and buffer:
        result[current_section] = "\n".join(buffer).strip()

    return result


# ─────────────────────────────────────────────
# FILE OUTPUT
# ─────────────────────────────────────────────

def write_output_files(job, parsed):
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    job_id = job["id"]
    company = job["company"]
    title = job["title"]

    header = (
        f"Company:    {company}\n"
        f"Title:      {title}\n"
        f"URL:        {job['url']}\n"
        f"Date Found: {job['date_found']}\n"
        f"Fit:        {parsed['fit']}\n"
        f"Reasoning:  {parsed['reasoning']}\n"
        f"Generated:  {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"{'─' * 60}\n\n"
    )

    cover_path = os.path.join(OUTPUT_DIR, build_filename(job_id, company, title, "cover_letter"))
    with open(cover_path, "w") as f:
        f.write(header)
        f.write(parsed["cover_letter"] or "")
    print(f"  → {os.path.basename(cover_path)}")

    notes_path = os.path.join(OUTPUT_DIR, build_filename(job_id, company, title, "resume_notes"))
    with open(notes_path, "w") as f:
        f.write(header)
        f.write(parsed["resume_notes"] or "")
    print(f"  → {os.path.basename(notes_path)}")

    return cover_path, notes_path


# ─────────────────────────────────────────────
# INDEX
# ─────────────────────────────────────────────

def append_to_index(run_entries):
    """
    Appends a summary of this run's processed jobs to output/jobs/index.txt.
    Each run gets a timestamped block for easy scanning.
    """
    if not run_entries:
        return

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    index_path = os.path.join(OUTPUT_DIR, "index.txt")

    with open(index_path, "a") as f:
        f.write(f"\n{'═' * 60}\n")
        f.write(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"{'═' * 60}\n")

        for entry in run_entries:
            fit = entry["fit"]
            marker = "✓" if fit == "GREEN" else "~" if fit == "STRETCH" else "✗"
            f.write(
                f"{marker} [{fit}] {entry['company']} — {entry['title']}\n"
                f"   ID:  {entry['job_id']}\n"
                f"   URL: {entry['url']}\n"
            )
            if entry.get("files"):
                for file in entry["files"]:
                    f.write(f"   →  {os.path.basename(file)}\n")
            f.write("\n")

    print(f"  [index] Updated: {index_path}")


# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────

def run_agent():
    print(f"\n{'=' * 50}")
    print("Job Application Agent")
    print(f"{'=' * 50}")

    try:
        resume_text = load_resume()
        print(f"[resume] Loaded from '{RESUME_PATH}'")
    except FileNotFoundError as e:
        print(f"[error] {e}")
        return

    conn = get_connection()
    jobs = fetch_unprocessed_jobs(conn)
    print(f"[db] {len(jobs)} unprocessed job(s) found\n")

    if not jobs:
        print("Nothing to process. Exiting.")
        conn.close()
        return

    client = Anthropic()

    green_count = 0
    stretch_count = 0
    skip_count = 0
    error_count = 0
    run_entries = []

    for job in jobs:
        job_id = job["id"]
        print(f"Processing: [{job_id}] {job['company']} — {job['title']}")

        try:
            raw = evaluate_job(client, job, resume_text)
            parsed = parse_response(raw)
            fit = parsed.get("fit", "UNKNOWN")

            entry = {
                "job_id": job_id,
                "company": job["company"],
                "title": job["title"],
                "url": job["url"],
                "fit": fit,
                "files": [],
            }

            if fit == "SKIP":
                print(f"  ✗ SKIP — {parsed.get('reasoning', '')}")
                skip_count += 1

            elif fit in ("GREEN", "STRETCH"):
                files = write_output_files(job, parsed)
                entry["files"] = list(files)
                if fit == "GREEN":
                    green_count += 1
                    print(f"  ✓ GREEN")
                else:
                    stretch_count += 1
                    print(f"  ~ STRETCH")

            else:
                print(f"  [warn] Unrecognized fit value: '{fit}' — skipping file write")
                error_count += 1

            run_entries.append(entry)
            mark_processed(conn, job_id)

        except Exception as e:
            print(f"  [error] {e}")
            error_count += 1

        print()

    conn.close()
    append_to_index(run_entries)

    print(f"{'=' * 50}")
    print("Run complete.")
    print(f"  GREEN:   {green_count}")
    print(f"  STRETCH: {stretch_count}")
    print(f"  SKIP:    {skip_count}")
    if error_count:
        print(f"  ERRORS:  {error_count} (will retry next run)")
    print(f"{'=' * 50}\n")


if __name__ == "__main__":
    run_agent()