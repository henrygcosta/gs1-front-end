"""Use cases for the air quality monitoring feature."""

from __future__ import annotations

from features.air_quality_monitoring.service import build_air_quality_monitoring
from features.common import FeatureContext


def execute_air_quality_monitoring(context: FeatureContext):
	"""Execute the air quality monitoring use case."""
	return build_air_quality_monitoring(context)
