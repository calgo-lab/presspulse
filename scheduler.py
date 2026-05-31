#!/usr/bin/env python3
import argparse
import base64
import json
import logging
import os
import sys
from pathlib import Path
from scraper import scrape
from classifier import classify

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=None, help="Direkter Artikel-URL (überspringt Listing-Seite)")
    parser.add_argument("--output-dir", default="/volume/output/data")
    args = parser.parse_args()

    try:
        data = scrape(args.url)
        data["eintraege"] = classify(data["eintraege"])

        out = Path(args.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        filepath = out / "presseschau.json"

        existing = json.loads(filepath.read_text()) if filepath.exists() else []
        existing.extend(data["eintraege"])
        filepath.write_text(json.dumps(existing, ensure_ascii=False, indent=2))

        logger.info("Gespeichert: %s (%d Einträge gesamt)", filepath, len(existing))
        for e in data["eintraege"]:
            logger.info("  • %s", e["name"])

        push_to_github(filepath, data["datum"])
    except Exception:
        logger.exception("Scraper fehlgeschlagen")
        sys.exit(1)


def push_to_github(filepath: Path, datum: str) -> None:
    import requests as req
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPO")
    if not token or not repo:
        logger.warning("GITHUB_TOKEN oder GITHUB_REPO nicht gesetzt  kein Push.")
        return

    api_url = f"https://api.github.com/repos/{repo}/contents/presseschau.json"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}

    sha = None
    existing = req.get(api_url, headers=headers)
    if existing.status_code == 200:
        sha = existing.json()["sha"]

    content = base64.b64encode(filepath.read_bytes()).decode()
    payload = {"message": f"presseschau {datum}", "content": content}
    if sha:
        payload["sha"] = sha

    resp = req.put(api_url, headers=headers, json=payload)
    resp.raise_for_status()
    logger.info("GitHub Push erfolgreich: %s", resp.json()["content"]["html_url"])


if __name__ == "__main__":
    main()