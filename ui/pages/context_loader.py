"""Cached loaders for the operational dashboard context."""

from __future__ import annotations

import streamlit as st

from features.common import FEATURE_CACHE_KWARGS, FeatureContext
from pipelines.alerting_pipeline import build_alert_feed
from pipelines.cleaning_pipeline import run_cleaning_pipeline
from pipelines.enrichment_pipeline import run_enrichment_pipeline
from pipelines.ingest_pipeline import run_ingest_pipeline
from pipelines.risk_scoring_pipeline import run_risk_scoring_pipeline
from state.view_model import DashboardFilterViewModel
from ui.pages.filtering import build_visible_context


@st.cache_data(show_spinner=False, ttl=300, hash_funcs=FEATURE_CACHE_KWARGS)
def load_operational_context(region: str, period_days: int, event_types: tuple[str, ...]) -> FeatureContext:
	"""Load and cache the canonical operational context for a dashboard recorte."""
	raw = run_ingest_pipeline(region=region, period_days=period_days)
	cleaned = run_cleaning_pipeline(raw)
	enriched = run_enrichment_pipeline(cleaned)
	risk_summary = run_risk_scoring_pipeline(enriched)
	alert_feed = build_alert_feed(enriched)
	return FeatureContext(
		region=region,
		period_days=period_days,
		event_types=list(event_types),
		raw_events=raw,
		cleaned_events=cleaned,
		enriched_events=enriched,
		risk_summary=risk_summary,
		alert_feed=alert_feed,
	)


@st.cache_data(show_spinner=False, ttl=300, hash_funcs=FEATURE_CACHE_KWARGS)
def load_visible_operational_context(
	region: str,
	period_days: int,
	event_types: tuple[str, ...],
	date_start: str | None,
	date_end: str | None,
	risk_level: str,
	threshold: float,
) -> FeatureContext:
	"""Load the cached base context and apply the active UI filters."""
	base_context = load_operational_context(region, period_days, event_types)
	filters = DashboardFilterViewModel(
		region=region,
		event_types=list(event_types),
		period_days=period_days,
		date_start=date_start,
		date_end=date_end,
		risk_level=risk_level,
		threshold=threshold,
	)
	return build_visible_context(base_context, filters)