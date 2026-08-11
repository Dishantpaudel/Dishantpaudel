"""3D ANSI-Shadow wordmark: DIPSHANT, rendered as three offset layers
(depth shades under a gradient-filled top layer) with a pulsing glow."""
import os

from theme import MONO, T, blend, svg_card

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "wordmark.svg")

# figlet "ANSI Shadow" glyphs, 6 rows each
GLYPHS = {
    "D": ["██████╗ ",
          "██╔══██╗",
          "██║  ██║",
          "██║  ██║",
          "██████╔╝",
          "╚═════╝ "],
    "I": ["██╗",
          "██║",
          "██║",
          "██║",
          "██║",
          "╚═╝"],
    "P": ["██████╗ ",
          "██╔══██╗",
          "██████╔╝",
          "██╔═══╝ ",
          "██║     ",
          "╚═╝     "],
    "S": ["███████╗",
          "██╔════╝",
          "███████╗",
          "╚════██║",
          "███████║",
          "╚══════╝"],
    "H": ["██╗  ██╗",
          "██║  ██║",
          "███████║",
          "██╔══██║",
          "██║  ██║",
          "╚═╝  ╚═╝"],
    "A": [" █████╗ ",
          "██╔══██╗",
          "███████║",
          "██╔══██║",
          "██║  ██║",
          "╚═╝  ╚═╝"],
    "N": ["███╗   ██╗",
          "████╗  ██║",
          "██╔██╗ ██║",
          "██║╚██╗██║",
          "██║ ╚████║",
          "╚═╝  ╚═══╝"],
    "T": ["████████╗",
          "╚══██╔══╝",
          "   ██║   ",
          "   ██║   ",
          "   ██║   ",
          "   ╚═╝   "],
}

WORD = "DIPSHANT"
FONT_SIZE = 13
CHAR_W = FONT_SIZE * 0.62
LINE_H = FONT_SIZE + 1


def compose(word):
    rows = ["".join(GLYPHS[ch][r] for ch in word) for r in range(6)]
    return rows


def layer(rows, dx, dy, fill_attr, extra=""):
    width = len(rows[0]) * CHAR_W
    out = [f'<g transform="translate({dx},{dy})"{extra}>']
    for i, row in enumerate(rows):
        out.append(
            f'<text xml:space="preserve" x="0" y="{(i + 1) * LINE_H}" '
            f'font-family="{MONO}" font-size="{FONT_SIZE}" {fill_attr} '
            f'textLength="{width:.0f}" lengthAdjust="spacing">{row}</text>')
    out.append("</g>")
    return "\n".join(out)


def main():
    rows = compose(WORD)
    text_w = len(rows[0]) * CHAR_W
    text_h = 6 * LINE_H

    pad_x = 24
    w = int(text_w + pad_x * 2)
    content_h = int(text_h + 46)

    deep = blend(T["accent"], "#000000", 0.62)
    mid = blend(T["accent"], "#000000", 0.35)
    grad = (f'<linearGradient id="wg" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{T["accent"]}"/>'
            f'<stop offset="1" stop-color="{T["accent2"]}"/></linearGradient>')

    ox, oy = pad_x, 16
    body = "\n".join([
        layer(rows, ox + 3.5, oy + 3.5, f'fill="{deep}"'),
        layer(rows, ox + 1.8, oy + 1.8, f'fill="{mid}"'),
        layer(rows, ox, oy, 'fill="url(#wg)"', ' class="wm-top"'),
        f'<text class="muted" x="{w / 2:.0f}" y="{content_h - 6}" '
        f'text-anchor="middle" font-family="{MONO}" font-size="12">'
        f'&#47;&#47; software engineer · barcelona</text>',
    ])

    glow = (
        f"@keyframes wmglow{{"
        f"0%,100%{{filter:drop-shadow(0 0 2px {T['accent']})}}"
        f"50%{{filter:drop-shadow(0 0 9px {T['accent2']})}}}}"
        ".wm-top{animation:wmglow 3.2s ease-in-out infinite;}"
    )
    svg = svg_card(w, 34 + content_h, "./wordmark --3d", body,
                   extra_dark=glow, defs=f"<defs>{grad}</defs>")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wordmark: {w}x{34 + content_h}")


if __name__ == "__main__":
    main()
