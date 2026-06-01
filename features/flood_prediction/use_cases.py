"""Use cases for the flood prediction feature."""

from __future__ import annotations

from features.common import FeatureContext
from features.flood_prediction.service import build_flood_prediction


def execute_flood_prediction(context: FeatureContext):
	"""Execute the flood prediction use case."""
	return build_flood_prediction(context)
