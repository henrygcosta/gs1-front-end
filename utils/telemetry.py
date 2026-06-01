"""Telemetry utilities for interaction and diagnostic events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from utils.time_utils import utc_now


@dataclass(slots=True)
class TelemetryEvent:
	"""Represents a telemetry event emitted by UI or pipelines."""

	name: str
	timestamp: datetime
	metadata: dict[str, str]


def build_event(name: str, metadata: dict[str, str] | None = None) -> TelemetryEvent:
	"""Create a telemetry event with a UTC timestamp."""
	return TelemetryEvent(name=name, timestamp=utc_now(), metadata=metadata or {})
