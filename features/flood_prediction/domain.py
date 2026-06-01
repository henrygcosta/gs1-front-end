"""Domain models for the flood prediction feature."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from features.common import NarrativeBlock


@dataclass(frozen=True, slots=True)
class FloodPredictionFeature:
	"""Flood prediction and prevention view model."""

	high_risk_regions: pd.DataFrame
	temporal_evolution: pd.DataFrame
	severity: pd.DataFrame
	preventive_alerts: pd.DataFrame
	narratives: list[NarrativeBlock]
