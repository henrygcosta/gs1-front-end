"""Dashboard overview page composition."""

from __future__ import annotations

import streamlit as st

from features.climate_overview.dto import ClimateOverviewRequest
from features.climate_overview.use_cases import execute_climate_overview
from state.selectors import get_filters_state
from state.view_model import build_dashboard_filter_view_model
from ui.charts import (
	render_air_quality_index,
	render_climate_heatmap,
	render_climate_time_series,
	render_fire_intensity,
	render_flood_forecast,
	render_geographic_risk_map,
	render_geospatial_heatmap,
	render_landslide_forecast,
	render_operational_bars,
	render_operational_indicators,
	render_rainfall_accumulation,
	render_risk_distribution,
	render_scatter_geo,
	render_temporal_disaster_evolution,
)
from ui.components.kpi_card import render_kpi
from ui.components.loading_block import loading_block
from ui.components.notification_banner import render_notification_banner
from ui.components.timeline_story import render_timeline_story
from ui.pages.context_loader import load_visible_operational_context


def render_dashboard_page() -> None:
	"""Compose the overview page with high-level KPIs and charts."""
	vm = build_dashboard_filter_view_model()

	with loading_block("Carregando dados do dashboard..."):
		visible_context = load_visible_operational_context(
			vm.region,
			vm.period_days,
			tuple(vm.event_types),
			vm.date_start,
			vm.date_end,
			vm.risk_level,
			vm.threshold,
		)
		feature_vm = execute_climate_overview(ClimateOverviewRequest(context=visible_context))

	filters = get_filters_state()
	if filters.risk_level != "all" or filters.threshold > 0:
		render_notification_banner(
			"Filtro operacional ativo",
			f"Regiao {filters.region}, risco {filters.risk_level}, threshold {filters.threshold:.2f}",
			kind="info",
		)


	# KPI row
	kpi_columns = st.columns(4)
	for idx, kpi in enumerate(feature_vm.kpis[:4]):
		with kpi_columns[idx]:
			render_kpi(kpi.get("label", "KPI"), kpi.get("value", "-"), delta=kpi.get("helper", ""))

	climate_tab, spatial_tab, sector_tab = st.tabs(["Clima", "Espacial", "Setoriais"])

	with climate_tab:
		st.markdown("## Analise climatica")
		left, right = st.columns([1.2, 1])
		with left:
			render_climate_time_series(visible_context.enriched_events, key="dashboard-climate-timeseries")
			render_rainfall_accumulation(visible_context.enriched_events, key="dashboard-rainfall-accumulation")
		with right:
			render_climate_heatmap(visible_context.enriched_events, key="dashboard-climate-heatmap")
			render_operational_indicators(visible_context.enriched_events, visible_context.alert_feed, key="dashboard-operational-indicators")
		render_operational_bars(visible_context.risk_summary, key="dashboard-risk-bar")
		render_risk_distribution(visible_context.enriched_events, key="dashboard-risk-distribution")
		render_timeline_story(visible_context.enriched_events)

	with spatial_tab:
		st.markdown("## Analise espacial")
		st.caption("Visão executiva da distribuição geográfica completa, para monitoramento amplo do cenário atual.")
		render_geographic_risk_map(visible_context.enriched_events, key="dashboard-geographic-risk-map")
		if st.toggle("Carregar mapas espaciais avançados", value=False, key="dashboard-load-advanced-spatial"):
			geo_left, geo_right = st.columns(2)
			with geo_left:
				render_geospatial_heatmap(visible_context.enriched_events, key="dashboard-geospatial-heatmap")
			with geo_right:
				render_scatter_geo(visible_context.enriched_events, key="dashboard-scatter-geo")
		else:
			st.info("Os mapas de densidade e scatter geo são carregados sob demanda para ampliar a leitura espacial sem duplicar a visão operacional.")

	with sector_tab:
		st.markdown("## Serie setorial e previsoes")
		render_fire_intensity(visible_context.enriched_events, key="dashboard-fire-intensity")
		if st.toggle("Carregar previsões e séries setoriais avançadas", value=False, key="dashboard-load-advanced-sector"):
			sector_left, sector_right = st.columns(2)
			with sector_left:
				render_air_quality_index(visible_context.enriched_events, key="dashboard-air-quality-index")
				st.subheader("Evolucao temporal de desastres")
				render_temporal_disaster_evolution(visible_context.enriched_events, key="dashboard-disaster-evolution")
			with sector_right:
				render_flood_forecast(visible_context.enriched_events, key="dashboard-flood-forecast")
				render_landslide_forecast(visible_context.enriched_events, key="dashboard-landslide-forecast")
		else:
			st.info("As séries setoriais avançadas ficam disponíveis sob demanda para reduzir processamento e melhorar a fluidez.")

	# Preserve the executive narrative at the end of the page.
	st.markdown("## Narrativa executiva")
	for block in feature_vm.narratives:
		st.info(f"**{block['title']}**\n\n{block['text']}")
