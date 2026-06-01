"""Session state initialization routines."""

from __future__ import annotations

from dataclasses import asdict
from uuid import uuid4

import streamlit as st

from state.models import AlertState, CacheState, DashboardFilterState, LoadingState, NavigationState, ThresholdState, UserPreferencesState
from state.session_keys import SessionKey
from utils.config import get_settings
from state.persistence import init_db


SUPPORTED_EVENT_TYPES = ["Flood", "Storm", "Heatwave", "Landslide", "Queimada", "Qualidade do Ar"]
LEGACY_EVENT_TYPES = ["Flood", "Storm", "Heatwave"]
LEGACY_ALIASES = {"Fire": "Queimada", "AirQuality": "Qualidade do Ar"}


def initialize_session_state() -> None:
	"""Create missing session state keys with safe defaults."""
	settings = get_settings()
	filters = DashboardFilterState(
		region=settings.default_region,
		event_types=SUPPORTED_EVENT_TYPES.copy(),
		period_days=settings.default_period_days,
		date_start=None,
		date_end=None,
		risk_level="all",
		threshold=0.0,
	)
	thresholds = ThresholdState()
	preferences = UserPreferencesState()
	navigation = NavigationState()
	cache = CacheState()
	loading = LoadingState()
	alerts = AlertState()

	defaults: dict[SessionKey, object] = {
		SessionKey.FILTERS: asdict(filters),
		SessionKey.SELECTED_REGION: filters.region,
		SessionKey.SELECTED_EVENT_TYPES: filters.event_types,
		SessionKey.SELECTED_PERIOD_DAYS: filters.period_days,
		SessionKey.SELECTED_DATE_START: filters.date_start,
		SessionKey.SELECTED_DATE_END: filters.date_end,
		SessionKey.SELECTED_RISK_LEVEL: filters.risk_level,
		SessionKey.SELECTED_THRESHOLD: filters.threshold,
		SessionKey.THRESHOLDS: asdict(thresholds),
		SessionKey.PREFERENCES: asdict(preferences),
		SessionKey.THEME: {"mode": preferences.theme_mode, "accent": "ocean"},
		SessionKey.CACHE: asdict(cache),
		SessionKey.ACTIVE_TAB: navigation.active_tab,
		SessionKey.NAVIGATION: asdict(navigation),
		SessionKey.APPROVED_ALERTS: alerts.approved_alerts,
		SessionKey.REVIEWED_ALERTS: alerts.reviewed_alerts,
		SessionKey.DISMISSED_ALERTS: alerts.dismissed_alerts,
		SessionKey.FEEDBACK_HISTORY: [],
		SessionKey.SENT_ALERTS: [],
		SessionKey.FEEDBACK_QUEUE: [],
		SessionKey.FEEDBACK_REVISION: 0,
		SessionKey.LOADING_FLAGS: loading.flags,
		SessionKey.ERROR_FLAGS: {},
		SessionKey.PIPELINE_RUN_ID: str(uuid4()),
	}

	for key, value in defaults.items():
		if key.value not in st.session_state:
			st.session_state[key.value] = value

	selected_event_types = list(st.session_state.get(SessionKey.SELECTED_EVENT_TYPES.value, []))
	if selected_event_types == LEGACY_EVENT_TYPES:
		st.session_state[SessionKey.SELECTED_EVENT_TYPES.value] = SUPPORTED_EVENT_TYPES.copy()
		filters_state = dict(st.session_state.get(SessionKey.FILTERS.value, {}))
		filters_state["event_types"] = SUPPORTED_EVENT_TYPES.copy()
		st.session_state[SessionKey.FILTERS.value] = filters_state
	elif any(event_type in LEGACY_ALIASES for event_type in selected_event_types):
		translated = [LEGACY_ALIASES.get(event_type, event_type) for event_type in selected_event_types]
		st.session_state[SessionKey.SELECTED_EVENT_TYPES.value] = translated
		filters_state = dict(st.session_state.get(SessionKey.FILTERS.value, {}))
		filters_state["event_types"] = translated
		st.session_state[SessionKey.FILTERS.value] = filters_state

	# Initialize optional persistence backend
	settings = get_settings()
	if settings.enable_feedback_persistence:
		init_db()
