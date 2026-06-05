"""Service layer for the anomaly detection feature."""

from __future__ import annotations

import streamlit as st

from features.anomaly_detection.domain import AnomalyDetectionFeature
from features.anomaly_detection.selectors import (
	select_confidence_bands,
	select_low_confidence,
	select_recommendations,
	select_text_analysis,
)
from features.common import FEATURE_CACHE_KWARGS, FeatureContext


@st.cache_data(show_spinner=False, hash_funcs=FEATURE_CACHE_KWARGS)
def build_anomaly_detection(context: FeatureContext) -> AnomalyDetectionFeature:
	"""Build the anomaly detection view model."""
	return AnomalyDetectionFeature(
		low_confidence=select_low_confidence(context),
		confidence_bands=select_confidence_bands(context),
		text_analysis=select_text_analysis(context),
		recommendations=select_recommendations(context),
	)

