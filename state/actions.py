"""State mutation actions for Streamlit session state."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from state.helpers import (
	append_to_state_list,
	append_unique_to_state_list,
	get_state_value,
	mutate_state_mapping,
	remove_from_state_list,
	set_state_value_if_changed,
)
from state.models import DashboardFilterState, NavigationState, ThresholdState, UserPreferencesState
from state.session_keys import SessionKey
from utils.time_utils import utc_now
from utils.config import get_settings
from state.persistence import save_feedback
from uuid import uuid4


def set_selected_region(region: str) -> None:
	"""Update selected region in session state."""
	set_state_value_if_changed(SessionKey.SELECTED_REGION.value, region)
	_update_filters(region=region)


def set_selected_event_types(event_types: list[str]) -> None:
	"""Update selected event types in session state."""
	set_state_value_if_changed(SessionKey.SELECTED_EVENT_TYPES.value, list(event_types))
	_update_filters(event_types=list(event_types))


def set_selected_period_days(days: int) -> None:
	"""Update selected period in days."""
	set_state_value_if_changed(SessionKey.SELECTED_PERIOD_DAYS.value, int(days))
	_update_filters(period_days=int(days))


def set_selected_date_range(start_date: str | None, end_date: str | None) -> None:
	"""Update the active date range."""
	set_state_value_if_changed(SessionKey.SELECTED_DATE_START.value, start_date)
	set_state_value_if_changed(SessionKey.SELECTED_DATE_END.value, end_date)
	_update_filters(date_start=start_date, date_end=end_date)


def set_active_tab(tab_name: str) -> None:
	"""Persist current active tab."""
	set_state_value_if_changed(SessionKey.ACTIVE_TAB.value, tab_name)
	update_navigation(active_tab=tab_name)


def set_active_page(page_name: str) -> None:
	"""Persist the logical page route."""
	update_navigation(current_page=page_name)


def set_filter_threshold(threshold: float) -> None:
	"""Persist the main operational threshold."""
	set_state_value_if_changed(SessionKey.SELECTED_THRESHOLD.value, float(threshold))
	_update_filters(threshold=float(threshold))


def set_selected_risk_level(risk_level: str) -> None:
	"""Persist the selected risk level."""
	set_state_value_if_changed(SessionKey.SELECTED_RISK_LEVEL.value, risk_level)
	_update_filters(risk_level=risk_level)


def set_thresholds(thresholds: ThresholdState) -> None:
	"""Persist structured threshold preferences."""
	set_state_value_if_changed(SessionKey.THRESHOLDS.value, asdict(thresholds))
	set_filter_threshold(thresholds.priority)


def update_preferences(**changes: Any) -> None:
	"""Merge preference changes into the session state."""
	current = dict(get_state_value(SessionKey.PREFERENCES.value, asdict(UserPreferencesState())) or {})
	current.update(changes)
	set_state_value_if_changed(SessionKey.PREFERENCES.value, current)


def set_theme_mode(mode: str) -> None:
	"""Persist the theme mode preference."""
	set_state_value_if_changed(SessionKey.THEME.value, {**dict(get_state_value(SessionKey.THEME.value, {}) or {}), "mode": mode})
	update_preferences(theme_mode=mode)


def set_theme_accent(accent: str) -> None:
	"""Persist the theme accent preference."""
	current = dict(get_state_value(SessionKey.THEME.value, {}) or {})
	current["accent"] = accent
	set_state_value_if_changed(SessionKey.THEME.value, current)


def set_cached_value(cache_key: str, value: Any) -> None:
	"""Store a local cache entry in session state."""
	mutate_state_mapping(
		SessionKey.CACHE.value,
		lambda cache: {**cache, "values": {**dict(cache.get("values", {})), cache_key: value}},
	)


def get_cached_value(cache_key: str, default: Any | None = None) -> Any | None:
	"""Read a local cache entry."""
	cache = dict(get_state_value(SessionKey.CACHE.value, {}) or {})
	values = dict(cache.get("values", {}))
	return values.get(cache_key, default)


def clear_cached_value(cache_key: str) -> None:
	"""Remove a local cache entry."""
	mutate_state_mapping(
		SessionKey.CACHE.value,
		lambda cache: {**cache, "values": {key: value for key, value in dict(cache.get("values", {})).items() if key != cache_key}},
	)


def clear_local_cache() -> None:
	"""Clear all local cache entries."""
	cache_state = get_state_value(SessionKey.CACHE.value, {})
	version = cache_state.get("version", "v1") if isinstance(cache_state, dict) else "v1"
	set_state_value_if_changed(SessionKey.CACHE.value, {"values": {}, "version": version})


def approve_alert(alert_id: str) -> None:
	"""Mark an alert as approved."""
	record_alert_moderation({"alert_id": alert_id}, decision="approve")


def review_alert(alert_id: str) -> None:
	"""Mark an alert as reviewed."""
	record_alert_moderation({"alert_id": alert_id}, decision="review")


def dismiss_alert(alert_id: str) -> None:
	"""Mark an alert as dismissed."""
	record_alert_moderation({"alert_id": alert_id}, decision="dismiss")


def add_navigation_history(entry: str) -> None:
	"""Append a page or tab to the navigation history."""
	mutate_state_mapping(
		SessionKey.NAVIGATION.value,
		lambda navigation: {**navigation, "history": [*list(navigation.get("history", [])), entry]},
	)


def update_navigation(**changes: Any) -> None:
	"""Merge navigation changes into the session state."""
	current = dict(get_state_value(SessionKey.NAVIGATION.value, asdict(NavigationState())) or {})
	current.update(changes)
	set_state_value_if_changed(SessionKey.NAVIGATION.value, current)
	if "active_tab" in changes:
		set_state_value_if_changed(SessionKey.ACTIVE_TAB.value, changes["active_tab"])


def set_loading_flag(block: str, is_loading: bool) -> None:
	"""Set a loading flag for a logical UI block."""
	mutate_state_mapping(SessionKey.LOADING_FLAGS.value, lambda flags: {**flags, block: bool(is_loading)})


def set_error_flag(block: str, error_message: str | None) -> None:
	"""Set or clear an error flag for a logical UI block."""
	mutate_state_mapping(
		SessionKey.ERROR_FLAGS.value,
		lambda flags: ({key: value for key, value in flags.items() if key != block} if error_message is None else {**flags, block: error_message}),
	)


def push_feedback(item: dict[str, Any]) -> None:
	"""Append a feedback item to the in-session feedback queue."""
	append_to_state_list(SessionKey.FEEDBACK_QUEUE.value, item)


def record_alert_moderation(alert: dict[str, Any], *, decision: str, observations: str = "", confirm_send: bool = False) -> dict[str, Any]:
	"""Persist a human moderation decision for an alert and return the stored record."""
	alert_id = str(alert.get("alert_id") or alert.get("event_id") or alert.get("id") or "")
	event_id = str(alert.get("event_id") or alert_id)
	decision_normalized = decision.strip().lower()
	created_at = utc_now().isoformat()
	status = {
		"approve": "approved",
		"review": "reviewed",
		"dismiss": "dismissed",
	}.get(decision_normalized, decision_normalized or "pending")
	record = {
		"alert_id": alert_id,
		"event_id": event_id,
		"decision": decision_normalized,
		"observations": observations.strip(),
		"confirm_send": bool(confirm_send and decision_normalized == "approve"),
		"status": status,
		"created_at": created_at,
		"title": str(alert.get("alert_title") or alert.get("title") or alert.get("event_type") or "Alerta"),
		"region": str(alert.get("region") or ""),
		"state": str(alert.get("state") or ""),
		"event_type": str(alert.get("event_type") or ""),
		"alert_level": str(alert.get("alert_level") or "info"),
		"risk_score": float(alert.get("risk_score") or 0.0),
	}
	set_loading_flag("feedback_workbench", True)
	try:
		append_to_state_list(SessionKey.FEEDBACK_HISTORY.value, record)
		set_state_value_if_changed(
			SessionKey.FEEDBACK_REVISION.value,
			int(get_state_value(SessionKey.FEEDBACK_REVISION.value, 0) or 0) + 1,
		)
		# Persist to durable storage when enabled
		try:
			if get_settings().enable_feedback_persistence:
				save_feedback(record)
		except Exception:
			# Persistence errors must not break UI flow
			pass
		if decision_normalized == "approve":
			append_unique_to_state_list(SessionKey.APPROVED_ALERTS.value, alert_id)
			remove_from_state_list(SessionKey.REVIEWED_ALERTS.value, alert_id)
			remove_from_state_list(SessionKey.DISMISSED_ALERTS.value, alert_id)
		elif decision_normalized == "review":
			append_unique_to_state_list(SessionKey.REVIEWED_ALERTS.value, alert_id)
			remove_from_state_list(SessionKey.APPROVED_ALERTS.value, alert_id)
			remove_from_state_list(SessionKey.DISMISSED_ALERTS.value, alert_id)
		elif decision_normalized == "dismiss":
			append_unique_to_state_list(SessionKey.DISMISSED_ALERTS.value, alert_id)
			remove_from_state_list(SessionKey.APPROVED_ALERTS.value, alert_id)
			remove_from_state_list(SessionKey.REVIEWED_ALERTS.value, alert_id)
		if record["confirm_send"]:
			append_unique_to_state_list(SessionKey.SENT_ALERTS.value, alert_id)
		return record
	finally:
		set_loading_flag("feedback_workbench", False)


def invalidate_pipeline_run() -> None:
	"""Invalidate pipeline caches by bumping the run id and clearing local cache."""
	new_id = str(uuid4())
	set_state_value_if_changed(SessionKey.PIPELINE_RUN_ID.value, new_id)
	clear_local_cache()


def _update_filters(**changes: Any) -> None:
	"""Merge filter changes into the canonical filter state."""
	current = dict(get_state_value(SessionKey.FILTERS.value, asdict(DashboardFilterState(region="", event_types=[], period_days=0))) or {})
	current.update(changes)
	set_state_value_if_changed(SessionKey.FILTERS.value, current)


def reset_filters() -> None:
	"""Restore the canonical filter state to its defaults."""
	_update_filters(region=get_state_value(SessionKey.SELECTED_REGION.value, "Global"), event_types=["Flood", "Storm", "Heatwave", "Landslide", "Queimada", "Qualidade do Ar"], period_days=int(get_state_value(SessionKey.SELECTED_PERIOD_DAYS.value, 30) or 30), date_start=None, date_end=None, risk_level="all", threshold=0.0)
	set_state_value_if_changed(SessionKey.SELECTED_DATE_START.value, None)
	set_state_value_if_changed(SessionKey.SELECTED_DATE_END.value, None)
	set_state_value_if_changed(SessionKey.SELECTED_RISK_LEVEL.value, "all")
	set_state_value_if_changed(SessionKey.SELECTED_THRESHOLD.value, 0.0)
