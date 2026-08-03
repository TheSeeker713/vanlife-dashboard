"""Named color tokens for both themes.

Kept in sync by hand with dark_theme.qss and light_theme.qss (Qt's QSS
dialect doesn't support CSS custom properties reliably across all widget
types in this Qt version, so the same hex values are duplicated in all
three places on purpose). Anything drawn in code rather than styled via
QSS (marker timeline ticks, canvas card accents, resource-monitor meters)
should pull from here instead of hardcoding a hex value, and should read
the active theme rather than assuming one.
"""
from __future__ import annotations

from typing import TypedDict


class Palette(TypedDict):
    bg: str
    panel: str
    panel_2: str
    border: str
    text: str
    text_muted: str
    accent: str
    accent_ink: str
    keeper: str
    broll: str
    reject: str
    warn: str


DARK: Palette = {
    "bg": "#131412",
    "panel": "#1b1c19",
    "panel_2": "#232420",
    "border": "#35362f",
    "text": "#ece9e2",
    "text_muted": "#8f8a7d",
    "accent": "#d9843c",
    "accent_ink": "#17130a",
    "keeper": "#4f9e6e",
    "broll": "#4a80b0",
    "reject": "#c1503f",
    "warn": "#c9a227",
}

LIGHT: Palette = {
    "bg": "#f4f3f0",
    "panel": "#ffffff",
    "panel_2": "#ebe9e5",
    "border": "#d9d6d0",
    "text": "#232019",
    "text_muted": "#746e63",
    "accent": "#c46a2b",
    "accent_ink": "#ffffff",
    "keeper": "#3f7d52",
    "broll": "#3b6f9e",
    "reject": "#b0503f",
    "warn": "#a9791f",
}

# Tag key -> palette key, used wherever a marker/quick-tag color is drawn.
TAG_PALETTE_KEY = {
    "keeper": "keeper",
    "broll": "broll",
    "reject": "reject",
    "audio_issue": "warn",
}


def palette_for(theme: str) -> Palette:
    return DARK if theme == "dark" else LIGHT
