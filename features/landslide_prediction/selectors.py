"""Selectors for the landslide prediction feature."""

from __future__ import annotations

import pandas as pd

from features.common import FeatureContext, narrative_blocks_from_findings, top_findings, top_records


def select_vulnerable_areas(context: FeatureContext) -> pd.DataFrame:
	"""Return the most vulnerable landslide-prone records."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	mask = frame["event_type"].str.contains("Landslide|Deslizamento", case=False, na=False) | frame["landslide_risk_probability"].ge(0.65)
	columns = ["event_id", "event_type", "region", "state", "latitude", "longitude", "landslide_risk_probability", "severity", "confidence", "precipitation_mm"]
	return top_records(frame.loc[mask, columns], sort_by="landslide_risk_probability", limit=20)


def select_risk_index(context: FeatureContext) -> pd.DataFrame:
	"""Return risk scores by state and region."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	mask = frame["event_type"].str.contains("Landslide|Deslizamento", case=False, na=False)
	return frame.loc[mask].groupby(["state", "region"], as_index=False).agg(avg_landslide_risk=("landslide_risk_probability", "mean"), avg_severity=("severity", "mean"), avg_confidence=("confidence", "mean"))


def select_rainfall_correlation(context: FeatureContext) -> pd.DataFrame:
	"""Return the relationship between rainfall and landslide risk."""
	frame = context.enriched_events
	if frame.empty:
		return frame.head(0).copy()
	mask = frame["event_type"].str.contains("Landslide|Deslizamento", case=False, na=False)
	selected = frame.loc[mask, ["precipitation_mm", "landslide_risk_probability", "state", "region"]].copy()
	if selected.empty:
		return selected
	selected["precipitation_mm"] = pd.to_numeric(selected["precipitation_mm"], errors="coerce")
	selected["landslide_risk_probability"] = pd.to_numeric(selected["landslide_risk_probability"], errors="coerce")
	return selected.dropna(subset=["precipitation_mm", "landslide_risk_probability"])


def select_emergency_priority(context: FeatureContext) -> pd.DataFrame:
	"""Return the top emergency-priority areas."""
	return top_records(select_vulnerable_areas(context), sort_by="landslide_risk_probability", limit=12)


def select_narratives(context: FeatureContext):
	"""Build landslide-prevention storytelling blocks."""
	return narrative_blocks_from_findings(top_findings(select_emergency_priority(context), label_column="event_type", limit=4), prefix="Prevencao de Deslizamentos")
