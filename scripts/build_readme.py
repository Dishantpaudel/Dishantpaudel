"""Resolve templates/README.tpl.md against the active theme -> README.md."""
import os

from theme import ACTIVE_THEME, THEMES, USERNAME

ROOT = os.path.join(os.path.dirname(__file__), "..")
TPL = os.path.join(ROOT, "templates", "README.tpl.md")
OUT = os.path.join(ROOT, "README.md")


def main():
    w = THEMES[ACTIVE_THEME]["widgets"]
    subs = {
        "username": USERNAME,
        "typing_color": w["typing_color"],
        "stats_theme": w["stats_theme"],
        "trophy_theme": w["trophy_theme"],
        "streak_theme": w.get("streak_theme", "default"),
        "graph_query": (f"theme={w['graph_theme']}" if "graph_theme" in w
                        else w["graph_qs"]),
        "views_color": w["typing_color"].lower(),
    }
    with open(TPL, encoding="utf-8") as f:
        text = f.read()
    for key, val in subs.items():
        text = text.replace("{" + key + "}", val)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"README.md built (theme={ACTIVE_THEME})")


if __name__ == "__main__":
    main()
