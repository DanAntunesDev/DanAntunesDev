import json
import os
from datetime import date
from pathlib import Path

from profile_config import HEATMAP_LEVELS, PALETTE

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "contrib-heatmap.svg"

CELL = 12
GAP = 3
STEP = CELL + GAP
LEFT = 34
TOP = 44
STATIC = os.environ.get("STATIC") == "1"
MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def weeks_of(days):
    weeks, current = [], []
    for day in days:
        weekday = (date.fromisoformat(day["date"]).weekday() + 1) % 7
        if weekday == 0 and current:
            weeks.append(current)
            current = []
        current.append((weekday, day))
    if current:
        weeks.append(current)
    return weeks


def main():
    data = json.loads(SOURCE.read_text())
    weeks = weeks_of(data["days"])
    width = LEFT + len(weeks) * STEP + 20
    height = TOP + 7 * STEP + 58
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        "<style>"
        ".c{opacity:%s;transform-box:fill-box;transform-origin:center;"
        "animation:in .45s cubic-bezier(.2,.8,.2,1) forwards}"
        "@keyframes in{from{opacity:0;transform:translateY(-6px) scale(.6)}"
        "to{opacity:1;transform:none}}"
        ".t{fill:%s;font-size:11px}.h{fill:%s;font-size:13px;font-weight:600}"
        "</style>" % ("1" if STATIC else "0", PALETTE["muted"], PALETTE["text"]),
        f'<rect width="{width}" height="{height}" rx="10" fill="{PALETTE["bg"]}" stroke="{PALETTE["border"]}"/>',
        f'<text class="h" x="{LEFT}" y="24">contribuições no último ano</text>',
    ]

    last_month = None
    for index, week in enumerate(weeks):
        month = int(week[0][1]["date"][5:7])
        if month != last_month:
            if index < len(weeks) - 2:
                parts.append(
                    f'<text class="t" x="{LEFT + index * STEP}" y="{TOP - 6}">{MONTHS[month - 1]}</text>'
                )
            last_month = month
        for weekday, day in week:
            delay = (index + weekday) * 0.012
            color = HEATMAP_LEVELS[min(day["level"], len(HEATMAP_LEVELS) - 1)]
            if day["count"] >= 15:
                color = HEATMAP_LEVELS[-1]
            parts.append(
                f'<rect class="c" style="animation-delay:{delay:.3f}s" x="{LEFT + index * STEP}" '
                f'y="{TOP + weekday * STEP}" width="{CELL}" height="{CELL}" rx="3" fill="{color}">'
                f'<title>{day["date"]}: {day["count"]}</title></rect>'
            )

    for weekday, label in ((1, "seg"), (3, "qua"), (5, "sex")):
        parts.append(f'<text class="t" x="6" y="{TOP + weekday * STEP + 10}">{label}</text>')

    footer_y = TOP + 7 * STEP + 26
    best = data.get("bestDay") or {"count": 0}
    stats = (
        f'{data["total"]} contribuições · sequência atual {data["currentStreak"]} dias · '
        f'maior sequência {data["longestStreak"]} dias · melhor dia {best["count"]}'
    )
    parts.append(f'<text class="t" x="{LEFT}" y="{footer_y}">{stats}</text>')

    legend_x = width - 20 - len(HEATMAP_LEVELS) * STEP - 70
    parts.append(f'<text class="t" x="{legend_x}" y="{footer_y + 20}">menos</text>')
    for index, color in enumerate(HEATMAP_LEVELS):
        parts.append(
            f'<rect x="{legend_x + 40 + index * STEP}" y="{footer_y + 10}" width="{CELL}" '
            f'height="{CELL}" rx="3" fill="{color}"/>'
        )
    parts.append(
        f'<text class="t" x="{legend_x + 44 + len(HEATMAP_LEVELS) * STEP}" y="{footer_y + 20}">mais</text>'
    )
    parts.append("</svg>")
    OUTPUT.write_text("\n".join(parts) + "\n")
    print(f"wrote {OUTPUT.name} ({len(weeks)} weeks)")


if __name__ == "__main__":
    main()
