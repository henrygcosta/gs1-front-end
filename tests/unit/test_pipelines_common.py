"""Tests for shared pipeline helpers and operational rules."""

from __future__ import annotations

import pandas as pd
import pytest

from pipelines.common import (
	band_geographic_criticality,
	band_score,
	dataframe_cache_key,
	ensure_columns,
	recommendation_for_event,
	risk_alert_level,
)
from utils.exceptions import PipelineError
from utils.time_utils import last_n_days_range, utc_now


def test_dataframe_cache_key_is_stable_for_object_columns() -> None:
	frame = pd.DataFrame({"a": [1, 2], "b": [["x", "y"], ["z"]]})
	assert dataframe_cache_key(frame) == dataframe_cache_key(frame.copy())


@pytest.mark.parametrize(
	("value", "expected"),
	[
		(0.10, "baixa"),
		(0.40, "moderada"),
		(0.60, "alta"),
		(0.95, "critica"),
	],
)
def test_band_score_maps_thresholds(value: float, expected: str) -> None:
	assert band_score(value) == expected


@pytest.mark.parametrize(
	("value", "expected"),
	[
		(0.10, "baixa"),
		(0.40, "media"),
		(0.70, "alta"),
		(0.95, "muito_alta"),
	],
)
def test_band_geographic_criticality_maps_thresholds(value: float, expected: str) -> None:
	assert band_geographic_criticality(value) == expected


@pytest.mark.parametrize(
	("score", "expected"),
	[
		(0.20, "observacao"),
		(0.50, "moderado"),
		(0.75, "alto"),
		(0.90, "critico"),
	],
)
def test_risk_alert_level_maps_semantic_levels(score: float, expected: str) -> None:
	assert risk_alert_level(score) == expected


def test_recommendation_for_event_is_domain_specific() -> None:
	message = recommendation_for_event("Flood", "critico")
	assert "monitoramento hidrologico" in message
	assert "escalar" in message.lower()


def test_ensure_columns_raises_for_missing_columns() -> None:
	frame = pd.DataFrame({"a": [1]})
	with pytest.raises(PipelineError, match="ingest.test: missing required columns: b"):
		ensure_columns(frame, ["a", "b"], stage="ingest.test")


def test_time_range_helper_returns_monotonic_bounds() -> None:
	start, end = last_n_days_range(7)
	assert start < end
	assert end <= utc_now()