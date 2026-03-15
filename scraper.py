"""
scraper.py — Phase 5: Greenhouse + Lever scraper
Checks both platforms, deduplicates, saves, and emails new matches.
"""

import requests
from datetime import datetime
from companies import GREENHOUSE_COMPANIES, LEVER_COMPANIES, WORKDAY_COMPANIES, SEARCH_KEYWORDS
from storage import load_seen_jobs, save_seen_jobs, filter_new_jobs, save_jobs
from notifier import send_notification


# ─────────────────────────────────────────────
# GREENHOUSE
# ─────────────────────────────────────────────

def fetch_greenhouse_jobs(board_token):
    """
    Calls the Greenhouse API for a given company and returns a list of jobs.
    Returns an empty list if anything goes wrong.
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"  [skipped] {board_token} — status {response.status_code}")
            return []

        data = response.json()
        return data.get("jobs", [])

    except requests.exceptions.RequestException as e:
        print(f"  [error] {board_token} — {e}")
        return []


# ─────────────────────────────────────────────
# LEVER
# ─────────────────────────────────────────────

def fetch_lever_jobs(company_id):
    """
    Calls the Lever API for a given company and returns a list of jobs.
    Lever returns all postings in one call — no pagination needed.
    """
    url = f"https://api.lever.co/v0/postings/{company_id}?mode=json"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"  [skipped] {company_id} — status {response.status_code}")
            return []

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"  [error] {company_id} — {e}")
        return []


# ─────────────────────────────────────────────
# SHARED
# ─────────────────────────────────────────────

def is_relevant(job_title):
    """
    Returns True if the job title contains any of our search keywords.
    Case-insensitive.
    """
    title_lower = job_title.lower()
    return any(keyword.lower() in title_lower for keyword in SEARCH_KEYWORDS)


def process_greenhouse(company, seen_jobs, all_new_matches):
    name = company["name"]
    token = company["board_token"]
    category = company.get("category", "general")

    print(f"\nChecking {name} (Greenhouse)...")
    jobs = fetch_greenhouse_jobs(token)
    relevant = [job for job in jobs if is_relevant(job["title"])]
    new_jobs, seen_jobs = filter_new_jobs(relevant, seen_jobs)

    if new_jobs:
        print(f"  ✓ {len(new_jobs)} NEW match(es):")
        for job in new_jobs:
            print(f"    - {job['title']}")
            print(f"      {job.get('absolute_url', 'No URL')}")
            all_new_matches.append({
                "id": str(job["id"]),
                "company": name,
                "title": job["title"],
                "url": job.get("absolute_url", ""),
                "location": job.get("location", {}).get("name", "Not listed"),
                "source": "Greenhouse",
                "category": category,
                "date_found": datetime.now().strftime("%Y-%m-%d"),
            })
    elif relevant:
        print(f"  — {len(relevant)} match(es) found but already seen")
    else:
        print(f"  — No matches")

    return seen_jobs


def process_lever(company, seen_jobs, all_new_matches):
    name = company["name"]
    company_id = company["company_id"]
    category = company.get("category", "general")

    print(f"\nChecking {name} (Lever)...")
    jobs = fetch_lever_jobs(company_id)
    relevant = [job for job in jobs if is_relevant(job.get("text", ""))]
    new_jobs, seen_jobs = filter_new_jobs(relevant, seen_jobs)

    if new_jobs:
        print(f"  ✓ {len(new_jobs)} NEW match(es):")
        for job in new_jobs:
            print(f"    - {job['text']}")
            print(f"      {job.get('hostedUrl', 'No URL')}")
            all_new_matches.append({
                "id": job["id"],
                "company": name,
                "title": job["text"],
                "url": job.get("hostedUrl", ""),
                "location": job.get("categories", {}).get("location", "Not listed"),
                "source": "Lever",
                "category": category,
                "date_found": datetime.now().strftime("%Y-%m-%d"),
            })
    elif relevant:
        print(f"  — {len(relevant)} match(es) found but already seen")
    else:
        print(f"  — No matches")

    return seen_jobs


# ─────────────────────────────────────────────
# WORKDAY
# ─────────────────────────────────────────────

def fetch_workday_jobs(url, keyword):
    """
    Calls the Workday hidden POST endpoint for a given company.
    Workday requires a POST request with a JSON body containing the search term.
    Returns a list of job postings.
    """
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }

    # This is the payload Workday expects — search term plus pagination
    payload = {
        "appliedFacets": {},
        "limit": 20,
        "offset": 0,
        "searchText": keyword,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"  [skipped] status {response.status_code}")
            return []

        data = response.json()
        return data.get("jobPostings", [])

    except requests.exceptions.RequestException as e:
        print(f"  [error] {e}")
        return []


def process_workday(company, seen_jobs, all_new_matches):
    name = company["name"]
    url = company["url"]
    category = company.get("category", "general")

    print(f"\nChecking {name} (Workday)...")

    # Search once per keyword and collect all unique results
    seen_in_this_run = set()
    all_jobs = []

    for keyword in SEARCH_KEYWORDS:
        jobs = fetch_workday_jobs(url, keyword)
        for job in jobs:
            job_id = job.get("bulletFields", [""])[0] + job.get("title", "")
            if job_id not in seen_in_this_run:
                seen_in_this_run.add(job_id)
                all_jobs.append(job)

    # Filter by keyword match on title
    relevant = [job for job in all_jobs if is_relevant(job.get("title", ""))]

    # Workday uses externalPath as a unique ID
    # We build a synthetic ID from the title + path since there's no clean numeric ID
    for job in relevant:
        job["id"] = job.get("externalPath", job.get("title", "")).strip("/").replace("/", "-")

    new_jobs, seen_jobs = filter_new_jobs(relevant, seen_jobs)

    if new_jobs:
        print(f"  ✓ {len(new_jobs)} NEW match(es):")
        for job in new_jobs:
            title = job.get("title", "No title")
            path = job.get("externalPath", "")
            # Build the full URL from the base domain + the job path
            base = url.split("/wday/")[0]
            job_url = f"{base}{path}" if path else base
            location = job.get("locationsText", "Not listed")

            print(f"    - {title}")
            print(f"      {job_url}")

            all_new_matches.append({
                "id": job["id"],
                "company": name,
                "title": title,
                "url": job_url,
                "location": location,
                "source": "Workday",
                "category": category,
                "date_found": datetime.now().strftime("%Y-%m-%d"),
            })
    elif relevant:
        print(f"  — {len(relevant)} match(es) found but already seen")
    else:
        print(f"  — No matches")

    return seen_jobs




def run_scraper():
    print("=" * 50)
    print(f"Job Scraper — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    seen_jobs = load_seen_jobs()
    print(f"\nPreviously seen jobs: {len(seen_jobs)}")

    all_new_matches = []

    # --- Greenhouse ---
    print("\n--- Greenhouse ---")
    for company in GREENHOUSE_COMPANIES:
        seen_jobs = process_greenhouse(company, seen_jobs, all_new_matches)

    # --- Lever ---
    print("\n--- Lever ---")
    for company in LEVER_COMPANIES:
        seen_jobs = process_lever(company, seen_jobs, all_new_matches)

    # --- Workday ---
    print("\n--- Workday ---")
    for company in WORKDAY_COMPANIES:
        seen_jobs = process_workday(company, seen_jobs, all_new_matches)

    # --- Save + notify ---
    if all_new_matches:
        save_jobs(all_new_matches)

    save_seen_jobs(seen_jobs)
    send_notification(all_new_matches)

    print("\n" + "=" * 50)
    print(f"Done. {len(all_new_matches)} new job(s) found this run.")
    print("=" * 50)

    return all_new_matches


if __name__ == "__main__":
    run_scraper()