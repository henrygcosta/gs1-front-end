"""Application constants used across layers."""

from __future__ import annotations

from enum import StrEnum


class Environment(StrEnum):
	"""Supported runtime environments."""

	DEVELOPMENT = "dev"
	TEST = "test"
	PRODUCTION = "prod"


class RiskLevel(StrEnum):
	"""Semantic risk levels for events and alerts."""

	LOW = "low"
	MEDIUM = "medium"
	HIGH = "high"
	CRITICAL = "critical"


DEFAULT_TIMEZONE: str = "UTC"
APP_VERSION: str = "0.1.0"
PIPELINE_VERSION: str = "2026.1"
CACHE_TTL_SECONDS: int = 300
