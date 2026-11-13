import io
import os
from pathlib import Path

import cv2
import numpy as np
import requests
from PIL import Image

from profile_config import USERNAME

ROOT = Path(__file__).resolve().parent.parent
AVATAR = ROOT / "assets" / "avatar.png"
OUTPUT = ROOT / "data" / "portrait.txt"
COLS = 96
HEAD_AND_SHOULDERS = 0.42
RAMP = " .`:-=+*cs#%@"


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
        bottom = top + int((bottom - top) * HEAD_AND_SHOULDERS)
        rgba = rgba[top:bottom, left:right]
        alpha = alpha[top:bottom, left:right]
        columns = np.where((alpha > 32).any(axis=0))[0]
        if len(columns):
            rgba = rgba[:, columns.min() : columns.max() + 1]
            alpha = alpha[:, columns.min() : columns.max() + 1]
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


def main():
    if not AVATAR.exists() or os.environ.get("REFRESH_AVATAR") == "1":
        download_avatar()
    gray, alpha = prepare(Image.open(AVATAR).convert("RGB"))
    lines = to_rows(gray, alpha)
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUTPUT.name} ({len(lines)} rows)")


if __name__ == "__main__":
    main()
