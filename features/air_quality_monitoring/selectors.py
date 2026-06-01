"""Selectors for the air quality monitoring feature."""

from __future__ import annotations

import pandas as pd

from features.common import FeatureContext, narrative_blocks_from_findings, top_findings


def select_indices(context: FeatureContext) -> pd.DataFrame:
	"""Return AQI and pollution indices by state."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	mask = frame["source"].eq("air_quality") | frame["event_type"].str.contains("Qualidade do ar|Air", case=False, na=False)
	return (
		frame.loc[mask]
		.groupby(["state", "region"], as_index=False)
		.agg(avg_aqi=("aqi", "mean"), avg_pm25=("pm25", "mean"), avg_pm10=("pm10", "mean"), avg_risk_score=("risk_score", "mean"))
		.sort_values(["avg_aqi", "avg_risk_score"], ascending=[False, False])
	)


def select_regional_comparisons(context: FeatureContext) -> pd.DataFrame:
	"""Return region-based air quality comparisons."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	mask = frame["source"].eq("air_quality") | frame["event_type"].str.contains("Qualidade do ar|Air", case=False, na=False)
	return frame.loc[mask].groupby("region", as_index=False).agg(avg_aqi=("aqi", "mean"), avg_risk_score=("risk_score", "mean"), total_events=("event_id", "count"))


def select_trend(context: FeatureContext) -> pd.DataFrame:
	"""Return a daily AQI trend."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	mask = frame["source"].eq("air_quality") | frame["event_type"].str.contains("Qualidade do ar|Air", case=False, na=False)
	return frame.loc[mask].groupby("date", as_index=False).agg(avg_aqi=("aqi", "mean"), avg_risk_score=("risk_score", "mean"), total_events=("event_id", "count"))


def select_narratives(context: FeatureContext):
	"""Build air quality storytelling blocks."""
	return narrative_blocks_from_findings(top_findings(select_indices(context), label_column="state", limit=4), prefix="Qualidade do Ar")
