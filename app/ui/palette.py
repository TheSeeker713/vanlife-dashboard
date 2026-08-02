"""Named color constants for the light theme.

Kept in sync by hand with theme.qss (Qt's QSS dialect doesn't support
CSS custom properties reliably across all widget types in this Qt version,
so the same hex values are duplicated in both places on purpose). Anything
drawn in code rather than styled via QSS (the marker timeline ticks, canvas
card accents) should pull from here instead of hardcoding a hex value.
"""
from __future__ import annotations

# Base surfaces
BACKGROUND = "#f5f4f2"
PANEL = "#ffffff"
BORDER = "#d8d5d0"
TEXT = "#232220"
TEXT_MUTED = "#6b6864"

# Primary accent (Confirm / Organize / active-state actions)
ACCENT = "#3d6b52"
ACCENT_HOVER = "#325a45"

# Tag colors, meaning-specific, never used purely for decoration
TAG_KEEPER = "#3d8b52"
TAG_BROLL = "#3b6fa0"
TAG_REJECT = "#b0503f"
TAG_AUDIO_ISSUE = "#c08a2e"
TAG_NEUTRAL = "#8a8680"

# Resource watchdog tiers
STATUS_OK = "#3d8b52"
STATUS_WARNING = "#c08a2e"
STATUS_CRITICAL = "#b0503f"
