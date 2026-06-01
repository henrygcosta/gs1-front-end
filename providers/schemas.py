"""Typed provider DTOs and schema helpers.

These dataclasses define stable shapes for the data exchanged between
providers and the rest of the application.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ClimateEventRecord:
	"""Validated climate event record from any provider."""

	event_id: str
	region: str
	state: str
	event_type: str
	severity: float
	confidence: float
	latitude: float
	longitude: float
	timestamp: datetime
	temperature_c: float | None = None
	precipitation_mm: float | None = None
	risk_factors: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class GeoRegion:
	"""Region metadata used for filters and mapping."""

	region: str
	state: str
	centroid_lat: float | None = None
	centroid_lon: float | None = None
	population: int | None = None


@dataclass(frozen=True, slots=True)
class FireEventRecord:
	"""Record representing detected fire / queimadas events."""

	fire_id: str
	region: str
	state: str
	brightness: float
	confidence: float
	latitude: float
	longitude: float
	timestamp: datetime
	vegetation_index: float | None = None


@dataclass(frozen=True, slots=True)
class AirQualityRecord:
	"""Air quality observation record or aggregated index."""

	sample_id: str
	region: str
	state: str
	pm25: float | None = None
	pm10: float | None = None
	no2: float | None = None
	o3: float | None = None
	aqi: int | None = None
	timestamp: datetime
	temperature_c: float | None = None
	humidity_pct: float | None = None
