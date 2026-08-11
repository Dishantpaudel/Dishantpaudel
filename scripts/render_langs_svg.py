"""Self-generated top-languages card: stacked byte-share bar + legend.
Sums linguist byte counts per language across owned non-fork repos.
Falls back to primary-language repo counts when unauthenticated and
per-repo language calls start rate-limiting."""
import os

import requests

from theme import MONO, T, svg_card, USERNAME

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "langs.svg")
W, CONTENT_H = 860, 170
TOP_N = 8

LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Vue": "#41b883", "Kotlin": "#A97BFF", "HTML": "#e34c26",
    "CSS": "#563d7c", "Java": "#b07219", "C++": "#f34b7d", "C": "#555555",
    "Shell": "#89e051", "Dockerfile": "#384d54", "Jupyter Notebook": "#DA5B0B",
    "Ruby": "#701516", "Go": "#00ADD8", "PHP": "#4F5D95", "Swift": "#F05138",
    "Dart": "#00B4AB", "SCSS": "#c6538c", "EJS": "#a91e50",
}


def session():
    s = requests.Session()
    s.headers["Accept"] = "application/vnd.github+json"
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("PROFILE_PAT")
    if token:
        s.headers["Authorization"] = f"bearer {token}"
    return s


def gather(s):
    # Primary language per repo: byte counts get drowned out by any repo
    # with vendored code, project counts reflect the actual project mix.
    repos = s.get(f"https://api.github.com/users/{USERNAME}/repos"
                  "?per_page=100&type=owner", timeout=30).json()
    totals = {}
    for r in repos:
        if not r["fork"] and r["language"]:
            totals[r["language"]] = totals.get(r["language"], 0) + 1
    return totals


def main():
    totals = gather(session())
    total = sum(totals.values()) or 1
    top = sorted(totals.items(), key=lambda kv: -kv[1])[:TOP_N]

    body = [f'<text class="fg" x="24" y="18" font-family="{MONO}" '
            f'font-size="13">most used languages · by project</text>']

    # stacked bar
    bx, by, bw, bh = 24, 36, W - 48, 16
    x = bx
    for i, (lang, size) in enumerate(top):
        w = bw * size / total
        color = LANG_COLORS.get(lang, T["accent"])
        rx = ' rx="8"' if i in (0, len(top) - 1) else ""
        body.append(f'<rect x="{x:.1f}" y="{by}" width="{max(w, 2):.1f}" '
                    f'height="{bh}"{rx} fill="{color}"/>')
        x += w

    # legend, two rows of four
    per_row = 4
    col_w = (W - 48) // per_row
    for i, (lang, size) in enumerate(top):
        cx = 24 + (i % per_row) * col_w
        cy = 86 + (i // per_row) * 34
        pct = 100 * size / total
        color = LANG_COLORS.get(lang, T["accent"])
        body.append(f'<circle cx="{cx + 6}" cy="{cy - 4}" r="6" fill="{color}"/>')
        body.append(f'<text class="fg" x="{cx + 20}" y="{cy}" '
                    f'font-family="{MONO}" font-size="12">{lang}</text>')
        body.append(f'<text class="muted" x="{cx + 20}" y="{cy + 15}" '
                    f'font-family="{MONO}" font-size="11">{pct:.1f}%</text>')

    svg = svg_card(W, 34 + CONTENT_H, "./langs --top", "\n".join(body))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("langs: " + ", ".join(f"{l} {100 * s / total:.0f}%" for l, s in top[:4]))


if __name__ == "__main__":
    main()
