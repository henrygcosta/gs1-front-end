"""DTOs for the landslide prediction feature."""

from __future__ import annotations

from dataclasses import dataclass

from features.common import FeatureContext


@dataclass(frozen=True, slots=True)
class LandslidePredictionRequest:
	"""Input payload for the landslide prediction use case."""

	context: FeatureContext
