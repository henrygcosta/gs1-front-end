"""DTOs for the flood prediction feature."""

from __future__ import annotations

from dataclasses import dataclass

from features.common import FeatureContext


@dataclass(frozen=True, slots=True)
class FloodPredictionRequest:
	"""Input payload for the flood prediction use case."""

	context: FeatureContext
