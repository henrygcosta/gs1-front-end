"""Use cases for the water management feature."""

from __future__ import annotations

from features.common import FeatureContext
from features.water_management.service import build_water_management


def execute_water_management(context: FeatureContext):
	"""Execute the water management use case."""
	return build_water_management(context)
