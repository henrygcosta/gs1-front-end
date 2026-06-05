"""Semantic color helpers for risk levels and status states."""

from __future__ import annotations

RISK_COLOR_MAP: dict[str, str] = {
	"info": "#0F4C5C",
	"neutral": "#475569",
	"low": "#2E7D32",
	"baixa": "#2E7D32",
	"medium": "#D97706",
	"moderado": "#D97706",
	"high": "#C2410C",
	"alto": "#C2410C",
	"critical": "#B42318",
	"critico": "#B42318",
}

STATE_COLOR_MAP: dict[str, str] = {
	"success": "#2E7D32",
	"info": "#0F4C5C",
	"warning": "#D97706",
	"error": "#B42318",
	"approved": "#2E7D32",
	"review": "#D97706",
	"dismissed": "#B42318",
}
