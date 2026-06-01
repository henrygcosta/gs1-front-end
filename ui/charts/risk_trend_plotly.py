"""Plotly risk trend chart renderer."""

from __future__ import annotations

import pandas as pd
import plotly.express as px

from ui.charts.base import render_plotly_panel


def render_risk_trend(enriched_events: pd.DataFrame, *, key: str) -> None:
	"""Render time-series risk trend with hover and zoom support."""
	trend = (
		enriched_events.groupby("date", as_index=False)
		.agg(avg_risk_score=("risk_score", "mean"))
		.sort_values("date")
	)

	fig = px.line(
		trend,
		x="date",
		y="avg_risk_score",
		markers=True,
		labels={"date": "Data", "avg_risk_score": "Risco medio"},
	)
	fig.update_layout(margin=dict(l=12, r=12, t=18, b=12), title_text=None)
	render_plotly_panel(title="Evolucao do risco medio", fig=fig, key=key, help_text="Serie temporal do risco medio consolidado", height=340)
