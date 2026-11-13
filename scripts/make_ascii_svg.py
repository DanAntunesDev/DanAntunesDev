import io
import os
from pathlib import Path
from xml.sax.saxutils import escape

import cv2
import numpy as np
import requests
from PIL import Image

from profile_config import PALETTE, USERNAME
from svg_frame import FONT, window

ROOT = Path(__file__).resolve().parent.parent
AVATAR = ROOT / "assets" / "avatar.png"
OUTPUT = ROOT / "portrait-ascii.svg"
WIDTH = 370
HEIGHT = 380
COLS = 62
RAMP = " .`:-=+*cs#%@"
STATIC = os.environ.get("STATIC") == "1"


def download_avatar():
    response = requests.get(f"https://github.com/{USERNAME}.png?size=460", timeout=30)
    response.raise_for_status()
    AVATAR.parent.mkdir(exist_ok=True)
    AVATAR.write_bytes(response.content)


def cut_out(image):
    try:
        from rembg import remove
    except ImportError:
        return image.convert("RGBA")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return Image.open(io.BytesIO(remove(buffer.getvalue()))).convert("RGBA")


def prepare(image):
    rgba = np.array(cut_out(image))
    alpha = rgba[:, :, 3]
    ys, xs = np.where(alpha > 32)
    if len(xs):
        pad = 6
        top, bottom = max(ys.min() - pad, 0), min(ys.max() + pad, alpha.shape[0])
        left, right = max(xs.min() - pad, 0), min(xs.max() + pad, alpha.shape[1])
        rgba = rgba[top:bottom, left:right]
        alpha = alpha[top:bottom, left:right]
    gray = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(gray)
    return gray, alpha


def to_rows(gray, alpha):
    height, width = gray.shape
    rows = max(1, round(COLS * height / width * 0.5))
    small = cv2.resize(gray, (COLS, rows), interpolation=cv2.INTER_AREA).astype(float)
    mask = cv2.resize(alpha, (COLS, rows), interpolation=cv2.INTER_AREA)
    inside = mask > 96
    low, high = np.percentile(small[inside], [3, 97]) if inside.any() else (0, 255)
    level = np.clip((small - low) / max(high - low, 1), 0, 1)
    lines = []
    for y in range(rows):
        chars = []
        for x in range(COLS):
            if not inside[y, x]:
                chars.append(" ")
                continue
            index = 1 + int(level[y, x] * (len(RAMP) - 2))
            chars.append(RAMP[index])
        lines.append("".join(chars).rstrip())
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def render(lines):
    area_top, area_bottom = 44, HEIGHT - 14
    line_height = min((area_bottom - area_top) / len(lines), (WIDTH - 32) / COLS * 2)
    char_width = line_height / 2
    font_size = char_width / 0.6
    text_width = char_width * COLS
    left = (WIDTH - text_width) / 2
    top = area_top + ((area_bottom - area_top) - line_height * len(lines)) / 2

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" font-family="{FONT}">',
        *window(WIDTH, HEIGHT, "~/whoami"),
        "<defs>",
    ]
    for index in range(len(lines)):
        y = top + index * line_height
        begin = 0.2 + index * 0.06
        width = "0" if not STATIC else f"{text_width + 4:.1f}"
        animate = (
            ""
            if STATIC
            else f'<animate attributeName="width" from="0" to="{text_width + 4:.1f}" '
            f'begin="{begin:.2f}s" dur="0.35s" fill="freeze"/>'
        )
        parts.append(
            f'<clipPath id="r{index}"><rect x="{left - 2:.1f}" y="{y:.1f}" width="{width}" '
            f'height="{line_height + 1:.1f}">{animate}</rect></clipPath>'
        )
    parts.append("</defs>")

    for index, line in enumerate(lines):
        y = top + index * line_height
        baseline = y + line_height * 0.82
        length = char_width * len(line)
        if not line:
            continue
        parts.append(
            f'<text clip-path="url(#r{index})" x="{left + (len(line) - len(line.lstrip())) * char_width:.1f}" '
            f'y="{baseline:.1f}" font-size="{font_size:.2f}" fill="{PALETTE["text"]}" '
            f'textLength="{char_width * len(line.lstrip()):.1f}" lengthAdjust="spacingAndGlyphs" '
            f'xml:space="preserve">{escape(line.lstrip())}</text>'
        )
        if not STATIC:
            begin = 0.2 + index * 0.06
            parts.append(
                f'<rect x="{left:.1f}" y="{y:.1f}" width="{char_width:.1f}" height="{line_height:.1f}" '
                f'fill="{PALETTE["red"]}" opacity="0">'
                f'<animate attributeName="x" from="{left:.1f}" to="{left + length:.1f}" '
                f'begin="{begin:.2f}s" dur="0.35s" fill="freeze"/>'
                f'<set attributeName="opacity" to="1" begin="{begin:.2f}s"/>'
                f'<set attributeName="opacity" to="0" begin="{begin + 0.35:.2f}s"/>'
                "</rect>"
            )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    if not AVATAR.exists() or os.environ.get("REFRESH_AVATAR") == "1":
        download_avatar()
    gray, alpha = prepare(Image.open(AVATAR).convert("RGB"))
    lines = to_rows(gray, alpha)
    OUTPUT.write_text(render(lines))
    print(f"wrote {OUTPUT.name} ({len(lines)} rows)")


if __name__ == "__main__":
    main()
