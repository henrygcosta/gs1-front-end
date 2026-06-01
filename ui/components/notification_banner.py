"""Notification banner component."""

from __future__ import annotations

import streamlit as st

from ui.theme.semantic_colors import STATE_COLOR_MAP


def render_notification_banner(title: str, message: str, *, kind: str = "info", action_label: str | None = None) -> bool:
	"""Render a reusable notification banner.

	Parameters
	----------
	title:
		Short banner headline.
	message:
		Supporting explanation.
	kind:
		Semantic state key controlling the accent color.
	action_label:
		Optional CTA rendered as a button inside the banner.

	Returns
	-------
	bool
		True when the optional action button is clicked.
	"""
	accent = STATE_COLOR_MAP.get(kind, STATE_COLOR_MAP["info"])
	st.markdown(
		f"""
		<div class="gs-banner" style="--gs-banner-accent: {accent};">
			<div class="gs-banner-title">{title}</div>
			<div class="gs-banner-message">{message}</div>
		</div>
		""",
		unsafe_allow_html=True,
	)
	if action_label:
		return st.button(action_label, use_container_width=False)
	return False
