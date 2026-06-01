"""DTOs for the human feedback feature."""

from __future__ import annotations

from dataclasses import dataclass

from features.common import FeatureContext


@dataclass(frozen=True, slots=True)
class HumanFeedbackRequest:
	"""Input payload for the human feedback use case."""

	context: FeatureContext

