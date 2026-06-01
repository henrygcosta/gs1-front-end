"""Design tokens for a consistent visual identity."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ColorTokens:
	"""Core color tokens used in the custom design system."""

	brand_primary: str = "#0F4C5C"
	brand_secondary: str = "#2E7D32"
	background: str = "#F6F7F9"
	surface: str = "#FFFFFF"
	text_primary: str = "#0F172A"
	text_secondary: str = "#475569"
	warning: str = "#D97706"
	danger: str = "#B42318"


@dataclass(frozen=True, slots=True)
class SpacingTokens:
	"""Spacing scale for layout rhythm."""

	xs: int = 4
	sm: int = 8
	md: int = 16
	lg: int = 24
	xl: int = 32


COLORS = ColorTokens()
SPACING = SpacingTokens()
