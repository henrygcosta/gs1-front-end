"""Selectors for the risk hotspots feature."""

from __future__ import annotations

import pandas as pd

from features.common import (
	FeatureContext,
	narrative_blocks_from_findings,
	top_findings,
	top_records,
)


def select_map_points(context: FeatureContext) -> pd.DataFrame:
	"""Return the geospatial points used by the hotspot map."""
	columns = ["event_id", "event_type", "region", "state", "latitude", "longitude", "risk_score", "alert_level", "geographic_criticality_score"]
	return top_records(context.enriched_events[columns] if not context.enriched_events.empty else context.enriched_events.head(0).copy(), sort_by="risk_score", limit=200)


def select_regional_summary(context: FeatureContext) -> pd.DataFrame:
	"""Summarize risk by region and state."""
	if context.enriched_events.empty:
		return context.enriched_events.head(0).copy()
	return (
		context.enriched_events.groupby(["region", "state"], as_index=False)
		.agg(total_events=("event_id", "count"), avg_risk_score=("risk_score", "mean"), avg_geographic_criticality=("geographic_criticality_score", "mean"))
		.sort_values(["avg_risk_score", "total_events"], ascending=[False, False])
	)


def select_heatmap(context: FeatureContext) -> pd.DataFrame:
	"""Return a heatmap-like frame for charting and storytelling."""
	if context.enriched_events.empty:
		return context.enriched_events.head(0).copy()
	return (
		context.enriched_events.groupby(["state", "event_type"], as_index=False)
		.agg(avg_risk_score=("risk_score", "mean"), total_events=("event_id", "count"), avg_confidence=("confidence", "mean"))
		.sort_values(["avg_risk_score", "total_events"], ascending=[False, False])
	)


def select_alert_distribution(context: FeatureContext) -> pd.DataFrame:
	"""Return alert counts by semantic level."""
	if context.alert_feed.empty:
		return context.alert_feed.head(0).copy()
	return context.alert_feed.groupby("alert_level", as_index=False).agg(total_alerts=("alert_id", "count"), avg_risk_score=("risk_score", "mean"))


def select_narratives(context: FeatureContext):
	"""Build narrative blocks for the hotspot panel."""
	return narrative_blocks_from_findings(top_findings(context.enriched_events, limit=4), prefix="Central Geoespacial")

