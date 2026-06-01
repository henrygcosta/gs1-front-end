"""Service layer for the geospatial center feature."""

from __future__ import annotations

import streamlit as st

from features.common import FEATURE_CACHE_KWARGS, FeatureContext
from features.geospatial_center.domain import GeospatialCenterFeature
from features.geospatial_center.selectors import select_alert_distribution, select_critical_regions, select_heatmaps, select_interactive_maps, select_narratives, select_spatial_risk


@st.cache_data(show_spinner=False, hash_funcs=FEATURE_CACHE_KWARGS)
def build_geospatial_center(context: FeatureContext) -> GeospatialCenterFeature:
	"""Build the geospatial operations view model."""
	return GeospatialCenterFeature(
		interactive_maps=select_interactive_maps(context),
		spatial_risk=select_spatial_risk(context),
		critical_regions=select_critical_regions(context),
		heatmaps=select_heatmaps(context),
		alert_distribution=select_alert_distribution(context),
		narratives=select_narratives(context),
	)
