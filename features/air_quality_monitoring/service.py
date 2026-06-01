"""Service layer for the air quality monitoring feature."""

from __future__ import annotations

import streamlit as st

from features.air_quality_monitoring.domain import AirQualityMonitoringFeature
from features.air_quality_monitoring.selectors import select_indices, select_narratives, select_regional_comparisons, select_trend
from features.common import FEATURE_CACHE_KWARGS, FeatureContext


@st.cache_data(show_spinner=False, hash_funcs=FEATURE_CACHE_KWARGS)
def build_air_quality_monitoring(context: FeatureContext) -> AirQualityMonitoringFeature:
	"""Build the air quality monitoring view model."""
	return AirQualityMonitoringFeature(
		indices=select_indices(context),
		regional_comparisons=select_regional_comparisons(context),
		trend=select_trend(context),
		narratives=select_narratives(context),
	)
