"""DTOs for the burning monitoring feature."""

from __future__ import annotations

from dataclasses import dataclass

from features.common import FeatureContext


@dataclass(frozen=True, slots=True)
class BurningMonitoringRequest:
	"""Input payload for the burning monitoring use case."""

	context: FeatureContext
