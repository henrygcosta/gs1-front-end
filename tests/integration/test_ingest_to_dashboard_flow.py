"""End-to-end data flow tests from providers to operational context."""

from __future__ import annotations

from ui.charts.operational_visualizations import _macro_region_code
from ui.pages.context_loader import load_visible_operational_context


def test_full_operational_context_contains_pipeline_outputs() -> None:
	visible_context = load_visible_operational_context(
		region="Brazil",
		period_days=7,
		event_types=("Flood", "Storm", "Heatwave", "Landslide", "Queimada", "Qualidade do Ar"),
		date_start=None,
		date_end=None,
		risk_level="all",
		threshold=0.0,
	)

	assert not visible_context.raw_events.empty
	assert not visible_context.enriched_events.empty
	assert not visible_context.risk_summary.empty
	assert not visible_context.alert_feed.empty
	assert set(visible_context.event_types) == {"Flood", "Storm", "Heatwave", "Landslide", "Queimada", "Qualidade do Ar"}
	assert visible_context.enriched_events.apply(_macro_region_code, axis=1).dropna().isin(["BR", "AM", "NE", "SE", "MT", "CO"]).any()
