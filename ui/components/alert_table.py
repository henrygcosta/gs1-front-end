"""Alert table component for list and action controls."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ui.components.alert_card import render_alert_card
from ui.components.empty_state import render_empty_state


def render_alert_table(df: pd.DataFrame) -> None:
	"""Render a simple alert table with key columns and action placeholders."""
	if df.empty:
		render_empty_state("Nenhum alerta prioritario", "Ajuste os filtros para ampliar o recorte operacional.")
		return

	for _, row in df.head(6).iterrows():
		render_alert_card(
			title=f"{row['event_type']} em {row.get('region', 'N/A')}",
			message=f"Risco {float(row['risk_score']):.2f} | confianca {float(row.get('confidence', 0.0)):.2f} | data {row.get('date', '')}",
			level=str(row.get("alert_level", "info")),
			source=str(row.get("source", "operacional")),
			action_text=str(row.get("recommended_action", "")),
		)
