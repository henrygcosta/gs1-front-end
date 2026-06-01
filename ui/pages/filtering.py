"""Helpers for applying dashboard filters to operational frames."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from features.common import FeatureContext
from pipelines.alerting_pipeline import build_alert_feed
from pipelines.risk_scoring_pipeline import run_risk_scoring_pipeline
from state.view_model import DashboardFilterViewModel
from features.common import FEATURE_CACHE_KWARGS


RISK_LEVEL_THRESHOLDS: dict[str, float] = {
	"all": 0.0,
	"low": 0.35,
	"moderate": 0.60,
	"high": 0.75,
	"critical": 0.85,
}

EVENT_TYPE_ALIASES: dict[str, str] = {
	"fire": "Queimada",
	"queimada": "Queimada",
	"airquality": "Qualidade do Ar",
	"qualidade do ar": "Qualidade do Ar",
}


def _canonical_event_type(event_type: str) -> str:
	"""Normalize legacy filter labels to the canonical dataset labels."""
	return EVENT_TYPE_ALIASES.get(event_type.strip().lower(), event_type)


def _date_mask(frame: pd.DataFrame, start: str | None, end: str | None) -> pd.Series:
	"""Build a boolean mask for the requested date window."""
	if frame.empty:
		return pd.Series(dtype=bool, index=frame.index)
	def _parse_filter_date(value: str | None) -> pd.Timestamp:
		return pd.to_datetime(value, format="%d-%m-%Y", utc=True, errors="coerce")

	if "timestamp" in frame.columns:
		timestamps = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
	elif "date" in frame.columns:
		timestamps = pd.to_datetime(frame["date"], utc=True, errors="coerce")
	else:
		return pd.Series(True, index=frame.index)
	mask = pd.Series(True, index=frame.index)
	if start:
		mask &= timestamps >= _parse_filter_date(start)
	if end:
		mask &= timestamps <= _parse_filter_date(end)
	return mask.fillna(False)


def filter_operational_frame(frame: pd.DataFrame, filters: DashboardFilterViewModel) -> pd.DataFrame:
	"""Apply the active UI filters to an operational frame."""
	if frame.empty:
		return frame.copy()
	result = frame.copy()
	if filters.event_types and "event_type" in result.columns:
		selected_event_types = {_canonical_event_type(event_type) for event_type in filters.event_types}
		result = result.loc[result["event_type"].isin(selected_event_types)].copy()
	result = result.loc[_date_mask(result, filters.date_start, filters.date_end)].copy()
	threshold = max(float(filters.threshold), RISK_LEVEL_THRESHOLDS.get(filters.risk_level, 0.0))
	if threshold > 0.0 and "risk_score" in result.columns:
		result = result.loc[pd.to_numeric(result["risk_score"], errors="coerce").fillna(0.0) >= threshold].copy()
	return result.reset_index(drop=True)


@st.cache_data(show_spinner=False, ttl=300, hash_funcs=FEATURE_CACHE_KWARGS)
def build_visible_context(context: FeatureContext, filters: DashboardFilterViewModel) -> FeatureContext:
	"""Build a filtered feature context that mirrors the active UI state."""
	raw_events = filter_operational_frame(context.raw_events, filters)
	cleaned_events = filter_operational_frame(context.cleaned_events, filters)
	enriched_events = filter_operational_frame(context.enriched_events, filters)
	risk_summary = run_risk_scoring_pipeline(enriched_events)
	alert_feed = build_alert_feed(enriched_events)
	return FeatureContext(
		region=context.region,
		period_days=context.period_days,
		event_types=list(filters.event_types),
		raw_events=raw_events,
		cleaned_events=cleaned_events,
		enriched_events=enriched_events,
		risk_summary=risk_summary,
		alert_feed=alert_feed,
	)