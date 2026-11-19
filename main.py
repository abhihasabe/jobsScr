from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from datetime import date
from scraper import fetch_jobs, ALL_SUPPORTED_SITES
from save_jobs import save_jobs_to_db

SUPPORTED_SITES = ALL_SUPPORTED_SITES

app = FastAPI(
    title="Multi-Source Job Aggregator API",
    version="2.0",
    description=f"Fetch and save jobs from multiple sources: {', '.join(ALL_SUPPORTED_SITES)}"
)

@app.get("/")
def root():
    """Welcome route with quick navigation links."""
    return {
        "status": "online",
        "message": "Job Aggregator API is running!",
        "interactive_docs": "/docs",
        "endpoints": {
            "GET /docs": "Interactive Swagger UI to test and trigger scrapers",
            "GET /sources": "List all 11 supported job boards",
            "GET /jobs": "Fetch jobs & auto-save to MySQL DB (e.g. /jobs?job_title=Python+Developer&limit=10)",
        },
    }

@app.get("/sources")
def get_supported_sources():
    """Return all available job sources."""
    return {"supported_sites": SUPPORTED_SITES}

@app.get("/jobs")
def get_jobs(
    job_title: str = Query(..., description="Job title or keywords (e.g. 'Python Developer')"),
    location: str = Query("", description="City/Country or 'Remote' (leave blank for remote/global jobs)"),
    companies: Optional[List[str]] = Query(None, description="Filter by company names"),
    sites: Optional[List[str]] = Query(None, description=f"Specific sites to query. Defaults to all: {', '.join(SUPPORTED_SITES)}"),
    limit: int = Query(20, le=100, description="Max jobs to fetch per source"),
    posted_after: Optional[date] = Query(None, description="Filter jobs posted on or after this date (YYYY-MM-DD)"),
    remote: Optional[bool] = Query(None, description="Filter remote jobs (true/false)"),
):
    selected_sites = sites or SUPPORTED_SITES

    invalid = set(selected_sites) - set(SUPPORTED_SITES)
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sites: {', '.join(invalid)}"
        )

    jobs = fetch_jobs(
        job_title=job_title,
        location=location,
        companies=companies,
        sites=selected_sites,
        limit=limit,
        posted_after=posted_after,
        remote=remote,
    )

    print(f"📥 Jobs fetched: {len(jobs)}")

    saved_count = save_jobs_to_db(jobs)

    print(f"📦 Jobs saved to DB: {saved_count}")

    return {
        "sources": selected_sites,
        "count": len(jobs),
        "saved": saved_count,
        "jobs": jobs,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

