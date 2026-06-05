"""Tests for session-state mutation actions and feedback persistence."""

from __future__ import annotations

from state.actions import (
	dismiss_alert,
	record_alert_moderation,
	reset_filters,
	review_alert,
	set_selected_event_types,
)
from state.selectors import (
	get_approved_alerts,
	get_dismissed_alerts,
	get_feedback_history,
	get_filters_state,
	get_reviewed_alerts,
	get_sent_alerts,
)


def test_record_alert_moderation_persists_history_and_sent_alert(sample_alert_feed) -> None:
	alert_row = sample_alert_feed.iloc[0].to_dict()
	record = record_alert_moderation(alert_row, decision="approve", observations="Enviar para defesa civil", confirm_send=True)

	assert record["status"] == "approved"
	assert record["confirm_send"] is True
	assert alert_row["alert_id"] in get_approved_alerts()
	assert alert_row["alert_id"] in get_sent_alerts()
	assert get_feedback_history()[-1]["observations"] == "Enviar para defesa civil"


def test_record_alert_moderation_review_and_dismiss_update_state(sample_alert_feed) -> None:
	alert_row = sample_alert_feed.iloc[0].to_dict()
	review_alert(alert_row["alert_id"])
	dismiss_alert(alert_row["alert_id"])

	assert alert_row["alert_id"] in get_dismissed_alerts()
	assert alert_row["alert_id"] not in get_approved_alerts()
	assert alert_row["alert_id"] not in get_reviewed_alerts()


def test_reset_filters_restores_default_operational_state() -> None:
	set_selected_event_types(["Flood"])
	reset_filters()

	filters = get_filters_state()
	assert filters.risk_level == "all"
	assert filters.threshold == 0.0
	assert filters.period_days == 30
	assert filters.event_types == ["Flood", "Storm", "Heatwave", "Landslide", "Queimada", "Qualidade do Ar"]
