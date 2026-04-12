# Automated ATS Job Discovery & Application Pipeline

A Python-based job discovery and application preparation pipeline that monitors multiple applicant tracking systems (ATS) — **Greenhouse, Lever, Workday, Ashby, and SmartRecruiters** — to surface new analytics and data roles before they appear on high-volume job boards like LinkedIn.

The system pulls job postings directly from company hiring platforms, filters for relevant roles, stores them in a SQLite database, and sends a daily email digest of newly discovered opportunities.

An **AI-powered agent layer** then evaluates each job for fit, generates a tailored cover letter draft, and produces resume bullet suggestions — all written to local files for your review.

Originally built to support a targeted job search in **food tech, restaurant technology, contract food service, and CPG food companies**, but the architecture is designed to work with any company using supported ATS platforms.

---

## Why This Exists

Most job seekers rely on aggregators like LinkedIn or Indeed.

By the time a role appears there, it often already has dozens or hundreds of applicants.

Many companies publish jobs directly to their **applicant tracking systems first**, and only later to aggregators.

This project monitors those systems directly to reduce the time between:

```
job posted → job discovered → application materials ready
```

---

## System Architecture

```
Company Registry
        │
        ▼
ATS Data Sources
(Greenhouse / Lever / Workday / Ashby / SmartRecruiters)
        │
        ▼
Job Ingestion Pipeline
(fetch → filter → normalize → store description)
        │
        ▼
SQLite Database
(deduplication + run metrics)
        │
        ▼
Email Notification
(daily digest)
        │
        ▼
Application Agent (agent.py)
(fit scoring → cover letter → resume notes)
        │
        ▼
Output Files
(output/jobs/)
```

---

## Data Pipeline

### 1. Company Registry (`companies.py`)

A curated list of ~60 companies and their corresponding ATS platforms. Each entry includes the company name, ATS platform, platform-specific token or slug, and an optional category tag (`food` or `analytics`).

### 2. ATS Data Collection (`scraper.py`)

Pulls postings directly from each ATS using a mix of official APIs and documented endpoints:

| Platform | Method |
|---|---|
| Greenhouse | Official API |
| Lever | Official API |
| Ashby | Official API |
| Workday | POST endpoint |
| SmartRecruiters | Official API |

Each platform returns different payload structures, which are normalized during processing. Job descriptions are fetched and stored at discovery time — available inline for Lever and Ashby, and via a second request for Greenhouse, Workday, and SmartRecruiters.

### 3. Filtering

Job postings are filtered by keyword matching against titles:

- Data Analyst
- Business Intelligence
- Analytics
- Data Science
- Internship variants

### 4. Storage (`storage.py`)

All jobs are stored in a **SQLite database** at `data/jobs.db` with two tables:

**`jobs`** — one row per unique job match:
```
id, company, title, url, location, source, category,
date_found, description, processed
```

**`runs`** — one row per scraper run with platform-level metrics.

The schema uses safe `ALTER TABLE` migrations, so existing data is never lost when new columns are added.

### 5. Notifications (`notifier.py`)

When new roles are discovered, the system sends a **tiered plain-text email digest** via Gmail SMTP:

- Tier 1 — Internships, Local or Remote
- Tier 2 — Internships, Other locations
- Tier 3 — Full-time, Local or Remote
- Tier 4 — Full-time, Other locations

Subject line flags internship count: `Job Scraper — 4 new job(s) ★ 2 internship(s) to review`

---

## Application Agent (`agent.py`)

After the scraper runs, the agent processes each unprocessed job through the **Claude API (claude-sonnet-4-20250514)** and generates application materials.

### Fit Scoring

Each job is scored against configurable criteria:

| Score | Criteria |
|---|---|
| **GREEN** | Internship, data analyst, BI, junior/entry-level, remote or hybrid, target region, relevant domain |
| **STRETCH** | Adjacent titles, onsite in target city, other industries if clearly analytical |
| **SKIP** | Senior/lead/manager, 3+ years required, onsite outside target area |

### Output

