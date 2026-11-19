# Multi-Source Job Scraper & Database Aggregator

An automated, high-performance job aggregator that scrapes live job postings across **11 major job platforms**, normalizes the data into a unified schema, and automatically inserts and updates records in a remote or local **MySQL database** with deduplication.

---

## 🚀 Features

- **11 Integrated Job Sources**:
  - **JobSpy Scrapers**: LinkedIn, Indeed, Google Jobs, ZipRecruiter, Glassdoor, Naukri (India), Bayt (Middle East), BDJobs (Bangladesh).
  - **Direct REST APIs**: RemoteOK (Global Remote), Arbeitnow (Europe & Global), Jobicy (Worldwide Remote).
- **FastAPI Web Service**: Interactive Swagger UI at `/docs` with live scraping and filtering endpoints.
- **Direct CLI Runner**: Headless script (`run.py`) designed for cron jobs and background tasks.
- **MySQL Auto-Sync & Deduplication**: Uses `INSERT ... ON DUPLICATE KEY UPDATE` to insert new jobs and update existing listings automatically.
- **Fault-Tolerant & Concurrent**: Scrapes independent sources in parallel; failures or rate-limits on one platform won't block the others.
- **A2 Hosting / cPanel Ready**: Includes exact instructions for 6-hour scheduled automated cron runs.

---

## 📁 Project Structure

```text
├── main.py                 # FastAPI web application (/docs, /sources, /jobs)
├── run.py                  # CLI script to scrape & push jobs into MySQL (used by cron)
├── scraper.py              # Unified scraping engine (JobSpy + Custom APIs)
├── additional_sources.py   # REST scrapers for RemoteOK, Arbeitnow, and Jobicy
├── save_jobs.py            # MySQL database insertion logic with type sanitization
├── db.py                   # PyMySQL database connection configuration
├── test.py                 # Quick DB connection test script
├── jobs.json               # Local backup snapshot of scraped jobs
├── requirements.txt        # Python package dependencies
└── jobspy/                 # Embedded core JobSpy scraping package
```

---

## 📋 Supported Job Sources

| Key | Platform | Type | Region / Specialty |
| :--- | :--- | :--- | :--- |
| `linkedin` | **LinkedIn** | Scraper | Global |
| `indeed` | **Indeed** | Scraper | Global |
| `google` | **Google Jobs** | Scraper | Aggregates ATS (Greenhouse, Lever, etc.) |
| `remoteok` | **RemoteOK** | REST API | Global Tech & Remote |
| `arbeitnow` | **Arbeitnow** | REST API | Europe & Global Tech |
| `jobicy` | **Jobicy** | REST API | Global Remote |
| `zip_recruiter` | **ZipRecruiter** | Scraper | US & Canada |
| `glassdoor` | **Glassdoor** | Scraper | Global |
| `naukri` | **Naukri** | Scraper | India's #1 Job Board |
| `bayt` | **Bayt** | Scraper | Middle East & North Africa |
| `bdjobs` | **BDJobs** | Scraper | Bangladesh |

---

## 🛠️ Local Setup & Installation

### 1. Clone & Navigate to Project
```bash
git clone <repository-url>
cd jobsScr
```

