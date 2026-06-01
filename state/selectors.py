"""Read-only selectors for session state."""

from __future__ import annotations

import streamlit as st

from state.models import AlertState, CacheState, DashboardFilterState, LoadingState, NavigationState, ThresholdState, UserPreferencesState
from state.session_keys import SessionKey


def get_selected_region() -> str:
	"""Return the selected region."""
	return str(st.session_state[SessionKey.SELECTED_REGION.value])


def get_selected_event_types() -> list[str]:
	"""Return selected event types."""
	return list(st.session_state[SessionKey.SELECTED_EVENT_TYPES.value])


def get_selected_period_days() -> int:
	"""Return selected period in days."""
	return int(st.session_state[SessionKey.SELECTED_PERIOD_DAYS.value])


def get_selected_date_range() -> tuple[str | None, str | None]:
	"""Return selected date range."""
	return (
		st.session_state.get(SessionKey.SELECTED_DATE_START.value),
		st.session_state.get(SessionKey.SELECTED_DATE_END.value),
	)


def get_selected_risk_level() -> str:
	"""Return selected risk level."""
	return str(st.session_state.get(SessionKey.SELECTED_RISK_LEVEL.value, "all"))


def get_selected_threshold() -> float:
	"""Return the main operational threshold."""
	return float(st.session_state.get(SessionKey.SELECTED_THRESHOLD.value, 0.0))


def get_loading_flags() -> dict[str, bool]:
	"""Return loading flags by block id."""
	return dict(st.session_state[SessionKey.LOADING_FLAGS.value])


def get_error_flags() -> dict[str, str]:
	"""Return error flags by block id."""
	return dict(st.session_state[SessionKey.ERROR_FLAGS.value])


def get_filters_state() -> DashboardFilterState:
	"""Return the canonical filter snapshot."""
	filters = dict(st.session_state.get(SessionKey.FILTERS.value, {}) or {})
	return DashboardFilterState(
		region=str(filters.get("region", st.session_state.get(SessionKey.SELECTED_REGION.value, "Global"))),
		event_types=list(filters.get("event_types", st.session_state.get(SessionKey.SELECTED_EVENT_TYPES.value, []))),
		period_days=int(filters.get("period_days", st.session_state.get(SessionKey.SELECTED_PERIOD_DAYS.value, 30))),
		date_start=filters.get("date_start", st.session_state.get(SessionKey.SELECTED_DATE_START.value)),
		date_end=filters.get("date_end", st.session_state.get(SessionKey.SELECTED_DATE_END.value)),
		risk_level=str(filters.get("risk_level", st.session_state.get(SessionKey.SELECTED_RISK_LEVEL.value, "all"))),
		threshold=float(filters.get("threshold", st.session_state.get(SessionKey.SELECTED_THRESHOLD.value, 0.0))),
	)


def get_thresholds_state() -> ThresholdState:
	"""Return the configured threshold snapshot."""
	thresholds = dict(st.session_state.get(SessionKey.THRESHOLDS.value, {}) or {})
	return ThresholdState(
		risk=float(thresholds.get("risk", 0.75)),
		confidence=float(thresholds.get("confidence", 0.60)),
		geographic_criticality=float(thresholds.get("geographic_criticality", 0.70)),
		priority=float(thresholds.get("priority", 0.65)),
	)


def get_preferences_state() -> UserPreferencesState:
	"""Return the current user preferences snapshot."""
	preferences = dict(st.session_state.get(SessionKey.PREFERENCES.value, {}) or {})
	return UserPreferencesState(
		theme_mode=str(preferences.get("theme_mode", "system")),
		language=str(preferences.get("language", "pt-BR")),
		auto_refresh=bool(preferences.get("auto_refresh", True)),
		show_advanced_metrics=bool(preferences.get("show_advanced_metrics", True)),
		items_per_page=int(preferences.get("items_per_page", 20)),
	)


def get_theme_state() -> dict[str, str]:
	"""Return the current theme dictionary."""
	return dict(st.session_state.get(SessionKey.THEME.value, {}) or {})


def get_cache_state() -> CacheState:
	"""Return the local cache snapshot."""
	cache = dict(st.session_state.get(SessionKey.CACHE.value, {}) or {})
	return CacheState(values=dict(cache.get("values", cache)), version=str(cache.get("version", "v1")))


def get_navigation_state() -> NavigationState:
	"""Return navigation state."""
	navigation = dict(st.session_state.get(SessionKey.NAVIGATION.value, {}) or {})
	return NavigationState(
		active_tab=str(navigation.get("active_tab", st.session_state.get(SessionKey.ACTIVE_TAB.value, "Overview"))),
		current_page=str(navigation.get("current_page", "dashboard")),
		history=list(navigation.get("history", [])),
	)


def get_approved_alerts() -> list[str]:
	"""Return approved alert ids."""
	return list(st.session_state.get(SessionKey.APPROVED_ALERTS.value, []))


def get_reviewed_alerts() -> list[str]:
	"""Return reviewed alert ids."""
	return list(st.session_state.get(SessionKey.REVIEWED_ALERTS.value, []))


def get_dismissed_alerts() -> list[str]:
	"""Return dismissed alert ids."""
	return list(st.session_state.get(SessionKey.DISMISSED_ALERTS.value, []))


def get_feedback_queue() -> list[dict[str, object]]:
	"""Return queued feedback entries."""
	return list(st.session_state.get(SessionKey.FEEDBACK_QUEUE.value, []))


def get_feedback_history() -> list[dict[str, object]]:
	"""Return the historical list of alert moderation records."""
	return list(st.session_state.get(SessionKey.FEEDBACK_HISTORY.value, []))


def get_feedback_revision() -> int:
	"""Return the feedback cache revision."""
	return int(st.session_state.get(SessionKey.FEEDBACK_REVISION.value, 0) or 0)


def get_sent_alerts() -> list[str]:
	"""Return alert ids that have already been confirmed for sending."""
	return list(st.session_state.get(SessionKey.SENT_ALERTS.value, []))


def get_session_snapshot() -> dict[str, object]:
	"""Return a flat debug snapshot of the main state groups."""
	return {
		"filters": get_filters_state(),
		"thresholds": get_thresholds_state(),
		"preferences": get_preferences_state(),
		"theme": get_theme_state(),
		"cache": get_cache_state(),
		"navigation": get_navigation_state(),
		"alerts": AlertState(
			approved_alerts=get_approved_alerts(),
			reviewed_alerts=get_reviewed_alerts(),
			dismissed_alerts=get_dismissed_alerts(),
		),
		"feedback_history": get_feedback_history(),
		"sent_alerts": get_sent_alerts(),
		"loading": LoadingState(flags=get_loading_flags()),
	}
