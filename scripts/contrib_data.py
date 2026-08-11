"""Shared loader for data/contributions.json."""
import datetime as dt
import json
import os

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def last_year_days(data):
    """Days covering the last 53 full weeks, aligned so column 0 starts on Sunday."""
    days = {d["date"]: d["count"] for d in data["days"]}
    last = dt.date.fromisoformat(data["days"][-1]["date"])
    start = last - dt.timedelta(days=370)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday
    out = []
    cur = start
    while cur <= last:
        out.append((cur, days.get(cur.isoformat(), 0)))
        cur += dt.timedelta(days=1)
    return out


def quantize(counts):
    """GitHub-style 5 levels: 0, then quartiles of the nonzero distribution."""
    nz = sorted(c for c in counts if c > 0)
    if not nz:
        return lambda c: 0
    q = [nz[int(len(nz) * f)] for f in (0.25, 0.5, 0.75)]

    def level(c):
        if c == 0:
            return 0
        for i, t in enumerate(q):
            if c <= t:
                return i + 1
        return 4
    return level
