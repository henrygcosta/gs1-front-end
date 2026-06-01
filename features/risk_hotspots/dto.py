"""DTOs for the risk hotspots feature."""

from __future__ import annotations

from dataclasses import dataclass

from features.common import FeatureContext


@dataclass(frozen=True, slots=True)
class RiskHotspotsRequest:
	"""Input payload for the risk hotspots use case."""

	context: FeatureContext

