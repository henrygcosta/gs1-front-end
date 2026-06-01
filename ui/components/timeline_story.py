"""Timeline storytelling component to highlight important events."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ui.components.status_badge import badge_html


def render_timeline_story(enriched_events: pd.DataFrame, limit: int = 5) -> None:
	"""Show a short timeline of most significant events for storytelling."""
	if enriched_events.empty:
		st.info("Sem eventos para contar uma historia.")
		return

	top = enriched_events.sort_values("risk_score", ascending=False).head(limit)
	for _, row in top.iterrows():
		level = str(row.get("alert_level", "info"))
		st.markdown(
			f"""
			<div class="gs-card">
				<div style="display:flex; align-items:flex-start; justify-content:space-between; gap:1rem;">
					<div style="min-width:0; flex:1 1 auto;">
						<div class='gs-card-title'>{row['event_type']} — {row['region']}</div>
						<div class='gs-card-copy'>{row['date']} | risco {row['risk_score']:.2f}</div>
					</div>
					<div style="flex:0 0 auto;">{badge_html(level, level)}</div>
				</div>
			</div>
			""",
			unsafe_allow_html=True,
		)
