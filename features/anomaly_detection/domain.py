"""Domain models for the anomaly detection feature."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from features.common import NarrativeBlock


@dataclass(frozen=True, slots=True)
class AnomalyDetectionFeature:
	"""Anomaly detection and uncertainty analysis view model."""

	low_confidence: pd.DataFrame
	confidence_bands: pd.DataFrame
	text_analysis: list[NarrativeBlock]
	recommendations: list[str]

