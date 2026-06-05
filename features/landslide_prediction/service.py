"""Service layer for the landslide prediction feature."""

from __future__ import annotations

import streamlit as st

from features.common import FEATURE_CACHE_KWARGS, FeatureContext
from features.landslide_prediction.domain import LandslidePredictionFeature
from features.landslide_prediction.selectors import (
	select_emergency_priority,
	select_narratives,
	select_rainfall_correlation,
	select_risk_index,
	select_vulnerable_areas,
)


@st.cache_data(show_spinner=False, hash_funcs=FEATURE_CACHE_KWARGS)
def build_landslide_prediction(context: FeatureContext) -> LandslidePredictionFeature:
	"""Build the landslide prediction view model."""
	return LandslidePredictionFeature(
		vulnerable_areas=select_vulnerable_areas(context),
		risk_index=select_risk_index(context),
		rainfall_correlation=select_rainfall_correlation(context),
		emergency_priority=select_emergency_priority(context),
		narratives=select_narratives(context),
	)
