"""Domain models for the water management feature."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from features.common import NarrativeBlock


@dataclass(frozen=True, slots=True)
class WaterManagementFeature:
	"""Hydric management and drought view model."""

	reservoirs: pd.DataFrame
	drought_risk: pd.DataFrame
	water_levels: pd.DataFrame
	narratives: list[NarrativeBlock]
