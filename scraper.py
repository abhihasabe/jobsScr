from __future__ import annotations

import pandas as pd
from datetime import date
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from jobspy import scrape_jobs
from additional_sources import (
    CUSTOM_SOURCES,
    fetch_custom_jobs,
)

JOBSPY_SITES = [
    "indeed",
    "linkedin",
    "zip_recruiter",
    "glassdoor",
    "google",
    "naukri",
    "bayt",
    "bdjobs",
]

ALL_SUPPORTED_SITES = JOBSPY_SITES + CUSTOM_SOURCES


def fetch_jobs(
    job_title: str,
    location: str = "",
    companies: Optional[List[str]] = None,
    sites: Optional[List[str]] = None,
    limit: int = 20,
    posted_after: Optional[date] = None,
    remote: Optional[bool] = None,
) -> List[Dict]:
    """
    Fetches jobs across multiple boards (JobSpy built-ins + custom REST job APIs)
    and unifies them into a clean list of dictionaries ready for DB insertion.
    """
    selected_sites = [s.lower().strip() for s in (sites or ALL_SUPPORTED_SITES)]

    # Separate into JobSpy supported sites and custom API sources
    jobspy_targets = [s for s in selected_sites if s in JOBSPY_SITES]
    custom_targets = [s for s in selected_sites if s in CUSTOM_SOURCES]

    search_targets = companies if companies else [""]
    all_jobs: List[Dict] = []

    # 1. Fetch from JobSpy sites
    if jobspy_targets:
        for company in search_targets:
            search_term = f"{job_title} {company}".strip()
            try:
                df = scrape_jobs(
                    site_name=jobspy_targets,
                    search_term=search_term,
                    location=location,
                    results_wanted=limit,
                )

                if not df.empty:
                    df["searched_company"] = company

                    if remote is not None and "is_remote" in df.columns:
                        df = df[df["is_remote"] == remote]

                    if posted_after and "date_posted" in df.columns:
                        df["date_posted"] = pd.to_datetime(df["date_posted"], errors="coerce")
                        df = df[df["date_posted"] >= pd.Timestamp(posted_after)]

                    # Ensure all date/datetime/Timestamp objects are converted to ISO string
                    for col in df.columns:
                        try:
                            df[col] = df[col].map(lambda x: x.isoformat() if hasattr(x, "isoformat") else x)
                        except Exception:
                            pass

                    records = df.fillna("").to_dict(orient="records")
                    for r in records:
                        if hasattr(r.get("date_posted"), "isoformat"):
                            r["date_posted"] = r["date_posted"].isoformat()
                        elif r.get("date_posted") is not None:
                            r["date_posted"] = str(r["date_posted"]) if r["date_posted"] != "" else ""

                    all_jobs.extend(records)
                else:
                    print(f"ℹ️ No jobs found for '{search_term}' on {jobspy_targets}")

            except Exception as e:
                print(f"⚠️ Error scraping JobSpy sites {jobspy_targets} for '{search_term}': {e}")

    # 2. Fetch from custom API sources concurrently
    if custom_targets:
        search_query = job_title.strip()
        with ThreadPoolExecutor(max_workers=len(custom_targets)) as executor:
            future_to_site = {
                executor.submit(fetch_custom_jobs, site, search_query, limit): site
                for site in custom_targets
            }

            for future in as_completed(future_to_site):
                site_name = future_to_site[future]
                try:
                    site_jobs = future.result()
                    for job in site_jobs:
                        # Remote filter
                        if remote is not None:
                            if bool(job.get("is_remote")) != remote:
                                continue

                        # Posted after filter
                        if posted_after and job.get("date_posted"):
                            try:
                                job_date = pd.to_datetime(job["date_posted"])
                                if job_date < pd.Timestamp(posted_after):
                                    continue
                            except Exception:
                                pass

                        all_jobs.append(job)

                    print(f"✅ Fetched {len(site_jobs)} jobs from {site_name}")
                except Exception as exc:
                    print(f"⚠️ Error fetching from custom source {site_name}: {exc}")

    return all_jobs
