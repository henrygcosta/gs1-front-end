"""View model structures derived from session state."""

from __future__ import annotations

from dataclasses import dataclass

from state import selectors


@dataclass(slots=True)
class DashboardFilterViewModel:
	"""Immutable filter values consumed by use cases and UI."""

	region: str
	event_types: list[str]
	period_days: int
	date_start: str | None = None
	date_end: str | None = None
	risk_level: str = "all"
	threshold: float = 0.0


def build_dashboard_filter_view_model() -> DashboardFilterViewModel:
	"""Build typed filter view model from session selectors."""
	filters = selectors.get_filters_state()
	return DashboardFilterViewModel(
		region=filters.region,
		event_types=filters.event_types,
		period_days=filters.period_days,
		date_start=filters.date_start,
		date_end=filters.date_end,
		risk_level=filters.risk_level,
		threshold=filters.threshold,
	)
