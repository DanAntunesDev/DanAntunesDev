from pathlib import Path
from xml.sax.saxutils import escape

from design import STATIC, BLUE, INK, MONO, MUTED, SANS, SERIF, card, label, svg_open

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "portrait.txt"
OUTPUT = ROOT / "hero.svg"
HEIGHT = 400
RAMP = " .`:-=+*cs#%@"
AREA = (440, 40, 836, 372)


def for_paper(line):
    out = []
    for char in line:
        index = RAMP.find(char)
        out.append(" " if index <= 0 else RAMP[len(RAMP) - index])
    return "".join(out)


def portrait():
    lines = [for_paper(line) for line in SOURCE.read_text().rstrip("\n").split("\n")]
    cols = max(len(line) for line in lines)
    left, top, right, bottom = AREA
    line_height = min((bottom - top) / len(lines), (right - left) / cols * 2)
    char_width = line_height / 2
    x0 = right - char_width * cols
    y0 = top + ((bottom - top) - line_height * len(lines)) / 2
    parts = ["<defs>"]
    for index in range(len(lines)):
        y = y0 + index * line_height
        begin = 0.35 + index * 0.07
        parts.append(
            f'<clipPath id="r{index}"><rect x="{x0 - 2:.1f}" y="{y:.1f}" '
            f'width="{char_width * cols + 4 if STATIC else 0:.1f}" height="{line_height + 1:.1f}">'
            + (
                ""
                if STATIC
                else f'<animate attributeName="width" from="0" to="{char_width * cols + 4:.1f}" '
                f'begin="{begin:.2f}s" dur="0.4s" fill="freeze"/>'
            )
            + "</rect></clipPath>"
        )
    parts.append("</defs>")
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip())
        y = y0 + index * line_height
        parts.append(
            f'<text clip-path="url(#r{index})" x="{x0 + indent * char_width:.1f}" '
            f'y="{y + line_height * 0.82:.1f}" font-family="{MONO}" '
            f'font-size="{char_width / 0.6:.2f}" fill="{INK}" fill-opacity="0.78" '
            f'textLength="{char_width * len(stripped):.1f}" lengthAdjust="spacingAndGlyphs" '
            f'xml:space="preserve">{escape(stripped)}</text>'
        )
    return parts


def main():
    parts = svg_open(HEIGHT)
    parts.append(card(0, 0, 860, HEIGHT))
    parts.append(
        f'<g class="fade" style="animation-delay:.1s"><rect x="46" y="52" width="8" height="8" '
        f'rx="1" fill="{BLUE}"/>{label(62, 60, "DESENVOLVEDOR FULLSTACK · MONTES CLAROS, MG")}</g>'
    )
    parts.append(
        f'<text class="fade" style="animation-delay:.25s" x="40" y="178" font-family="{SERIF}" '
        f'font-size="118" fill="{INK}" letter-spacing="-2">Daniel</text>'
    )
    parts.append(
        f'<text class="fade" style="animation-delay:.45s" x="52" y="280" font-family="{SERIF}" '
        f'font-style="italic" font-size="118" fill="{INK}" letter-spacing="-2">Antunes</text>'
    )
    for index, line in enumerate(
        ["Construo APIs, automações e produtos SaaS,", "do banco de dados até o WhatsApp."]
    ):
        parts.append(
            f'<text class="fade" style="animation-delay:{0.7 + index * 0.12:.2f}s" x="46" '
            f'y="{326 + index * 25}" font-family="{SANS}" font-size="17" fill="#3A3935">{line}</text>'
        )
    parts.append(
        f'<text class="fade" style="animation-delay:1s" x="46" y="374" font-family="{MONO}" '
        f'font-size="12.5" fill="{INK}">@_whoami.dev <tspan fill="{BLUE}">↗</tspan></text>'
    )
    parts.extend(portrait())
    parts.append("</svg>")
    OUTPUT.write_text("\n".join(parts) + "\n")
    print(f"wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
