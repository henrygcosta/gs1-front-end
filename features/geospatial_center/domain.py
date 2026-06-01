"""Domain models for the geospatial center feature."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from features.common import NarrativeBlock


@dataclass(frozen=True, slots=True)
class GeospatialCenterFeature:
	"""Interactive geospatial operations view model."""

	interactive_maps: pd.DataFrame
	spatial_risk: pd.DataFrame
	critical_regions: pd.DataFrame
	heatmaps: pd.DataFrame
	alert_distribution: pd.DataFrame
	narratives: list[NarrativeBlock]
