"""Tests for the risk scoring aggregation pipeline."""

from __future__ import annotations

import pandas as pd

from pipelines.risk_scoring_pipeline import run_risk_scoring_pipeline


def test_risk_scoring_pipeline_builds_expected_summary(sample_enriched_frame: pd.DataFrame) -> None:
	summary = run_risk_scoring_pipeline(sample_enriched_frame)

	assert set(summary["event_type"]) == {"Flood", "Queimada", "Qualidade do Ar"}
	assert set(["total_events", "avg_risk_score", "priority_rank", "alert_title"]).issubset(summary.columns)
	assert summary.loc[summary["event_type"] == "Flood", "alert_level"].iloc[0] in {"alto", "critico", "moderado"}
	assert sorted(summary["priority_rank"].tolist()) == [1, 2, 3]
	assert summary.iloc[0]["avg_risk_score"] >= summary.iloc[-1]["avg_risk_score"]


def test_risk_scoring_pipeline_handles_empty_frames() -> None:
	empty = run_risk_scoring_pipeline(pd.DataFrame())

	assert empty.empty
	assert list(empty.columns) == [
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
