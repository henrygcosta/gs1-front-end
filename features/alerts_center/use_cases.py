"""Use cases for the alerts center feature."""

from __future__ import annotations

from features.alerts_center.dto import AlertsCenterRequest
from features.alerts_center.service import build_alerts_center


def execute_alerts_center(request: AlertsCenterRequest):
	"""Execute the alerts center use case."""
	return build_alerts_center(request.context)