### 2. Create and Activate Virtual Environment
```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Database Credentials
Edit `db.py` or set environment variables:
```python
# db.py
import os
import pymysql

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "190.92.174.87"),     # Use "localhost" on cPanel
        user=os.getenv("DB_USER", "worldjob_abhi"),
        password=os.getenv("DB_PASSWORD", "Mayu@7081"),
        database=os.getenv("DB_NAME", "worldjob_jobs"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
```

### 5. Verify Database Connection
```bash
python3 test.py
```
Expected output:
```text
Running DB test...
Connected DB: {'db_name': 'worldjob_jobs'}
Total rows in jobs table: {'total': ...}
✅ DB connection test succeeded!
```

---

## 💻 How to Run

### Option A: Run the FastAPI Web Server (Interactive API)

1. **Start the API server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   *(Or run `python3 main.py`)*

2. **Open Swagger UI in your browser**:
   👉 **`http://localhost:8000/docs`**

3. **Fetch & Save Jobs via cURL**:
   ```bash
   # Scrape software engineer roles in San Francisco (or remote) and auto-save to DB
   curl -G "http://localhost:8000/jobs" \
     --data-urlencode "job_title=Software Engineer" \
     --data-urlencode "location=San Francisco, CA" \
     --data-urlencode "limit=15"
   ```

   **Target specific platforms**:
   ```bash
   curl -G "http://localhost:8000/jobs" \
     --data-urlencode "job_title=Python Developer" \
     --data-urlencode "sites=remoteok" \
     --data-urlencode "sites=arbeitnow" \
     --data-urlencode "sites=linkedin" \
     --data-urlencode "limit=15"
   ```

---

### Option B: Run via CLI (Direct Scrape & DB Push)

Scrapes jobs and pushes them straight into MySQL without running the web server:
```bash
python3 run.py
```

- Query settings can be adjusted directly in `run.py`:
  ```python
  JOB_TITLE = "Software Engineer"
  LOCATION = "San Francisco, CA"   # Or "Remote", "New York", "India", etc.
  SELECTED_SITES = ["indeed", "linkedin", "google", "remoteok", "arbeitnow", "jobicy"]
  ```

---

### Option C: Push Existing `jobs.json` to Database
If you already have a `jobs.json` snapshot and want to insert it without re-scraping:
```bash
python3 save_jobs.py
```

---

## 🌐 A2 Hosting / cPanel Deployment & Automation

To run this application on **A2 Hosting** or any **cPanel** host and have it scrape & push jobs into MySQL automatically every 6 hours:

### 1. Upload Project Files
1. Open cPanel **File Manager**.
2. Upload and extract your project files into your application folder (e.g., `~/whitehattoolbox.com/jobScr`).
3. In `db.py`, set `host="localhost"` since MySQL is on the same server.

### 2. Install Dependencies via cPanel Terminal
In cPanel, open **Terminal** (under the "Advanced" section) and run:
```bash
source /home/worldjob/virtualenv/whitehattoolbox.com/jobScr/3.12/bin/activate && cd /home/worldjob/whitehattoolbox.com/jobScr && pip install -r requirements.txt
```

### 3. Schedule the 6-Hour Cron Job
1. In cPanel, navigate to **Cron Jobs**.
2. Under **Common Settings**, select **"Once every 6 hours"** (`0 */6 * * *`):
   - **Minute**: `0`
   - **Hour**: `*/6` (runs at 00:00, 06:00, 12:00, 18:00)
   - **Day**: `*`
   - **Month**: `*`
   - **Weekday**: `*`
3. Enter the following **Command**:
   ```bash
   /home/worldjob/virtualenv/whitehattoolbox.com/jobScr/3.12/bin/python /home/worldjob/whitehattoolbox.com/jobScr/run.py >> /home/worldjob/whitehattoolbox.com/jobScr/cron.log 2>&1
   ```
4. Click **Add New Cron Job**.

All automated execution logs with timestamps will be saved to `cron.log` in your project folder.

---

## 📊 Database Schema (`jobs` table)

The `save_jobs_to_db` function maps to the following MySQL table fields:

- `id` (VARCHAR / Primary Key)
- `site` (VARCHAR: `indeed`, `linkedin`, `remoteok`, etc.)
- `job_url`, `job_url_direct` (VARCHAR / TEXT)
- `title`, `description` (TEXT)
- `job_type`, `job_level`, `job_function`, `listing_type`
- `company`, `company_industry`, `company_url`, `company_logo`, `company_description`
- `company_num_employees`, `company_revenue`, `company_rating`, `company_reviews_count`
- `location`, `is_remote` (TINYINT: 0 or 1), `work_from_home_type`
- `salary_source`, `salary_interval`, `min_amount`, `max_amount`, `currency`
- `date_posted` (DATE), `vacancy_count`, `emails`, `skills`, `experience_range`
- `searched_company`
- `updated_at` (TIMESTAMP)

---

## 📄 License
MIT License
