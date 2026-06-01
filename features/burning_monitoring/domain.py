"""Domain models for the burning monitoring feature."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from features.common import NarrativeBlock


@dataclass(frozen=True, slots=True)
class BurningMonitoringFeature:
	"""Wildfire and burning monitoring view model."""

	map_points: pd.DataFrame
	temporal_evolution: pd.DataFrame
	alerts: pd.DataFrame
	narratives: list[NarrativeBlock]
