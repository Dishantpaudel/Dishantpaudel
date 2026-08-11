"""Truecolor ASCII portrait: each character keeps its source pixel color,
blended toward the theme accent so the portrait sits in the palette.

Per-row <text textLength> locks column alignment across OS font metrics.
"""
import os

from PIL import Image

from theme import MONO, T, blend, rgb_to_hex, svg_card

SRC = os.path.join(os.path.dirname(__file__), "..", "assets", "photo_prepped.png")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "ascii-portrait.svg")

COLS = 88
CHAR_W, CHAR_H = 7.2, 13  # rendered cell size in svg units
RAMP = " .'-:;=+*x#%@█"  # light -> dense
ACCENT_BLEND = 0.30


def esc_char(ch):
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)


def tspan(color, chars):
    text = "".join(esc_char(ch) for ch in chars)
    if color is None:
        return f"<tspan>{text}</tspan>"
    return f'<tspan fill="{color}">{text}</tspan>'


def main():
    img = Image.open(SRC).convert("RGB")
    # cell is CHAR_W wide x CHAR_H tall, so fewer rows than cols keeps aspect
    rows = int(COLS * img.height / img.width * CHAR_W / CHAR_H)
    small = img.resize((COLS, rows), Image.LANCZOS)
    px = small.load()

    body = []
    width = COLS * CHAR_W
    for y in range(rows):
        spans = []
        run_color, run_chars = None, []
        for x in range(COLS):
            r, g, b = px[x, y]
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            ch = RAMP[int(lum / 255 * (len(RAMP) - 1))]
            if ch == " ":
                color = None
            else:
                # quantize to soften color count, then pull toward accent
                q = (r // 24 * 24, g // 24 * 24, b // 24 * 24)
                color = blend(rgb_to_hex(q), T["accent"], ACCENT_BLEND)
            if color != run_color and run_chars:
                spans.append((run_color, "".join(run_chars)))
                run_chars = []
            run_color = color
            run_chars.append(ch)
        if run_chars:
            spans.append((run_color, "".join(run_chars)))

        tspans = "".join(tspan(c, s) for c, s in spans)
        body.append(
            f'<text xml:space="preserve" x="10" y="{14 + y * CHAR_H}" '
            f'font-family="{MONO}" font-size="12" textLength="{width:.0f}" '
            f'lengthAdjust="spacing">{tspans}</text>')

    w = int(width + 20)
    h = int(rows * CHAR_H + 24)
    svg = svg_card(w, 34 + h, "./portrait --ascii --truecolor", "\n".join(body))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    size_kb = os.path.getsize(OUT) / 1024
    print(f"ascii portrait: {COLS}x{rows} chars, {size_kb:.0f} KB")


if __name__ == "__main__":
    main()
