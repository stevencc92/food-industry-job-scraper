# Food Industry Job Scraper

An automated job monitoring tool that tracks analytics and data roles across food tech, restaurant technology, contract food service, and CPG food companies.

Built as part of a career transition from food service operations into data analytics. The company list and search keywords were put together deliberately, targeting verticals where a background in professional kitchens might be relevant rather than incidental.

---

## Why This Exists

Checking 75 company job boards manually every day isn't realistic. This tool does it automatically and sends an email digest of new postings since the last run, so the searching happens in the background.

The target companies were chosen with some intention. Places like Afresh, Toast, and Olo are working on problems that show up in real kitchen and food service environments -- food waste, inventory, operational data. Having spent time in those environments felt like a reasonable reason to pay closer attention to what those companies are hiring for.

---

## How It Works

The scraper is organized into four modules:

**`companies.py`** — The master list of target companies, organized by ATS platform (Greenhouse, Lever, Workday) and paired with a curated list of relevant job title keywords.

**`scraper.py`** — The main engine. Loops through each company, calls the Greenhouse API, filters results by keyword, and hands matches off to storage and notifications.

**`storage.py`** — Handles persistence. Saves matches to `jobs.json` and maintains a `seen_jobs.json` file so the scraper only surfaces genuinely new postings on each run — not the same 11 jobs every morning.

**`notifier.py`** — Sends a plain-text email digest via Gmail SMTP whenever new matches are found. Credentials are stored in a local `.env` file and never committed to version control.

Scheduling is handled by **macOS launchd** via a `.plist` configuration file — the scraper runs automatically each morning without any manual intervention.

---

## Target Companies (Greenhouse — Phase 1)

A selection of the companies currently monitored:

| Company | Vertical |
|---|---|
| Toast | Restaurant Tech |
| Olo | Restaurant Tech |
| SevenRooms | Restaurant Tech |
| Afresh | Food Tech / Waste Reduction |
| Instacart | Grocery Tech |
| Impossible Foods | CPG / Alt Protein |
| Chobani | CPG / Food Manufacturing |
| Daily Harvest | CPG / DTC Food |
| Aramark | Contract Food Service |
| Compass Group | Contract Food Service |
| Sodexo | Contract Food Service |

75 companies total across Greenhouse, Lever, and Workday platforms.

---

## Tech Stack

- **Python 3.12**
- `requests` — API calls to Greenhouse
- `python-dotenv` — Credential management
- `smtplib` — Email delivery via Gmail SMTP
- **macOS launchd** — Scheduling

---

## Project Structure

```
job-scraper/
├── companies.py        # Master company + keyword list
├── scraper.py          # Main scraper logic
├── storage.py          # Deduplication + persistence
├── notifier.py         # Email digest
├── .env                # Credentials (not committed)
├── .gitignore
└── logs/               # Run logs (not committed)
```

---

## Setup

> This project is configured for my personal job search and runs locally on my machine. If you want to adapt it for your own use:

1. Clone the repo and create a virtual environment
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install requests python-dotenv
```

2. Create a `.env` file with your Gmail credentials
```
SCRAPER_EMAIL=your_sender@gmail.com
SCRAPER_PASSWORD=your_16_char_app_password
NOTIFY_EMAIL=your_personal@gmail.com
```

3. Run it
```bash
python3.12 scraper.py
```

---

## Roadmap

- [x] Greenhouse API integration
- [x] Keyword filtering
- [x] Deduplication across runs
- [x] Email digest notifications
- [x] macOS launchd scheduling
- [ ] Lever API integration
- [ ] Workday scraping
- [ ] SQLite storage (replacing flat JSON files)
- [ ] HTML email formatting
- [ ] Web dashboard for browsing saved jobs

---

## Background

I'm a third-year Computer Science student at Southern New Hampshire University specializing in Data Analytics, currently working as a Chef de Partie at a regional medical center in San Jose. This project is part of a portfolio built around food service operations and data, an area I've been trying to develop a practical foothold in alongside my studies.

Other projects: [healthcare-food-waste-analysis](https://github.com/stevencc92/healthcare-food-waste-analysis) · [healthcare-waste-audit](https://github.com/stevencc92/healthcare-waste-audit)