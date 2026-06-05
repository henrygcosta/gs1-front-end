"""Service layer for the risk hotspots feature."""

from __future__ import annotations

import streamlit as st

from features.common import FEATURE_CACHE_KWARGS, FeatureContext
from features.risk_hotspots.domain import RiskHotspotsFeature
from features.risk_hotspots.selectors import (
	select_alert_distribution,
	select_heatmap,
	select_map_points,
	select_narratives,
	select_regional_summary,
)


@st.cache_data(show_spinner=False, hash_funcs=FEATURE_CACHE_KWARGS)
def build_risk_hotspots(context: FeatureContext) -> RiskHotspotsFeature:
	"""Build the geospatial hotspot view model."""
	return RiskHotspotsFeature(
		map_points=select_map_points(context),
		regional_summary=select_regional_summary(context),
		heatmap=select_heatmap(context),
		alert_distribution=select_alert_distribution(context),
		narratives=select_narratives(context),
	)

