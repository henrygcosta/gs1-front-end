"""Use cases for the anomaly detection feature."""

from __future__ import annotations

from features.anomaly_detection.service import build_anomaly_detection
from features.common import FeatureContext


def execute_anomaly_detection(context: FeatureContext):
	"""Execute the anomaly detection use case."""
	return build_anomaly_detection(context)

