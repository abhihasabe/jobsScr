from db import get_connection

def save_jobs_to_db(jobs: list):
    if not jobs:
        print("⚠️ No jobs received to save")
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    affected_rows = 0

    sql = """
    INSERT INTO jobs (
        id,
        site,
        job_url,
        job_url_direct,
        title,
        description,
        job_type,
        job_level,
        job_function,
        listing_type,
        company,
        company_industry,
        company_url,
        company_logo,
        company_description,
        company_num_employees,
        company_revenue,
        company_rating,
        company_reviews_count,
        location,
        is_remote,
        work_from_home_type,
        salary_source,
        salary_interval,
        min_amount,
        max_amount,
        currency,
        date_posted,
        vacancy_count,
        emails,
        skills,
        experience_range,
        searched_company
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s
    )
    ON DUPLICATE KEY UPDATE
        title = VALUES(title),
        description = VALUES(description),
        job_type = VALUES(job_type),
        job_level = VALUES(job_level),
        job_function = VALUES(job_function),
        listing_type = VALUES(listing_type),
        company = VALUES(company),
        company_industry = VALUES(company_industry),
        company_url = VALUES(company_url),
        company_logo = VALUES(company_logo),
        company_description = VALUES(company_description),
        company_num_employees = VALUES(company_num_employees),
        company_revenue = VALUES(company_revenue),
        company_rating = VALUES(company_rating),
        company_reviews_count = VALUES(company_reviews_count),
        location = VALUES(location),
        is_remote = VALUES(is_remote),
        work_from_home_type = VALUES(work_from_home_type),
        salary_source = VALUES(salary_source),
        salary_interval = VALUES(salary_interval),
        min_amount = VALUES(min_amount),
        max_amount = VALUES(max_amount),
        currency = VALUES(currency),
        date_posted = VALUES(date_posted),
        vacancy_count = VALUES(vacancy_count),
        emails = VALUES(emails),
        skills = VALUES(skills),
        experience_range = VALUES(experience_range),
        searched_company = VALUES(searched_company),
        updated_at = CURRENT_TIMESTAMP
    """

    try:
        for job in jobs:
            try:
                # Type-safe field normalization
                is_remote_val = job.get("is_remote")
                is_remote_int = 1 if is_remote_val in (True, 1, "1", "true", "True") else 0

                skills = job.get("skills")
                if isinstance(skills, list):
                    skills = ", ".join(str(s) for s in skills)

                emails = job.get("emails")
                if isinstance(emails, list):
                    emails = ", ".join(str(e) for e in emails)

                job_type = job.get("job_type")
                if isinstance(job_type, list):
                    job_type = ", ".join(str(t) for t in job_type)

                # Ensure numerical and date columns receive None instead of empty string
                min_amount = job.get("min_amount") or None
                max_amount = job.get("max_amount") or None
                date_posted = job.get("date_posted") or None
                vacancy_count = job.get("vacancy_count") or None
                company_rating = job.get("company_rating") or None
                company_reviews_count = job.get("company_reviews_count") or None

                cursor.execute(sql, (
                    job.get("id"),
                    job.get("site"),
                    job.get("job_url"),
                    job.get("job_url_direct"),
                    job.get("title"),
                    job.get("description"),
                    job_type,
                    job.get("job_level"),
                    job.get("job_function"),
                    job.get("listing_type"),
                    job.get("company"),
                    job.get("company_industry"),
                    job.get("company_url"),
                    job.get("company_logo"),
                    job.get("company_description"),
                    job.get("company_num_employees"),
                    job.get("company_revenue"),
                    company_rating,
                    company_reviews_count,
                    job.get("location"),
                    is_remote_int,
                    job.get("work_from_home_type"),
                    job.get("salary_source"),
                    job.get("interval"),  # from JSON
                    min_amount,
                    max_amount,
                    job.get("currency"),
                    date_posted,
                    vacancy_count,
                    emails,
                    skills,
                    job.get("experience_range"),
                    job.get("searched_company"),
                ))

                # Fix row counting
                if cursor.rowcount > 0:
                    affected_rows += 1

            except Exception as row_error:
                print("⚠️ Skipped one job due to error:", row_error)

        conn.commit()
        print(f"✅ Jobs inserted/updated: {affected_rows}")

    except Exception as e:
        conn.rollback()
        print("❌ DB Save Failed:", e)

    finally:
        cursor.close()
        conn.close()

    return affected_rows


if __name__ == "__main__":
    import json
    import os

    json_path = "jobs.json"
    if os.path.exists(json_path):
        print(f"📂 Reading existing jobs from '{json_path}'...")
        with open(json_path, "r", encoding="utf-8") as f:
            jobs_data = json.load(f)
        print(f"Loaded {len(jobs_data)} jobs. Pushing to database...")
        saved = save_jobs_to_db(jobs_data)
        print(f"🎉 Completed! {saved} jobs pushed/updated in database.")
    else:
        print(f"❌ '{json_path}' not found. Run 'python run.py' or start the API first.")

