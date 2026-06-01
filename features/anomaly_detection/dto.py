"""DTOs for the anomaly detection feature."""

from __future__ import annotations

from dataclasses import dataclass

from features.common import FeatureContext


@dataclass(frozen=True, slots=True)
class AnomalyDetectionRequest:
	"""Input payload for anomaly detection use cases."""

	context: FeatureContext

