"""Selectors for the human feedback feature."""

from __future__ import annotations

import pandas as pd

from features.common import (
	FeatureContext,
	NarrativeBlock,
	narrative_blocks_from_findings,
	top_findings,
)
from state.selectors import (
	get_approved_alerts,
	get_dismissed_alerts,
	get_feedback_history,
	get_reviewed_alerts,
	get_sent_alerts,
)


def select_queue(context: FeatureContext | None = None) -> pd.DataFrame:
	"""Return the actionable alert queue for the current session."""
	if context is None:
		return pd.DataFrame(columns=["alert_id", "event_id", "event_type", "region", "state", "alert_level", "risk_score", "recommended_action", "alert_title", "alert_message"])
	queue = context.alert_feed.copy()
	if queue.empty:
		return queue.head(0).copy()
	approved_ids = set(get_approved_alerts())
	reviewed_ids = set(get_reviewed_alerts())
	dismissed_ids = set(get_dismissed_alerts())
	sent_ids = set(get_sent_alerts())
	history_ids = {str(item.get("alert_id", item.get("event_id", ""))) for item in get_feedback_history()}
	if "alert_id" in queue.columns:
		queue = queue.loc[~queue["alert_id"].astype(str).isin(sent_ids | dismissed_ids)].copy()
		queue.loc[:, "decision_status"] = queue["alert_id"].astype(str).map(
			lambda alert_id: "approved" if alert_id in approved_ids else "reviewed" if alert_id in reviewed_ids else "dismissed" if alert_id in dismissed_ids else "pending"
		)
		queue.loc[:, "history_logged"] = queue["alert_id"].astype(str).isin(history_ids)
	queue = queue.sort_values(["risk_score", "timestamp"], ascending=[False, False])
	columns = [column for column in ["alert_id", "event_id", "event_type", "region", "state", "alert_level", "risk_score", "recommended_action", "alert_title", "alert_message", "timestamp", "confidence", "geographic_criticality_score", "decision_status", "history_logged"] if column in queue.columns]
	return queue[columns].copy()


def select_moderation_stats(context: FeatureContext) -> dict[str, int]:
	"""Return the moderation summary for the current session."""
	return {
		"approved": len(get_approved_alerts()),
		"reviewed": len(get_reviewed_alerts()),
		"dismissed": len(get_dismissed_alerts()),
		"sent": len(get_sent_alerts()),
		"queued": len(select_queue(context)),
	}


def select_history(context: FeatureContext) -> pd.DataFrame:
	"""Return a compact moderation history based on the queue and current alerts."""
	history = get_feedback_history()
	if not history:
		return pd.DataFrame(columns=["alert_id", "event_id", "decision", "observations", "confirm_send", "status", "created_at", "title", "region", "state", "event_type", "alert_level", "risk_score"])
	frame = pd.DataFrame(history)
	return frame.sort_values("created_at", ascending=False).reset_index(drop=True)


def select_narratives(context: FeatureContext) -> list[NarrativeBlock]:
	"""Build human review insights."""
	return narrative_blocks_from_findings(top_findings(context.alert_feed, limit=3), prefix="Revisao Humana")

