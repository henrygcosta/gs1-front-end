"""Shared Plotly chart rendering helpers."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from state.selectors import get_preferences_state


def render_plotly_panel(*, title: str, fig: go.Figure, key: str, help_text: str | None = None, height: int | None = None, footer_gap_px: int = 16) -> None:
	"""Render a Plotly figure inside a consistent visual container."""
	preferences = get_preferences_state()
	is_dark = preferences.theme_mode.lower() == "dark"
	grid_color = "rgba(148, 163, 184, 0.16)" if is_dark else "rgba(148, 163, 184, 0.18)"
	text_color = "#E5E7EB" if is_dark else "#0F172A"
	legend_bg = "rgba(15, 23, 42, 0.78)" if is_dark else "rgba(255, 255, 255, 0.82)"
	legend_border = "rgba(148, 163, 184, 0.24)" if is_dark else "rgba(226, 232, 240, 0.92)"
	template = "plotly_dark" if is_dark else "plotly_white"
	fig.update_layout(
		template=template,
		margin={"l": 12, "r": 12, "t": 44, "b": 12},
		autosize=True,
		paper_bgcolor="rgba(0,0,0,0)",
		plot_bgcolor="rgba(0,0,0,0)",
		font={"color": text_color, "family": "Manrope, Aptos, Segoe UI, sans-serif"},
		title={"text": "", "font": {"color": text_color}},
		legend={
			"font": {"color": text_color},
			"title_font": {"color": text_color},
			"bgcolor": legend_bg,
			"bordercolor": legend_border,
			"borderwidth": 1,
			"orientation": "h",
			"itemclick": "toggle",
			"itemdoubleclick": "toggleothers",
		},
		legend_font_color=text_color,
		legend_title_font_color=text_color,
	)
	fig.layout.title = None
	fig.update_xaxes(showgrid=True, gridcolor=grid_color, zeroline=False)
	fig.update_yaxes(showgrid=True, gridcolor=grid_color, zeroline=False)
	st.markdown(f"**{title}**")
	if help_text:
		st.caption(help_text)
	if height is not None:
		fig.update_layout(height=height)
	st.plotly_chart(fig, use_container_width=True, key=key, config={"responsive": True, "displaylogo": False})
	st.markdown(f"<div style='height: {footer_gap_px}px;'></div>", unsafe_allow_html=True)
