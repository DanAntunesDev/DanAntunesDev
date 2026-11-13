import json
from collections import OrderedDict
from pathlib import Path

from design import PURPLE, INK, STATIC, shimmer, LINE, MONO, MUTED, SANS, SERIF, card, label, svg_open

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "stats.svg"
HEIGHT = 340
MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def number(value):
    return f"{value:,}".replace(",", ".")


def main():
    data = json.loads(SOURCE.read_text())
    days = data["days"]
    months = OrderedDict()
    for day in days:
        months[day["date"][:7]] = months.get(day["date"][:7], 0) + day["count"]
    months = list(months.items())[-12:]
    active = sum(1 for day in days if day["count"] > 0)
    best = (data.get("bestDay") or {"count": 0})["count"]
    peak = max((value for _, value in months), default=0) or 1

    css = (
        ".b{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);"
        "animation:grow .8s cubic-bezier(.2,.8,.2,1) forwards}"
        "@keyframes grow{to{transform:scaleY(1)}}"
    )
    parts = svg_open(HEIGHT, css)
    parts.append(card(0, 0, 860, HEIGHT))
    parts.append(label(40, 52, "OS ÚLTIMOS 12 MESES NO GITHUB"))
    parts.append(
        f'<text class="fade" x="38" y="112" font-family="{SERIF}" font-size="58" fill="{INK}">'
        f'{number(data["total"])} <tspan font-style="italic">contribuições</tspan></text>'
    )

    left, base, area, gap = 40, 286, 130, 9
    width = (520 - gap * (len(months) - 1)) / max(len(months), 1)
    for index, (key, value) in enumerate(months):
        height = max(3, value / peak * area)
        x = left + index * (width + gap)
        is_peak = value == peak and value > 0
        color = PURPLE if is_peak else (INK if value else "#CFCCC2")
        parts.append(
            f'<rect class="b" style="animation-delay:{0.2 + index * 0.06:.2f}s" x="{x:.1f}" '
            f'y="{base - height:.1f}" width="{width:.1f}" height="{height:.1f}" rx="2" fill="{color}"/>'
        )
        if is_peak:
            parts.append(
                f'<text class="fade" style="animation-delay:1s" x="{x + width / 2:.1f}" '
                f'y="{base - height - 8:.1f}" text-anchor="middle" font-family="{MONO}" '
                f'font-size="11" fill="{PURPLE}">{number(value)}</text>'
            )
        parts.append(
            f'<text x="{x + width / 2:.1f}" y="{base + 20}" text-anchor="middle" '
            f'font-family="{MONO}" font-size="10.5" fill="{MUTED}">{MONTHS[int(key[5:]) - 1]}</text>'
        )

    blocks = [
        (
            f'{data["currentStreak"]} <tspan font-style="italic">dias</tspan>',
            f'sequência atual · a maior foi de {data["longestStreak"]}',
        ),
        (
            f'{active} <tspan fill="{MUTED}">/ {len(days)}</tspan>',
            "dias com commit",
        ),
        (number(best), "no dia mais movimentado"),
    ]
    for index, (value, caption) in enumerate(blocks):
        y = 150 + index * 74
        if index:
            parts.append(f'<path d="M600 {y - 40}H820" stroke="{LINE}"/>')
        parts.append(
            f'<text class="fade" style="animation-delay:{0.4 + index * 0.15:.2f}s" x="600" '
            f'y="{y}" font-family="{SERIF}" font-size="38" fill="{INK}">{value}</text>'
        )
        parts.append(
            f'<text x="600" y="{y + 20}" font-family="{SANS}" font-size="12.5" '
            f'fill="{MUTED}">{caption}</text>'
        )
    if not STATIC:
        parts.append(
            f'<circle cx="822" cy="47" r="4" fill="{PURPLE}"><animate attributeName="r" '
            'values="4;7;4" dur="2.4s" repeatCount="indefinite"/><animate attributeName="opacity" '
            'values="1;.35;1" dur="2.4s" repeatCount="indefinite"/></circle>'
        )
    parts.append(shimmer("stats", 0, 0, 860, HEIGHT, 4.2))
    parts.append("</svg>")
    OUTPUT.write_text("\n".join(parts) + "\n")
    print(f"wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
