from profile_config import PALETTE

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


def window(width, height, title):
    return [
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" '
        f'fill="{PALETTE["bg"]}" stroke="{PALETTE["border"]}"/>',
        f'<path d="M0.5 30.5H{width - 0.5}" stroke="{PALETTE["border"]}"/>',
        f'<circle cx="18" cy="15.5" r="5" fill="{PALETTE["red"]}"/>',
        '<circle cx="34" cy="15.5" r="5" fill="#d29922"/>',
        f'<circle cx="50" cy="15.5" r="5" fill="{PALETTE["blue"]}"/>',
        f'<text x="{width / 2}" y="20" text-anchor="middle" fill="{PALETTE["muted"]}" '
        f'font-size="11">{title}</text>',
    ]
