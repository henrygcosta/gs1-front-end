"""Service layer for the flood prediction feature."""

from __future__ import annotations

import streamlit as st

from features.common import FEATURE_CACHE_KWARGS, FeatureContext
from features.flood_prediction.domain import FloodPredictionFeature
from features.flood_prediction.selectors import select_high_risk_regions, select_narratives, select_preventive_alerts, select_severity, select_temporal_evolution


@st.cache_data(show_spinner=False, hash_funcs=FEATURE_CACHE_KWARGS)
def build_flood_prediction(context: FeatureContext) -> FloodPredictionFeature:
	"""Build the flood prediction view model."""
	return FloodPredictionFeature(
		high_risk_regions=select_high_risk_regions(context),
		temporal_evolution=select_temporal_evolution(context),
		severity=select_severity(context),
		preventive_alerts=select_preventive_alerts(context),
		narratives=select_narratives(context),
	)
