"""Activity graph: daily contributions over the last 90 days as a smooth,
self-drawing area chart. Replaces the third-party activity-graph widget,
which is no longer reliable."""
import datetime as dt
import math
import os

from contrib_data import load
from theme import MONO, T, svg_card

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "activity.svg")

W = 860
DAYS = 90


def nice_axis(v):
    """Pick a 1/2/5 x 10^n step so the axis has at most 5 round-number intervals."""
    v = max(v, 1)
    exp = 10 ** math.floor(math.log10(v))
    for m in (0.1, 0.2, 0.5, 1, 2, 5, 10):
        step = max(1, int(m * exp))
        if step * 5 >= v:
            return step, step * math.ceil(v / step)
    return 10 * exp, 10 * exp


def smooth_path(pts):
    """Catmull-Rom spline through pts as cubic Beziers.

    Control points are clamped between their segment's endpoints, so the curve
    never overshoots: peaks sit exactly on the data and it never dips below 0.
    """
    def clamp(v, a, b):
        return max(min(a, b), min(max(a, b), v))

    d = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, clamp(p1[1] + (p2[1] - p0[1]) / 6, p1[1], p2[1]))
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, clamp(p2[1] - (p3[1] - p1[1]) / 6, p1[1], p2[1]))
        d.append(f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}")
    return " ".join(d)


def main():
    data = load()
    counts = {d["date"]: d["count"] for d in data["days"]}
    last = dt.date.fromisoformat(data["days"][-1]["date"])
    days = [last - dt.timedelta(days=DAYS - 1 - i) for i in range(DAYS)]
    vals = [counts.get(d.isoformat(), 0) for d in days]

    total = sum(vals)
    active = sum(1 for v in vals if v)
    best_i = max(range(DAYS), key=lambda i: vals[i])
    avg = total / active if active else 0
    step, ymax = nice_axis(max(vals))

    x0, x1, top, h = 56, W - 28, 64, 170
    base = top + h

    def xy(i, v):
        return x0 + (x1 - x0) * i / (DAYS - 1), base - h * v / ymax

    body = []
    # headline stats
    stats = [("contributions", f"{total}"), ("active days", f"{active}/{DAYS}"),
             ("best day", f"{vals[best_i]}"), ("avg / active day", f"{avg:.1f}")]
    col = (W - 48) / len(stats)
    for k, (label, value) in enumerate(stats):
        cx = 24 + col * k
        body.append(f'<text class="accent" x="{cx:.0f}" y="24" font-family="{MONO}" '
                    f'font-size="18" font-weight="700">{value}</text>')
        body.append(f'<text class="muted" x="{cx:.0f}" y="40" font-family="{MONO}" '
                    f'font-size="11">{label}</text>')

    # gridlines + y labels
    for g in range(ymax // step + 1):
        v = step * g
        y = base - h * v / ymax
        body.append(f'<line class="grid" x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}"/>')
        body.append(f'<text class="muted" x="{x0 - 10}" y="{y + 4:.1f}" text-anchor="end" '
                    f'font-family="{MONO}" font-size="10">{v:g}</text>')

    pts = [xy(i, v) for i, v in enumerate(vals)]
    line = smooth_path(pts)
    body.append(f'<path d="{line} L{x1:.1f},{base:.1f} L{x0:.1f},{base:.1f} Z" '
                f'fill="url(#actFill)" class="area"/>')
    body.append(f'<path d="{line}" fill="none" class="act-line" stroke-width="2.4" '
                f'stroke-linejoin="round" stroke-linecap="round" pathLength="1000"/>')
    for (x, y), v in zip(pts, vals):
        if v:
            body.append(f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="2.3"/>')

    # best-day callout
    bx, by = pts[best_i]
    anchor = "end" if bx > x1 - 140 else "start"
    dx = -8 if anchor == "end" else 8
    body.append(f'<circle class="peak" cx="{bx:.1f}" cy="{by:.1f}" r="5"/>')
    body.append(f'<text class="accent2" x="{bx + dx:.1f}" y="{max(by - 10, top + 10):.1f}" '
                f'text-anchor="{anchor}" font-family="{MONO}" font-size="11">'
                f'{vals[best_i]} on {days[best_i].strftime("%d %b")}</text>')

    # month ticks
    for i, d in enumerate(days):
        if d.day == 1 or i == 0:
            x = pts[i][0]
            body.append(f'<line class="grid" x1="{x:.1f}" y1="{base}" x2="{x:.1f}" y2="{base + 5}"/>')
            body.append(f'<text class="muted" x="{x:.1f}" y="{base + 18}" text-anchor="middle" '
                        f'font-family="{MONO}" font-size="10">{d.strftime("%b")}</text>')

    L, D = T["light"], T
    defs = f"""<defs><linearGradient id="actFill" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" class="stop-a" stop-opacity="0.45"/>
<stop offset="1" class="stop-a" stop-opacity="0"/>
</linearGradient></defs>"""
    # The resting state is the finished drawing; the animation only plays on
    # top of it, so renderers that skip animations still show the full line.
    common = (".act-line{animation:draw 2.4s ease-out}"
              "@keyframes draw{from{stroke-dasharray:1000;stroke-dashoffset:1000}"
              "to{stroke-dasharray:1000;stroke-dashoffset:0}}"
              ".grid{stroke-width:1;opacity:.35}")
    extra_light = (f"{common}.act-line{{stroke:{L['accent']}}}.stop-a{{stop-color:{L['accent']}}}"
                   f".grid{{stroke:{L['muted']}}}.dot{{fill:{L['accent']}}}"
                   f".peak{{fill:{L['accent2']}}}")
    extra_dark = (f".act-line{{stroke:{D['accent']};filter:drop-shadow(0 0 3px {D['accent']})}}"
                  f".stop-a{{stop-color:{D['accent']}}}.grid{{stroke:{D['muted']}}}"
                  f".dot{{fill:{D['accent']}}}.peak{{fill:{D['accent2']}}}")
    svg = svg_card(W, 34 + base + 30, f"./activity --last-{DAYS}-days", "\n".join(body),
                   extra_dark=extra_dark, extra_light=extra_light, defs=defs)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"activity: {total} contributions over {DAYS} days, {active} active")


if __name__ == "__main__":
    main()
