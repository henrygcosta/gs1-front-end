"""DTOs for the alerts center feature."""

from __future__ import annotations

from dataclasses import dataclass

from features.common import FeatureContext


@dataclass(frozen=True, slots=True)
class AlertsCenterRequest:
	"""Input payload for the alerts center use case."""

	context: FeatureContext

