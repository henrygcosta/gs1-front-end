"""Use cases for the climate overview feature."""

from __future__ import annotations

from features.climate_overview.dto import ClimateOverviewRequest, ClimateOverviewViewModel
from features.climate_overview.service import build_climate_overview


def execute_climate_overview(request: ClimateOverviewRequest) -> ClimateOverviewViewModel:
	"""Execute the general dashboard overview use case."""
	feature = build_climate_overview(request.context)
	return ClimateOverviewViewModel(
		headline=feature.headline,
		kpis=[{"label": metric.label, "value": metric.value, "helper": metric.helper or "", "kind": metric.kind} for metric in feature.kpis],
		panorama=feature.panorama,
		critical_indicators=feature.critical_indicators,
		executive_summary=feature.executive_summary,
		narratives=[{"title": block.title, "text": block.text, "kind": block.kind} for block in feature.narratives],
		top_findings=feature.top_findings,
	)

