import json
from datetime import date
from pathlib import Path

from design import HEAT, PURPLE, STATIC, shimmer, INK, MONO, MUTED, SERIF, card, label, svg_open

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "heatmap.svg"
HEIGHT = 256
CELL = 12
STEP = 14.6
LEFT = 42
TOP = 92
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


def wave(column, row):
    if STATIC:
        return ""
    begin = 4.0 + (column + row) * 0.035
    return (
        '<animate attributeName="fill-opacity" values="1;0.25;1;1" keyTimes="0;0.03;0.07;1" '
        f'dur="9s" begin="{begin:.3f}s" repeatCount="indefinite"/>'
    )


def level_of(day):
    if day["count"] >= 15:
        return len(HEAT) - 1
    return min(day["level"], len(HEAT) - 2)


def main():
    data = json.loads(SOURCE.read_text())
    weeks = weeks_of(data["days"])[-53:]
    css = (
        ".c{opacity:0;transform-box:fill-box;transform-origin:center;"
        "animation:pop .5s cubic-bezier(.2,.8,.2,1) forwards}"
        "@keyframes pop{from{opacity:0;transform:translateY(-8px) scale(.5)}to{opacity:1;transform:none}}"
    )
    parts = svg_open(HEIGHT, css, sans=False)
    parts.append(card(0, 0, 860, HEIGHT))
    parts.append(
        f'<text x="40" y="60" font-family="{SERIF}" font-size="36" fill="{INK}">Todo dia, '
        f'<tspan font-style="italic" fill="{PURPLE}">em roxo</tspan></text>'
    )
    parts.append(label(820, 56, "ATUALIZADO DIARIAMENTE", anchor="end"))

    last_month = None
    for index, week in enumerate(weeks):
        x = LEFT + index * STEP
        month = int(week[-1][1]["date"][5:7])
        if month != last_month and 0 < index < len(weeks) - 1:
            parts.append(
                f'<text x="{x:.1f}" y="{TOP + 7 * STEP + 18:.1f}" font-family="{MONO}" '
                f'font-size="10.5" fill="{MUTED}">{MONTHS[month - 1]}</text>'
            )
        last_month = month
        for weekday, day in week:
            delay = (index * 0.9 + weekday * 2) * 0.012
            parts.append(
                f'<rect class="c" style="animation-delay:{delay:.3f}s" x="{x:.1f}" '
                f'y="{TOP + weekday * STEP:.1f}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{HEAT[level_of(day)]}">{wave(index, weekday)}'
                f'<title>{day["date"]}: {day["count"]}</title></rect>'
            )

    legend_y = TOP + 7 * STEP + 42
    legend_x = 820 - len(HEAT) * 14 - 34
    parts.append(
        f'<text x="{legend_x - 8}" y="{legend_y}" font-family="{MONO}" font-size="10.5" '
        f'fill="{MUTED}" text-anchor="end">menos</text>'
    )
    for index, color in enumerate(HEAT):
        parts.append(
            f'<rect x="{legend_x + index * 14}" y="{legend_y - 10}" width="11" height="11" '
            f'rx="2" fill="{color}"/>'
        )
    parts.append(
        f'<text x="{legend_x + len(HEAT) * 14 + 4}" y="{legend_y}" font-family="{MONO}" '
        f'font-size="10.5" fill="{MUTED}">mais</text>'
    )
    parts.append(shimmer("heat", 0, 0, 860, HEIGHT, 3.6))
    parts.append("</svg>")
    OUTPUT.write_text("\n".join(parts) + "\n")
    print(f"wrote {OUTPUT.name} ({len(weeks)} weeks)")


if __name__ == "__main__":
    main()
