"""Geospatial scatter chart renderer."""

from __future__ import annotations

import pandas as pd
import plotly.express as px

from ui.charts.base import render_plotly_panel


def render_geo_scatter_map(enriched_events: pd.DataFrame, *, key: str) -> None:
	"""Render geospatial risk distribution using latitude/longitude."""
	fig = px.scatter_map(
		enriched_events,
		lat="latitude",
		lon="longitude",
		color="risk_score",
		hover_name="event_type",
		hover_data={"risk_score": ":.2f", "severity": ":.2f", "confidence": ":.2f"},
		zoom=2,
	)
	fig.update_layout(title_text=None, margin={"l": 0, "r": 0, "t": 8, "b": 40})
	render_plotly_panel(title="Hotspots geograficos de risco", fig=fig, key=key, help_text="Mapa de calor dos eventos mais sensiveis", height=360, footer_gap_px=44)
