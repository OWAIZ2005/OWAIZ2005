"""Tests for the rolling 365-day contribution window.

Run from the repo root:  python -m unittest discover -s tests -v
No network access: GitHub's page is simulated, and data files live in a temp directory.
"""
import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import fetch_contributions as fetch  # noqa: E402
import render_heatmap_svg as render  # noqa: E402


def page(end: date, counts: dict | None = None, n: int = 365, header_total: int | None = None,
         drop_tooltip_for: date | None = None) -> str:
    """Build a GitHub-style contributions page of n days ending on `end`."""
    counts = counts or {}
    start = end - timedelta(days=n - 1)
    cells, tips, total = [], [], 0
    for i in range(n):
        d = start + timedelta(days=i)
        c = counts.get(d, 0)
        total += c
        cid = f"contribution-day-component-{i}"
        level = 0 if c == 0 else min(4, 1 + c // 3)
        cells.append(f'<td class="ContributionCalendar-day" data-date="{d}" data-level="{level}" id="{cid}"></td>')
        if d != drop_tooltip_for:
            text = "No contributions" if c == 0 else f"{c} contribution{'s' if c != 1 else ''}"
            tips.append(f'<tool-tip for="{cid}">{text} on {d}.</tool-tip>')
    ht = total if header_total is None else header_total
    return (f'<h2 id="js-contribution-activity-description">{ht} contributions in the last year</h2>'
            f'<table><tr>{"".join(cells)}</tr></table>{"".join(tips)}')


class Resp:
    def __init__(self, text="", status=200):
        self.text, self.status_code = text, status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class Base(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.json = self.dir / "contributions.json"
        self.svg = self.dir / "heatmap.svg"
        for target, name, value in ((fetch, "OUT", self.json), (render, "DATA", self.json), (render, "OUT", self.svg)):
            p = mock.patch.object(target, name, value)
            p.start()
            self.addCleanup(p.stop)

    def run_fetch(self, end: date, counts=None, today=None, **kw) -> int:
        resp = Resp(page(end, counts, **kw))
        with mock.patch.object(fetch.requests, "get", return_value=resp), \
                mock.patch("sys.stderr", new=mock.MagicMock()), mock.patch("sys.stdout", new=mock.MagicMock()):
            return fetch.main(today or end)

    def data(self) -> dict:
        return json.loads(self.json.read_text(encoding="utf-8"))

    def render(self) -> int:
        with mock.patch("sys.stderr", new=mock.MagicMock()), mock.patch("sys.stdout", new=mock.MagicMock()):
            return render.main()


class RollingWindow(Base):
    D = date(2026, 3, 10)

    def test_new_empty_day_advances_window_and_drops_oldest(self):
        self.assertEqual(self.run_fetch(self.D, {self.D: 2}), 0)
        before = self.data()
        self.assertEqual(self.run_fetch(self.D + timedelta(1), {self.D: 2}), 0)
        after = self.data()
        self.assertEqual(len(after["days"]), 365)
        self.assertEqual(after["days"][-1], {"date": str(self.D + timedelta(1)), "count": 0, "level": 0})
        self.assertEqual(after["days"][0]["date"], before["days"][1]["date"])  # oldest day left
        self.assertEqual(after["total"], before["total"])                      # counts unchanged
        self.assertEqual(after["refreshed_on"], str(self.D + timedelta(1)))
        self.assertEqual(self.render(), 0)
        self.assertIn("2 contributions in the last year", self.svg.read_text(encoding="utf-8"))

    def test_new_day_with_contributions(self):
        self.run_fetch(self.D)
        n = self.D + timedelta(1)
        self.run_fetch(n, {n: 4})
        d = self.data()
        self.assertEqual((d["days"][-1]["count"], d["total"]), (4, 4))
        self.render()
        s = self.svg.read_text(encoding="utf-8")
        self.assertIn("4 contributions in the last year", s)
        self.assertIn("current streak 1d", s)
        self.assertIn("best day 4", s)

    def test_oldest_day_with_contributions_leaves_window(self):
        first = self.D - timedelta(364)
        self.run_fetch(self.D, {first: 5, self.D: 1})
        self.assertEqual(self.data()["total"], 6)
        self.run_fetch(self.D + timedelta(1), {first: 5, self.D: 1})  # `first` is now outside the window
        d = self.data()
        self.assertEqual(d["total"], 1)
        self.assertNotIn(str(first), [x["date"] for x in d["days"]])
        self.render()
        s = self.svg.read_text(encoding="utf-8")
        self.assertIn("1 contributions in the last year", s)
        self.assertIn("active days 1", s)
        self.assertIn("longest streak 1d", s)

    def test_same_day_rerun_writes_nothing_and_render_is_identical(self):
        self.run_fetch(self.D, {self.D: 3})
        self.render()
        j, s = self.json.read_bytes(), self.svg.read_bytes()
        self.assertEqual(self.run_fetch(self.D, {self.D: 3}), 0)
        self.render()
        self.assertEqual(self.json.read_bytes(), j)
        self.assertEqual(self.svg.read_bytes(), s)  # git would see no diff -> no commit

    def test_same_day_rerun_with_new_contribution_updates(self):
        self.run_fetch(self.D)
        self.run_fetch(self.D, {self.D: 1})
        self.assertEqual(self.data()["total"], 1)

    def test_366_day_page_is_trimmed_to_365(self):
        self.run_fetch(self.D, {self.D - timedelta(365): 9, self.D: 1}, n=366)
        d = self.data()
        self.assertEqual((len(d["days"]), d["total"]), (365, 1))

    def test_stats_streaks_active_best(self):
        counts = {self.D - timedelta(i): c for i, c in enumerate([1, 2, 0, 3, 4, 5, 0, 7])}
        self.run_fetch(self.D, counts)
        st = render.compute_stats(self.data()["days"])
        self.assertEqual(st, {"total": 22, "active": 6, "current": 2, "longest": 3, "best": 7})

    def test_current_streak_survives_empty_today_but_breaks_after_two_days(self):
        y = self.D - timedelta(1)
        self.run_fetch(self.D, {y: 1, y - timedelta(1): 1})
        self.assertEqual(render.compute_stats(self.data()["days"])["current"], 2)  # today empty, yesterday active
        n = self.D + timedelta(1)
        self.run_fetch(n, {y: 1, y - timedelta(1): 1})
        self.assertEqual(render.compute_stats(self.data()["days"])["current"], 0)  # streak broken

    def test_transitions_month_year_leap(self):
        for end in (date(2026, 1, 31), date(2025, 12, 31), date(2028, 2, 29), date(2028, 3, 1)):
            for step in (0, 1):
                with self.subTest(end=end, step=step):
                    e = end + timedelta(step)
                    self.json.unlink(missing_ok=True)
                    self.assertEqual(self.run_fetch(e, {e: 1}), 0)
                    d = self.data()["days"]
                    self.assertEqual((len(d), d[-1]["date"]), (365, str(e)))
                    self.assertEqual(self.render(), 0)
                    svg = self.svg.read_text(encoding="utf-8")
                    self.assertIn(e.strftime("%b"), svg)  # month label for the newest month is drawn
        # the window ending 2028-03-01 contains the leap day exactly once
        self.assertIn("2028-02-29", [x["date"] for x in self.data()["days"]])

    def test_grid_never_exceeds_53_columns(self):
        for i in range(7):
            e = date(2026, 5, 1) + timedelta(i)
            with self.subTest(end=e):
                self.run_fetch(e)
                self.assertEqual(self.render(), 0)
                xs = [int(x) for x in __import__("re").findall(r'<rect x="(\d+)"', self.svg.read_text(encoding="utf-8"))]
                self.assertLessEqual(max(xs) + render.CELL, render.W - 24 + 1)


class FailuresNeverOverwriteValidData(Base):
    D = date(2026, 3, 10)

    def setUp(self):
        super().setUp()
        self.run_fetch(self.D, {self.D: 2})
        self.valid = self.json.read_bytes()

    def assert_preserved(self, rc, expected_rc):
        self.assertEqual(rc, expected_rc)
        self.assertEqual(self.json.read_bytes(), self.valid)

    def attempt(self, resp=None, exc=None, today=None):
        with mock.patch.object(fetch.requests, "get", return_value=resp, side_effect=exc), \
                mock.patch("sys.stderr", new=mock.MagicMock()):
            return fetch.main(today or self.D + timedelta(1))

    def test_http_error_keeps_data(self):
        self.assert_preserved(self.attempt(Resp("", 500)), 0)

    def test_connection_error_keeps_data(self):
        self.assert_preserved(self.attempt(exc=requests.ConnectionError("down")), 0)

    def test_timeout_keeps_data(self):
        self.assert_preserved(self.attempt(exc=requests.Timeout("slow")), 0)

    def test_http_error_without_existing_data_fails(self):
        self.json.unlink()
        self.assertEqual(self.attempt(Resp("", 503)), 1)
        self.assertFalse(self.json.exists())

    def test_invalid_pages_fail_and_keep_data(self):
        n = self.D + timedelta(1)
        cases = {
            "no calendar": "<html>hello</html>",
            "empty body": "",
            "missing tooltip": page(n, drop_tooltip_for=n - timedelta(10)),
            "too few days": page(n, n=200),
            "too many days": page(n, n=400),
            "header total mismatch": page(n, {n: 1}, header_total=99),
            "stale calendar": page(n - timedelta(30)),
            "future calendar": page(n + timedelta(30)),
            "bad date": page(n).replace(f'data-date="{n}"', 'data-date="2026-13-45"'),
            "duplicate date": page(n).replace(f'data-date="{n - timedelta(5)}"', f'data-date="{n - timedelta(6)}"'),
        }
        for name, html in cases.items():
            with self.subTest(case=name):
                self.assert_preserved(self.attempt(Resp(html)), 1)

    def test_render_rejects_corrupt_stored_data(self):
        d = self.data()
        for name, bad in {
            "short": {**d, "days": d["days"][:300]},
            "gap": {**d, "days": d["days"][:10] + d["days"][11:] + [d["days"][-1]]},
            "negative": {**d, "days": [{**x, "count": -1} if i == 3 else x for i, x in enumerate(d["days"])]},
            "no days key": {"username": "x"},
        }.items():
            with self.subTest(case=name):
                self.json.write_text(json.dumps(bad), encoding="utf-8")
                self.svg.write_text("previous good svg", encoding="utf-8")
                self.assertEqual(self.render(), 1)
                self.assertEqual(self.svg.read_text(encoding="utf-8"), "previous good svg")


if __name__ == "__main__":
    unittest.main()
