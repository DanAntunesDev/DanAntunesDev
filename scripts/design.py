import base64
import os
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"

STATIC = os.environ.get("STATIC") == "1"
WIDTH = 860
PAPER = "#F3F2EC"
INK = "#141414"
MUTED = "#6E6C66"
LINE = "#DDDBD2"
BLUE = "#2F55F5"
RED = "#EF3B2D"
YELLOW = "#FFC21A"
PURPLE = "#7C3AED"
HEAT = ["#E3E1D9", "#DDD0FB", "#C0A6F7", "#9F75F0", "#7C3AED", "#5B21B6"]

SERIF = "'Serif','Instrument Serif',Georgia,serif"
MONO = "'Mono','JetBrains Mono',ui-monospace,Menlo,monospace"
SANS = "'Sans',Inter,-apple-system,'Segoe UI',sans-serif"


def _font(family, file, style="normal"):
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return (
        f"@font-face{{font-family:'{family}';font-style:{style};font-weight:400;"
        f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
    )


@lru_cache
def font_css(serif=True, mono=True, sans=True):
    faces = []
    if serif:
        faces.append(_font("Serif", "instrument-serif-latin-400-normal.woff2"))
        faces.append(_font("Serif", "instrument-serif-latin-400-italic.woff2", "italic"))
    if mono:
        faces.append(_font("Mono", "jetbrains-mono-latin-500-normal.woff2"))
    if sans:
        faces.append(_font("Sans", "inter-latin-400-normal.woff2"))
    return "".join(faces)


STILL = "*{animation:none!important;opacity:1!important;transform:none!important}"


def svg_open(height, css="", serif=True, mono=True, sans=True, width=WIDTH):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f"<style>{font_css(serif, mono, sans)}"
        ".fade{opacity:0;animation:fade .7s ease-out forwards}"
        "@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}"
        f"{css}{STILL if STATIC else ''}</style>",
    ]


def card(x, y, width, height, fill=PAPER):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18" fill="{fill}"/>'


def label(x, y, text, fill=MUTED, size=11, anchor="start", extra=""):
    return (
        f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" letter-spacing="1.8" '
        f'fill="{fill}" text-anchor="{anchor}" {extra}>{text}</text>'
    )


def shimmer(key, x, y, width, height, begin, period=7.0, color="#FFFFFF", strength=0.55):
    if STATIC:
        return ""
    band = width * 0.45
    sweep = 1.1 / period
    return (
        f'<defs><clipPath id="clip-{key}"><rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18"/>'
        f'</clipPath><linearGradient id="glow-{key}" x1="0" x2="1" y1="0" y2="0">'
        f'<stop offset="0" stop-color="{color}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{color}" stop-opacity="{strength}"/>'
        f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
        f'<g clip-path="url(#clip-{key})"><rect y="{y}" width="{band:.0f}" height="{height}" '
        f'fill="url(#glow-{key})" transform="skewX(-18)">'
        f'<animate attributeName="x" values="{x - band * 1.6:.0f};{x + width + band:.0f};{x + width + band:.0f}" '
        f'keyTimes="0;{sweep:.3f};1" dur="{period}s" begin="{begin}s" repeatCount="indefinite"/>'
        "</rect></g>"
    )


def blink(x, y, width, height, fill, begin=1.2):
    if STATIC:
        return ""
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{fill}" opacity="0">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" '
        f'begin="{begin}s" repeatCount="indefinite"/></rect>'
    )
