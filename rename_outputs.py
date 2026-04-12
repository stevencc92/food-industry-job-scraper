"""
rename_outputs.py — One-off script to retroactively rename existing output files
to include company and title in the filename.

Run once from the project root:
    python3 rename_outputs.py

Safe to run multiple times — skips files that are already renamed.
"""

import os
import re

OUTPUT_DIR = "output/jobs"


def slugify(text, max_length=40):
    """Convert a string to a safe filename slug."""
    text = text.strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "_", text)
    text = text.strip("_-")
    return text[:max_length]


def parse_header(filepath):
    """
    Reads the header block from an output file and returns company and title.
    Returns (None, None) if parsing fails.
    """
    company = None
    title = None

    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("Company:"):
                    company = line.replace("Company:", "").strip()
                elif line.startswith("Title:"):
                    title = line.replace("Title:", "").strip()
                if company and title:
                    break
    except Exception as e:
        print(f"  [error] Could not read {filepath}: {e}")

    return company, title


def rename_outputs():
    if not os.path.exists(OUTPUT_DIR):
        print(f"Output directory '{OUTPUT_DIR}' not found. Nothing to do.")
        return

    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".txt") and f != "index.txt"]

    if not files:
        print("No output files found.")
        return

    print(f"Found {len(files)} file(s) to process...\n")

    renamed = 0
    skipped = 0
    errors = 0

    for filename in sorted(files):
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Detect file type
        if "_cover_letter.txt" in filename:
            suffix = "_cover_letter.txt"
        elif "_resume_notes.txt" in filename:
            suffix = "_resume_notes.txt"
        else:
            print(f"  [skip] Unrecognized file pattern: {filename}")
            skipped += 1
            continue

        # Extract job ID from filename
        base = filename.replace(suffix, "")  # e.g. "job_7550844"
        parts = base.split("_", 1)
        if len(parts) < 2:
            print(f"  [skip] Could not extract job ID from: {filename}")
            skipped += 1
            continue
        job_id = parts[1]  # e.g. "7550844"

        # Skip if already renamed.
        # Original pattern exactly: job_{id}_cover_letter.txt or job_{id}_resume_notes.txt
        # Anything else (extra slugs, messy ATS IDs) gets left alone.
        expected_original = f"job_{job_id}{suffix}"
        if filename != expected_original:
            print(f"  [skip] Already renamed or complex ID: {filename}")
            skipped += 1
            continue

        # Parse company and title from file header
        company, title = parse_header(filepath)
        if not company or not title:
            print(f"  [error] Could not parse header from: {filename}")
            errors += 1
            continue

        # Build new filename
        company_slug = slugify(company)
        title_slug = slugify(title)
        new_filename = f"job_{job_id}_{company_slug}_{title_slug}{suffix}"
        new_filepath = os.path.join(OUTPUT_DIR, new_filename)

        # Rename
        try:
            os.rename(filepath, new_filepath)
            print(f"  ✓ {filename}")
            print(f"    → {new_filename}")
            renamed += 1
        except Exception as e:
            print(f"  [error] Could not rename {filename}: {e}")
            errors += 1

    print(f"\nDone. {renamed} renamed, {skipped} skipped, {errors} errors.")


if __name__ == "__main__":
    rename_outputs()