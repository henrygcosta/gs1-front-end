"""Selectors for the burning monitoring feature."""

from __future__ import annotations

import pandas as pd

from features.common import (
	FeatureContext,
	narrative_blocks_from_findings,
	top_findings,
	top_records,
)


def select_fire_events(context: FeatureContext) -> pd.DataFrame:
	"""Return burning-related events for the operational map."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	mask = frame["source"].eq("fire") | frame["event_type"].str.contains("Queimada|Fire", case=False, na=False)
	columns = ["event_id", "event_type", "region", "state", "latitude", "longitude", "risk_score", "alert_level", "confidence"]
	return top_records(frame.loc[mask, columns], sort_by="risk_score", limit=150)


def select_temporal_evolution(context: FeatureContext) -> pd.DataFrame:
	"""Return a temporal series for wildfire monitoring."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	mask = frame["source"].eq("fire") | frame["event_type"].str.contains("Queimada|Fire", case=False, na=False)
	return frame.loc[mask].groupby("date", as_index=False).agg(avg_risk_score=("risk_score", "mean"), total_events=("event_id", "count"))


def select_alerts(context: FeatureContext) -> pd.DataFrame:
	"""Return fire-related alerts."""
	frame = context.alert_feed
	if frame.empty:
		return frame.head(0).copy()
	mask = frame["source"].eq("fire") | frame["event_type"].str.contains("Queimada|Fire", case=False, na=False)
	return top_records(frame.loc[mask], sort_by="risk_score", limit=12)


def select_narratives(context: FeatureContext):
	"""Build short wildfire storytelling blocks."""
	return narrative_blocks_from_findings(top_findings(select_alerts(context), limit=4), prefix="Queimadas")
