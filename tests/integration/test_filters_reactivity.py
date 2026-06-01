"""Integration tests for filter reactivity and visible context slicing."""

from __future__ import annotations

from ui.pages.context_loader import load_visible_operational_context


def test_risk_threshold_filter_reduces_visible_events() -> None:
	full_context = load_visible_operational_context(
		region="Brazil",
		period_days=30,
		event_types=("Flood", "Queimada", "Qualidade do Ar"),
		date_start=None,
		date_end=None,
		risk_level="all",
		threshold=0.0,
	)
	high_context = load_visible_operational_context(
		region="Brazil",
		period_days=30,
		event_types=("Flood", "Queimada", "Qualidade do Ar"),
		date_start=None,
		date_end=None,
		risk_level="critical",
		threshold=0.85,
	)

	assert len(high_context.enriched_events) <= len(full_context.enriched_events)
	assert (high_context.enriched_events["risk_score"] >= 0.85).all()


def test_event_type_filter_limits_visible_event_types() -> None:
	context = load_visible_operational_context(
		region="Brazil",
		period_days=30,
		event_types=("Flood",),
		date_start=None,
		date_end=None,
		risk_level="all",
		threshold=0.0,
	)

	assert set(context.enriched_events["event_type"].unique()).issubset({"Flood"})
