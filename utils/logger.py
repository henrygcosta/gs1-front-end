"""Logging helpers for the application."""

from __future__ import annotations

import logging


def _configure_root_logger() -> None:
	"""Configure root logger once with a consistent format."""
	if logging.getLogger().handlers:
		return

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
	)


def get_logger(name: str) -> logging.Logger:
	"""Get a named logger with shared configuration."""
	_configure_root_logger()
	return logging.getLogger(name)
