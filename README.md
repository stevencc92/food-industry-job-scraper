
# Automated ATS Job Discovery Pipeline

A Python-based job discovery pipeline that monitors multiple applicant tracking systems (ATS) — including **Greenhouse, Lever, Workday, and Ashby** — to surface new analytics and data roles before they appear on high-volume job boards like LinkedIn.

The system pulls job postings directly from company hiring platforms, filters them for relevant roles, deduplicates previously seen postings, and sends a daily email digest of newly discovered opportunities.

Originally built to support a targeted job search in **food tech, restaurant technology, contract food service, and CPG food companies**, but the architecture is designed to work with any company using supported ATS platforms.

---

# Why This Exists

Most job seekers rely on job aggregators like LinkedIn or Indeed.

By the time a role appears there, it often already has dozens or hundreds of applicants.

Many companies publish jobs directly to their **applicant tracking systems first**, and only later to aggregators.

This project monitors those systems directly to reduce the time between:

```
job posted → job discovered
```

The goal is simple: **surface relevant roles earlier and automatically**

---

# System Architecture

```
Company Registry
        │
        ▼
ATS Data Sources
(Greenhouse / Lever / Workday / Ashby)
        │
        ▼
Job Ingestion Pipeline
(fetch → filter → normalize)
        │
        ▼
Deduplication Layer
(seen_jobs registry)
        │
        ▼
Storage
(jobs.json + logs)
        │
        ▼
Notification System
(daily email digest)
```

---

# Data Pipeline

## 1. Company Registry

A curated list of companies and their corresponding ATS platforms.

Each company entry includes:

- company name  
- ATS platform  
- platform slug  
- job keyword filters  

Example structure:

```
company
platform
slug
```

---

## 2. ATS Data Collection

The scraper pulls postings directly from ATS platforms using a mix of:

### Official APIs
- Greenhouse
- Ashby

### Endpoint-based queries
- Lever
- Workday

Each platform returns slightly different payload structures, which are normalized during processing.

---

## 3. Filtering

Job postings are filtered using keyword matching to surface relevant roles such as:

- Data Analyst  
- Analytics  
- Business Intelligence  
- Data Science  
- Internships  

Additional filtering tiers prioritize:

- internships  
- food-industry companies  
- general analytics roles  

---

## 4. Normalization

Source-specific responses are transformed into a consistent job structure:

```
id
company
title
location
url
source
category
date_found
```

This allows the system to treat all ATS sources as a unified dataset.

---

## 5. Deduplication

A `seen_jobs.json` registry prevents previously surfaced jobs from appearing in future runs.

Only **new job postings** discovered since the last run are reported.

---

## 6. Notifications

When new relevant roles are discovered, the system sends a **plain-text email digest** via Gmail SMTP summarizing the matches.

---

# Example Output

Example daily email digest:

```
New Job Matches (Last 24 Hours)

Toast — Data Analyst — Remote
Afresh — Data Analyst Intern — San Francisco
Olo — Business Intelligence Analyst — Remote
```

---

# Tech Stack

## Core
- Python 3.12
- requests
- python-dotenv

## Notifications
- smtplib (Gmail SMTP)

## Automation
- macOS launchd scheduled task

## Storage
- JSON persistence (`jobs.json`)
- seen registry (`seen_jobs.json`)
- run logs

---

# Project Structure

```
food-industry-job-scraper/

├── companies.py      # Master company registry
├── scraper.py        # Main ingestion pipeline
├── storage.py        # Persistence + deduplication
├── notifier.py       # Email digest notifications
├── logs/             # Execution logs (not committed)
├── jobs.json         # Stored job matches
├── seen_jobs.json    # Deduplication registry
├── .env              # Email credentials (not committed)
└── .gitignore
```

---

# Current Deployment

The scraper currently runs as a **scheduled local Python job on macOS** using `launchd`.

This allows the pipeline to execute automatically each morning and send a daily digest without manual execution.

Future versions may migrate scheduling to **GitHub Actions or cloud automation** for improved portability and monitoring.

---

# Setup

Clone the repository:

```bash
git clone https://github.com/stevencc92/food-industry-job-scraper.git
cd food-industry-job-scraper
```

Create a virtual environment:

```bash
python3.12 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install requests python-dotenv
```

Create a `.env` file:

```
SCRAPER_EMAIL=your_sender@gmail.com
SCRAPER_PASSWORD=your_gmail_app_password
NOTIFY_EMAIL=your_personal_email@gmail.com
```

Run the scraper manually:

```bash
python scraper.py
```

---

# Roadmap

## Data Infrastructure
- Migrate storage from JSON → **SQLite**
- Store historical job postings
- Track job discovery timestamps
- Support structured querying

## Reliability & Observability
- Track scraper run metrics
- Record platform failures and request errors
- Measure ATS source reliability

## Automation
- GitHub Actions scheduled runs
- Cloud-based execution independent of local machine

## Analytics
- Job posting frequency by company
- Hiring trends across ATS platforms
- Most common analytics role keywords
- Location distribution

## UX Improvements
- HTML formatted email reports
- Web dashboard for browsing historical postings

---

# Background

Author: **Steven Cockrum**

Computer Science student specializing in **Data Analytics** at Southern New Hampshire University.

Currently transitioning from **13+ years in culinary operations** into data analytics, with portfolio projects focused on operational systems and data within the food industry.

Related projects:

- Healthcare Food Waste Analysis  
- Healthcare Waste Audit  

---

# Future Vision

As the dataset grows, this system can evolve from a job notification tool into a **job market intelligence dataset**, enabling analysis of hiring patterns across companies, locations, and applicant tracking systems.
