"""Self-generated GitHub stats card: repos, stars, followers, contributions.
REST API (token optional) + contributions.json — no third-party widget."""
import os

import requests

from contrib_data import load
from theme import MONO, T, svg_card, USERNAME

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "stats.svg")
W, CONTENT_H = 860, 150


def api(path):
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("PROFILE_PAT")
    if token:
        headers["Authorization"] = f"bearer {token}"
    r = requests.get(f"https://api.github.com{path}", headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()


def main():
    user = api(f"/users/{USERNAME}")
    contrib = load()
    last_year = int(contrib["days"][-1]["date"][:4])
    years = max(1, last_year - int(user["created_at"][:4]) + 1)

    stats = [
        ("Repositories", str(user["public_repos"])),
        ("Years on GitHub", str(years)),
        ("Followers", str(user["followers"])),
        ("Contributions", f"{contrib['total']:,}"),
    ]

    body = []
    n = len(stats)
    for i, (label, value) in enumerate(stats):
        cx = W * (2 * i + 1) // (2 * n)
        cls = "accent" if i % 2 == 0 else "accent2"
        body.append(f'<text class="{cls}" x="{cx}" y="78" text-anchor="middle" '
                    f'font-family="{MONO}" font-size="38" font-weight="bold">{value}</text>')
        body.append(f'<text class="fg" x="{cx}" y="110" text-anchor="middle" '
                    f'font-family="{MONO}" font-size="13">{label}</text>')
        if i:
            sx = W * i // n
            body.append(f'<line x1="{sx}" y1="40" x2="{sx}" y2="112" '
                        f'stroke="{T["muted"]}" stroke-width="1" opacity="0.3"/>')

    svg = svg_card(W, 34 + CONTENT_H, "./stats --github", "\n".join(body))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"stats: repos={user['public_repos']} years={years} "
          f"followers={user['followers']}")


if __name__ == "__main__":
    main()
