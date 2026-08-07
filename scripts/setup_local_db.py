"""Provision local PostgreSQL database for Resume Shortlister.

Usage:
  set PGPASSWORD=your_postgres_password
  python scripts/setup_local_db.py

Creates user `shortlister`, database `resume_shortlister`, and applies schema.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_NAME = os.getenv("POSTGRES_DB", "resume_shortlister")
DB_USER = os.getenv("POSTGRES_USER", "shortlister")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "shortlister")
ADMIN_USER = os.getenv("POSTGRES_ADMIN_USER", "postgres")
ADMIN_PASS = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_ADMIN_PASSWORD", "")

INIT_SQL = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "init.sql")


def main():
    if not ADMIN_PASS:
        print("ERROR: Set PGPASSWORD or POSTGRES_ADMIN_PASSWORD to your postgres superuser password.")
        print("Example: $env:PGPASSWORD='yourpassword'; python scripts/setup_local_db.py")
        sys.exit(1)

    print(f"Connecting as {ADMIN_USER}...")
    conn = psycopg2.connect(
        host="localhost", port=5432, user=ADMIN_USER, password=ADMIN_PASS, dbname="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (DB_USER,))
    if not cur.fetchone():
        cur.execute(f"CREATE USER {DB_USER} WITH PASSWORD %s", (DB_PASS,))
        print(f"Created user: {DB_USER}")
    else:
        cur.execute(f"ALTER USER {DB_USER} WITH PASSWORD %s", (DB_PASS,))
        print(f"Updated password for user: {DB_USER}")

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    if not cur.fetchone():
        cur.execute(f'CREATE DATABASE "{DB_NAME}" OWNER {DB_USER}')
        print(f"Created database: {DB_NAME}")
    else:
        print(f"Database exists: {DB_NAME}")

    cur.close()
    conn.close()

    print("Applying schema...")
    app_conn = psycopg2.connect(
        host="localhost", port=5432, user=DB_USER, password=DB_PASS, dbname=DB_NAME
    )
    app_conn.autocommit = True
    app_cur = app_conn.cursor()

    with open(INIT_SQL, "r", encoding="utf-8") as f:
        sql = f.read()

    # init.sql uses CREATE TABLE without IF NOT EXISTS — skip if users table exists
    app_cur.execute(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
    )
    if app_cur.fetchone()[0]:
        print("Schema already exists, skipping init.sql")
    else:
        app_cur.execute(sql)
        print("Schema applied from init.sql")

    app_cur.close()
    app_conn.close()
    print(f"\nDatabase ready: postgresql://{DB_USER}:{DB_PASS}@localhost:5432/{DB_NAME}")


if __name__ == "__main__":
    main()
