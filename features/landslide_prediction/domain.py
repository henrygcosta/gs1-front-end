"""Domain models for the landslide prediction feature."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from features.common import NarrativeBlock


@dataclass(frozen=True, slots=True)
class LandslidePredictionFeature:
	"""Landslide prediction and emergency prioritization view model."""

	vulnerable_areas: pd.DataFrame
	risk_index: pd.DataFrame
	rainfall_correlation: pd.DataFrame
	emergency_priority: pd.DataFrame
	narratives: list[NarrativeBlock]
