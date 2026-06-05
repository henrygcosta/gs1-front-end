"""Global application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from utils.constants import CACHE_TTL_SECONDS, Environment


def _env_bool(name: str, default: bool) -> bool:
	"""Read a boolean environment variable with a safe default."""
	value = os.getenv(name)
	if value is None:
		return default
	return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int, minimum: int, maximum: int) -> int:
	"""Read and clamp an integer environment variable."""
	value = os.getenv(name)
	if value is None:
		return default
	try:
		parsed = int(value)
	except ValueError:
		return default
	return max(minimum, min(maximum, parsed))


def _env_environment(name: str, default: Environment) -> Environment:
	"""Read a validated environment enum value from the process environment."""
	value = os.getenv(name)
	if value is None:
		return default
	try:
		return Environment(value)
	except ValueError:
		return default


@dataclass(frozen=True, slots=True)
class Settings:
	"""Runtime settings loaded from environment variables."""

	app_title: str = "Climate Intelligence Command Center"
	page_icon: str = ":earth_americas:"
	environment: Environment = _env_environment("GS_ENVIRONMENT", Environment.DEVELOPMENT)
	cache_ttl_seconds: int = _env_int("GS_CACHE_TTL_SECONDS", CACHE_TTL_SECONDS, 60, 7200)
	default_region: str = os.getenv("GS_DEFAULT_REGION", "Global")
	default_period_days: int = _env_int("GS_DEFAULT_PERIOD_DAYS", 30, 1, 365)
	use_mock_provider: bool = _env_bool("GS_USE_MOCK_PROVIDER", True)
	# Persistence: optional local storage for human feedback history
	enable_feedback_persistence: bool = _env_bool("GS_ENABLE_FEEDBACK_PERSISTENCE", True)
	feedback_db_path: str = os.getenv("GS_FEEDBACK_DB_PATH", "data/feedback.db")
	# UI helpers
	enable_cache_invalidation_button: bool = _env_bool("GS_ENABLE_CACHE_INVALIDATION_BUTTON", True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	"""Return a cached instance of application settings."""
	return Settings()
