"""DTOs for the water management feature."""

from __future__ import annotations

from dataclasses import dataclass

from features.common import FeatureContext


@dataclass(frozen=True, slots=True)
class WaterManagementRequest:
	"""Input payload for the water management use case."""

	context: FeatureContext
