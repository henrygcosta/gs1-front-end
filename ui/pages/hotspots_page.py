"""Hotspots page showing prioritized geographic risk zones."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from state.view_model import build_dashboard_filter_view_model
from ui.charts import render_geographic_risk_map, render_risk_trend
from ui.components.alert_card import render_alert_card
from ui.pages.context_loader import load_visible_operational_context


def render_hotspots_page() -> None:
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

	st.markdown("## Hotspots Prioritários")
	st.caption("Visão operacional para decidir onde agir agora, com foco apenas em pontos acima do limite de risco.")
	st.markdown("### Onde estão os problemas")
	frame = visible_context.enriched_events
	if "is_critical" in frame.columns:
		critical_events = frame.loc[frame["is_critical"]].copy()
	else:
		critical_events = frame.loc[frame["alert_level"].isin(["alto", "critico"])].copy() if "alert_level" in frame.columns else frame.head(0).copy()
	if critical_events.empty:
		critical_events = frame.sort_values("risk_score", ascending=False).head(25).copy()

	critical_count = int(critical_events.get("is_critical", critical_events["risk_score"] >= 0.85).sum()) if not critical_events.empty else 0
	top_region = str(critical_events.groupby("region")["risk_score"].mean().sort_values(ascending=False).index[0]) if not critical_events.empty and "region" in critical_events.columns else "N/A"
	avg_risk = float(critical_events["risk_score"].mean()) if not critical_events.empty else 0.0

	summary_columns = st.columns(3)
	with summary_columns[0]:
		st.metric("Eventos críticos", f"{critical_count}")
	with summary_columns[1]:
		st.metric("Região mais pressionada", top_region)
	with summary_columns[2]:
		st.metric("Risco médio", f"{avg_risk:.2f}")

	render_geographic_risk_map(
		critical_events,
		key="hotspots-geographic-risk-map",
		title="Regiões com Maior Criticidade",
		help_text="Mapa focado apenas nos eventos acima do limite e nos hotspots que exigem ação imediata.",
	)

	st.markdown("### Como o risco está evoluindo")
	trend_source = critical_events.copy()
	date_column = "timestamp" if "timestamp" in trend_source.columns else "date" if "date" in trend_source.columns else None
	trend_message = "Risco estabilizado no recorte atual."
	if date_column and not trend_source.empty:
		trend_source.loc[:, "trend_date"] = pd.to_datetime(trend_source[date_column], utc=True, errors="coerce")
		trend_source = trend_source.dropna(subset=["trend_date", "risk_score"]).sort_values("trend_date")
		if len(trend_source) >= 4:
			recent_window = max(1, min(7, len(trend_source) // 3))
			recent_avg = float(trend_source.tail(recent_window)["risk_score"].mean())
			previous_slice = trend_source.iloc[: max(1, len(trend_source) - recent_window)]
			previous_avg = float(previous_slice.tail(recent_window)["risk_score"].mean()) if not previous_slice.empty else recent_avg
			delta = recent_avg - previous_avg
			if delta > 0.03:
				trend_message = f"Risco médio em crescimento. Alta de {delta:.2f} no período mais recente."
			elif delta < -0.03:
				trend_message = f"Risco reduzindo. Queda de {abs(delta):.2f} no período mais recente."
			else:
				trend_message = "Risco estabilizado. Oscilação recente pequena e sem aceleração relevante."
	st.info(trend_message)
	render_risk_trend(critical_events, key="hotspots-risk-trend")

	st.markdown("### Ranking de risco e ações recomendadas")
	for _, row in critical_events.sort_values("risk_score", ascending=False).head(5).iterrows():
		severity = str(row.get("geographic_criticality_class", "N/A"))
		risk_score = float(row.get("risk_score", 0.0))
		location = f"{row.get('region', 'N/A')}/{row.get('state', 'N/A')}"
		render_alert_card(
			title=f"{row['event_type']} em {location}",
			message=f"Local: {location} | Severidade: {severity} | Score: {risk_score:.2f}",
			level=str(row.get("alert_level", "info")),
			source="Prioridade operacional",
			action_text=str(row.get("recommended_action", "")),
		)

	