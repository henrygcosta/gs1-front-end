"""Reusable error state component."""

from __future__ import annotations

import streamlit as st


def render_error_state(title: str, description: str, *, details: str | None = None) -> None:
	"""Render a standardized error state message.

	Parameters
	----------
	title:
		Error headline.
	description:
		Short explanation for the user.
	details:
		Optional technical details shown in a smaller caption.
	"""
	st.markdown(
		f"""
		<div class="gs-card" style="border-left: 4px solid #B42318;">
			<div class="gs-card-title">{title}</div>
			<div class="gs-card-copy">{description}</div>
		</div>
		""",
		unsafe_allow_html=True,
	)
	if details:
		st.caption(details)
