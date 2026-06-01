"""Integration tests for human-in-the-loop feedback persistence."""

from __future__ import annotations

from features.human_feedback.use_cases import execute_human_feedback
from state.actions import record_alert_moderation


def test_approval_confirmation_removes_alert_from_queue(sample_feature_context) -> None:
	alert_row = sample_feature_context.alert_feed.iloc[0].to_dict()
	record_alert_moderation(alert_row, decision="approve", observations="ok")
	record_alert_moderation(alert_row, decision="approve", observations="enviado", confirm_send=True)

	feature_vm = execute_human_feedback(sample_feature_context)

	assert alert_row["alert_id"] not in feature_vm.queue["alert_id"].astype(str).tolist()
	assert feature_vm.moderation_stats["sent"] >= 1
	assert feature_vm.history.iloc[0]["confirm_send"] in {True, False}


def test_rejection_persists_history_and_keeps_state_consistent(sample_feature_context) -> None:
	alert_row = sample_feature_context.alert_feed.iloc[0].to_dict()
	record_alert_moderation(alert_row, decision="dismiss", observations="falso positivo")

	feature_vm = execute_human_feedback(sample_feature_context)

	assert feature_vm.history.iloc[0]["decision"] == "dismiss"
	assert alert_row["alert_id"] not in feature_vm.queue["alert_id"].astype(str).tolist()
