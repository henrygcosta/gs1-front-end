"""Application footer components."""

from __future__ import annotations

import streamlit as st


def render_footer(*, left_text: str, right_text: str) -> None:
	"""Render a minimal footer strip.

	Parameters
	----------
	left_text:
		Primary footer label.
	right_text:
		Secondary footer label shown at the right edge.
	"""
	st.markdown(
		f"""
		<div class="gs-footer">
			<span>{left_text}</span>
			<span>{right_text}</span>
		</div>
		""",
		unsafe_allow_html=True,
	)
