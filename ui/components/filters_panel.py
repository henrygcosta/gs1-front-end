"""Reusable filters panel component."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, timedelta

import streamlit as st

from state.view_model import DashboardFilterViewModel


FilterSubmitCallback = Callable[[str, list[str], int, tuple[object, object] | None, str, float], None]


EVENT_TYPE_OPTIONS = ["Flood", "Storm", "Heatwave", "Landslide", "Queimada", "Qualidade do Ar"]
EVENT_TYPE_ALIASES = {
	"Fire": "Queimada",
	"AirQuality": "Qualidade do Ar",
}


def _display_event_types(event_types: list[str]) -> list[str]:
	"""Translate legacy event labels to the current UI labels."""
	return [EVENT_TYPE_ALIASES.get(event_type, event_type) for event_type in event_types]


def render_filters_panel(*, view_model: DashboardFilterViewModel, on_submit: FilterSubmitCallback) -> None:
	"""Render the operational filters panel.

	Parameters
	----------
	view_model:
		Current filter snapshot used to seed the widgets.
	on_submit:
		Callback invoked with the submitted filter values.
	"""
	st.markdown("## Filtros Analiticos")
	default_start = date.fromisoformat(view_model.date_start) if view_model.date_start else date.today() - timedelta(days=view_model.period_days)
	default_end = date.fromisoformat(view_model.date_end) if view_model.date_end else date.today()
	region_options = ["Global", "Brazil", "South America"]
	region_index = region_options.index(view_model.region) if view_model.region in region_options else 0
	risk_options = ["all", "observacao", "moderado", "alto", "critico"]
	risk_index = risk_options.index(view_model.risk_level) if view_model.risk_level in risk_options else 0
	def _emit_filters() -> None:
		region = str(st.session_state.get("filters_region", view_model.region))
		event_types = list(st.session_state.get("filters_event_types", view_model.event_types))
		period_days = int(st.session_state.get("filters_period_days", view_model.period_days))
		date_range = st.session_state.get("filters_date_range")
		risk_level = str(st.session_state.get("filters_risk_level", view_model.risk_level))
		threshold = float(st.session_state.get("filters_threshold", view_model.threshold))
		on_submit(region, event_types, period_days, date_range, risk_level, threshold)

	st.radio("Regiao", options=region_options, index=region_index, key="filters_region", on_change=_emit_filters)
	st.multiselect(
		"Tipos de evento",
		options=EVENT_TYPE_OPTIONS,
		default=_display_event_types(view_model.event_types),
		key="filters_event_types",
		on_change=_emit_filters,
	)
	st.slider("Periodo (dias)", min_value=7, max_value=180, value=view_model.period_days, key="filters_period_days", on_change=_emit_filters)
	st.date_input("Janela de datas", value=(default_start, default_end), format="DD-MM-YYYY", key="filters_date_range", on_change=_emit_filters)
	st.radio("Nivel de risco", options=risk_options, index=risk_index, key="filters_risk_level", on_change=_emit_filters)
	st.slider("Threshold principal", min_value=0.0, max_value=1.0, value=view_model.threshold, step=0.05, key="filters_threshold", on_change=_emit_filters)