For each GREEN or STRETCH job, the agent writes two files to `output/jobs/`:

```
job_{id}_{Company}_{Title}_cover_letter.txt
job_{id}_{Company}_{Title}_resume_notes.txt
```

Each file includes a header with company, title, URL, fit score, and reasoning, followed by the generated content.

A cumulative `output/jobs/index.txt` is updated after each run — one scannable file showing every job processed, its score, and which files were written.

SKIP jobs are logged to the console only — no files are written.

### Cost

Running the agent against ~300 jobs with no descriptions costs approximately **$2.50**. Ongoing daily runs against a small number of new jobs cost cents per run.

---

## Project Structure

```
food-industry-job-scraper/

├── scraper.py          # Main ingestion pipeline
├── storage.py          # SQLite persistence + deduplication
├── agent.py            # AI-powered application material generator
├── notifier.py         # Email digest notifications
├── companies.py        # Master company registry
├── rename_outputs.py   # One-off utility to rename legacy output files
├── resume.txt          # Plain text resume for agent input (not committed)
├── data/
│   └── jobs.db         # SQLite database (not committed)
├── output/
│   └── jobs/           # Generated cover letters and resume notes (not committed)
├── .env                # Credentials (not committed)
└── .gitignore
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/stevencc92/food-industry-job-scraper.git
cd food-industry-job-scraper
```

### 2. Create a virtual environment

```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install requests python-dotenv anthropic
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```
# Email (scraper notifications)
SCRAPER_EMAIL=your_sender@gmail.com
SCRAPER_PASSWORD=your_gmail_app_password
NOTIFY_EMAIL=your_personal_email@gmail.com

# Anthropic API (agent)
ANTHROPIC_API_KEY=sk-ant-...
```

For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) rather than your account password.

For the Anthropic API key, create one at [console.anthropic.com](https://console.anthropic.com).

### 5. Add your resume

Create a `resume.txt` in the project root containing a plain text version of your resume. This is the input the agent uses to generate tailored cover letters and resume notes. Your formatted Word or PDF resume is never touched.

### 6. Run the scraper

```bash
python3 scraper.py
```

### 7. Run the agent

```bash
python3 agent.py
```

The agent processes all unprocessed jobs, writes output files, and marks each job as processed. Re-running it will only pick up new jobs from subsequent scraper runs.

---

## Scheduling (macOS)

The scraper runs automatically each morning via **macOS launchd**. A `.plist` file configures the schedule — see Apple's launchd documentation for setup details. The `.plist` is not committed as it contains local paths.

---

## Customizing for Your Search

To adapt this for your own job search:

**Edit `companies.py`** to add or remove companies. Each entry needs the company name, ATS platform, and the platform-specific token or company ID (found in the company's careers page URL).

**Edit the keyword list in `companies.py`** to change which job titles get flagged.

**Edit the fit scoring criteria in `agent.py`** — the `SYSTEM_PROMPT` contains the GREEN / STRETCH / SKIP criteria. Update the target location, experience level, and domain preferences to match your situation.

**Update `resume.txt`** with your own resume content.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| HTTP | requests |
| Storage | SQLite (via sqlite3) |
| AI | Anthropic Claude API (claude-sonnet-4-20250514) |
| Notifications | smtplib (Gmail SMTP) |
| Scheduling | macOS launchd |
| Config | python-dotenv |

---

## Roadmap

- GitHub Actions scheduled runs for cloud-based execution
- HTML formatted email digest
- Web dashboard for browsing historical postings
- Job posting frequency and hiring trend analysis
- Application status tracking layer

---

## Background

**Author: Steven Cockrum**

Computer Science student specializing in Data Analytics at Southern New Hampshire University, transitioning from 13+ years in culinary operations into data analytics.

Portfolio projects:
- Healthcare Food Waste Analysis
- Hospital Food Services Audit — *When Metrics Fail*

---

## Future Vision

As the dataset grows, this system can evolve from a job notification tool into a **job market intelligence dataset**, enabling analysis of hiring patterns across companies, locations, and applicant tracking systems.
