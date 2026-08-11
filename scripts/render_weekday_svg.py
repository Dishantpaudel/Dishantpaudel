"""Weekday pulse: commits-by-weekday horizontal bars + 12-month weekly
sparkline area chart. The 'more graphs' upgrade over the reference profile."""
import datetime as dt
import os

from contrib_data import load, last_year_days
from theme import MONO, T, blend, svg_card

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "weekday-pulse.svg")

W = 860
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def main():
    data = load()
    days = last_year_days(data)

    by_wd = [0] * 7
    for date, count in days:
        by_wd[date.weekday()] += count
    max_wd = max(by_wd) or 1
    full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday"]
    top_day = full[by_wd.index(max(by_wd))]

    weekly = []
    for i in range(0, len(days) - 6, 7):
        chunk = days[i:i + 7]
        weekly.append((chunk[0][0], sum(c for _, c in chunk)))
    max_week = max((c for _, c in weekly), default=1) or 1

    body = []
    # left: bars
    bx, by, bw, bh, gap = 90, 26, 280, 18, 10
    body.append(f'<text class="fg" x="24" y="14" font-family="{MONO}" '
                f'font-size="13">commits by weekday</text>')
    for i, v in enumerate(by_wd):
        y = by + i * (bh + gap)
        w = max(2, bw * v / max_wd)
        color = blend(T["accent"], T["accent2"], i / 6)
        body.append(f'<text class="muted" x="{bx - 10}" y="{y + bh - 4}" '
                    f'text-anchor="end" font-family="{MONO}" font-size="11">{WEEKDAYS[i]}</text>')
        body.append(f'<rect class="bar" x="{bx}" y="{y}" width="{w:.1f}" height="{bh}" '
                    f'rx="4" fill="{color}"/>')
        body.append(f'<text class="muted" x="{bx + w + 8:.1f}" y="{y + bh - 4}" '
                    f'font-family="{MONO}" font-size="11">{v}</text>')
    bars_bottom = by + 7 * (bh + gap)
    body.append(f'<text class="accent" x="24" y="{bars_bottom + 8}" '
                f'font-family="{MONO}" font-size="12">→ busiest on {top_day}s</text>')

    # right: sparkline area chart of weekly totals
    sx, sy, sw, sh = 470, 40, W - 470 - 40, 150
    body.append(f'<text class="fg" x="{sx}" y="14" font-family="{MONO}" '
                f'font-size="13">weekly contributions · last 12 months</text>')
    pts = []
    n = len(weekly)
    for i, (_, c) in enumerate(weekly):
        x = sx + sw * i / max(1, n - 1)
        y = sy + sh - sh * c / max_week
        pts.append((x, y))
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{sx:.1f},{sy + sh:.1f} {line} {pts[-1][0]:.1f},{sy + sh:.1f}"
    body.append(f'<polygon points="{area}" fill="{T["accent"]}" opacity="0.18"/>')
    body.append(f'<polyline points="{line}" fill="none" stroke="{T["accent"]}" '
                f'stroke-width="2" stroke-linejoin="round" class="spark"/>')
    peak_i = max(range(n), key=lambda i: weekly[i][1])
    px, py = pts[peak_i]
    peak_date, peak_count = weekly[peak_i]
    body.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{T["accent2"]}"/>')
    anchor = "end" if px > sx + sw - 90 else "start"
    body.append(f'<text class="accent2" x="{px:.1f}" y="{max(py - 10, 26):.1f}" '
                f'text-anchor="{anchor}" font-family="{MONO}" font-size="11">'
                f'peak {peak_count} · {peak_date.strftime("%b %Y")}</text>')
    body.append(f'<line x1="{sx}" y1="{sy + sh}" x2="{sx + sw}" y2="{sy + sh}" '
                f'stroke="{T["muted"]}" stroke-width="1" opacity="0.5"/>')
    first_lbl = weekly[0][0].strftime("%b %Y")
    last_lbl = weekly[-1][0].strftime("%b %Y")
    body.append(f'<text class="muted" x="{sx}" y="{sy + sh + 18}" '
                f'font-family="{MONO}" font-size="10">{first_lbl}</text>')
    body.append(f'<text class="muted" x="{sx + sw}" y="{sy + sh + 18}" '
                f'text-anchor="end" font-family="{MONO}" font-size="10">{last_lbl}</text>')

    content_h = max(bars_bottom + 20, sy + sh + 30)
    spark_glow = f".spark{{filter:drop-shadow(0 0 3px {T['accent']})}}"
    svg = svg_card(W, 34 + content_h + 10, "./weekday --pulse", "\n".join(body),
                   extra_dark=spark_glow)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"weekday-pulse: top={top_day}, peak week={peak_count}")


if __name__ == "__main__":
    main()
