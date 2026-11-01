"""Fetch the public GitHub contribution calendar (no token) into data/contributions.json.

Exit codes:
  0  data written, or nothing meaningful changed, or a transient network problem with existing data kept
  1  the page could not be parsed (GitHub markup changed / unexpected data), or no data exists at all
"""
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from render_heatmap_svg import streaks

USERNAME = "OWAIZ2005"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"
EXPECTED_DAYS = range(360, 373)  # a calendar year, with slack for partial weeks


class ParseError(Exception):
    """The page was fetched but its contents are not a contribution calendar we understand."""


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
            raise ParseError(f"no usable tooltip for {td.get('data-date')}: {text!r}")
        try:
            date.fromisoformat(td["data-date"])
            level = int(td.get("data-level", 0))
        except ValueError as e:
            raise ParseError(f"bad cell attributes for {td.get('data-date')}: {e}") from e
        days.append({"date": td["data-date"], "count": count, "level": level})
    if not days:
        raise ParseError("no contribution cells found (page layout may have changed)")
    if len(days) not in EXPECTED_DAYS:
        raise ParseError(f"found {len(days)} days, expected about 365")
    days.sort(key=lambda d: d["date"])
    total = sum(d["count"] for d in days)
    h2 = soup.find("h2", id="js-contribution-activity-description")
    if h2:
        m = re.search(r"([\d,]+)\s+contributions?", h2.get_text(" ", strip=True))
        if m and int(m.group(1).replace(",", "")) != total:
            raise ParseError(f"total mismatch: header {m.group(1)} vs summed {total}")
    return {"username": USERNAME, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "total": total, "days": days}


def signature(data: dict) -> tuple:
    """What the heatmap meaningfully shows: non-zero days plus the streaks.

    A new empty day scrolling into the rolling window changes nothing visible, so it must
    not trigger a commit. Streaks are included because the current streak breaks with time.
    """
    nonzero = tuple((d["date"], d["count"]) for d in data["days"] if d["count"])
    return nonzero, streaks(data["days"])


def report(level: str, msg: str) -> None:
    """Print to stderr, as a GitHub Actions annotation when running there."""
    print(f"::{level}::{msg}" if level in ("error", "warning") else msg, file=sys.stderr)


def main() -> int:
    try:
        r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        # Transient: keep the existing data, but say so.
        if OUT.exists():
            report("warning", f"could not reach GitHub ({e}); keeping existing data/contributions.json")
            return 0
        report("error", f"could not reach GitHub and there is no existing data: {e}")
        return 1
    try:
        data = parse_calendar(r.text)
    except ParseError as e:
        # Not transient: the output would silently go stale, so fail the run.
        report("error", f"could not parse the contribution calendar: {e}. data/contributions.json was NOT updated")
        return 1

    if OUT.exists():
        try:
            if signature(json.loads(OUT.read_text(encoding="utf-8"))) == signature(data):
                print(f"no meaningful change ({data['total']} contributions); data file left untouched")
                return 0
        except (ValueError, KeyError, TypeError):
            report("warning", "existing data/contributions.json is unreadable; replacing it")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(data['days'])} days, {data['total']} contributions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
