import pandas as pd
from jobspy import scrape_jobs
from datetime import date
from typing import List, Dict

def fetch_jobs(
    job_title: str,
    location: str,
    companies: list[str] | None,
    sites: list[str],
    limit: int,
    posted_after: date | None,
    remote: bool | None,
) -> List[Dict]:
    all_jobs = []

    search_targets = companies if companies else [""]

    for company in search_targets:
        search_term = f"{job_title} {company}".strip()

        df = scrape_jobs(
            site_name=sites,
            search_term=search_term,
            location=location,
            results_wanted=limit,
        )

        if df.empty:
            print(f"No jobs found for '{search_term}' on {sites}")
            continue

        df["searched_company"] = company

        if remote is not None and "is_remote" in df.columns:
            df = df[df["is_remote"] == remote]

        if posted_after and "date_posted" in df.columns:
            df["date_posted"] = pd.to_datetime(df["date_posted"], errors="coerce")
            df = df[df["date_posted"] >= pd.Timestamp(posted_after)]

        all_jobs.append(df)

    if not all_jobs:
        return []

    final_df = pd.concat(all_jobs, ignore_index=True)

    # Convert datetime columns to ISO format
    final_df = final_df.apply(
        lambda col: col.map(lambda x: x.isoformat() if hasattr(x, "isoformat") else x)
        if pd.api.types.is_datetime64_any_dtype(col) else col
    )

    return final_df.fillna("").to_dict(orient="records")