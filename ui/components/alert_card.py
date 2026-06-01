"""Alert card component used in lists and dashboards."""

from __future__ import annotations

import streamlit as st

from ui.components.status_badge import badge_html


def render_alert_card(*, title: str, message: str, level: str, source: str | None = None, action_text: str | None = None) -> None:
	"""Render a structured alert card.

	Parameters
	----------
	title:
		Alert headline.
	message:
		Body copy describing the condition.
	level:
		Semantic alert level used for the badge color.
	source:
		Optional source or system label.
	action_text:
		Optional follow-up instruction shown at the end of the card.
	"""
	meta = f"<div class='gs-card-copy'>{source}</div>" if source else ""
	action = f"<div class='gs-card-copy' style='margin-top: 0.35rem;'><strong>Próxima ação:</strong> {action_text}</div>" if action_text else ""
	st.markdown(
		f"""
		<div class="gs-card gs-alert-card">
			<div style="display:flex; align-items:flex-start; justify-content:space-between; gap:1rem;">
				<div style="min-width:0; flex:1 1 auto;">
					<div class='gs-card-title'>{title}</div>
					<div class='gs-card-copy'>{message}</div>
					{meta}
					{action}
				</div>
				<div style="flex:0 0 auto;">{badge_html(level.title(), level)}</div>
			</div>
		</div>
		""",
		unsafe_allow_html=True,
	)
