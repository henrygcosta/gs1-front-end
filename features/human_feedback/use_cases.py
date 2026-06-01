"""Use cases for the human feedback feature."""

from __future__ import annotations

from features.common import FeatureContext
from features.human_feedback.service import build_human_feedback


def execute_human_feedback(context: FeatureContext, feedback_revision: int = 0):
	"""Execute the human feedback use case."""
	return build_human_feedback(context, feedback_revision=feedback_revision)

