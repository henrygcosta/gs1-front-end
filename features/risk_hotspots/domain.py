"""Domain models for the risk hotspots feature."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from features.common import NarrativeBlock


@dataclass(frozen=True, slots=True)
class RiskHotspotsFeature:
	"""Geospatial risk hotspot view model."""

	map_points: pd.DataFrame
	regional_summary: pd.DataFrame
	heatmap: pd.DataFrame
	alert_distribution: pd.DataFrame
	narratives: list[NarrativeBlock]

