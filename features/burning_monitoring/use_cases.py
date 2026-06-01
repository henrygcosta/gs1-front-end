"""Use cases for the burning monitoring feature."""

from __future__ import annotations

from features.burning_monitoring.service import build_burning_monitoring
from features.common import FeatureContext


def execute_burning_monitoring(context: FeatureContext):
	"""Execute the burning monitoring use case."""
	return build_burning_monitoring(context)
