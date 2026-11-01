"""Convert assets/portrait_prepped.png into avi-ascii.svg (monochrome, typed-in row reveal).

Animation is SMIL. Each row's reveal is driven by <set>/<animate> on a clip rect whose *base*
state is fully visible, so a renderer that ignores SMIL simply shows the finished portrait.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "portrait_prepped.png"
OUT = ROOT / "avi-ascii.svg"

RAMP = " .`:-=+*cs#%@"
COLS, ROWS = 110, 66
FONT_SIZE, CW, LH = 8, 4.8, 8          # cell is 4.8 x 8 px -> 110x66 grid is 528x528
PAD = 16
W = H = int(COLS * CW) + 2 * PAD       # 560 x 560
GAMMA = 0.6                            # <1 brightens midtones so the face reads as dense
FG, BG, BORDER = "#e6edf3", "#0d1117", "#30363d"
ROW_STAGGER, ROW_DUR = 0.075, 0.55     # seconds
FONT = "ui-monospace,SFMono-Regular,Consolas,'DejaVu Sans Mono',monospace"


def to_rows() -> list[str]:
    im = Image.open(SRC).convert("RGBA").resize((COLS, ROWS), Image.LANCZOS)
    a = np.array(im)
    lum, alpha = a[..., 0].astype(np.float32), a[..., 3]
    inside = alpha > 110
    lo, hi = np.percentile(lum[inside], [3, 99])
    lum = np.clip((lum - lo) / (hi - lo), 0, 1) ** GAMMA
    sharp = cv2.GaussianBlur(lum, (0, 0), 1.2)
    lum = np.clip(lum + 0.6 * (lum - sharp), 0, 1)
    idx = np.rint(lum * (len(RAMP) - 1)).astype(int)
    idx = np.clip(idx, 1, len(RAMP) - 1)  # subject never renders as pure blank
    rows = []
    for y in range(ROWS):
        rows.append("".join(RAMP[idx[y, x]] if inside[y, x] else " " for x in range(COLS)))
    return rows


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(rows: list[str]) -> str:
    width = COLS * CW
    defs, body = [], []
    for i, row in enumerate(rows):
        if not row.strip():
            continue
        t0 = round(0.4 + i * ROW_STAGGER, 3)
        t1 = round(t0 + ROW_DUR, 3)
        y = PAD + i * LH
        defs.append(
            f'<clipPath id="c{i}"><rect x="{PAD}" y="{y}" width="{width}" height="{LH}">'
            f'<set attributeName="width" to="0" begin="0s"/>'
            f'<animate attributeName="width" from="0" to="{width}" dur="{ROW_DUR}s" begin="{t0}s" fill="freeze"/>'
            f'</rect></clipPath>')
        body.append(
            f'<text x="{PAD}" y="{y + LH - 1.6}" textLength="{width}" lengthAdjust="spacing" '
            f'clip-path="url(#c{i})" xml:space="preserve">{esc(row)}</text>')
        # blinking-free cursor block that rides the reveal edge, then vanishes
        body.append(
            f'<rect x="{PAD}" y="{y + 0.5}" width="{CW}" height="{LH - 1}" fill="{FG}" opacity="0">'
            f'<set attributeName="opacity" to="0.85" begin="{t0}s"/>'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + width}" dur="{ROW_DUR}s" begin="{t0}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{t1}s"/></rect>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ASCII portrait">
<defs>{"".join(defs)}</defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<g font-family="{FONT}" font-size="{FONT_SIZE}" fill="{FG}">
{chr(10).join(body)}
</g>
</svg>
'''


def main() -> int:
    if not SRC.exists():
        print("run scripts/prep_photo.py first", file=sys.stderr)
        return 1
    rows = to_rows()
    OUT.write_text(build_svg(rows), encoding="utf-8")
    print(f"wrote {OUT.name} ({COLS}x{ROWS})")
    print("\n".join(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
