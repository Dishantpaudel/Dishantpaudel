"""Pipelines: how the main work projects move data, drawn as animated
flow diagrams. Static content; only the theme changes it."""
import os

from theme import MONO, T, esc, svg_card

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "pipelines.svg")

W = 860

PIPELINES = [
    ("voice-ai", "32 languages · ~2 s to first audio · fully self-hosted", [
        ("caller", "speaks"),
        ("speech-to-text", "Nemotron · Whisper"),
        ("LLM", "self-hosted Qwen"),
        ("text-to-speech", "VoxCPM2"),
        ("reply", "streamed audio"),
    ]),
    ("review-radar", "F1 0.903 on 50k reviews · ~3 ms per review · side project", [
        ("review", "customer text"),
        ("clean", "typos · negation"),
        ("features", "TF-IDF n-grams"),
        ("model", "logistic regression"),
        ("threshold", "profit-optimal"),
        ("flag", "negative · urgent"),
    ]),
    ("burnout-predictor", "full MLOps lifecycle on 3,000 records · side project", [
        ("data", "versioned · DVC"),
        ("model", "XGBoost"),
        ("tuning", "Optuna"),
        ("tracking", "MLflow"),
        ("explain", "SHAP"),
        ("serve", "FastAPI"),
    ]),
    ("barcelona-housing", "rental search built around the household · side project", [
        ("household", "people · budget"),
        ("sources", "18 connectors"),
        ("normalise", "source kept"),
        ("dedupe", "cross-site match"),
        ("fit score", "price per person"),
        ("alerts", "new · price drops"),
    ]),
    ("jobfinder", "ranks jobs against a real profile, never invents facts · side project", [
        ("job APIs", "~1,900 postings"),
        ("score", "deterministic"),
        ("shortlist", "best matches"),
        ("tailor", "Claude"),
        ("fact check", "no new numbers"),
        ("CV + letter", "HTML · PDF"),
    ]),
]


def row(y, name, caption, nodes):
    out = []
    out.append(f'<text class="accent" x="24" y="{y}" font-family="{MONO}" font-size="13" '
               f'font-weight="700">$ {esc(name)}</text>')
    out.append(f'<text class="muted" x="{W - 24}" y="{y}" text-anchor="end" '
               f'font-family="{MONO}" font-size="11">{esc(caption)}</text>')
    n = len(nodes)
    gap = 30
    nw = (W - 48 - gap * (n - 1)) / n
    ny, nh = y + 14, 50
    for i, (label, sub) in enumerate(nodes):
        x = 24 + i * (nw + gap)
        out.append(f'<rect class="node" x="{x:.1f}" y="{ny}" width="{nw:.1f}" height="{nh}" '
                   f'rx="8" style="animation-delay:{i * 0.25:.2f}s"/>')
        out.append(f'<text class="fg" x="{x + nw / 2:.1f}" y="{ny + 22}" text-anchor="middle" '
                   f'font-family="{MONO}" font-size="12" font-weight="600">{esc(label)}</text>')
        out.append(f'<text class="muted" x="{x + nw / 2:.1f}" y="{ny + 38}" text-anchor="middle" '
                   f'font-family="{MONO}" font-size="10">{esc(sub)}</text>')
        if i < n - 1:
            ax0, ax1, ay = x + nw + 4, x + nw + gap - 6, ny + nh / 2
            out.append(f'<line class="flow" x1="{ax0:.1f}" y1="{ay}" x2="{ax1:.1f}" y2="{ay}" '
                       f'marker-end="url(#arrow)"/>')
    return out, ny + nh


def main():
    body = []
    y = 26
    for name, caption, nodes in PIPELINES:
        part, bottom = row(y, name, caption, nodes)
        body.extend(part)
        y = bottom + 38

    L, D = T["light"], T
    defs = """<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
markerWidth="6" markerHeight="6" orient="auto-start-reverse">
<path d="M0,0 L10,5 L0,10 z" class="arrow-head"/></marker></defs>"""
    common = (".flow{stroke-width:2;stroke-dasharray:4 4;animation:flow .8s linear infinite}"
              "@keyframes flow{to{stroke-dashoffset:-8}}"
              ".node{stroke-width:1.2;animation:pulse 3s ease-in-out infinite}"
              "@keyframes pulse{50%{stroke-opacity:.45}}")
    extra_light = (f"{common}.node{{fill:{L['bg']};stroke:{L['accent']}}}"
                   f".flow{{stroke:{L['accent2']}}}.arrow-head{{fill:{L['accent2']}}}")
    extra_dark = (f".node{{fill:{D['bg']};stroke:{D['accent']};"
                  f"filter:drop-shadow(0 0 4px {D['accent']}55)}}"
                  f".flow{{stroke:{D['accent2']}}}.arrow-head{{fill:{D['accent2']}}}")
    svg = svg_card(W, 34 + y - 14, "./pipelines --show", "\n".join(body),
                   extra_dark=extra_dark, extra_light=extra_light, defs=defs)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"pipelines: {len(PIPELINES)} flows")


if __name__ == "__main__":
    main()
