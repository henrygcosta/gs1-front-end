"""Use cases for the risk hotspots feature."""

from __future__ import annotations

from features.common import FeatureContext
from features.risk_hotspots.service import build_risk_hotspots


def execute_risk_hotspots(context: FeatureContext):
	"""Execute the hotspot analysis use case."""
	return build_risk_hotspots(context)

