"""
storage.py — Handles saving jobs and tracking which ones we've already seen.
Two jobs:
  1. Save new matches to jobs.json
  2. Maintain a seen_jobs.json so we never notify about the same job twice
"""

import json
import os

# These files will live in your project folder
JOBS_FILE = "jobs.json"
SEEN_FILE = "seen_jobs.json"


# ─────────────────────────────────────────────
# SEEN JOBS — the scraper's memory
# ─────────────────────────────────────────────

def load_seen_jobs():
    """
    Loads the set of job IDs we've already seen.
    If the file doesn't exist yet (first run), returns an empty set.
    A set is like a list but automatically ignores duplicates.
    """
    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r") as f:
        data = json.load(f)
        return set(data)  # convert list → set for fast lookups


def save_seen_jobs(seen_jobs):
    """
    Saves the current set of seen job IDs to disk.
    We convert the set to a list first because JSON can't store sets directly.
    """
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen_jobs), f, indent=2)


def filter_new_jobs(jobs, seen_jobs):
    """
    Given a list of jobs and the set of already-seen IDs,
    returns only the jobs we haven't notified about before.
    """
    new_jobs = []

    for job in jobs:
        job_id = str(job["id"])  # Greenhouse uses numeric IDs — convert to string for consistency

        if job_id not in seen_jobs:
            new_jobs.append(job)
            seen_jobs.add(job_id)  # mark it as seen immediately

    return new_jobs, seen_jobs  # return both so the scraper can save the updated seen list


# ─────────────────────────────────────────────
# JOBS FILE — the running log of all matches
# ─────────────────────────────────────────────

def load_jobs():
    """
    Loads all previously saved jobs.
    Returns an empty list if the file doesn't exist yet.
    """
    if not os.path.exists(JOBS_FILE):
        return []

    with open(JOBS_FILE, "r") as f:
        return json.load(f)


def save_jobs(new_jobs):
    """
    Appends new matches to the jobs file.
    Loads what's already there, adds the new ones, saves it back.
    """
    existing = load_jobs()
    combined = existing + new_jobs

    with open(JOBS_FILE, "w") as f:
        json.dump(combined, f, indent=2)

    print(f"  [storage] {len(new_jobs)} new job(s) saved to {JOBS_FILE}")