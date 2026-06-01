"""DTOs for the geospatial center feature."""

from __future__ import annotations

from dataclasses import dataclass

from features.common import FeatureContext


@dataclass(frozen=True, slots=True)
class GeospatialCenterRequest:
	"""Input payload for the geospatial center use case."""

	context: FeatureContext
