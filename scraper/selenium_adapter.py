# scraper/selenium_adapter.py
# Optional Selenium adapter to render JS-heavy pages.
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

class SeleniumAdapter(BaseScraper):
    def __init__(self, driver_path=None, headless=True, **kwargs):
        super().__init__(**kwargs)
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        self.driver_path = driver_path
        self.opts = opts

    def _render(self, url: str) -> str:
        driver = webdriver.Chrome(options=self.opts) if not self.driver_path else webdriver.Chrome(self.driver_path, options=self.opts)
        driver.get(url)
        time.sleep(2)  # wait a bit for JS to run — tune this
        html = driver.page_source
        driver.quit()
        return html

    def scrape(self, url: str, session=None) -> List[Dict[str, Any]]:
        html = self._render(url)
        return self.parse_job_cards(html)
