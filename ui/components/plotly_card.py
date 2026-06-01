"""Generic Plotly card wrapper."""

from __future__ import annotations

import plotly.graph_objects as go

from ui.charts.base import render_plotly_panel


def render_plotly_card(*, title: str, fig: go.Figure, key: str, help_text: str | None = None, height: int | None = None) -> None:
	"""Render a Plotly figure using the shared application card style."""
	render_plotly_panel(title=title, fig=fig, key=key, help_text=help_text, height=height)
