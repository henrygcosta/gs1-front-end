"""Event type distribution chart renderer."""

from __future__ import annotations

import pandas as pd
import plotly.express as px

from ui.charts.base import render_plotly_panel


def render_event_type_bar(risk_summary: pd.DataFrame, *, key: str) -> None:
	"""Render bar chart by event type and average risk."""
	fig = px.bar(
		risk_summary,
		x="event_type",
		y="avg_risk_score",
		color="avg_risk_score",
		labels={"event_type": "Tipo de evento", "avg_risk_score": "Risco medio"},
	)
	fig.update_layout(margin=dict(l=12, r=12, t=18, b=12), title_text=None)
	render_plotly_panel(title="Risco medio por tipo de evento", fig=fig, key=key, help_text="Comparativo operacional por classe de evento", height=340)
