"""Service layer for the climate overview feature."""

from __future__ import annotations

import streamlit as st

from features.climate_overview.domain import ClimateOverviewFeature
from features.climate_overview.selectors import (
	select_critical_indicators,
	select_executive_summary,
	select_kpis,
	select_narratives,
	select_panorama,
)
from features.common import FEATURE_CACHE_KWARGS, FeatureContext, top_findings


@st.cache_data(show_spinner=False, hash_funcs=FEATURE_CACHE_KWARGS)
def build_climate_overview(context: FeatureContext) -> ClimateOverviewFeature:
	"""Build the dashboard overview view model."""
	headline = f"Centro em vigilancia: {len(context.enriched_events)} eventos analisados"
	findings = top_findings(context.enriched_events, limit=4)
	return ClimateOverviewFeature(
		headline=headline,
		kpis=select_kpis(context),
		panorama=select_panorama(context),
		critical_indicators=select_critical_indicators(context),
		executive_summary=select_executive_summary(context),
		narratives=select_narratives(context),
		top_findings=[finding.description for finding in findings],
	)

