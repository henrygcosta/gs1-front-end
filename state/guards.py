"""Guard clauses for session state integrity."""

from __future__ import annotations

import streamlit as st

from state.session_keys import SessionKey


def ensure_session_keys() -> None:
	"""Raise a RuntimeError if required session keys are missing."""
	missing = [key.value for key in SessionKey if key.value not in st.session_state]
	if missing:
		raise RuntimeError(f"Missing session state keys: {', '.join(missing)}")


def has_initialized_state() -> bool:
	"""Return True when the session has all expected keys."""
	return not [key.value for key in SessionKey if key.value not in st.session_state]
