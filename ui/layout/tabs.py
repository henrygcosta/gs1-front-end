"""Tabs composition helpers for application navigation."""

from __future__ import annotations

import streamlit as st

from ui.copy.labels import TAB_FEEDBACK, TAB_HOTSPOTS, TAB_OVERVIEW, TAB_ANOMALIES


def render_main_tabs() -> tuple[st.delta_generator.DeltaGenerator, ...]:
	"""Render main application tabs and return tab containers."""
	return st.tabs([TAB_OVERVIEW, TAB_HOTSPOTS, TAB_ANOMALIES, TAB_FEEDBACK])
