"""Custom exception hierarchy for predictable error handling."""

from __future__ import annotations


class ApplicationError(Exception):
	"""Base class for known application errors."""


class DataProviderError(ApplicationError):
	"""Raised when provider data retrieval fails."""


class PipelineError(ApplicationError):
	"""Raised when a pipeline stage cannot complete."""


class ValidationError(ApplicationError):
	"""Raised when data or user input validation fails."""
