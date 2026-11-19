from __future__ import annotations

import requests
import datetime
from typing import List, Dict, Any

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

CUSTOM_SOURCES = ["remoteok", "arbeitnow", "jobicy"]


def fetch_remoteok(search_term: str = "", limit: int = 20) -> List[Dict[str, Any]]:
    """Fetch remote tech jobs from RemoteOK public API."""
    url = "https://remoteok.com/api"
    jobs: List[Dict[str, Any]] = []

    try:
        response = requests.get(url, headers=HEADERS, timeout=12)
        if response.status_code != 200:
            print(f"⚠️ RemoteOK returned status code {response.status_code}")
            return []

        data = response.json()
        search_lower = search_term.lower().strip()

        # Item 0 is metadata/legal statement in RemoteOK API
        items = data[1:] if len(data) > 1 and isinstance(data[0], dict) and "legal" in data[0] else data

        for item in items:
            if not isinstance(item, dict):
                continue

            position = item.get("position", "")
            tags = item.get("tags") or []
            tags_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
            description = item.get("description", "")
            company = item.get("company", "")

            # Filter by search_term if provided
            if search_lower:
                combined_text = f"{position} {tags_str} {company} {description}".lower()
                if search_lower not in combined_text:
                    continue

            # Format date
            date_raw = item.get("date")
            date_posted = None
            if date_raw:
                try:
                    date_posted = date_raw.split("T")[0]
                except Exception:
                    date_posted = None

            min_salary = item.get("salary_min")
            max_salary = item.get("salary_max")

            jobs.append({
                "id": f"ro-{item.get('id')}",
                "site": "remoteok",
                "job_url": item.get("url") or f"https://remoteok.com/remote-jobs/{item.get('id')}",
                "job_url_direct": item.get("apply_url") or item.get("url"),
                "title": position,
                "description": description,
                "job_type": "fulltime",
                "job_level": "",
                "job_function": "",
                "listing_type": "",
                "company": company,
                "company_industry": "",
                "company_url": "",
                "company_logo": item.get("company_logo", ""),
                "company_description": "",
                "company_num_employees": "",
                "company_revenue": "",
                "company_rating": None,
                "company_reviews_count": None,
                "location": item.get("location") or "Remote",
                "is_remote": True,
                "work_from_home_type": "Remote",
                "salary_source": "direct_data" if min_salary else "",
                "interval": "yearly",
                "min_amount": float(min_salary) if min_salary else None,
                "max_amount": float(max_salary) if max_salary else None,
                "currency": "USD",
                "date_posted": date_posted,
                "vacancy_count": None,
                "emails": "",
                "skills": tags_str,
                "experience_range": "",
                "searched_company": "",
            })

            if len(jobs) >= limit:
                break

    except Exception as e:
        print(f"❌ Failed to fetch from RemoteOK: {e}")

    return jobs


def fetch_arbeitnow(search_term: str = "", limit: int = 20) -> List[Dict[str, Any]]:
    """Fetch jobs from Arbeitnow public job board API (Europe / Remote / Global)."""
    url = "https://www.arbeitnow.com/api/job-board-api"
    params = {"search": search_term} if search_term else {}
    jobs: List[Dict[str, Any]] = []

    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=12)
        if response.status_code != 200:
            print(f"⚠️ Arbeitnow returned status code {response.status_code}")
            return []

        payload = response.json()
        data = payload.get("data", [])

        for item in data:
            if not isinstance(item, dict):
                continue

            created_at = item.get("created_at")
            date_posted = None
            if created_at:
                try:
                    date_posted = datetime.datetime.fromtimestamp(created_at).strftime("%Y-%m-%d")
                except Exception:
                    date_posted = None

            tags = item.get("tags") or []
            tags_str = ", ".join(tags) if isinstance(tags, list) else str(tags)

            job_types = item.get("job_types") or []
            job_type_str = ", ".join(job_types).lower() if isinstance(job_types, list) else str(job_types).lower()

            is_remote_flag = bool(item.get("remote", False))

            jobs.append({
                "id": f"an-{item.get('slug')}",
                "site": "arbeitnow",
                "job_url": item.get("url", ""),
                "job_url_direct": item.get("url", ""),
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "job_type": job_type_str or "fulltime",
                "job_level": "",
                "job_function": "",
                "listing_type": "",
                "company": item.get("company_name", ""),
                "company_industry": "",
                "company_url": "",
                "company_logo": "",
                "company_description": "",
                "company_num_employees": "",
                "company_revenue": "",
                "company_rating": None,
                "company_reviews_count": None,
                "location": item.get("location") or ("Remote" if is_remote_flag else ""),
                "is_remote": is_remote_flag,
                "work_from_home_type": "Remote" if is_remote_flag else "",
                "salary_source": "",
                "interval": "",
                "min_amount": None,
                "max_amount": None,
                "currency": "",
                "date_posted": date_posted,
                "vacancy_count": None,
                "emails": "",
                "skills": tags_str,
                "experience_range": "",
                "searched_company": "",
            })

            if len(jobs) >= limit:
                break

    except Exception as e:
        print(f"❌ Failed to fetch from Arbeitnow: {e}")

    return jobs


