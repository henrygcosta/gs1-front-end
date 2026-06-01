"""Small KPI card component."""

from __future__ import annotations

import streamlit as st

from ui.components.status_badge import badge_html


def render_kpi(title: str, value: str, delta: str | None = None) -> None:
	"""Render a compact KPI card with a title, value and optional delta."""
	badge = f"<div style='margin-top: 0.45rem;'>{badge_html(delta, 'info')}</div>" if delta else ""
	st.markdown(
		f"""
		<div class="gs-card">
			<div class="gs-card-copy">{title}</div>
			<div class="gs-title" style="font-size: 1.55rem; margin-bottom: 0.1rem;">{value}</div>
			{badge}
		</div>
		""",
		unsafe_allow_html=True,
	)

