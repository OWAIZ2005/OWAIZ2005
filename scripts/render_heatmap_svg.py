"""Render data/contributions.json to contrib-heatmap.svg (53x7 grid, diagonal reveal)."""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

BG, BORDER, TEXT, MUTED = "#0d1117", "#30363d", "#c9d1d9", "#8b949e"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL, GAP = 11, 3
STEP = CELL + GAP
PAD_L, PAD_T = 48, 92
W = PAD_L + 53 * STEP + 24
H = 232
FONT = "ui-monospace,SFMono-Regular,Consolas,'DejaVu Sans Mono',monospace"


def streaks(days):
    counts = {date.fromisoformat(d["date"]): d["count"] for d in days}
    longest = run = 0
    cur_day = min(counts)
    last = max(counts)
    while cur_day <= last:
        run = run + 1 if counts[cur_day] > 0 else 0
        longest = max(longest, run)
        cur_day += timedelta(days=1)
    # current streak: today may still be empty, so allow starting from yesterday
    d = last if counts[last] > 0 else last - timedelta(days=1)
    current = 0
    while counts.get(d, 0) > 0:
        current += 1
        d -= timedelta(days=1)
    return current, longest


WINDOW = 365  # the heatmap always shows exactly this many consecutive days


def validate_days(days) -> None:
    """Refuse to render anything but exactly WINDOW consecutive days."""
    if len(days) != WINDOW:
        raise ValueError(f"expected {WINDOW} days, found {len(days)}")
    dates = [date.fromisoformat(d["date"]) for d in days]
    if any((b - a).days != 1 for a, b in zip(dates, dates[1:])):
        raise ValueError("days are not consecutive")
    if any(not isinstance(d["count"], int) or d["count"] < 0 for d in days):
        raise ValueError("invalid contribution count")


def compute_stats(days) -> dict:
    cur, longest = streaks(days)
    return {"total": sum(d["count"] for d in days),
            "active": sum(1 for d in days if d["count"] > 0),
            "current": cur, "longest": longest,
            "best": max(d["count"] for d in days)}


def main() -> int:
    if not DATA.exists():
        print("missing data/contributions.json", file=sys.stderr)
        return 1
    try:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        days = data["days"]
        validate_days(days)
    except (ValueError, KeyError, TypeError) as e:
        print(f"invalid data/contributions.json, heatmap not rendered: {e}", file=sys.stderr)
        return 1
    st = compute_stats(days)
    cur, longest, active, best, total = st["current"], st["longest"], st["active"], st["best"], st["total"]
    refreshed = data.get("refreshed_on") or str(data.get("fetched_at", ""))[:10]

    first = date.fromisoformat(days[0]["date"])
    grid_start = first - timedelta(days=(first.weekday() + 1) % 7)  # Sunday-aligned
    out = []
    months = []
    last_month = None
    for d in days:
        dt = date.fromisoformat(d["date"])
        col, row = (dt - grid_start).days // 7, (dt.weekday() + 1) % 7
        x, y = PAD_L + col * STEP, PAD_T + row * STEP
        delay = round((col + row) * 0.02, 2)
        tip = f"{d['count']} contribution{'s' if d['count'] != 1 else ''} on {d['date']}"
        out.append(
            f'<g><title>{tip}</title><rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
            f'fill="{PALETTE[min(d["level"], 4)]}">'
            f'<set attributeName="opacity" to="0" begin="0s"/>'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.35s" begin="{delay}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="-6 0" to="0 0" '
            f'dur="0.35s" begin="{delay}s" fill="freeze"/></rect></g>')
        if row == 0 and dt.month != last_month:
            if not months or x - months[-1][0] > 3 * STEP:
                months.append((x, dt.strftime("%b")))
            last_month = dt.month
    labels = "".join(f'<text x="{x}" y="{PAD_T - 8}" fill="{MUTED}" font-size="10">{m}</text>' for x, m in months)
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        labels += f'<text x="{PAD_L - 8}" y="{PAD_T + row * STEP + 9}" fill="{MUTED}" font-size="10" text-anchor="end">{name}</text>'

    lx = W - 24 - (4 + 5 * STEP + 28)
    legend = f'<text x="{lx - 6}" y="{H - 20}" fill="{MUTED}" font-size="10" text-anchor="end">Less</text>'
    legend += "".join(f'<rect x="{lx + i * STEP}" y="{H - 30}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>'
                      for i, c in enumerate(PALETTE))
    legend += f'<text x="{lx + 5 * STEP + 4}" y="{H - 20}" fill="{MUTED}" font-size="10">More</text>'

    stats = (f'{total} contributions in the last year  ·  current streak {cur}d  ·  '
             f'longest streak {longest}d  ·  active days {active}  ·  best day {best}')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" aria-label="GitHub contribution heatmap">
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<text x="24" y="34" fill="#39d353" font-size="13">$</text>
<text x="40" y="34" fill="{TEXT}" font-size="13">git log --contributions --last-year</text>
<text x="24" y="60" fill="{MUTED}" font-size="11">{stats}</text>
<line x1="24" y1="72" x2="{W - 24}" y2="72" stroke="{BORDER}"/>
{labels}
{"".join(out)}
{legend}
<text x="24" y="{H - 20}" fill="{MUTED}" font-size="10">updated {refreshed}</text>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.name}: total={total} current={cur} longest={longest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
