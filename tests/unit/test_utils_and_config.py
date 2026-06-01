"""Tests for small utility helpers and cached config behavior."""

from __future__ import annotations

from utils.config import Settings, get_settings
from utils.time_utils import last_n_days_range


def test_get_settings_returns_cached_dataclass_instance() -> None:
	first = get_settings()
	second = get_settings()

	assert isinstance(first, Settings)
	assert first is second


def test_last_n_days_range_returns_ordered_values() -> None:
	start, end = last_n_days_range(1)
	assert start < end