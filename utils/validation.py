"""Validation helpers shared by providers, pipelines, and UI state."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

from utils.exceptions import ValidationError

T = TypeVar("T")


def ensure_not_empty(value: Sequence[T], field_name: str) -> Sequence[T]:
	"""Ensure a sequence is not empty and return it when valid."""
	if len(value) == 0:
		raise ValidationError(f"Field '{field_name}' cannot be empty.")
	return value


def ensure_positive_int(value: int, field_name: str) -> int:
	"""Ensure an integer is positive and return it when valid."""
	if value <= 0:
		raise ValidationError(f"Field '{field_name}' must be greater than zero.")
	return value
