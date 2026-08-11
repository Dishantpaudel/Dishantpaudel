"""Custom contribution heatmap: month labels, weekday labels, legend, total,
glow on the hottest cells. Dark/light aware via in-SVG media query."""
import os

from contrib_data import load, last_year_days, quantize
from theme import MONO, T, svg_card

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "heatmap.svg")

CELL, GAP = 11, 4
PITCH = CELL + GAP
LEFT, TOP = 46, 30
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def main():
    data = load()
    days = last_year_days(data)
    level = quantize([c for _, c in days])
    year_total = sum(c for _, c in days)

    weeks = [days[i:i + 7] for i in range(0, len(days), 7)]
    n_weeks = len(weeks)
    grid_w = n_weeks * PITCH - GAP
    width = LEFT + grid_w + 16
    grid_h = 7 * PITCH - GAP

    ramp_css_l, ramp_css_d = [], []
    for i in range(5):
        ramp_css_l.append(f".lv{i}{{fill:{T['light']['ramp'][i]}}}")
        ramp_css_d.append(f".lv{i}{{fill:{T['ramp'][i]}}}")
    glow = (f".lv4{{fill:{T['ramp'][4]};"
            f"filter:drop-shadow(0 0 3px {T['accent']})}}")

    body = []
    seen_month = None
    for x, week in enumerate(weeks):
        first_date = week[0][0]
        if first_date.day <= 7 and first_date.month != seen_month:
            seen_month = first_date.month
            body.append(
                f'<text class="muted" x="{LEFT + x * PITCH}" y="{TOP - 10}" '
                f'font-family="{MONO}" font-size="10">'
                f'{MONTHS[first_date.month - 1]}</text>')
        for y, (date, count) in enumerate(week):
            body.append(
                f'<rect class="lv{level(count)}" x="{LEFT + x * PITCH}" '
                f'y="{TOP + y * PITCH}" width="{CELL}" height="{CELL}" '
                f'rx="2.5"><title>{date.isoformat()}: {count}</title></rect>')

    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        body.append(
            f'<text class="muted" x="{LEFT - 8}" '
            f'y="{TOP + row * PITCH + CELL - 2}" text-anchor="end" '
            f'font-family="{MONO}" font-size="10">{label}</text>')

    footer_y = TOP + grid_h + 22
    body.append(
        f'<text class="fg" x="{LEFT}" y="{footer_y}" font-family="{MONO}" '
        f'font-size="12">{year_total:,} contributions in the last year</text>')
    legend_x = width - 16 - 5 * PITCH - 44
    body.append(
        f'<text class="muted" x="{legend_x - 8}" y="{footer_y}" '
        f'text-anchor="end" font-family="{MONO}" font-size="10">Less</text>')
    for i in range(5):
        body.append(
            f'<rect class="lv{i}" x="{legend_x + i * PITCH}" '
            f'y="{footer_y - 10}" width="{CELL}" height="{CELL}" rx="2.5"/>')
    body.append(
        f'<text class="muted" x="{legend_x + 5 * PITCH + 6}" y="{footer_y}" '
        f'font-family="{MONO}" font-size="10">More</text>')

    svg = svg_card(width, 34 + footer_y + 14, "./render --contributions",
                   "\n".join(body),
                   extra_dark="\n".join(ramp_css_d) + glow,
                   extra_light="\n".join(ramp_css_l))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"heatmap: {n_weeks} weeks, {year_total} contributions")


if __name__ == "__main__":
    main()
