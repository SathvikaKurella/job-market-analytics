# etl/pipeline.py
from scraper.sample_adapter import SampleAdapter
from etl.db import init_db, upsert_job
from utils.text_utils import parse_salary
from datetime import datetime
import os

def run_sample_etl(sample_html_path: str):
    """
    Demo pipeline: read local sample HTML and load into DB
    """
    init_db()
    adapter = SampleAdapter()
    with open(sample_html_path, "r", encoding="utf-8") as f:
        html = f.read()
    jobs = adapter.parse_job_cards(html)
    for j in jobs:
        salary_min, salary_max, currency = parse_salary(j.get("salary_raw") or "")
        remote = False
        loc = j.get("location","").lower()
        if "remote" in loc:
            remote = True
        payload = {
            "source": j.get("source"),
            "job_title": j.get("job_title"),
            "company": j.get("company"),
            "location": j.get("location"),
            "salary_raw": j.get("salary_raw"),
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_currency": currency,
            "remote": remote,
            "description": j.get("description"),
            "requirements": j.get("requirements"),
            "url": j.get("url"),
        }
        upsert_job(payload)
    print(f"Inserted {len(jobs)} sample jobs into DB.")
