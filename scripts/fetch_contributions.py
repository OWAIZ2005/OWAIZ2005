"""Fetch the public GitHub contribution calendar (no token) into data/contributions.json."""
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "OWAIZ2005"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def parse_calendar(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    tips = {t.get("for"): t.get_text(strip=True) for t in soup.find_all("tool-tip")}
    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        text = tips.get(td.get("id"), "")
        m = re.match(r"(\d+) contributions?", text)
        if m:
            count = int(m.group(1))
        elif text.startswith("No contributions"):
            count = 0
        else:
            # Tooltip missing: refuse to guess a count.
            raise ValueError(f"no tooltip for {td.get('data-date')}")
        days.append({"date": td["data-date"], "count": count, "level": int(td.get("data-level", 0))})
    if not days:
        raise ValueError("no contribution cells found")
    days.sort(key=lambda d: d["date"])
    for d in days:
        date.fromisoformat(d["date"])  # validate
    total = sum(d["count"] for d in days)
    h2 = soup.find("h2", id="js-contribution-activity-description")
    if h2:
        m = re.search(r"([\d,]+)\s+contributions?", h2.get_text(" ", strip=True))
        if m and int(m.group(1).replace(",", "")) != total:
            raise ValueError(f"total mismatch: header {m.group(1)} vs summed {total}")
    return {"username": USERNAME, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "total": total, "days": days}


def main() -> int:
    try:
        r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}, timeout=30)
        r.raise_for_status()
        data = parse_calendar(r.text)
    except (requests.RequestException, ValueError) as e:
        print(f"fetch failed: {e}", file=sys.stderr)
        if OUT.exists():
            print("keeping existing data/contributions.json", file=sys.stderr)
            return 0  # don't break the daily job; stale data is better than none
        return 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print(f"{len(data['days'])} days, {data['total']} contributions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
