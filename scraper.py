"""
scraper.py — Phase 2: Greenhouse scraper with deduplication + storage
Now remembers which jobs it's seen and only surfaces new ones each run.
"""

import requests
from datetime import datetime
from companies import GREENHOUSE_COMPANIES, SEARCH_KEYWORDS
from storage import load_seen_jobs, save_seen_jobs, filter_new_jobs, save_jobs
from notifier import send_notification


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


def is_relevant(job_title):
    """
    Returns True if the job title contains any of our search keywords.
    Case-insensitive.
    """
    title_lower = job_title.lower()
    return any(keyword.lower() in title_lower for keyword in SEARCH_KEYWORDS)


def run_scraper():
    print("=" * 50)
    print(f"Job Scraper — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    # Load the IDs of jobs we've already seen
    seen_jobs = load_seen_jobs()
    print(f"\nPreviously seen jobs: {len(seen_jobs)}")

    all_new_matches = []

    for company in GREENHOUSE_COMPANIES:
        name = company["name"]
        token = company["board_token"]

        print(f"\nChecking {name}...")
        jobs = fetch_greenhouse_jobs(token)

        # Filter by keyword first
        relevant = [job for job in jobs if is_relevant(job["title"])]

        # Then filter out ones we've already seen
        new_jobs, seen_jobs = filter_new_jobs(relevant, seen_jobs)

        if new_jobs:
            print(f"  ✓ {len(new_jobs)} NEW match(es):")
            for job in new_jobs:
                print(f"    - {job['title']}")
                print(f"      {job.get('absolute_url', 'No URL')}")

                # Build a clean record to save
                all_new_matches.append({
                    "id": str(job["id"]),
                    "company": name,
                    "title": job["title"],
                    "url": job.get("absolute_url", ""),
                    "location": job.get("location", {}).get("name", "Not listed"),
                    "date_found": datetime.now().strftime("%Y-%m-%d"),
                })
        elif relevant:
            print(f"  — {len(relevant)} match(es) found but already seen")
        else:
            print(f"  — No matches")

    # Save everything
    if all_new_matches:
        save_jobs(all_new_matches)

    save_seen_jobs(seen_jobs)

    # Send email digest
    send_notification(all_new_matches)

    # Summary
    print("\n" + "=" * 50)
    print(f"Done. {len(all_new_matches)} new job(s) found this run.")
    print("=" * 50)

    return all_new_matches


if __name__ == "__main__":
    run_scraper()