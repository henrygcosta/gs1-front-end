"""Domain models for the air quality monitoring feature."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from features.common import NarrativeBlock


@dataclass(frozen=True, slots=True)
class AirQualityMonitoringFeature:
	"""Air quality monitoring and trend analysis view model."""

	indices: pd.DataFrame
	regional_comparisons: pd.DataFrame
	trend: pd.DataFrame
	narratives: list[NarrativeBlock]
