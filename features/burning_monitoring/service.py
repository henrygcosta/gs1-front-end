"""Service layer for the burning monitoring feature."""

from __future__ import annotations

import streamlit as st

from features.burning_monitoring.domain import BurningMonitoringFeature
from features.burning_monitoring.selectors import (
	select_alerts,
	select_fire_events,
	select_narratives,
	select_temporal_evolution,
)
from features.common import FEATURE_CACHE_KWARGS, FeatureContext


@st.cache_data(show_spinner=False, hash_funcs=FEATURE_CACHE_KWARGS)
def build_burning_monitoring(context: FeatureContext) -> BurningMonitoringFeature:
	"""Build the burning monitoring view model."""
	return BurningMonitoringFeature(
		map_points=select_fire_events(context),
		temporal_evolution=select_temporal_evolution(context),
		alerts=select_alerts(context),
		narratives=select_narratives(context),
	)
