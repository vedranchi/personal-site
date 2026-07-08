#!/usr/bin/env python3
"""Scrape Vedran's ProCyclingStats profile into src/data/cycling.json.

procyclingstats parses PCS HTML, but PCS is behind Cloudflare — a plain request
gets a 403 "Just a moment..." challenge page. So we fetch the HTML ourselves with
curl_cffi (which impersonates a real Chrome TLS/JA3 fingerprint) and hand it to the
library's parsers via their `html=` argument.

Run: .venv/bin/python scripts/scrape_pcs.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests
from procyclingstats import Rider, RiderResults

RIDER_SLUG = "vedran-cicov"
BASE_URL = "https://www.procyclingstats.com/"
OUT = Path(__file__).resolve().parent.parent / "src" / "data" / "cycling.json"

# Country codes that appear for this rider — extend as needed.
COUNTRY_NAMES = {
    "MK": "North Macedonia",
    "BA": "Bosnia and Herzegovina",
    "RS": "Serbia",
    "BG": "Bulgaria",
    "GR": "Greece",
    "AL": "Albania",
    "XK": "Kosovo",
}


def fetch(path: str) -> str:
    """Fetch a PCS page as a real browser would, raising on non-200."""
    url = BASE_URL + path
    res = requests.get(url, impersonate="chrome", timeout=30)
    if res.status_code != 200:
        raise RuntimeError(f"GET {url} -> HTTP {res.status_code}")
    if "just a moment" in res.text.lower():
        raise RuntimeError(f"Cloudflare challenge not bypassed for {url}")
    return res.text


def safe(fn, default=None):
    """Call a parser method, returning `default` if PCS's HTML doesn't have it."""
    try:
        return fn()
    except Exception:
        return default


def normalize_date(d: str | None) -> str | None:
    """PCS gives dates like '2007-3-2'; normalize to ISO 'YYYY-MM-DD'."""
    if not d:
        return None
    try:
        return datetime.strptime(d, "%Y-%m-%d").date().isoformat()
    except ValueError:
        parts = d.split("-")
        if len(parts) == 3:
            y, m, day = parts
            return f"{int(y):04d}-{int(m):02d}-{int(day):02d}"
        return d


def build_rider() -> dict:
    html = fetch(f"rider/{RIDER_SLUG}")
    r = Rider(f"rider/{RIDER_SLUG}", html=html, update_html=False)

    teams = safe(r.teams_history, []) or []
    current_team = None
    if teams:
        latest = max(teams, key=lambda t: t.get("season", 0))
        current_team = {
            "name": latest.get("team_name"),
            "class": latest.get("class"),
            "season": latest.get("season"),
        }

    nat = safe(r.nationality)
    return {
        "name": safe(r.name) or "Vedran Cicov",
        "nationality": nat,
        "nationalityName": COUNTRY_NAMES.get(nat, nat),
        "birthdate": normalize_date(safe(r.birthdate)),
        "team": current_team,
        "teams": teams,
    }


def build_results() -> list[dict]:
    html = fetch(f"rider/{RIDER_SLUG}/results")
    rr = RiderResults(f"rider/{RIDER_SLUG}/results", html=html, update_html=False)
    raw = safe(rr.results, []) or []

    results = []
    for row in raw:
        stage_url = row.get("stage_url")
        results.append(
            {
                "date": normalize_date(row.get("date")),
                "rank": row.get("rank"),
                "race": row.get("stage_name"),
                "raceClass": row.get("class"),
                "country": row.get("nationality"),
                "distanceKm": row.get("distance"),
                "uciPoints": row.get("uci_points") or 0,
                "pcsPoints": row.get("pcs_points") or 0,
                "url": BASE_URL + stage_url if stage_url else None,
            }
        )
    # Most recent first.
    results.sort(key=lambda x: x["date"] or "", reverse=True)
    return results


def main() -> int:
    print(f"Scraping ProCyclingStats for {RIDER_SLUG} …")
    rider = build_rider()
    results = build_results()

    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": f"{BASE_URL}rider/{RIDER_SLUG}/",
        "rider": rider,
        "results": results,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    podiums = [r for r in results if r["rank"] and r["rank"] <= 3]
    print(f"  rider: {rider['name']} ({rider['nationalityName']})")
    print(f"  results: {len(results)} | podiums: {len(podiums)}")
    print(f"  wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
