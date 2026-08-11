"""Streak card: all-time total | current streak in an animated ring | longest
streak. Current streak tolerates a zero-count today (walk from yesterday)."""
import datetime as dt
import math
import os

from contrib_data import load
from theme import MONO, T, svg_card

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "streak.svg")

W, CONTENT_H = 860, 200


def streaks(day_list):
    counts = {dt.date.fromisoformat(d["date"]): d["count"] for d in day_list}
    last = max(counts)

    cur = 0
    probe = last if counts.get(last, 0) > 0 else last - dt.timedelta(days=1)
    cur_end = probe
    while counts.get(probe, 0) > 0:
        cur += 1
        probe -= dt.timedelta(days=1)
    cur_start = probe + dt.timedelta(days=1)

    best = best_len = 0
    best_range = (None, None)
    run_start = None
    run = 0
    for day in sorted(counts):
        if counts[day] > 0:
            if run == 0:
                run_start = day
            run += 1
            if run > best_len:
                best_len = run
                best_range = (run_start, day)
        else:
            run = 0
    return cur, (cur_start, cur_end), best_len, best_range


def fmt_range(a, b):
    if not a or not b:
        return "—"
    if a.year == b.year:
        return f"{a.strftime('%b %d')} – {b.strftime('%b %d, %Y')}"
    return f"{a.strftime('%b %d, %Y')} – {b.strftime('%b %d, %Y')}"


def col(cx, title, value, sub, body, value_class="fg", value_size=42):
    body.append(f'<text class="{value_class}" x="{cx}" y="100" text-anchor="middle" '
                f'font-family="{MONO}" font-size="{value_size}" font-weight="bold">{value}</text>')
    body.append(f'<text class="fg" x="{cx}" y="134" text-anchor="middle" '
                f'font-family="{MONO}" font-size="14">{title}</text>')
    body.append(f'<text class="muted" x="{cx}" y="156" text-anchor="middle" '
                f'font-family="{MONO}" font-size="11">{sub}</text>')


def main():
    data = load()
    total = data["total"]
    first = data["days"][0]["date"]
    cur, cur_range, best, best_range = streaks(data["days"])

    body = []
    col(W // 6, "Total Contributions",
        f"{total:,}", f"since {dt.date.fromisoformat(first).strftime('%b %d, %Y')}", body)

    # center: ring gauge, radius 52 at (W/2, 84)
    cx, cy, r = W // 2, 90, 52
    circ = 2 * math.pi * r
    frac = min(1.0, cur / best) if best else 0
    dash = circ * frac
    ring_css_d = (
        f".ring-bg{{stroke:{T['muted']};}}"
        f".ring{{stroke:{T['accent']};filter:drop-shadow(0 0 4px {T['accent']});}}"
    )
    ring_css_l = (
        f".ring-bg{{stroke:{T['light']['muted']};}}"
        f".ring{{stroke:{T['light']['accent']};}}"
    )
    anim = (f"@keyframes ringdraw{{from{{stroke-dashoffset:{circ:.1f}}}"
            f"to{{stroke-dashoffset:{circ - dash:.1f}}}}}"
            ".ring{animation:ringdraw 1.4s ease-out forwards;}")
    body.append(f'<circle class="ring-bg" cx="{cx}" cy="{cy}" r="{r}" fill="none" '
                f'stroke-width="8" opacity="0.35"/>')
    body.append(f'<circle class="ring" cx="{cx}" cy="{cy}" r="{r}" fill="none" '
                f'stroke-width="8" stroke-linecap="round" '
                f'stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ - dash:.1f}" '
                f'transform="rotate(-90 {cx} {cy})"/>')
    body.append(f'<text class="accent" x="{cx}" y="{cy + 12}" text-anchor="middle" '
                f'font-family="{MONO}" font-size="34" font-weight="bold">{cur}</text>')
    body.append(f'<text class="fg" x="{cx}" y="168" text-anchor="middle" '
                f'font-family="{MONO}" font-size="14">Current Streak</text>')
    body.append(f'<text class="muted" x="{cx}" y="188" text-anchor="middle" '
                f'font-family="{MONO}" font-size="11">{fmt_range(*cur_range) if cur else "—"}</text>')

    col(5 * W // 6, "Longest Streak", str(best), fmt_range(*best_range), body,
        value_class="accent2")

    svg = svg_card(W, 34 + CONTENT_H + 12, "./streak --stats", "\n".join(body),
                   extra_dark=ring_css_d + anim, extra_light=ring_css_l + anim)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"streak: current={cur} longest={best} total={total}")


if __name__ == "__main__":
    main()
