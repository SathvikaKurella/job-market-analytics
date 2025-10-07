# etl/jsearch_pipeline.py
from scraper.jsearch_adapter import JSearchAdapter
from etl.db import init_db, upsert_job

def run_jsearch_etl(query="Data Engineer", location="United States", pages=1):
    """
    ETL pipeline to fetch real jobs from JSearch API and load into DB.
    """
    init_db()
    adapter = JSearchAdapter()
    jobs = adapter.fetch_jobs(query=query, location=location, pages=pages)
    print(f"Fetched {len(jobs)} jobs from JSearch API.")
    for job in jobs:
        upsert_job(job)
    print(f"Inserted {len(jobs)} records into DB.")
