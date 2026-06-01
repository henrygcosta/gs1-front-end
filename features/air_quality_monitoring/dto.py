"""DTOs for the air quality monitoring feature."""

from __future__ import annotations

from dataclasses import dataclass

from features.common import FeatureContext


@dataclass(frozen=True, slots=True)
class AirQualityMonitoringRequest:
	"""Input payload for the air quality monitoring use case."""

	context: FeatureContext
