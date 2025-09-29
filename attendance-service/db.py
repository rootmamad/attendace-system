import os
import psycopg2
import psycopg2.extras

def get_conn():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "attendance_db"),
        user=os.getenv("POSTGRES_USER", "attendance_user"),
        password=int(os.getenv("POSTGRES_PASSWORD", "1234")),
        host=os.getenv("POSTGRES_HOST", "db"),
        port=os.getenv("POSTGRES_PORT", "5432")
    )