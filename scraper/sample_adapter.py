# scraper/sample_adapter.py
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import re

class SampleAdapter(BaseScraper):
    """
    A simple adapter that parses the sample HTML in samples/sample_jobs_page.html.
    Use this as a testing/demo adapter.
    """
    def parse_job_cards(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "lxml")
        jobs = []
        for div in soup.select(".job"):
            url = div.get("data-url") or div.select_one("a[href]") and div.select_one("a[href]")['href']
            title_el = div.select_one(".title")
            company_el = div.select_one(".company")
            location_el = div.select_one(".location")
            salary_el = div.select_one(".salary")
            desc_el = div.select_one(".description")
            req_el = div.select_one(".requirements")
            job = {
                "source": "sample",
                "job_title": title_el.get_text(strip=True) if title_el else None,
                "company": company_el.get_text(strip=True) if company_el else None,
                "location": location_el.get_text(strip=True) if location_el else None,
                "salary_raw": salary_el.get_text(strip=True) if salary_el else None,
                "description": desc_el.get_text(strip=True) if desc_el else None,
                "requirements": req_el.get_text(strip=True) if req_el else None,
                "url": url,
            }
            jobs.append(job)
        return jobs
