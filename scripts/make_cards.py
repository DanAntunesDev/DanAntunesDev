from pathlib import Path

from design import BLUE, INK, MONO, MUTED, RED, SANS, SERIF, YELLOW, card, label, svg_open

ROOT = Path(__file__).resolve().parent.parent

HIGHLIGHTS = [
    ("BACKEND", "APIs multi-tenant", ["NestJS, Prisma e PostgreSQL com", "isolamento por cliente e 2FA."], BLUE, "#FFFFFF"),
    ("AUTOMAÇÃO", "Agentes de IA", ["Fluxos n8n e IA na API oficial", "da Meta para clínicas e hospitais."], RED, "#FFFFFF"),
    ("PRODUTO", "Chegaí", ["SaaS de agendamento e gestão", "para barbearias. Em construção."], YELLOW, INK),
]

PROJECTS = [
    ("Chegaí", ["Agendamento, WhatsApp oficial e", "white label para barbearias."], "TypeScript · NestJS", BLUE),
    ("geek-panel", ["Painel em pixel art para o", "GeekMagic SmallTV."], "TypeScript", RED),
    ("pet-scheduler-api", ["API de agendamento para", "serviços de pet shop."], "Node.js", YELLOW),
]


def highlights():
    height, width, gap = 212, (860 - 32) / 3, 16
    parts = svg_open(height)
    for index, (tag, title, body, fill, ink) in enumerate(HIGHLIGHTS):
        x = index * (width + gap)
        parts.append(f'<g class="fade" style="animation-delay:{0.1 + index * 0.15:.2f}s">')
        parts.append(card(x, 0, width, height, fill))
        parts.append(label(x + 24, 40, tag, fill=ink))
        parts.append(
            f'<text x="{x + width - 24}" y="41" text-anchor="end" font-family="{SANS}" '
            f'font-size="15" fill="{ink}">↗</text>'
        )
        parts.append(
            f'<text x="{x + 22}" y="112" font-family="{SERIF}" font-style="italic" '
            f'font-size="36" fill="{ink}">{title}</text>'
        )
        for line_index, line in enumerate(body):
            parts.append(
                f'<text x="{x + 24}" y="{152 + line_index * 20}" font-family="{SANS}" '
                f'font-size="13" fill="{ink}" fill-opacity=".92">{line}</text>'
            )
        parts.append("</g>")
    parts.append("</svg>")
    (ROOT / "highlights.svg").write_text("\n".join(parts) + "\n")


def projects():
    height, width, gap, top = 236, (860 - 32) / 3, 16, 64
    parts = svg_open(height)
    parts.append(
        f'<text x="2" y="40" font-family="{SERIF}" font-size="36" fill="#E6E4DC">O que estou '
        f'<tspan font-style="italic">codando</tspan></text>'
    )
    for index, (name, body, stack, color) in enumerate(PROJECTS):
        x = index * (width + gap)
        parts.append(f'<g class="fade" style="animation-delay:{0.2 + index * 0.15:.2f}s">')
        parts.append(card(x, top, width, height - top, "#FFFFFF"))
        parts.append(f'<rect x="{x + 24}" y="{top + 32}" width="8" height="8" rx="1" fill="{color}"/>')
        parts.append(
            f'<text x="{x + 40}" y="{top + 41}" font-family="{SANS}" font-size="17" '
            f'font-weight="600" fill="{INK}">{name}</text>'
        )
        for line_index, line in enumerate(body):
            parts.append(
                f'<text x="{x + 24}" y="{top + 76 + line_index * 21}" font-family="{SANS}" '
                f'font-size="13" fill="#3A3935">{line}</text>'
            )
        parts.append(
            f'<text x="{x + 24}" y="{height - 26}" font-family="{MONO}" font-size="11" '
            f'fill="{MUTED}">{stack}</text>'
        )
        parts.append("</g>")
    parts.append("</svg>")
    (ROOT / "projects.svg").write_text("\n".join(parts) + "\n")


if __name__ == "__main__":
    highlights()
    projects()
    print("wrote highlights.svg and projects.svg")
