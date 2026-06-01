"""Map panel wrapper for unified map rendering."""

from __future__ import annotations

import streamlit as st


def render_map_panel(title: str) -> None:
	"""Render a titled map panel container."""
	st.caption(title)
