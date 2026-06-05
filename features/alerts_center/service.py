"""Service layer for the alerts center feature."""

from __future__ import annotations

import streamlit as st

from features.alerts_center.domain import AlertsCenterFeature
from features.alerts_center.selectors import (
	select_ai_insights,
	select_critical_alerts,
	select_history,
	select_moderation_stats,
	select_recommendations,
)
from features.common import FEATURE_CACHE_KWARGS, FeatureContext


@st.cache_data(show_spinner=False, hash_funcs=FEATURE_CACHE_KWARGS)
def build_alerts_center(context: FeatureContext) -> AlertsCenterFeature:
	"""Build the alert center view model."""
	return AlertsCenterFeature(
		critical_alerts=select_critical_alerts(context),
		moderation_stats=select_moderation_stats(context),
		history=select_history(context),
		ai_insights=select_ai_insights(context),
		recommendations=select_recommendations(context),
	)

