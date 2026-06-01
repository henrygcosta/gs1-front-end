"""Smoke tests for empty and error states in the core rules."""

from __future__ import annotations

import pandas as pd
import pytest

from pipelines.common import ensure_columns
from pipelines.risk_scoring_pipeline import run_risk_scoring_pipeline
from utils.exceptions import PipelineError


def test_empty_risk_summary_has_the_expected_schema() -> None:
	empty = run_risk_scoring_pipeline(pd.DataFrame())

	assert empty.empty
	assert "alert_title" in empty.columns


def test_missing_required_columns_raise_pipeline_error() -> None:
	with pytest.raises(PipelineError, match="missing required columns"):
		ensure_columns(pd.DataFrame({"a": [1]}), ["a", "b"], stage="unit.test")
