"""Feature engineering pipeline stage.

Creates chart-ready datasets optimized for dashboard rendering.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
import streamlit as st

from utils.exceptions import PipelineError
from utils.logger import get_logger

LOGGER = get_logger(__name__)


@dataclass(slots=True)
class VisualizationDatasets:
	"""Chart-ready datasets generated from enriched events."""

	timeline_by_date: pd.DataFrame = field(default_factory=pd.DataFrame)
	event_type_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
	state_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
	region_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
	hotspots_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
	risk_distribution: pd.DataFrame = field(default_factory=pd.DataFrame)
	source_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
	alert_feed_preview: pd.DataFrame = field(default_factory=pd.DataFrame)


def _summarize_group(frame: pd.DataFrame, group_column: str) -> pd.DataFrame:
	"""Aggregate operational metrics for a grouping dimension."""
	return (
		frame.groupby(group_column, as_index=False)
		.agg(
			total_events=("event_id", "count"),
			avg_risk_score=("risk_score", "mean"),
			avg_severity=("severity", "mean"),
			critical_events=("is_critical", "sum"),
			avg_priority=("priority_score", "mean"),
		)
		.sort_values(by=["avg_risk_score", "critical_events"], ascending=[False, False])
	)


@st.cache_data(show_spinner=False, ttl=300)
def build_visualization_datasets(enriched_events: pd.DataFrame, alert_feed: pd.DataFrame | None = None) -> VisualizationDatasets:
	"""Build datasets optimized for plots, tables and cards."""
	try:
		if enriched_events.empty:
			return VisualizationDatasets()

		timeline = (
			enriched_events.groupby(["date", "source"], as_index=False)
			.agg(total_events=("event_id", "count"), avg_risk_score=("risk_score", "mean"), critical_events=("is_critical", "sum"))
			.sort_values(by=["date", "avg_risk_score"], ascending=[False, False])
		)
		by_event_type = _summarize_group(enriched_events, "event_type")
		by_state = _summarize_group(enriched_events, "state")
		by_region = _summarize_group(enriched_events, "region")
		hotspots = (
			enriched_events[["event_id", "event_type", "region", "state", "risk_score", "geographic_criticality_score", "priority_score", "latitude", "longitude", "semantic_alert", "alert_level"]]
			.sort_values(by=["priority_score", "risk_score"], ascending=[False, False])
			.head(30)
			.reset_index(drop=True)
		)
		risk_distribution = enriched_events[["event_id", "severity_class", "geographic_criticality_class", "alert_level", "source"]].copy()
		source_summary = _summarize_group(enriched_events, "source")
		alert_preview = alert_feed.head(20).copy() if alert_feed is not None and not alert_feed.empty else enriched_events[
			["event_id", "event_type", "region", "state", "alert_level", "semantic_alert", "recommended_action"]
		].head(20).copy()

		LOGGER.debug("Visualization datasets built: timeline=%d hotspots=%d", len(timeline), len(hotspots))
		return VisualizationDatasets(
			timeline_by_date=timeline,
			event_type_summary=by_event_type,
			state_summary=by_state,
			region_summary=by_region,
			hotspots_summary=hotspots,
			risk_distribution=risk_distribution,
			source_summary=source_summary,
			alert_feed_preview=alert_preview,
		)
	except Exception as exc:  # pragma: no cover - defensive guard
		LOGGER.exception("Feature engineering pipeline failed")
		raise PipelineError("Failed to build visualization datasets") from exc
