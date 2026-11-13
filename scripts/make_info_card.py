import os
from pathlib import Path
from xml.sax.saxutils import escape

from profile_config import HANDLE, INFO, PALETTE
from svg_frame import FONT, window

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "info-card.svg"
WIDTH = 490
HEIGHT = 380
STATIC = os.environ.get("STATIC") == "1"


def main():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" font-family="{FONT}">',
        "<style>"
        ".l{opacity:%s;animation:in .5s ease-out forwards}"
        "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}"
        ".k{fill:%s;font-weight:700}.v{fill:%s}"
        "</style>" % ("1" if STATIC else "0", PALETTE["red"], PALETTE["text"]),
        *window(WIDTH, HEIGHT, "~/neofetch"),
    ]

    user, host = HANDLE.split("@")
    lines = [
        f'<tspan fill="{PALETTE["blue"]}" font-weight="700">{user}</tspan>'
        f'<tspan fill="{PALETTE["text"]}">@</tspan>'
        f'<tspan fill="{PALETTE["blue"]}" font-weight="700">{host}</tspan>',
        f'<tspan fill="{PALETTE["border"]}">{"─" * len(HANDLE)}</tspan>',
    ]
    width = max(len(key) for key, _ in INFO)
    for key, value in INFO:
        lines.append(
            f'<tspan class="k">{escape(key.ljust(width))}</tspan>'
            f'<tspan class="v">  {escape(value)}</tspan>'
        )

    y = 62
    for index, line in enumerate(lines):
        delay = 0.6 + index * 0.18
        parts.append(
            f'<text class="l" style="animation-delay:{delay:.2f}s" x="22" y="{y}" '
            f'font-size="12.5" xml:space="preserve">{line}</text>'
        )
        y += 26 if index > 0 else 22

    swatch_y = y + 4
    for index, color in enumerate(["#161b22", "#0f2a5c", "#1e4fd8", PALETTE["blue"], "#8fb0ff", PALETTE["red"]]):
        delay = 0.6 + len(lines) * 0.18 + index * 0.06
        parts.append(
            f'<rect class="l" style="animation-delay:{delay:.2f}s" x="{22 + index * 26}" '
            f'y="{swatch_y}" width="22" height="12" rx="2" fill="{color}"/>'
        )

    parts.append("</svg>")
    OUTPUT.write_text("\n".join(parts) + "\n")
    print(f"wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
