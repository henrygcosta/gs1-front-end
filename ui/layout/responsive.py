"""Responsive layout helper utilities."""

from __future__ import annotations


def get_column_count(viewport: str) -> int:
	"""Return recommended column count for a viewport profile."""
	if viewport == "mobile":
		return 1
	if viewport == "tablet":
		return 2
	return 3
