"""Use cases for the landslide prediction feature."""

from __future__ import annotations

from features.common import FeatureContext
from features.landslide_prediction.service import build_landslide_prediction


def execute_landslide_prediction(context: FeatureContext):
	"""Execute the landslide prediction use case."""
	return build_landslide_prediction(context)
