"""Service layer for the water management feature."""

from __future__ import annotations

import streamlit as st

from features.common import FEATURE_CACHE_KWARGS, FeatureContext
from features.water_management.domain import WaterManagementFeature
from features.water_management.selectors import select_drought_risk, select_narratives, select_reservoirs, select_water_levels


@st.cache_data(show_spinner=False, hash_funcs=FEATURE_CACHE_KWARGS)
def build_water_management(context: FeatureContext) -> WaterManagementFeature:
	"""Build the hydric management view model."""
	return WaterManagementFeature(
		reservoirs=select_reservoirs(context),
		drought_risk=select_drought_risk(context),
		water_levels=select_water_levels(context),
		narratives=select_narratives(context),
	)
