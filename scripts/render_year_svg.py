"""Year in review: contributions per month for the last 12 months as
gradient bars, plus a column of headline numbers."""
import datetime as dt
import os

from contrib_data import load
from theme import MONO, T, svg_card

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "year-review.svg")

W = 860


def last_12_months(last):
    months = []
    y, m = last.year, last.month
    for _ in range(12):
        months.append((y, m))
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    return months[::-1]


def main():
    data = load()
    last = dt.date.fromisoformat(data["days"][-1]["date"])
    months = last_12_months(last)
    per_month = {ym: 0 for ym in months}
    active_days = 0
    for d in data["days"]:
        date = dt.date.fromisoformat(d["date"])
        ym = (date.year, date.month)
        if ym in per_month:
            per_month[ym] += d["count"]
            active_days += 1 if d["count"] else 0
    vals = [per_month[ym] for ym in months]
    total = sum(vals)
    best = max(range(12), key=lambda i: vals[i])
    top_v = max(vals) or 1

    body = []
    cx0, cw, top, h = 28, 560, 28, 170
    base = top + h
    slot = cw / 12
    bw = slot * 0.62
    for i, v in enumerate(vals):
        bh = max(3, h * v / top_v)
        x = cx0 + slot * i + (slot - bw) / 2
        y = base - bh
        cls = "bar best" if i == best else "bar"
        body.append(f'<rect class="{cls}" x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" '
                    f'height="{bh:.1f}" rx="5" fill="url(#barFill)"/>')
        body.append(f'<text class="{"accent2" if i == best else "fg"}" x="{x + bw / 2:.1f}" '
                    f'y="{y - 7:.1f}" text-anchor="middle" font-family="{MONO}" '
                    f'font-size="11">{v}</text>')
        label = dt.date(months[i][0], months[i][1], 1).strftime("%b")
        body.append(f'<text class="muted" x="{x + bw / 2:.1f}" y="{base + 18}" '
                    f'text-anchor="middle" font-family="{MONO}" font-size="10">{label}</text>')
    body.append(f'<line class="axis" x1="{cx0}" y1="{base}" x2="{cx0 + cw}" y2="{base}"/>')

    # right column: headline numbers
    best_label = dt.date(months[best][0], months[best][1], 1).strftime("%B %Y")
    kpis = [(f"{total:,}", "contributions · 12 months"),
            (f"{active_days}", "active days"),
            (f"{vals[best]}", f"best month · {best_label}"),
            (f"{total / 12:.0f}", "average per month")]
    kx = cx0 + cw + 40
    body.append(f'<line class="axis" x1="{kx - 20}" y1="{top - 6}" x2="{kx - 20}" y2="{base + 20}"/>')
    for k, (value, label) in enumerate(kpis):
        y = top + 12 + k * 50
        body.append(f'<text class="accent" x="{kx}" y="{y}" font-family="{MONO}" '
                    f'font-size="20" font-weight="700">{value}</text>')
        body.append(f'<text class="muted" x="{kx}" y="{y + 17}" font-family="{MONO}" '
                    f'font-size="11">{label}</text>')

    L, D = T["light"], T
    defs = """<defs><linearGradient id="barFill" x1="0" y1="1" x2="0" y2="0">
<stop offset="0" class="stop-a"/><stop offset="1" class="stop-b"/>
</linearGradient></defs>"""
    # No fill-mode: bars rest at full height, so they show even where
    # animations do not run.
    common = (".bar{transform-box:fill-box;transform-origin:bottom;"
              "animation:grow .9s cubic-bezier(.2,.8,.2,1)}"
              "@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}"
              ".axis{stroke-width:1;opacity:.4}")
    extra_light = (f"{common}.stop-a{{stop-color:{L['accent']}}}.stop-b{{stop-color:{L['accent2']}}}"
                   f".axis{{stroke:{L['muted']}}}")
    extra_dark = (f".stop-a{{stop-color:{D['accent']}}}.stop-b{{stop-color:{D['accent2']}}}"
                  f".axis{{stroke:{D['muted']}}}"
                  f".best{{filter:drop-shadow(0 0 5px {D['accent2']})}}")
    svg = svg_card(W, 34 + base + 32, "./year --in-review", "\n".join(body),
                   extra_dark=extra_dark, extra_light=extra_light, defs=defs)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"year-review: {total} contributions, best {best_label} ({vals[best]})")


if __name__ == "__main__":
    main()
