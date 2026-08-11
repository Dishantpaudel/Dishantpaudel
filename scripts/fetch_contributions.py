"""Fetch the contribution calendar into data/contributions.json.

With GITHUB_TOKEN (or PROFILE_PAT) set: GitHub GraphQL, per account-creation
year so the streak card can use all-time data. Without a token (local dev):
falls back to the public jogruber contributions API, which mirrors the same
public calendar.
"""
import datetime as dt
import json
import os
import sys

import requests

from theme import USERNAME

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")

GRAPHQL = "https://api.github.com/graphql"
CAL_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    createdAt
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch_year_graphql(token: str, start: dt.datetime, end: dt.datetime):
    r = requests.post(
        GRAPHQL,
        headers={"Authorization": f"bearer {token}"},
        json={"query": CAL_QUERY,
              "variables": {"login": USERNAME,
                            "from": start.isoformat(),
                            "to": end.isoformat()}},
        timeout=30,
    )
    r.raise_for_status()
    payload = r.json()
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]


def fetch_graphql(token: str) -> dict:
    now = dt.datetime.now(dt.timezone.utc)
    user = fetch_year_graphql(token, now - dt.timedelta(days=365), now)
    created = dt.datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00"))

    days = {}
    cursor = created
    while cursor < now:
        window_end = min(cursor + dt.timedelta(days=365), now)
        cal = fetch_year_graphql(token, cursor, window_end)[
            "contributionsCollection"]["contributionCalendar"]
        for week in cal["weeks"]:
            for d in week["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
        cursor = window_end
    return days


def fetch_public() -> dict:
    r = requests.get(
        f"https://github-contributions-api.jogruber.de/v4/{USERNAME}",
        timeout=30,
    )
    r.raise_for_status()
    return {d["date"]: d["count"] for d in r.json()["contributions"]}


def main():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("PROFILE_PAT")
    if token:
        days = fetch_graphql(token)
        source = "graphql"
    else:
        days = fetch_public()
        source = "public-api"

    # the public API pads the current year with future zero-count days
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    days = {d: c for d, c in days.items() if d <= today}

    ordered = sorted(days.items())
    data = {
        "user": USERNAME,
        "source": source,
        "total": sum(days.values()),
        "days": [{"date": d, "count": c} for d, c in ordered],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    print(f"wrote {len(ordered)} days ({source}), total {data['total']}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
