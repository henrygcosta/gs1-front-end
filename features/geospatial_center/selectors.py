"""Selectors for the geospatial center feature."""

from __future__ import annotations

import pandas as pd

from features.common import FeatureContext, narrative_blocks_from_findings, top_findings, top_records


def select_interactive_maps(context: FeatureContext) -> pd.DataFrame:
	"""Return the core geospatial points for interactive maps."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	columns = ["event_id", "event_type", "region", "state", "latitude", "longitude", "risk_score", "alert_level", "geographic_criticality_score"]
	return top_records(frame[columns], sort_by="risk_score", limit=250)


def select_spatial_risk(context: FeatureContext) -> pd.DataFrame:
	"""Return a spatial risk summary by state and region."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	return frame.groupby(["region", "state"], as_index=False).agg(total_events=("event_id", "count"), avg_risk_score=("risk_score", "mean"), avg_geographic_criticality=("geographic_criticality_score", "mean"))


def select_critical_regions(context: FeatureContext) -> pd.DataFrame:
	"""Return the most critical regions sorted by risk."""
	return top_records(select_spatial_risk(context), sort_by="avg_risk_score", limit=10)


def select_heatmaps(context: FeatureContext) -> pd.DataFrame:
	"""Return a heatmap-friendly regional frame."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	return frame.groupby(["state", "event_type"], as_index=False).agg(total_events=("event_id", "count"), avg_risk_score=("risk_score", "mean"), avg_confidence=("confidence", "mean"))


def select_alert_distribution(context: FeatureContext) -> pd.DataFrame:
	"""Return alert distribution by semantic level."""
	frame = context.alert_feed
	if frame.empty:
		return frame.head(0).copy()
	return frame.groupby("alert_level", as_index=False).agg(total_alerts=("alert_id", "count"), avg_risk_score=("risk_score", "mean"))


def select_narratives(context: FeatureContext):
	"""Build geospatial storytelling blocks."""
	return narrative_blocks_from_findings(top_findings(context.enriched_events, limit=4), prefix="Central Geoespacial")
