"""DTOs for the climate overview feature."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from features.common import FeatureContext


@dataclass(frozen=True, slots=True)
class ClimateOverviewRequest:
	"""Input payload for the climate overview use case."""

	context: FeatureContext


@dataclass(frozen=True, slots=True)
class ClimateOverviewViewModel:
	"""UI-friendly view model for the climate overview screen."""

	headline: str
	kpis: list[dict[str, str]]
	panorama: pd.DataFrame
	critical_indicators: pd.DataFrame
	executive_summary: pd.DataFrame
	narratives: list[dict[str, str]]
	top_findings: list[str]

