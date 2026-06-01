"""Domain models for the alerts center feature."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from features.common import NarrativeBlock


@dataclass(frozen=True, slots=True)
class AlertsCenterFeature:
	"""Operational alert center view model."""

	critical_alerts: pd.DataFrame
	moderation_stats: dict[str, int]
	history: pd.DataFrame
	ai_insights: list[NarrativeBlock]
	recommendations: list[str]

