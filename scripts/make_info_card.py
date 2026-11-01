"""Generate info-card.svg: a neofetch-style terminal card with a line-by-line fade-in."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"

W, H = 600, 560  # H matches avi-ascii.svg so the README table columns align
BG, BAR, BORDER = "#0d1117", "#161b22", "#30363d"
TEXT, MUTED, GREEN = "#e6edf3", "#8b949e", "#39d353"
FONT = "ui-monospace,SFMono-Regular,Consolas,'DejaVu Sans Mono',monospace"
FS = 15
CHAR_W = FS * 0.62  # conservative monospace advance (real is ~0.60)
LINE = 22
X0, KEY_W = 28, 13  # left margin, key column width in characters

PROFILE = [
    ("USER", "Mohamed Basheer"),
    ("ROLE", "CSE Student / Developer"),
    ("EDUCATION", "B.Tech Computer Science Engineering"),
    ("FOCUS", "AI / ML / Full Stack Development"),
    ("LANGUAGES", "C++ / Python / SQL / JavaScript / Dart"),
    ("BACKEND", "Node.js / FastAPI / Express.js"),
    ("FRAMEWORKS", "Flutter"),
    ("AI / ML", "LLMs / LangChain / YOLOv8 / OpenCV"),
    ("DATABASES", "PostgreSQL / Firebase / Redis"),
    ("INTERESTS", "AI Agents / LLMs / Systems Engineering"),
]
PROJECTS = ["Universal Prompt Enhancer", "AI Lead Finder", "NAD Group Rewards"]
ACHIEVEMENTS = ["2nd place in a hackathon with 100+ teams",
                "IEEE Tech for Good funding recipient",
                "Research Lead — Hydroponics"]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> int:
    lines = []  # (kind, svg-fragment-builder args)
    lines.append(("head", "mohamed@basheer"))
    lines.append(("rule", "-" * 15))
    for k, v in PROFILE:
        lines.append(("kv", (k, v)))
    lines.append(("gap", None))
    lines.append(("section", "PROJECTS"))
    lines += [("item", p) for p in PROJECTS]
    lines.append(("gap", None))
    lines.append(("section", "ACHIEVEMENTS"))
    lines += [("item", a) for a in ACHIEVEMENTS]

    top = 36 + 34  # title bar + padding
    out, y, n = [], top, 0
    max_chars = 0
    for kind, val in lines:
        if kind == "gap":
            y += LINE * 0.6
            continue
        d = round(0.3 + n * 0.09, 2)
        n += 1
        anim = (f'<set attributeName="opacity" to="0" begin="0s"/>'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{d}s" fill="freeze"/>')
        if kind == "head":
            frag = f'<text x="{X0}" y="{y}" fill="{GREEN}" font-weight="bold">{esc(val)}{anim}</text>'
            max_chars = max(max_chars, len(val))
        elif kind == "rule":
            frag = f'<text x="{X0}" y="{y}" fill="{BORDER}">{val}{anim}</text>'
        elif kind == "kv":
            k, v = val
            frag = (f'<text x="{X0}" y="{y}" xml:space="preserve"><tspan fill="{GREEN}">{esc(k)}</tspan>'
                    f'<tspan x="{X0 + KEY_W * CHAR_W:.1f}" fill="{TEXT}">{esc(v)}</tspan>{anim}</text>')
            max_chars = max(max_chars, KEY_W + len(v))
        elif kind == "section":
            frag = f'<text x="{X0}" y="{y}" fill="{GREEN}" font-weight="bold">{val}{anim}</text>'
        else:
            frag = f'<text x="{X0}" y="{y}" fill="{TEXT}" xml:space="preserve"><tspan fill="{MUTED}">&gt; </tspan>{esc(val)}{anim}</text>'
            max_chars = max(max_chars, 2 + len(val))
        out.append(frag)
        y += LINE

    # Layout guards: fail loudly instead of shipping clipped text.
    need_w = X0 + max_chars * CHAR_W + 24
    if need_w > W:
        print(f"text too wide: needs {need_w:.0f}px, card is {W}px", file=sys.stderr)
        return 1
    if y > H - 16:
        print(f"content too tall: ends at {y:.0f}px, card is {H}px", file=sys.stderr)
        return 1

    cursor_y = y + 4
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Profile information card">
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M0.5 36 V10.5 A10 10 0 0 1 10.5 0.5 H{W - 10.5} A10 10 0 0 1 {W - 0.5} 10.5 V36 Z" fill="{BAR}"/>
<line x1="0.5" y1="36" x2="{W - 0.5}" y2="36" stroke="{BORDER}"/>
<circle cx="22" cy="18" r="5.5" fill="#ff5f56"/><circle cx="42" cy="18" r="5.5" fill="#ffbd2e"/><circle cx="62" cy="18" r="5.5" fill="#27c93f"/>
<text x="{W / 2}" y="22" fill="{MUTED}" font-family="{FONT}" font-size="12" text-anchor="middle">basheer@github: ~</text>
<g font-family="{FONT}" font-size="{FS}">
{chr(10).join(out)}
<rect x="{X0}" y="{cursor_y - 11}" width="8" height="14" fill="{GREEN}" opacity="0">
<set attributeName="opacity" to="1" begin="{0.3 + n * 0.09 + 0.4:.2f}s"/>
<animate attributeName="opacity" values="1;0;1" dur="1.1s" begin="{0.3 + n * 0.09 + 0.4:.2f}s" repeatCount="3"/>
<set attributeName="opacity" to="1" begin="{0.3 + n * 0.09 + 0.4 + 3.3:.2f}s"/></rect>
</g>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.name}; content ends at y={y:.0f}/{H}, widest ~{need_w:.0f}/{W}px")
    return 0


if __name__ == "__main__":
    sys.exit(main())
