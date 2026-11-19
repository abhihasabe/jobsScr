from __future__ import annotations

import os
import sys
import json
from datetime import datetime

# Ensure working directory is always the script's directory (crucial for Cron jobs)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from scraper import fetch_jobs, ALL_SUPPORTED_SITES
from save_jobs import save_jobs_to_db

# Configure search parameters
JOB_TITLE = "Software Engineer"
LOCATION = "San Francisco, CA"  # Can also be "Remote", "New York", "India", etc.

# You can pick specific sources or use ALL_SUPPORTED_SITES:
# Built-in JobSpy: "indeed", "linkedin", "zip_recruiter", "glassdoor", "google", "naukri", "bayt", "bdjobs"
# Additional APIs: "remoteok", "arbeitnow", "jobicy"
SELECTED_SITES = [
    "indeed",
    "linkedin",
    "google",
    "remoteok",
    "arbeitnow",
    "jobicy",
]

now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"\n==================================================")
print(f"🕒 [{now_str}] Starting automated job scrape...")
print(f"🚀 Fetching jobs from {len(SELECTED_SITES)} sources:")
print("   " + ", ".join(SELECTED_SITES))

jobs = fetch_jobs(
    job_title=JOB_TITLE,
    location=LOCATION,
    sites=SELECTED_SITES,
    limit=15,  # per site
)

print(f"\n📥 Total jobs collected across all sources: {len(jobs)}")

if jobs:
    # Save snapshot to jobs.json (default=str handles any date/datetime objects)
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False, default=str)
    print("✅ jobs.json snapshot created successfully")

    # Push all fetched jobs to MySQL DB
    print("📤 Pushing latest jobs to database...")
    saved_count = save_jobs_to_db(jobs)
    print(f"🎉 Complete! {saved_count} jobs inserted/updated in MySQL database.")
else:
    print("⚠️ No jobs returned from the selected sources.")

print(f"🏁 Finished execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

