"""Low-level helpers for safe session state access."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import TypeVar

import streamlit as st


T = TypeVar("T")


def get_state_value(key: str, default: T | None = None) -> T | None:
	"""Return a session value or a default if missing."""
	return st.session_state.get(key, default)


def set_state_value_if_changed(key: str, value: T) -> bool:
	"""Update session state only when the value actually changes.

	Returns True when the key was written and False when the assignment was a no-op.
	"""
	current_value = st.session_state.get(key, object())
	if current_value == value:
		return False
	st.session_state[key] = value
	return True


def mutate_state_mapping(key: str, mutator: Callable[[dict[str, object]], dict[str, object]]) -> bool:
	"""Apply a mapping transform and persist it only when the result changes."""
	current_value = st.session_state.get(key, {})
	mapping = dict(current_value) if isinstance(current_value, dict) else {}
	updated_mapping = mutator(deepcopy(mapping))
	if updated_mapping == mapping:
		return False
	st.session_state[key] = updated_mapping
	return True


def append_unique_to_state_list(key: str, item: T) -> bool:
	"""Append an item to a list-like session value if it is not already present."""
	current_value = st.session_state.get(key, [])
	items = list(current_value) if isinstance(current_value, list) else []
	if item in items:
		return False
	items.append(item)
	st.session_state[key] = items
	return True


def append_to_state_list(key: str, item: T) -> bool:
	"""Append an item to a list-like session value, allowing duplicates."""
	current_value = st.session_state.get(key, [])
	items = list(current_value) if isinstance(current_value, list) else []
	items.append(item)
	st.session_state[key] = items
	return True


def remove_from_state_list(key: str, item: T) -> bool:
	"""Remove an item from a list-like session value if present."""
	current_value = st.session_state.get(key, [])
	items = list(current_value) if isinstance(current_value, list) else []
	if item not in items:
		return False
	items.remove(item)
	st.session_state[key] = items
	return True
