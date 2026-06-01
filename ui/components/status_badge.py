"""Semantic status badge component."""

from __future__ import annotations

import streamlit as st

from ui.theme.semantic_colors import RISK_COLOR_MAP, STATE_COLOR_MAP


def _badge_color(kind: str) -> str:
	"""Return a semantic color for the requested badge kind."""
	palette = {**RISK_COLOR_MAP, **STATE_COLOR_MAP}
	return palette.get(kind.lower(), palette.get(kind.title(), STATE_COLOR_MAP["info"]))


def render_status_badge(label: str, kind: str = "info") -> None:
	"""Render a compact semantic badge.

	Parameters
	----------
	label:
		Text shown inside the badge.
	kind:
		Semantic color key such as ``success`` or ``critical``.
	"""
	color = _badge_color(kind)
	st.markdown(
		f'<span class="gs-badge" style="--gs-badge-color: {color};">{label}</span>',
		unsafe_allow_html=True,
	)


def badge_html(label: str, kind: str = "info") -> str:
	"""Return HTML for a semantic badge without rendering it."""
	color = _badge_color(kind)
	return f'<span class="gs-badge" style="--gs-badge-color: {color};">{label}</span>'
