"""Service layer for the human feedback feature."""

from __future__ import annotations

import streamlit as st

from features.common import FEATURE_CACHE_KWARGS, FeatureContext
from features.human_feedback.domain import HumanFeedbackFeature
from features.human_feedback.selectors import select_history, select_moderation_stats, select_narratives, select_queue


@st.cache_data(show_spinner=False, hash_funcs=FEATURE_CACHE_KWARGS)
def build_human_feedback(context: FeatureContext, feedback_revision: int = 0) -> HumanFeedbackFeature:
	"""Build the feedback moderation view model."""
	return HumanFeedbackFeature(
		queue=select_queue(context),
		moderation_stats=select_moderation_stats(context),
		history=select_history(context),
		narratives=select_narratives(context),
	)

