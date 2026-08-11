"""Single source of truth for the profile's visual identity.

Change ACTIVE_THEME, rerun the render scripts + build_readme.py, commit.
Every generated SVG and every third-party widget URL derives from here.
"""

USERNAME = "Dishantpaudel"
DISPLAY_NAME = "Dipshant Paudel"
PROMPT_HOST = "dipshant@github"

ACTIVE_THEME = "tokyonight"

THEMES = {
    "terminal-green": {
        "bg": "#0d1117", "panel": "#161b22", "border": "#2ea043",
        "fg": "#c9d1d9", "muted": "#8b949e",
        "accent": "#00ff41", "accent2": "#7ee787",
        "ramp": ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
        "light": {
            "bg": "#ffffff", "panel": "#f6f8fa", "border": "#1a7f37",
            "fg": "#1f2328", "muted": "#57606a",
            "accent": "#1a7f37", "accent2": "#2da44e",
            "ramp": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
        },
        "widgets": {
            "stats_theme": "chartreuse-dark", "trophy_theme": "matrix",
            "graph_qs": "bg_color=0d1117&color=00ff41&line=00ff41&point=c9d1d9&title_color=00ff41",
            "streak_theme": "highcontrast",
            "typing_color": "00FF41",
        },
    },
    "tokyonight": {
        "bg": "#1a1b26", "panel": "#24283b", "border": "#3d59a1",
        "fg": "#c0caf5", "muted": "#565f89",
        "accent": "#7aa2f7", "accent2": "#bb9af7",
        "ramp": ["#24283b", "#3d59a1", "#5a7fd6", "#7aa2f7", "#b4f9f8"],
        "light": {
            "bg": "#ffffff", "panel": "#f2f3f8", "border": "#9aa5ce",
            "fg": "#343b58", "muted": "#8990b3",
            "accent": "#2e5bcd", "accent2": "#7847bd",
            "ramp": ["#e9ecf4", "#b3c3f0", "#7d9bea", "#4a74e0", "#2e5bcd"],
        },
        "widgets": {
            "stats_theme": "tokyonight", "trophy_theme": "tokyonight",
            "graph_theme": "tokyo-night",
            "streak_theme": "tokyonight",
            "typing_color": "70A5FD",
        },
    },
    "dracula": {
        "bg": "#282a36", "panel": "#343746", "border": "#6272a4",
        "fg": "#f8f8f2", "muted": "#6272a4",
        "accent": "#bd93f9", "accent2": "#ff79c6",
        "ramp": ["#343746", "#4d3d70", "#7452a8", "#9b6ee0", "#bd93f9"],
        "light": {
            "bg": "#ffffff", "panel": "#f5f3fa", "border": "#b0a4d6",
            "fg": "#2e2a3a", "muted": "#8b84a3",
            "accent": "#7c4dbe", "accent2": "#d6438f",
            "ramp": ["#efeaf8", "#d3bff0", "#b18ee4", "#9265d3", "#7c4dbe"],
        },
        "widgets": {
            "stats_theme": "dracula", "trophy_theme": "dracula",
            "graph_theme": "dracula", "streak_theme": "dracula",
            "typing_color": "BD93F9",
        },
    },
    "cyberpunk": {
        "bg": "#0b0221", "panel": "#160933", "border": "#54126b",
        "fg": "#e6e6fa", "muted": "#7a6f9b",
        "accent": "#ff2aff", "accent2": "#00e5ff",
        "ramp": ["#160933", "#54126b", "#a01db3", "#e02aff", "#00e5ff"],
        "light": {
            "bg": "#ffffff", "panel": "#faf2fc", "border": "#d093e0",
            "fg": "#3a2a44", "muted": "#9b84a8",
            "accent": "#b31bbf", "accent2": "#0899ab",
            "ramp": ["#f6e9f9", "#e9b8f2", "#d97fe8", "#c93fd9", "#b31bbf"],
        },
        "widgets": {
            "stats_theme": "synthwave", "trophy_theme": "radical",
            "graph_qs": "bg_color=0b0221&color=ff2aff&line=00e5ff&point=e6e6fa&title_color=ff2aff",
            "streak_theme": "black-ice",
            "typing_color": "FF2AFF",
        },
    },
}

T = THEMES[ACTIVE_THEME]

MONO = "ui-monospace,SFMono-Regular,Consolas,'Liberation Mono',Menlo,monospace"


def css_vars(extra_dark: str = "", extra_light: str = "") -> str:
    """Shared stylesheet: light defaults, dark palette under prefers-color-scheme.

    GitHub serves README SVGs through camo inside <img>; the browser still
    evaluates media queries inside the SVG against the OS color scheme.
    """
    L, D = T["light"], T
    return f"""<style>
  .card-bg {{ fill: {L['panel']}; stroke: {L['border']}; }}
  .title-fg {{ fill: {L['muted']}; }}
  .fg {{ fill: {L['fg']}; }}
  .muted {{ fill: {L['muted']}; }}
  .accent {{ fill: {L['accent']}; }}
  .accent2 {{ fill: {L['accent2']}; }}
  {extra_light}
  @media (prefers-color-scheme: dark) {{
    .card-bg {{ fill: {D['panel']}; stroke: {D['border']}; }}
    .title-fg {{ fill: {D['muted']}; }}
    .fg {{ fill: {D['fg']}; }}
    .muted {{ fill: {D['muted']}; }}
    .accent {{ fill: {D['accent']}; }}
    .accent2 {{ fill: {D['accent2']}; }}
    {extra_dark}
  }}
</style>"""


def svg_card(width: int, height: int, title: str, body: str,
             extra_dark: str = "", extra_light: str = "", defs: str = "") -> str:
    """Terminal-window card: rounded rect, border, traffic lights, title bar.

    Body content is translated below the 34px title bar.
    """
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{title}">
{css_vars(extra_dark, extra_light)}
{defs}
<rect class="card-bg" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" stroke-width="1"/>
<circle cx="20" cy="17" r="5" fill="#ff5f56"/>
<circle cx="38" cy="17" r="5" fill="#ffbd2e"/>
<circle cx="56" cy="17" r="5" fill="#27c93f"/>
<text class="title-fg" x="{width / 2:.0f}" y="21" text-anchor="middle" font-family="{MONO}" font-size="12">{PROMPT_HOST}: ~ {title}</text>
<line x1="0" y1="34" x2="{width}" y2="34" class="card-bg" stroke-width="1" fill="none"/>
<g transform="translate(0,34)">
{body}
</g>
</svg>"""


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*(max(0, min(255, int(c))) for c in rgb))


def blend(hex_a: str, hex_b: str, t: float) -> str:
    a, b = hex_to_rgb(hex_a), hex_to_rgb(hex_b)
    return rgb_to_hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))
