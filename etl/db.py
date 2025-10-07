# etl/db.py
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Numeric, Boolean, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from sqlalchemy import inspect

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "jobsdb")
DB_USER = os.getenv("DB_USER", "jobuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "jobpassword")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, future=True)
metadata = MetaData()

job_postings = Table(
    "job_postings",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("source", String(255)),
    Column("scraped_at", TIMESTAMP(timezone=True), server_default=text("now()")),
    Column("job_title", String(512)),
    Column("company", String(512)),
    Column("location", String(512)),
    Column("salary_raw", Text),
    Column("salary_min", Numeric),
    Column("salary_max", Numeric),
    Column("salary_currency", String(16)),
    Column("remote", Boolean),
    Column("description", Text),
    Column("requirements", Text),
    Column("url", String(1024), unique=True),
)

def init_db():
    metadata.create_all(engine)

def upsert_job(job: dict):
    """
    Upsert a job posting using the URL as unique key.
    """
    with engine.begin() as conn:
        stmt = pg_insert(job_postings).values(**job)
        do_update_stmt = stmt.on_conflict_do_update(
            index_elements=[job_postings.c.url],
            set_={
                "job_title": stmt.excluded.job_title,
                "company": stmt.excluded.company,
                "location": stmt.excluded.location,
                "salary_raw": stmt.excluded.salary_raw,
                "salary_min": stmt.excluded.salary_min,
                "salary_max": stmt.excluded.salary_max,
                "salary_currency": stmt.excluded.salary_currency,
                "remote": stmt.excluded.remote,
                "description": stmt.excluded.description,
                "requirements": stmt.excluded.requirements,
            }
        )
        conn.execute(do_update_stmt)
