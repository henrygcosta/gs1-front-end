"""Risk scoring aggregation pipeline stage."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from pipelines.common import dataframe_cache_key, recommendation_for_event, risk_alert_level
from utils.exceptions import PipelineError
from utils.logger import get_logger


LOGGER = get_logger(__name__)


@st.cache_data(show_spinner=False, ttl=300, hash_funcs={pd.DataFrame: dataframe_cache_key})
def run_risk_scoring_pipeline(enriched_events: pd.DataFrame) -> pd.DataFrame:
	"""Build an operational risk summary aggregated by event type."""
	try:
		if enriched_events.empty:
			return pd.DataFrame(
				columns=[
					"event_type",
					"total_events",
					"avg_risk_score",
					"max_risk_score",
					"critical_events",
					"avg_severity",
					"avg_confidence",
					"avg_geographic_criticality",
					"dominant_state",
					"dominant_region",
					"alert_level",
					"semantic_alert",
					"recommended_action",
					"priority_rank",
					"alert_title",
				]
			)

		summary = (
			enriched_events.groupby("event_type", as_index=False)
			.agg(
				total_events=("event_id", "count"),
				avg_risk_score=("risk_score", "mean"),
				max_risk_score=("risk_score", "max"),
				critical_events=("is_critical", "sum"),
				avg_severity=("severity", "mean"),
				avg_confidence=("confidence", "mean"),
				avg_geographic_criticality=("geographic_criticality_score", "mean"),
			)
			.sort_values(by=["avg_risk_score", "critical_events"], ascending=[False, False])
			.reset_index(drop=True)
		)

		dominant_state = enriched_events.groupby("event_type")["state"].agg(
			lambda series: series.mode().iloc[0] if not series.mode().empty else pd.NA
		)
		dominant_region = enriched_events.groupby("event_type")["region"].agg(
			lambda series: series.mode().iloc[0] if not series.mode().empty else pd.NA
		)

		summary = summary.assign(
			dominant_state=summary["event_type"].map(dominant_state),
			dominant_region=summary["event_type"].map(dominant_region),
			alert_level=summary["avg_risk_score"].apply(risk_alert_level),
		)
		summary = summary.assign(
			semantic_alert=summary.apply(
				lambda row: f"{str(row['alert_level']).upper()} - {row['event_type']} com {row['critical_events']} eventos criticos",
				axis=1,
			),
			recommended_action=summary.apply(
				lambda row: recommendation_for_event(str(row["event_type"]), str(row["alert_level"])),
				axis=1,
			),
			priority_rank=summary["avg_risk_score"].rank(method="dense", ascending=False).astype(int),
			alert_title=summary.apply(lambda row: f"{str(row['alert_level']).upper()} - {row['event_type']}", axis=1),
		)

		LOGGER.debug("Risk summary generated: %d rows", len(summary))
		return summary
	except Exception as exc:  # pragma: no cover - defensive guard
		LOGGER.exception("Risk scoring pipeline failed")
		raise PipelineError("Failed to compute risk summary") from exc
