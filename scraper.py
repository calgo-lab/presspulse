import logging
import re
import requests
from bs4 import BeautifulSoup
from datetime import date
from myparser import extract_entries

logger = logging.getLogger(__name__)

LISTING_URL = "https://www.deutschlandfunk.de/internationale-presseschau-100.html"
BASE_URL = "https://www.deutschlandfunk.de"
LINK_SELECTOR = "article.b-article-teaser > a"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


def get_page(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")


def find_article_url() -> str:
    soup = get_page(LISTING_URL)
    for link in soup.select(LINK_SELECTOR):
        href = link.get("href", "")
        if "presseschau" in href.lower():
            return href if href.startswith("http") else BASE_URL + href
    raise ValueError(f"Kein Artikel-Link gefunden. Selektor '{LINK_SELECTOR}' im Browser prüfen.")


def scrape(url=None) -> dict:
    url = url or find_article_url()
    soup = get_page(url)
    artikel_datum = _extract_date(soup, url)
    return {
        "datum": artikel_datum,
        "eintraege": extract_entries(soup, artikel_datum, url),
    }


def _extract_date(soup: BeautifulSoup, url: str) -> str:
    time_el = soup.select_one("time")
    if time_el and time_el.get("datetime"):
        return time_el["datetime"][:10]
    m = re.search(r"(\d{4}-\d{2}-\d{2})", url)
    if m:
        return m.group(1)
    return date.today().isoformat()
