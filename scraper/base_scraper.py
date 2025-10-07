# scraper/base_scraper.py
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import requests
import time
import random
import logging

logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self, user_agent: str=None, throttle=(1,2)):
        self.user_agent = user_agent or "JobMarketAnalyticsBot/1.0"
        self.throttle = throttle

    def _get(self, url: str, session=None):
        headers = {"User-Agent": self.user_agent}
        s = session or requests
        resp = s.get(url, headers=headers)
        resp.raise_for_status()
        # polite random sleep
        time.sleep(random.uniform(*self.throttle))
        return resp.text

    def parse_job_cards(self, html: str) -> List[Dict[str, Any]]:
        """
        Extract job postings from HTML and return list of dicts.
        Must be implemented by adapter.
        """
        raise NotImplementedError("Subclasses should implement parse_job_cards")

    def scrape(self, url: str, session=None) -> List[Dict[str, Any]]:
        html = self._get(url, session=session)
        return self.parse_job_cards(html)
