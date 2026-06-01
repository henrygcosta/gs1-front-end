"""Anomalies inspection page."""

from __future__ import annotations

import streamlit as st

from ui.components.notification_banner import render_notification_banner
from ui.charts.confidence_distribution import render_confidence_distribution
from ui.charts import render_operational_indicators, render_risk_distribution, render_temporal_disaster_evolution
from state.view_model import build_dashboard_filter_view_model
from ui.pages.context_loader import load_visible_operational_context


def render_anomalies_page() -> None:
	vm = build_dashboard_filter_view_model()
	visible_context = load_visible_operational_context(
		vm.region,
		vm.period_days,
		tuple(vm.event_types),
		vm.date_start,
		vm.date_end,
		vm.risk_level,
		vm.threshold,
	)

	st.markdown("## Anomalias e Incertezas")
	st.caption("Use esta aba para revisar incertezas, baixa confianca e recortes que precisam de validacao humana.")

	ind_left, ind_right = st.columns([1, 2])
	with ind_left:
		render_operational_indicators(visible_context.enriched_events, visible_context.alert_feed, key="anomalies-operational-indicators")
	with ind_right:
		render_confidence_distribution(visible_context.enriched_events, key="anomalies-confidence-distribution")

	left, right = st.columns(2)
	with left:
		render_risk_distribution(visible_context.enriched_events, key="anomalies-risk-distribution")
	with right:
		render_temporal_disaster_evolution(visible_context.enriched_events, key="anomalies-temporal-evolution")

	low_conf = visible_context.enriched_events[visible_context.enriched_events["confidence"] < 0.6]
	if low_conf.empty:
		st.info("Sem eventos com baixa confianca no recorte atual.")
	else:
		st.dataframe(low_conf[["event_id", "event_type", "date", "confidence", "risk_score"]])
