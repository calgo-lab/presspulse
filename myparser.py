import re
from bs4 import BeautifulSoup

ENTRY_SELECTOR = "div.article-details-text.u-space-bottom-xl"
_CAPS_PATTERN = re.compile(r"([A-ZÄÖÜ]{2,}(?:[\s\-\.][A-ZÄÖÜ]{2,})*)\s+[a-zäöü]")


def extract_entries(soup: BeautifulSoup, datum: str, artikel_url: str) -> list[dict]:
    entries = []
    for div in soup.select(ENTRY_SELECTOR):
        text = div.get_text(" ", strip=True)
        if len(text) < 30:
            continue

        name, url = _extract_name_and_url(div, artikel_url)
        entries.append({"name": name, "url": url, "text": text, "datum": datum})
    return entries


def _extract_name_and_url(div, artikel_url: str):
    link = div.find("a")
    if link:
        return link.get_text(strip=True), link.get("href", artikel_url)

    text = div.get_text(" ", strip=True)
    m = _CAPS_PATTERN.search(text)
    if m:
        return m.group(1).strip(), artikel_url

    return "Unbekannt", artikel_url
