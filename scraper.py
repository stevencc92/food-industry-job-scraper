"""
scraper.py — Phase 6: Greenhouse + Lever + Workday + Ashby + SmartRecruiters
Checks all five platforms, deduplicates, saves, and emails new matches.
Descriptions are fetched and stored per job where available.
"""

import requests
from datetime import datetime
from companies import (
    GREENHOUSE_COMPANIES, LEVER_COMPANIES, WORKDAY_COMPANIES,
    ASHBY_COMPANIES, SMARTRECRUITERS_COMPANIES, SEARCH_KEYWORDS
)
from storage import load_seen_jobs, filter_new_jobs, save_jobs, save_run_metrics
from notifier import send_notification


# ─────────────────────────────────────────────
# DESCRIPTION HELPERS
# ─────────────────────────────────────────────

def clean_description(text):
    """
    Strips excess whitespace from a description string.
    Returns None if the result is empty.
    """
    if not text:
        return None
    cleaned = " ".join(text.split())
    return cleaned if cleaned else None


def fetch_greenhouse_description(board_token, job_id):
    """
    Greenhouse list endpoint does not include descriptions.
    Fetches the full job detail from the Greenhouse API.
    Returns plain text description or None.
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        # content is HTML — use absolute_url as fallback context, strip tags simply
        raw = data.get("content", "") or ""
        # Basic tag strip — good enough for LLM input
        import re
        plain = re.sub(r"<[^>]+>", " ", raw)
        return clean_description(plain)
    except Exception:
        return None


def fetch_workday_description(job_url):
    """
    Workday list endpoint does not include descriptions.
    Fetches the job page and extracts visible text as a best-effort description.
    Returns plain text or None.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(job_url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None
        import re
        plain = re.sub(r"<[^>]+>", " ", response.text)
        # Trim to a reasonable length for LLM input
        return clean_description(plain[:3000])
    except Exception:
        return None


def fetch_smartrecruiters_description(company_id, job_id):
    """
    SmartRecruiters list endpoint does not include descriptions.
    Fetches the job detail from the SmartRecruiters public API.
    Returns plain text description or None.
    """
    url = f"https://api.smartrecruiters.com/v1/companies/{company_id}/postings/{job_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        sections = data.get("jobAd", {}).get("sections", {})
        parts = []
        for key in ("companyDescription", "jobDescription", "qualifications", "additionalInformation"):
            text = sections.get(key, {}).get("text", "") or ""
            if text:
                import re
                plain = re.sub(r"<[^>]+>", " ", text)
                parts.append(plain)
        return clean_description(" ".join(parts)) if parts else None
    except Exception:
        return None


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

            # Greenhouse requires a second API call per job for description
            description = fetch_greenhouse_description(token, job["id"])

            all_new_matches.append({
                "id": str(job["id"]),
                "company": name,
                "title": job["title"],
                "url": job.get("absolute_url", ""),
                "location": job.get("location", {}).get("name", "Not listed"),
                "source": "Greenhouse",
                "category": category,
                "date_found": datetime.now().strftime("%Y-%m-%d"),
                "description": description,
            })
    elif relevant:
        print(f"  — {len(relevant)} match(es) found but already seen")
    else:
        print(f"  — No matches")

    return seen_jobs, {"found": len(new_jobs), "errors": 0 if jobs else 1}


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

            # Lever includes descriptionPlain in the list response — no extra call needed
            description = clean_description(job.get("descriptionPlain", ""))

            all_new_matches.append({
                "id": job["id"],
                "company": name,
                "title": job["text"],
                "url": job.get("hostedUrl", ""),
                "location": job.get("categories", {}).get("location", "Not listed"),
                "source": "Lever",
                "category": category,
                "date_found": datetime.now().strftime("%Y-%m-%d"),
                "description": description,
            })
    elif relevant:
        print(f"  — {len(relevant)} match(es) found but already seen")
    else:
        print(f"  — No matches")

    return seen_jobs, {"found": len(new_jobs), "errors": 0 if jobs else 1}


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
    board_name = company.get("board_name")

    print(f"\nChecking {name} (Workday)...")

    seen_in_this_run = set()
    all_jobs = []
    errors = 0

    for keyword in SEARCH_KEYWORDS:
        jobs = fetch_workday_jobs(url, keyword)
        if not jobs and keyword == SEARCH_KEYWORDS[0]:
            errors = 1
        for job in jobs:
            job_id = job.get("bulletFields", [""])[0] + job.get("title", "")
            if job_id not in seen_in_this_run:
                seen_in_this_run.add(job_id)
                all_jobs.append(job)

    relevant = [job for job in all_jobs if is_relevant(job.get("title", ""))]

    for job in relevant:
        job["id"] = job.get("externalPath", job.get("title", "")).strip("/").replace("/", "-")

    new_jobs, seen_jobs = filter_new_jobs(relevant, seen_jobs)

    if new_jobs:
        print(f"  ✓ {len(new_jobs)} NEW match(es):")
        for job in new_jobs:
            title = job.get("title", "No title")
            path = job.get("externalPath", "")
            location = job.get("locationsText", "Not listed")

            base_domain = url.split("/wday/")[0]
            if path:
                if board_name:
                    job_url = f"{base_domain}/en-US/{board_name}{path}"
                else:
                    job_url = f"{base_domain}{path}"
            else:
                job_url = base_domain

            print(f"    - {title}")
            print(f"      {job_url}")

            # Workday requires fetching the job page for description
            description = fetch_workday_description(job_url)

            all_new_matches.append({
                "id": job["id"],
                "company": name,
                "title": title,
                "url": job_url,
                "location": location,
                "source": "Workday",
                "category": category,
                "date_found": datetime.now().strftime("%Y-%m-%d"),
                "description": description,
            })
    elif relevant:
        print(f"  — {len(relevant)} match(es) found but already seen")
    else:
        print(f"  — No matches")

    return seen_jobs, {"found": len(new_jobs), "errors": errors}


# ─────────────────────────────────────────────
# ASHBY
# ─────────────────────────────────────────────

def fetch_ashby_jobs(company_id):
    """
    Calls Ashby's official public job board API.
    Returns a list of public job postings.
    """
    url = f"https://api.ashbyhq.com/posting-api/job-board/{company_id}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 404:
            print(f"  [skipped] {company_id} — not found")
            return []

        if response.status_code != 200:
            print(f"  [skipped] {company_id} — status {response.status_code}")
            return []

        data = response.json()
        return [j for j in data.get("jobs", []) if j.get("isListed")]

    except requests.exceptions.RequestException as e:
        print(f"  [error] {company_id} — {e}")
        return []


def process_ashby(company, seen_jobs, all_new_matches):
    name = company["name"]
    company_id = company["company_id"]
    category = company.get("category", "general")

    print(f"\nChecking {name} (Ashby)...")
    jobs = fetch_ashby_jobs(company_id)
    relevant = [job for job in jobs if is_relevant(job.get("title", ""))]
    new_jobs, seen_jobs = filter_new_jobs(relevant, seen_jobs)

    if new_jobs:
        print(f"  ✓ {len(new_jobs)} NEW match(es):")
        for job in new_jobs:
            title = job.get("title", "No title")
            location = job.get("location", "Not listed")
            job_url = job.get("jobUrl") or f"https://jobs.ashbyhq.com/{company_id}/{job['id']}"

            print(f"    - {title}")
            print(f"      {job_url}")

            # Ashby includes descriptionPlain in the list response — no extra call needed
            description = clean_description(job.get("descriptionPlain", ""))

            all_new_matches.append({
                "id": job["id"],
                "company": name,
                "title": title,
                "url": job_url,
                "location": location,
                "source": "Ashby",
                "category": category,
                "date_found": datetime.now().strftime("%Y-%m-%d"),
                "description": description,
            })
    elif relevant:
        print(f"  — {len(relevant)} match(es) found but already seen")
    else:
        print(f"  — No matches")

    return seen_jobs, {"found": len(new_jobs), "errors": 0 if jobs else 1}


# ─────────────────────────────────────────────
# SMARTRECRUITERS
# ─────────────────────────────────────────────

def fetch_smartrecruiters_jobs(company_id, keyword):
    """
    Calls the SmartRecruiters public jobs API for a given company and keyword.
    Uses the q= query parameter to search server-side — no auth required.
    Returns a list of job postings.
    API docs: https://dev.smartrecruiters.com/customer-api/live-docs/job-posting-api/
    """
    url = f"https://api.smartrecruiters.com/v1/companies/{company_id}/postings"

    params = {
        "q": keyword,
        "limit": 100,
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 404:
            print(f"  [skipped] {company_id} — not found")
            return []

        if response.status_code != 200:
            print(f"  [skipped] {company_id} — status {response.status_code}")
            return []

        data = response.json()
        return data.get("content", [])

    except requests.exceptions.RequestException as e:
        print(f"  [error] {company_id} — {e}")
        return []


def process_smartrecruiters(company, seen_jobs, all_new_matches):
    name = company["name"]
    company_id = company["company_id"]
    category = company.get("category", "general")

    print(f"\nChecking {name} (SmartRecruiters)...")

    seen_in_this_run = set()
    all_jobs = []
    errors = 0

    for keyword in SEARCH_KEYWORDS:
        jobs = fetch_smartrecruiters_jobs(company_id, keyword)
        if not jobs and keyword == SEARCH_KEYWORDS[0]:
            errors = 1
        for job in jobs:
            job_id = job.get("id", "")
            if job_id and job_id not in seen_in_this_run:
                seen_in_this_run.add(job_id)
                all_jobs.append(job)

    relevant = [job for job in all_jobs if is_relevant(job.get("name", ""))]
    new_jobs, seen_jobs = filter_new_jobs(relevant, seen_jobs)

    if new_jobs:
        print(f"  ✓ {len(new_jobs)} NEW match(es):")
        for job in new_jobs:
            title = job.get("name", "No title")
            location_obj = job.get("location", {})
            location = location_obj.get("city") or location_obj.get("country") or "Not listed"
            job_url = f"https://jobs.smartrecruiters.com/{company_id}/{job.get('id', '')}"

            print(f"    - {title}")
            print(f"      {job_url}")

            # SmartRecruiters requires a second API call per job for description
            description = fetch_smartrecruiters_description(company_id, job.get("id", ""))

            all_new_matches.append({
                "id": job["id"],
                "company": name,
                "title": title,
                "url": job_url,
                "location": location,
                "source": "SmartRecruiters",
                "category": category,
                "date_found": datetime.now().strftime("%Y-%m-%d"),
                "description": description,
            })
    elif relevant:
        print(f"  — {len(relevant)} match(es) found but already seen")
    else:
        print(f"  — No matches")

    return seen_jobs, {"found": len(new_jobs), "errors": errors}


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def run_scraper():
    print("=" * 50)
    print(f"Job Scraper — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    seen_jobs = load_seen_jobs()
    print(f"\nPreviously seen jobs: {len(seen_jobs)}")

    all_new_matches = []

    # --- Greenhouse ---
    print("\n--- Greenhouse ---")
    greenhouse_found, greenhouse_errors = 0, 0
    for company in GREENHOUSE_COMPANIES:
        seen_jobs, result = process_greenhouse(company, seen_jobs, all_new_matches)
        greenhouse_found += result["found"]
        greenhouse_errors += result["errors"]

    # --- Lever ---
    print("\n--- Lever ---")
    lever_found, lever_errors = 0, 0
    for company in LEVER_COMPANIES:
        seen_jobs, result = process_lever(company, seen_jobs, all_new_matches)
        lever_found += result["found"]
        lever_errors += result["errors"]

    # --- Workday ---
    print("\n--- Workday ---")
    workday_found, workday_errors = 0, 0
    for company in WORKDAY_COMPANIES:
        seen_jobs, result = process_workday(company, seen_jobs, all_new_matches)
        workday_found += result["found"]
        workday_errors += result["errors"]

    # --- Ashby ---
    print("\n--- Ashby ---")
    ashby_found, ashby_errors = 0, 0
    for company in ASHBY_COMPANIES:
        seen_jobs, result = process_ashby(company, seen_jobs, all_new_matches)
        ashby_found += result["found"]
        ashby_errors += result["errors"]

    # --- SmartRecruiters ---
    print("\n--- SmartRecruiters ---")
    smartrecruiters_found, smartrecruiters_errors = 0, 0
    for company in SMARTRECRUITERS_COMPANIES:
        seen_jobs, result = process_smartrecruiters(company, seen_jobs, all_new_matches)
        smartrecruiters_found += result["found"]
        smartrecruiters_errors += result["errors"]

    # --- Save + notify ---
    if all_new_matches:
        save_jobs(all_new_matches)

    send_notification(all_new_matches)

    # --- Save run metrics ---
    companies_checked = (
        len(GREENHOUSE_COMPANIES) + len(LEVER_COMPANIES) +
        len(WORKDAY_COMPANIES) + len(ASHBY_COMPANIES) +
        len(SMARTRECRUITERS_COMPANIES)
    )
    companies_with_hits = len(set(job["company"] for job in all_new_matches))

    save_run_metrics({
        "run_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "jobs_found": len(all_new_matches),
        "greenhouse_found": greenhouse_found,
        "lever_found": lever_found,
        "workday_found": workday_found,
        "ashby_found": ashby_found,
        "smartrecruiters_found": smartrecruiters_found,
        "companies_checked": companies_checked,
        "companies_with_hits": companies_with_hits,
        "errors": (
            greenhouse_errors + lever_errors + workday_errors +
            ashby_errors + smartrecruiters_errors
        ),
    })

    print("\n" + "=" * 50)
    print(f"Done. {len(all_new_matches)} new job(s) found this run.")
    print("=" * 50)

    return all_new_matches


if __name__ == "__main__":
    run_scraper()