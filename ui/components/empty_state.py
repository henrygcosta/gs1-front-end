"""Reusable empty state component."""

from __future__ import annotations

import streamlit as st


def render_empty_state(title: str, description: str, *, action_label: str | None = None) -> bool:
	"""Render a standardized empty data state message.

	Parameters
	----------
	title:
		Empty state headline.
	description:
		Supporting copy explaining the missing content.
	action_label:
		Optional button label returned as a boolean click state.
	"""
	st.markdown(
		f"""
		<div class="gs-card">
			<div class="gs-card-title">{title}</div>
			<div class="gs-card-copy">{description}</div>
		</div>
		""",
		unsafe_allow_html=True,
	)
	if action_label:
		return st.button(action_label)
	return False
