"""Domain models for the human feedback feature."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from features.common import NarrativeBlock


@dataclass(frozen=True, slots=True)
class HumanFeedbackFeature:
	"""Human moderation and review view model."""

	queue: pd.DataFrame
	moderation_stats: dict[str, int]
	history: pd.DataFrame
	narratives: list[NarrativeBlock]

