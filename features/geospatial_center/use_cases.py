"""Use cases for the geospatial center feature."""

from __future__ import annotations

from features.common import FeatureContext
from features.geospatial_center.service import build_geospatial_center


def execute_geospatial_center(context: FeatureContext):
	"""Execute the geospatial center use case."""
	return build_geospatial_center(context)
