"""Centralized session state keys."""

from __future__ import annotations

from enum import StrEnum


class SessionKey(StrEnum):
	"""Named keys used in st.session_state."""

	FILTERS = "filters"
	SELECTED_REGION = "selected_region"
	SELECTED_EVENT_TYPES = "selected_event_types"
	SELECTED_PERIOD_DAYS = "selected_period_days"
	SELECTED_DATE_START = "selected_date_start"
	SELECTED_DATE_END = "selected_date_end"
	SELECTED_RISK_LEVEL = "selected_risk_level"
	SELECTED_THRESHOLD = "selected_threshold"
	THRESHOLDS = "thresholds"
	PREFERENCES = "preferences"
	THEME = "theme"
	CACHE = "cache"
	ACTIVE_TAB = "active_tab"
	NAVIGATION = "navigation"
	APPROVED_ALERTS = "approved_alerts"
	REVIEWED_ALERTS = "reviewed_alerts"
	DISMISSED_ALERTS = "dismissed_alerts"
	FEEDBACK_HISTORY = "feedback_history"
	SENT_ALERTS = "sent_alerts"
	FEEDBACK_QUEUE = "feedback_queue"
	FEEDBACK_REVISION = "feedback_revision"
	LOADING_FLAGS = "loading_flags"
	ERROR_FLAGS = "error_flags"
	PIPELINE_RUN_ID = "pipeline_run_id"
