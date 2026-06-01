"""Typed state models used across the application."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class DashboardFilterState:
	"""Operational filters selected by the user."""

	region: str
	event_types: list[str]
	period_days: int
	date_start: str | None = None
	date_end: str | None = None
	risk_level: str = "all"
	threshold: float = 0.0


@dataclass(slots=True)
class ThresholdState:
	"""User-adjustable semantic thresholds."""

	risk: float = 0.75
	confidence: float = 0.60
	geographic_criticality: float = 0.70
	priority: float = 0.65


@dataclass(slots=True)
class UserPreferencesState:
	"""Persistent user preferences for the session."""

	theme_mode: str = "system"
	language: str = "pt-BR"
	auto_refresh: bool = True
	show_advanced_metrics: bool = True
	items_per_page: int = 20


@dataclass(slots=True)
class NavigationState:
	"""Navigation state kept independent from the UI widgets."""

	active_tab: str = "Overview"
	current_page: str = "dashboard"
	history: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CacheState:
	"""In-session cache for derived values and expensive computations."""

	values: dict[str, object] = field(default_factory=dict)
	version: str = "v1"


@dataclass(slots=True)
class LoadingState:
	"""Boolean loading flags keyed by feature or workflow block."""

	flags: dict[str, bool] = field(default_factory=dict)


@dataclass(slots=True)
class AlertState:
	"""User decisions about alerts."""

	approved_alerts: list[str] = field(default_factory=list)
	reviewed_alerts: list[str] = field(default_factory=list)
	dismissed_alerts: list[str] = field(default_factory=list)


@dataclass(slots=True)
class FeedbackRecordState:
	"""Human moderation record persisted in session history."""

	alert_id: str
	event_id: str
	decision: str
	observations: str = ""
	confirm_send: bool = False
	status: str = "pending"
	created_at: str = ""
	title: str = ""
	region: str = ""
	state: str = ""
	event_type: str = ""
	alert_level: str = "info"
	risk_score: float = 0.0


@dataclass(slots=True)
class SessionSnapshot:
	"""Convenient immutable snapshot of the high-level session state."""

	filters: DashboardFilterState
	thresholds: ThresholdState
	preferences: UserPreferencesState
	navigation: NavigationState
	cache: CacheState
	loading: LoadingState
	alerts: AlertState
