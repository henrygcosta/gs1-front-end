"""Shared pytest fixtures for the climate dashboard test suite."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest

import state.helpers as state_helpers
import state.initializer as state_initializer
import state.selectors as state_selectors
from features.common import FeatureContext
from pipelines.alerting_pipeline import build_alert_feed
from pipelines.enrichment_pipeline import run_enrichment_pipeline
from pipelines.risk_scoring_pipeline import run_risk_scoring_pipeline
from state.view_model import DashboardFilterViewModel


def _build_sample_operational_rows() -> pd.DataFrame:
	"""Build a small mixed-source operational dataset for tests."""
	base_time = datetime(2026, 5, 1, 12, tzinfo=UTC)
	return pd.DataFrame(
		[
			{
				"source": "climate",
				"domain": "climate_risk",
				"record_type": "event",
				"event_id": "EVT-001",
				"region": "Brazil",
				"state": "BR",
				"event_type": "Flood",
				"latitude": -23.55,
				"longitude": -46.63,
				"timestamp": base_time,
				"severity": 0.92,
				"confidence": 0.83,
				"temperature_c": 26.0,
				"precipitation_mm": 74.0,
				"brightness": pd.NA,
				"vegetation_index": pd.NA,
				"pm25": pd.NA,
				"pm10": pd.NA,
				"no2": pd.NA,
				"o3": pd.NA,
				"aqi": pd.NA,
				"risk_factors": ("high rainfall", "river overflow"),
				"centroid_lat": -23.55,
				"centroid_lon": -46.63,
				"population": 1200000,
				"payload_weight": 1.0,
			},
			{
				"source": "fire",
				"domain": "fire_monitoring",
				"record_type": "event",
				"event_id": "EVT-002",
				"region": "Amazonas",
				"state": "AM",
				"event_type": "Queimada",
				"latitude": -3.1,
				"longitude": -60.0,
				"timestamp": base_time - timedelta(days=1),
				"severity": 0.88,
				"confidence": 0.61,
				"temperature_c": pd.NA,
				"precipitation_mm": pd.NA,
				"brightness": 1430.0,
				"vegetation_index": 0.22,
				"pm25": pd.NA,
				"pm10": pd.NA,
				"no2": pd.NA,
				"o3": pd.NA,
				"aqi": pd.NA,
				"risk_factors": ("thermal anomaly", "vegetation stress"),
				"centroid_lat": -3.1,
				"centroid_lon": -60.0,
				"population": 500000,
				"payload_weight": 1.0,
			},
			{
				"source": "air_quality",
				"domain": "air_quality_monitoring",
				"record_type": "observation",
				"event_id": "EVT-003",
				"region": "Sudeste",
				"state": "SE",
				"event_type": "Qualidade do Ar",
				"latitude": pd.NA,
				"longitude": pd.NA,
				"timestamp": base_time - timedelta(days=2),
				"severity": 0.72,
				"confidence": 0.74,
				"temperature_c": 31.0,
				"precipitation_mm": pd.NA,
				"brightness": pd.NA,
				"vegetation_index": pd.NA,
				"pm25": 58.0,
				"pm10": 91.0,
				"no2": 39.0,
				"o3": 27.0,
				"aqi": 175.0,
				"risk_factors": ("particulate exposure", "urban dispersion"),
				"centroid_lat": -19.92,
				"centroid_lon": -43.94,
				"population": 89000000,
				"payload_weight": 1.0,
			},
		],
	)


@pytest.fixture()
def sample_operational_frame() -> pd.DataFrame:
	"""Return a compact mixed-source operational dataset."""
	return _build_sample_operational_rows()


@pytest.fixture()
def sample_enriched_frame(sample_operational_frame: pd.DataFrame) -> pd.DataFrame:
	"""Return the enriched dataset used by most business-rule tests."""
	return run_enrichment_pipeline(sample_operational_frame)


@pytest.fixture()
def sample_risk_summary(sample_enriched_frame: pd.DataFrame) -> pd.DataFrame:
	"""Return the aggregated risk summary for the sample dataset."""
	return run_risk_scoring_pipeline(sample_enriched_frame)


@pytest.fixture()
def sample_alert_feed(sample_enriched_frame: pd.DataFrame) -> pd.DataFrame:
	"""Return the semantic alert feed for the sample dataset."""
	return build_alert_feed(sample_enriched_frame)


@pytest.fixture()
def sample_filters() -> DashboardFilterViewModel:
	"""Return a representative dashboard filter snapshot."""
	return DashboardFilterViewModel(
		region="Brazil",
		event_types=["Flood", "Queimada", "Qualidade do Ar"],
		period_days=30,
		date_start=None,
		date_end=None,
		risk_level="high",
		threshold=0.75,
	)


@pytest.fixture()
def sample_feature_context(
	sample_operational_frame: pd.DataFrame,
	sample_enriched_frame: pd.DataFrame,
	sample_risk_summary: pd.DataFrame,
	sample_alert_feed: pd.DataFrame,
) -> FeatureContext:
	"""Return a reusable feature context for integration tests."""
	return FeatureContext(
		region="Brazil",
		period_days=30,
		event_types=["Flood", "Queimada", "Qualidade do Ar"],
		raw_events=sample_operational_frame,
		cleaned_events=sample_operational_frame,
		enriched_events=sample_enriched_frame,
		risk_summary=sample_risk_summary,
		alert_feed=sample_alert_feed,
	)


@pytest.fixture(autouse=True)
def isolated_streamlit_state(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
	"""Isolate Streamlit state and reset cached state helpers for every test."""
	state_store: dict[str, object] = {}
	for module in (state_helpers, state_initializer, state_selectors):
		monkeypatch.setattr(module.st, "session_state", state_store, raising=False)

	import streamlit as st

	monkeypatch.setattr(st, "session_state", state_store, raising=False)
	state_initializer.initialize_session_state()
	return state_store


@pytest.fixture(autouse=True)
def clear_cached_callables() -> None:
	"""Clear Streamlit and functools caches used by the application."""
	from features.alerts_center.service import build_alerts_center
	from features.air_quality_monitoring.service import build_air_quality_monitoring
	from features.anomaly_detection.service import build_anomaly_detection
	from features.burning_monitoring.service import build_burning_monitoring
	from features.climate_overview.service import build_climate_overview
	from features.flood_prediction.service import build_flood_prediction
	from features.geospatial_center.service import build_geospatial_center
	from features.human_feedback.service import build_human_feedback
	from features.landslide_prediction.service import build_landslide_prediction
	from features.risk_hotspots.service import build_risk_hotspots
	from features.water_management.service import build_water_management
	from pipelines import alerting_pipeline, cleaning_pipeline, enrichment_pipeline, ingest_pipeline, risk_scoring_pipeline
	from providers import provider_factory
	from ui.pages import context_loader, filtering

	for cached in (
		provider_factory.get_provider_container,
		build_climate_overview,
		build_alerts_center,
		build_risk_hotspots,
		build_anomaly_detection,
		build_human_feedback,
		build_burning_monitoring,
		build_air_quality_monitoring,
		build_water_management,
		build_geospatial_center,
		build_flood_prediction,
		build_landslide_prediction,
		ingest_pipeline.run_ingest_pipeline,
		cleaning_pipeline.run_cleaning_pipeline,
		enrichment_pipeline.run_enrichment_pipeline,
		risk_scoring_pipeline.run_risk_scoring_pipeline,
		alerting_pipeline.build_alert_feed,
		filtering.build_visible_context,
		context_loader.load_operational_context,
		context_loader.load_visible_operational_context,
	):
		clear = getattr(cached, "clear", None)
		if callable(clear):
			clear()
