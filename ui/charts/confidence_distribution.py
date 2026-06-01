"""Confidence distribution chart renderer."""

from __future__ import annotations

import pandas as pd
import plotly.express as px

from ui.charts.base import render_plotly_panel


def render_confidence_distribution(enriched_events: pd.DataFrame, *, key: str) -> None:
	"""Render confidence histogram for anomaly interpretation."""
	fig = px.histogram(
		enriched_events,
		x="confidence",
		nbins=20,
		labels={"confidence": "Confianca"},
	)
	fig.update_layout(margin=dict(l=12, r=12, t=18, b=12), title_text=None)
	render_plotly_panel(title="Distribuicao de confianca dos eventos", fig=fig, key=key, help_text="Leitura das incertezas do recorte atual", height=340)
