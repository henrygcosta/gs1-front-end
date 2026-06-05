"""Selectors for the flood prediction feature."""

from __future__ import annotations

import pandas as pd

from features.common import (
	FeatureContext,
	narrative_blocks_from_findings,
	top_findings,
	top_records,
)


def select_high_risk_regions(context: FeatureContext) -> pd.DataFrame:
	"""Return regions with the highest flood risk."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	return top_records(frame.sort_values("flood_risk_probability", ascending=False), sort_by="flood_risk_probability", limit=12)


def select_temporal_evolution(context: FeatureContext) -> pd.DataFrame:
	"""Return a daily flood-risk trend."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	return frame.groupby("date", as_index=False).agg(avg_flood_risk=("flood_risk_probability", "mean"), avg_risk_score=("risk_score", "mean"), total_events=("event_id", "count"))


def select_severity(context: FeatureContext) -> pd.DataFrame:
	"""Return flood severity indicators by state."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	return frame.groupby(["state", "region"], as_index=False).agg(avg_severity=("severity", "mean"), avg_flood_risk=("flood_risk_probability", "mean"), avg_confidence=("confidence", "mean"))


def select_preventive_alerts(context: FeatureContext) -> pd.DataFrame:
	"""Return preventive flood alerts."""
	frame = context.alert_feed
	if frame.empty:
		return frame.head(0).copy()
	mask = frame["event_type"].str.contains("Flood|Enchente|Flood", case=False, na=False) | frame["risk_score"].ge(0.75)
	return top_records(frame.loc[mask], sort_by="risk_score", limit=12)


def select_narratives(context: FeatureContext):
	"""Build flood-prevention storytelling blocks."""
	return narrative_blocks_from_findings(top_findings(select_high_risk_regions(context), label_column="event_type", limit=4), prefix="Prevencao de Enchentes")
