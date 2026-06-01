"""Selectors for the water management feature."""

from __future__ import annotations

import pandas as pd

from features.common import FeatureContext, narrative_blocks_from_findings, top_findings, top_records


def select_reservoirs(context: FeatureContext) -> pd.DataFrame:
	"""Synthesize reservoir health from rainfall and drought pressure."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	grouped = frame.groupby(["state", "region"], as_index=False).agg(avg_precipitation_mm=("precipitation_mm", "mean"), avg_drought_risk=("drought_risk_probability", "mean"), avg_temperature_c=("temperature_c", "mean"))
	grouped["reservoir_fill"] = (1.0 - grouped["avg_drought_risk"].fillna(0.0) * 0.7) + (grouped["avg_precipitation_mm"].fillna(0.0).clip(0, 120) / 120.0 * 0.3)
	return grouped.sort_values(["reservoir_fill", "avg_drought_risk"], ascending=[True, False])


def select_drought_risk(context: FeatureContext) -> pd.DataFrame:
	"""Return the highest drought-pressure records."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	return top_records(frame.sort_values("drought_risk_probability", ascending=False), sort_by="drought_risk_probability", limit=20)


def select_water_levels(context: FeatureContext) -> pd.DataFrame:
	"""Return a daily water-level proxy series."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	series = frame.groupby("date", as_index=False).agg(avg_reservoir_fill=("precipitation_mm", "mean"), avg_drought_risk=("drought_risk_probability", "mean"), total_events=("event_id", "count"))
	series["water_level_index"] = (series["avg_reservoir_fill"].fillna(0.0).clip(0, 120) / 120.0 * 0.6) + (1.0 - series["avg_drought_risk"].fillna(0.0)) * 0.4
	return series.sort_values("date")


def select_narratives(context: FeatureContext):
	"""Build water management storytelling blocks."""
	return narrative_blocks_from_findings(top_findings(select_drought_risk(context), limit=4), prefix="Gestao Hídrica")
