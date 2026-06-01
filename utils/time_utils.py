"""Time and date utility functions."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta


def utc_now() -> datetime:
	"""Return current UTC time with timezone info."""
	return datetime.now(UTC)


def last_n_days_range(days: int) -> tuple[datetime, datetime]:
	"""Return a UTC date range covering the last N days."""
	end = utc_now()
	start = end - timedelta(days=days)
	return start, end
