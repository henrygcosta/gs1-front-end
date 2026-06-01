"""Reusable loading block component."""

from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator

import streamlit as st


@contextmanager
def loading_block(label: str) -> Iterator[None]:
	"""Wrap expensive UI sections with a standardized spinner."""
	with st.spinner(label):
		yield


def render_loading_placeholder(label: str, *, lines: int = 3) -> None:
	"""Render a lightweight loading placeholder inside a card."""
	rows = "".join("<div style='height: 0.8rem; border-radius: 999px; background: var(--gs-placeholder); margin: 0.55rem 0;'></div>" for _ in range(max(1, lines)))
	st.markdown(
		f"""
		<div class="gs-card">
			<div class='gs-card-title'>{label}</div>
			{rows}
		</div>
		""",
		unsafe_allow_html=True,
	)
