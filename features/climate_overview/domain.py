"""Domain models for the climate overview feature."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from features.common import MetricCard, NarrativeBlock


@dataclass(frozen=True, slots=True)
class ClimateOverviewFeature:
	"""Bundle of outputs used by the general dashboard."""

	headline: str
	kpis: list[MetricCard]
	panorama: pd.DataFrame
	critical_indicators: pd.DataFrame
	executive_summary: pd.DataFrame
	narratives: list[NarrativeBlock]
	top_findings: list[str]