def fetch_jobicy(search_term: str = "", limit: int = 20) -> List[Dict[str, Any]]:
    """Fetch remote jobs from Jobicy public API."""
    url = "https://jobicy.com/api/v2/remote-jobs"
    params = {"count": min(limit, 50)}
    if search_term:
        params["tag"] = search_term

    jobs: List[Dict[str, Any]] = []

    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=12)
        if response.status_code != 200:
            print(f"⚠️ Jobicy returned status code {response.status_code}")
            return []

        payload = response.json()
        data = payload.get("jobs", [])

        for item in data:
            if not isinstance(item, dict):
                continue

            pub_date = item.get("pubDate")
            date_posted = None
            if pub_date:
                try:
                    date_posted = pub_date.split(" ")[0]
                except Exception:
                    date_posted = None

            min_salary = item.get("annualSalaryMin")
            max_salary = item.get("annualSalaryMax")

            industries = item.get("jobIndustry") or []
            industry_str = ", ".join(industries) if isinstance(industries, list) else str(industries)

            job_types = item.get("jobType") or []
            job_type_str = ", ".join(job_types) if isinstance(job_types, list) else str(job_types)

            jobs.append({
                "id": f"ji-{item.get('id')}",
                "site": "jobicy",
                "job_url": item.get("url", ""),
                "job_url_direct": item.get("url", ""),
                "title": item.get("jobTitle", ""),
                "description": item.get("jobDescription", ""),
                "job_type": job_type_str.lower() or "fulltime",
                "job_level": item.get("jobLevel", ""),
                "job_function": "",
                "listing_type": "",
                "company": item.get("companyName", ""),
                "company_industry": industry_str,
                "company_url": "",
                "company_logo": item.get("companyLogo", ""),
                "company_description": "",
                "company_num_employees": "",
                "company_revenue": "",
                "company_rating": None,
                "company_reviews_count": None,
                "location": item.get("jobGeo") or "Remote",
                "is_remote": True,
                "work_from_home_type": "Remote",
                "salary_source": "direct_data" if min_salary else "",
                "interval": "yearly" if min_salary else "",
                "min_amount": float(min_salary) if min_salary else None,
                "max_amount": float(max_salary) if max_salary else None,
                "currency": item.get("salaryCurrency") or "USD",
                "date_posted": date_posted,
                "vacancy_count": None,
                "emails": "",
                "skills": industry_str,
                "experience_range": "",
                "searched_company": "",
            })

            if len(jobs) >= limit:
                break

    except Exception as e:
        print(f"❌ Failed to fetch from Jobicy: {e}")

    return jobs


def fetch_custom_jobs(site: str, search_term: str = "", limit: int = 20) -> List[Dict[str, Any]]:
    """Dispatch helper for custom APIs."""
    site_key = site.lower().strip()
    if site_key == "remoteok":
        return fetch_remoteok(search_term=search_term, limit=limit)
    elif site_key == "arbeitnow":
        return fetch_arbeitnow(search_term=search_term, limit=limit)
    elif site_key == "jobicy":
        return fetch_jobicy(search_term=search_term, limit=limit)
    return []
