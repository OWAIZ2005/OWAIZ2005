"""Fetch the public GitHub contribution calendar (no token) into data/contributions.json.

The stored data is always exactly the latest WINDOW (365) consecutive days. It is rewritten
whenever the window or any count changes, so the range advances every day even when the newest
day is empty. A same-day rerun that produces identical data writes nothing.

Exit codes:
  0  data written, or identical to what is stored, or a transient network problem with existing data kept
  1  the page could not be parsed (GitHub markup changed / unexpected data), or no data exists at all
"""
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "OWAIZ2005"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"
WINDOW = 365      # days kept and rendered
MAX_RAW_DAYS = 372  # a calendar year plus slack for partial weeks; anything larger is suspicious
MAX_STALENESS = timedelta(days=2)  # calendar's last day may differ from UTC today by timezone, not more


class ParseError(Exception):
    """The page was fetched but its contents are not a contribution calendar we understand."""


def parse_calendar(html: str, today: date | None = None) -> dict:
    today = today or datetime.now(timezone.utc).date()
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
    if not WINDOW <= len(days) <= MAX_RAW_DAYS:
        raise ParseError(f"found {len(days)} days, expected {WINDOW}-{MAX_RAW_DAYS}")
    days.sort(key=lambda d: d["date"])
    dates = [date.fromisoformat(d["date"]) for d in days]
    if any((b - a).days != 1 for a, b in zip(dates, dates[1:])):
        raise ParseError("days are not consecutive (duplicate or missing dates)")
    if not today - MAX_STALENESS <= dates[-1] <= today + MAX_STALENESS:
        raise ParseError(f"calendar ends {dates[-1]}, which is not current (today is {today} UTC)")
    h2 = soup.find("h2", id="js-contribution-activity-description")
    if h2:
        m = re.search(r"([\d,]+)\s+contributions?", h2.get_text(" ", strip=True))
        if m and int(m.group(1).replace(",", "")) != sum(d["count"] for d in days):
            raise ParseError(f"total mismatch: header {m.group(1)} vs summed {sum(d['count'] for d in days)}")
    days = days[-WINDOW:]  # exactly the latest 365 days; older cells (if any) fall out of the window
    return {"username": USERNAME, "refreshed_on": today.isoformat(),
            "total": sum(d["count"] for d in days), "days": days}


def report(level: str, msg: str) -> None:
    """Print to stderr, as a GitHub Actions annotation when running there."""
    print(f"::{level}::{msg}" if level in ("error", "warning") else msg, file=sys.stderr)


def main(today: date | None = None) -> int:
    try:
        r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        # Transient: keep the existing data (it keeps its own, older refreshed_on), but say so.
        if OUT.exists():
            report("warning", f"could not reach GitHub ({e}); keeping existing data/contributions.json")
            return 0
        report("error", f"could not reach GitHub and there is no existing data: {e}")
        return 1
    try:
        data = parse_calendar(r.text, today)
    except ParseError as e:
        # Not transient: the output would silently go stale, so fail the run.
        report("error", f"could not parse the contribution calendar: {e}. data/contributions.json was NOT updated")
        return 1

    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
            if old.get("days") == data["days"] and old.get("refreshed_on") == data["refreshed_on"]:
                print(f"data unchanged ({data['days'][0]['date']} to {data['days'][-1]['date']}, "
                      f"{data['total']} contributions); nothing written")
                return 0
        except (ValueError, AttributeError):
            report("warning", "existing data/contributions.json is unreadable; replacing it")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{data['days'][0]['date']} to {data['days'][-1]['date']}: "
          f"{len(data['days'])} days, {data['total']} contributions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
