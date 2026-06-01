"""Sidebar rendering and filter interactions."""

from __future__ import annotations

import streamlit as st

from state.actions import (
	invalidate_pipeline_run,
	set_filter_threshold,
	set_selected_date_range,
	set_selected_event_types,
	set_selected_period_days,
	set_selected_region,
	set_selected_risk_level,
	set_theme_mode,
)
from state.selectors import get_preferences_state
from state.view_model import build_dashboard_filter_view_model
from ui.components.filters_panel import render_filters_panel


def _sync_theme_mode() -> None:
	"""Persist the selected theme mode to session state."""
	mode = str(st.session_state.get("sidebar_theme_mode", "system"))
	set_theme_mode(mode)

def render_sidebar() -> None:
	"""Render sidebar filter controls in a form to reduce rerenders."""
	vm = build_dashboard_filter_view_model()

	with st.sidebar:
		preferences = get_preferences_state()
		st.markdown("## Preferências")
		theme_options = ["system", "light", "dark"]
		theme_index = theme_options.index(preferences.theme_mode) if preferences.theme_mode in theme_options else 0
		st.radio(
			"Tema",
			options=theme_options,
			index=theme_index,
			key="sidebar_theme_mode",
			on_change=_sync_theme_mode,
		)

		def apply_filters(
			region: str,
			event_types: list[str],
			period_days: int,
			date_range: tuple[object, object] | None,
			risk_level: str,
			threshold: float,
		) -> None:
			"""Apply submitted filter values to session state."""
			set_selected_region(region)
			set_selected_event_types(event_types)
			set_selected_period_days(period_days)
			if isinstance(date_range, tuple) and len(date_range) == 2:
				start_date = date_range[0].isoformat() if date_range[0] else None
				end_date = date_range[1].isoformat() if date_range[1] else None
				set_selected_date_range(start_date, end_date)
			set_selected_risk_level(risk_level)
			set_filter_threshold(threshold)

		render_filters_panel(
			view_model=vm,
			on_submit=apply_filters,
		)

		from utils.config import get_settings

		if get_settings().enable_cache_invalidation_button:
			if st.button("Invalidar caches e recarregar"):
				invalidate_pipeline_run()
