# scraper/jsearch_adapter.py
import requests
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class JSearchAdapter:
    """
    Adapter for the JSearch API (https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
    """
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("JSEARCH_API_KEY")
        self.url = "https://jsearch.p.rapidapi.com/search"

    def fetch_jobs(self, query="Data Engineer", location="United States", pages=1) -> List[Dict]:
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "jsearch.p.rapidapi.com"
        }
        all_jobs = []
        for page in range(1, pages + 1):
            params = {"query": f"{query} in {location}", "page": page}
            resp = requests.get(self.url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json().get("data", [])
            for job in data:
                all_jobs.append({
                    "source": "jsearch",
                    "job_title": job.get("job_title"),
                    "company": job.get("employer_name"),
                    "location": job.get("job_city") or job.get("job_country"),
                    "salary_raw": job.get("job_salary_currency") and f"{job.get('job_salary_currency')} {job.get('job_salary_min')} - {job.get('job_salary_max')}",
                    "salary_min": job.get("job_salary_min"),
                    "salary_max": job.get("job_salary_max"),
                    "salary_currency": job.get("job_salary_currency"),
                    "remote": job.get("job_is_remote"),
                    "description": job.get("job_description"),
                    "requirements": job.get("job_required_skills"),
                    "url": job.get("job_apply_link"),
                })
        return all_jobs
