"""Chart panel wrapper to maintain consistent paddings and headings."""

from __future__ import annotations

import streamlit as st


def render_chart_panel(title: str) -> None:
	"""Open a visual panel with a title for charts.

	Use as a simple contextual wrapper before calling the chart renderer.
	"""
	st.caption(title)
