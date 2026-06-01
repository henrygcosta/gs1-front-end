"""Selectors for the alerts center feature."""

from __future__ import annotations

import pandas as pd

from features.common import FeatureContext, NarrativeBlock, narrative_blocks_from_findings, top_findings, top_records
from state.selectors import get_approved_alerts, get_dismissed_alerts, get_reviewed_alerts


def select_critical_alerts(context: FeatureContext) -> pd.DataFrame:
	"""Return the most critical alerts for the moderation queue."""
	columns = ["alert_id", "event_id", "event_type", "region", "state", "risk_score", "alert_level", "recommended_action", "timestamp"]
	return top_records(context.alert_feed[columns] if not context.alert_feed.empty else context.alert_feed.head(0).copy(), sort_by="risk_score", limit=10)


def select_moderation_stats(context: FeatureContext) -> dict[str, int]:
	"""Return moderation counts for alert decisions."""
	return {
		"approved": len(get_approved_alerts()),
		"reviewed": len(get_reviewed_alerts()),
		"dismissed": len(get_dismissed_alerts()),
		"critical_queue": len(context.alert_feed),
	}


def select_history(context: FeatureContext) -> pd.DataFrame:
	"""Return a compact alert history table."""
	if context.alert_feed.empty:
		return context.alert_feed.head(0).copy()
	return context.alert_feed[["timestamp", "event_type", "region", "state", "risk_score", "alert_level", "recommended_action"]].copy()


def select_ai_insights(context: FeatureContext) -> list[NarrativeBlock]:
	"""Build AI-style insights from the alert queue."""
	findings = top_findings(context.alert_feed.rename(columns={"event_type": "label"}), label_column="label", limit=4)
	return narrative_blocks_from_findings(findings, prefix="Central de Alertas")


def select_recommendations(context: FeatureContext) -> list[str]:
	"""Return concise recommendations for the alert center."""
	return [finding.description for finding in top_findings(context.alert_feed, limit=4)]

