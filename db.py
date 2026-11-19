import os
import pymysql

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "190.92.174.87"),
        user=os.getenv("DB_USER", "worldjob_abhi"),
        password=os.getenv("DB_PASSWORD", "Mayu@7081"),
        database=os.getenv("DB_NAME", "worldjob_jobs"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )