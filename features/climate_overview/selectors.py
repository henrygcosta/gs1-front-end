"""Selectors for the climate overview feature."""

from __future__ import annotations

import pandas as pd

from features.common import (
	FeatureContext,
	MetricCard,
	NarrativeBlock,
	executive_headline,
	narrative_blocks_from_findings,
	top_findings,
	top_records,
)


def select_kpis(context: FeatureContext) -> list[MetricCard]:
	"""Build the main KPI set for the dashboard."""
	criticals = int(context.enriched_events.get("is_critical", pd.Series(dtype=bool)).fillna(False).sum())
	alert_count = len(context.alert_feed)
	avg_risk = context.enriched_events["risk_score"].mean() if not context.enriched_events.empty else 0.0
	top_region = (
		context.enriched_events.groupby("region")["risk_score"].mean().sort_values(ascending=False).index[0]
		if not context.enriched_events.empty and "region" in context.enriched_events.columns
		else context.region
	)
	return [
		MetricCard(label="Eventos no periodo", value=str(len(context.enriched_events)), helper=f"Janela de {context.period_days} dias", kind="info"),
		MetricCard(label="Alertas criticos", value=str(alert_count), helper="Feed priorizado", kind="warning"),
		MetricCard(label="Eventos criticos", value=str(criticals), helper="Leitura operacional", kind="critical"),
		MetricCard(label="Risco medio", value=f"{avg_risk:.2f}", helper=f"Regiao foco: {top_region}", kind="info"),
	]


def select_panorama(context: FeatureContext) -> pd.DataFrame:
	"""Build a panorama by event type and state."""
	if context.enriched_events.empty:
		return context.enriched_events.head(0).copy()
	return (
		context.enriched_events.groupby(["state", "event_type"], as_index=False)
		.agg(total_events=("event_id", "count"), avg_risk_score=("risk_score", "mean"), avg_confidence=("confidence", "mean"))
		.sort_values(["avg_risk_score", "total_events"], ascending=[False, False])
	)


def select_critical_indicators(context: FeatureContext) -> pd.DataFrame:
	"""Return the most relevant indicators for the dashboard."""
	columns = ["event_id", "event_type", "region", "state", "risk_score", "geographic_criticality_score", "alert_level", "date"]
	frame = context.enriched_events
	return top_records(frame[columns] if not frame.empty else frame.head(0).copy(), sort_by="risk_score", limit=8)


def select_executive_summary(context: FeatureContext) -> pd.DataFrame:
	"""Return a compact summary table for the executive section."""
	if context.risk_summary.empty:
		return context.risk_summary.head(0).copy()
	return context.risk_summary[["event_type", "total_events", "avg_risk_score", "alert_level", "semantic_alert", "recommended_action"]].copy()


def select_narratives(context: FeatureContext) -> list[NarrativeBlock]:
	"""Build short narrative blocks for the dashboard."""
	findings = top_findings(context.enriched_events, limit=4)
	blocks = narrative_blocks_from_findings(findings, prefix="Painel Geral")
	blocks.insert(0, NarrativeBlock(title="Resumo executivo", text=executive_headline(context), kind="info"))
	return blocks

