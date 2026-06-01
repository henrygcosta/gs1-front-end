"""Alert generation pipeline stage."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from pipelines.common import dataframe_cache_key, recommendation_for_event, risk_alert_level
from utils.exceptions import PipelineError
from utils.logger import get_logger


LOGGER = get_logger(__name__)


@dataclass(frozen=True)
class AlertThresholds:
	"""Thresholds used to select events for the alert feed."""

	moderate: float = 0.60
	high: float = 0.75
	critical: float = 0.85


@st.cache_data(show_spinner=False, ttl=300, hash_funcs={pd.DataFrame: dataframe_cache_key})
def build_alert_feed(enriched_events: pd.DataFrame, thresholds: AlertThresholds = AlertThresholds()) -> pd.DataFrame:
	"""Build a semantic alert feed from the enriched event stream."""
	try:
		if enriched_events.empty:
			return pd.DataFrame(
				columns=[
					"alert_id",
					"event_id",
					"source",
					"domain",
					"event_type",
					"region",
					"state",
					"timestamp",
					"risk_score",
					"geographic_criticality_score",
					"alert_level",
					"alert_title",
					"alert_message",
					"recommended_action",
				]
			)

		alerts = enriched_events.loc[
			enriched_events["risk_score"] >= thresholds.moderate,
			[
				"event_id",
				"source",
				"domain",
				"event_type",
				"region",
				"state",
				"timestamp",
				"risk_score",
				"geographic_criticality_score",
				"alert_level",
				"alert_title",
				"recommended_action",
			],
		].copy()

		alerts.loc[:, "alert_message"] = alerts.apply(
			lambda row: (
				f"{str(row['alert_level']).upper()} detected for {row['event_type']} in {row['region']}/{row['state']}"
				f". {row['recommended_action']}"
			),
			axis=1,
		)
		alerts.loc[:, "domain"] = alerts["domain"].fillna("operational")
		alerts.loc[:, "alert_level"] = alerts["risk_score"].apply(risk_alert_level)
		alerts.loc[:, "recommended_action"] = alerts["event_type"].apply(
			lambda event_type: recommendation_for_event(str(event_type), "high")
		)
		alerts.loc[:, "alert_id"] = alerts.apply(
			lambda row: f"{row['event_id']}-{str(row['alert_level'])}-{str(row['source'])}", axis=1
		)
		alerts = alerts.loc[alerts["risk_score"] >= thresholds.moderate].copy()
		alerts = alerts.sort_values(by=["risk_score", "timestamp"], ascending=[False, False]).reset_index(drop=True)
		alerts.loc[:, "alert_id"] = alerts["alert_id"].astype(str)
		LOGGER.debug("Alert feed generated: %d rows", len(alerts))
		return alerts
	except Exception as exc:  # pragma: no cover - defensive guard
		LOGGER.exception("Alerting pipeline failed")
		raise PipelineError("Failed to build alert feed") from exc
