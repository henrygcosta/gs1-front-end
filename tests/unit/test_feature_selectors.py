"""Tests for business selectors in the human feedback feature."""

from __future__ import annotations

from features.human_feedback.selectors import select_history, select_moderation_stats, select_queue
from state.actions import record_alert_moderation


def test_select_queue_excludes_sent_and_dismissed_alerts(sample_feature_context) -> None:
	alert_row = sample_feature_context.alert_feed.iloc[0].to_dict()
	record_alert_moderation(alert_row, decision="approve", observations="ok", confirm_send=True)

	queue = select_queue(sample_feature_context)

	assert alert_row["alert_id"] not in queue["alert_id"].astype(str).tolist()


def test_select_queue_marks_approved_status_and_history_logged(sample_feature_context) -> None:
	alert_row = sample_feature_context.alert_feed.iloc[0].to_dict()
	record_alert_moderation(alert_row, decision="approve", observations="seguir")

	queue = select_queue(sample_feature_context)
	row = queue.loc[queue["alert_id"].astype(str) == str(alert_row["alert_id"])].iloc[0]

	assert row["decision_status"] == "approved"
	assert bool(row["history_logged"]) is True


def test_select_history_and_stats_reflect_session_state(sample_feature_context) -> None:
	alert_row = sample_feature_context.alert_feed.iloc[0].to_dict()
	record_alert_moderation(alert_row, decision="review", observations="validar manualmente")

	history = select_history(sample_feature_context)
	stats = select_moderation_stats(sample_feature_context)

	assert not history.empty
	assert history.iloc[0]["decision"] == "review"
	assert stats["reviewed"] >= 1
	assert stats["queued"] >= 1
