"""
storage.py — Handles saving jobs and tracking which ones we've already seen.
Backed by SQLite instead of flat JSON files.

Database lives at: data/jobs.db
Tables:
  - jobs: all matched jobs, deduplicated by primary key
  - runs: one row per scraper run with platform-level metrics
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join("data", "jobs.db")


# ─────────────────────────────────────────────
# CONNECTION + SETUP
# ─────────────────────────────────────────────

def get_connection():
    """
    Opens a connection to the SQLite database.
    Creates the data/ directory and all tables if they don't exist yet.
    """
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _create_tables(conn)
    return conn


def _create_tables(conn):
    """
    Creates all tables if they don't already exist.
    Also handles migrations for new columns added after initial deployment —
    existing data is never lost.
    """
    # jobs table — one row per unique job match
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id          TEXT PRIMARY KEY,
            company     TEXT,
            title       TEXT,
            url         TEXT,
            location    TEXT,
            source      TEXT,
            category    TEXT,
            date_found  TEXT,
            description TEXT,
            processed   BOOLEAN DEFAULT 0
        )
    """)

    # runs table — one row per scraper run
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at                  TEXT,
            jobs_found              INTEGER,
            greenhouse_found        INTEGER,
            lever_found             INTEGER,
            workday_found           INTEGER,
            ashby_found             INTEGER,
            smartrecruiters_found   INTEGER,
            companies_checked       INTEGER,
            companies_with_hits     INTEGER,
            errors                  INTEGER
        )
    """)

    # Migrations — safe to run on existing databases, existing data never lost
    existing_job_columns = [
        row[1] for row in conn.execute("PRAGMA table_info(jobs)").fetchall()
    ]
    existing_run_columns = [
        row[1] for row in conn.execute("PRAGMA table_info(runs)").fetchall()
    ]

    if "smartrecruiters_found" not in existing_run_columns:
        conn.execute("ALTER TABLE runs ADD COLUMN smartrecruiters_found INTEGER")

    if "description" not in existing_job_columns:
        conn.execute("ALTER TABLE jobs ADD COLUMN description TEXT")

    if "processed" not in existing_job_columns:
        conn.execute("ALTER TABLE jobs ADD COLUMN processed BOOLEAN DEFAULT 0")

    conn.commit()


# ─────────────────────────────────────────────
# SEEN JOBS — derived from the jobs table
# ─────────────────────────────────────────────

def load_seen_jobs():
    """
    Returns a set of all job IDs we've already stored.
    The jobs table is the single source of truth — no separate seen file needed.
    """
    conn = get_connection()
    try:
        cursor = conn.execute("SELECT id FROM jobs")
        return set(row["id"] for row in cursor.fetchall())
    finally:
        conn.close()


def filter_new_jobs(jobs, seen_jobs):
    """
    Given a list of jobs and the set of already-seen IDs,
    returns only the jobs we haven't stored before.
    Marks each new job as seen immediately so duplicates within
    the same run are also caught.
    """
    new_jobs = []

    for job in jobs:
        job_id = str(job["id"])

        if job_id not in seen_jobs:
            new_jobs.append(job)
            seen_jobs.add(job_id)

    return new_jobs, seen_jobs


# ─────────────────────────────────────────────
# JOBS TABLE — saving and loading
# ─────────────────────────────────────────────

def save_jobs(new_jobs):
    """
    Inserts new job matches into the database.
    INSERT OR IGNORE means duplicate IDs are silently skipped —
    the primary key enforces deduplication at the DB level.
    Includes description if present in the job dict.
    """
    conn = get_connection()
    try:
        conn.executemany("""
            INSERT OR IGNORE INTO jobs
                (id, company, title, url, location, source, category, date_found, description)
            VALUES
                (:id, :company, :title, :url, :location, :source, :category, :date_found, :description)
        """, [_normalize_job(j) for j in new_jobs])
        conn.commit()
        print(f"  [storage] {len(new_jobs)} new job(s) saved to {DB_PATH}")
    finally:
        conn.close()


def _normalize_job(job):
    """Ensures every job dict has a description key before insert."""
    return {**job, "description": job.get("description") or None}


def load_jobs():
    """
    Returns all stored jobs as a list of plain dicts.
    Useful for manual querying and future analysis.
    """
    conn = get_connection()
    try:
        cursor = conn.execute("SELECT * FROM jobs ORDER BY date_found DESC")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


# ─────────────────────────────────────────────
# RUN METRICS — one row per scraper run
# ─────────────────────────────────────────────

def save_run_metrics(metrics):
    """
    Writes one row to the runs table at the end of each scraper run.
    metrics is a dict with keys matching the runs table columns.
    """
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO runs
                (run_at, jobs_found, greenhouse_found, lever_found,
                 workday_found, ashby_found, smartrecruiters_found,
                 companies_checked, companies_with_hits, errors)
            VALUES
                (:run_at, :jobs_found, :greenhouse_found, :lever_found,
                 :workday_found, :ashby_found, :smartrecruiters_found,
                 :companies_checked, :companies_with_hits, :errors)
        """, metrics)
        conn.commit()
        print(f"  [storage] Run metrics saved.")
    finally:
        conn.close()