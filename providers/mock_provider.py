"""Mock data providers with realistic, reproducible data for development.

Each provider returns a `pandas.DataFrame` and uses `st.cache_data` to
improve performance and emulate API caching semantics.
"""

from __future__ import annotations

from datetime import timedelta
from hashlib import sha1

import numpy as np
import pandas as pd
import streamlit as st

from utils.exceptions import DataProviderError
from utils.logger import get_logger
from utils.time_utils import utc_now

LOGGER = get_logger(__name__)

REGION_STATE_MAP: dict[str, str] = {
	"Global": "Global",
	"Brazil": "BR",
	"Amazonas": "AM",
	"Nordeste": "NE",
	"Sudeste": "SE",
	"Pantanal": "MT",
	"Centro-Oeste": "CO",
}


def _region_state(region: str) -> str:
	"""Map a region to a representative state or macro-region code."""
	return REGION_STATE_MAP.get(region, "BR")


def _derive_temperature_and_precipitation(rng: np.random.Generator, event_type: str) -> tuple[float, float]:
	"""Generate realistic climate indicators for a specific event type."""
	base_temperature = 28.0 if event_type != "Heatwave" else 38.0
	base_precipitation = 12.0 if event_type in {"Flood", "Storm"} else 3.0
	temperature = float(max(-5.0, base_temperature + rng.normal(0, 3)))
	precipitation = float(max(0.0, base_precipitation + rng.normal(0, 8)))
	return temperature, precipitation


def _deterministic_random(seed_input: str) -> np.random.Generator:
	"""Return a numpy Generator seeded deterministically from input string."""
	digest = sha1(seed_input.encode("utf-8")).digest()
	seed = int.from_bytes(digest[:8], "big")
	return np.random.default_rng(seed)


class MockClimateProvider:
	"""Synthetic climate event generator.

	Produces repeated daily events for several event types with geo coordinates
	and plausible severity/confidence values.
	"""

	@st.cache_data(show_spinner=False, ttl=300)
	def fetch_events(_self, region: str, period_days: int) -> pd.DataFrame:
		try:
			base = utc_now()
			rng = _deterministic_random(f"climate:{region}:{period_days}")

			event_types = ["Flood", "Storm", "Heatwave", "Landslide", "Drought"]
			rows: list[dict[str, object]] = []
			state = _region_state(region)

			for day in range(period_days):
				timestamp = base - timedelta(days=int(day))
				for idx, et in enumerate(event_types):
					severity = float(min(1.0, 0.2 + rng.random() * 0.9 * (1 + idx * 0.1)))
					confidence = float(min(1.0, 0.4 + rng.random() * 0.6))
					lat = -23.55 + (rng.random() - 0.5) * 5.0
					lon = -46.63 + (rng.random() - 0.5) * 5.0
					temperature, precipitation = _derive_temperature_and_precipitation(rng, et)
					risk_factors = {
						"Flood": ("high rainfall", "river overflow"),
						"Storm": ("wind gusts", "convective activity"),
						"Heatwave": ("heat stress", "low humidity"),
						"Landslide": ("slope saturation", "soil instability"),
						"Drought": ("water deficit", "low precipitation"),
					}.get(et, ("climate anomaly",))
					rows.append(
						{
							"event_id": f"CLM-{region[:3].upper()}-{day:04d}-{idx}",
							"region": region,
							"state": state,
							"event_type": et,
							"severity": severity,
							"confidence": confidence,
							"latitude": lat,
							"longitude": lon,
							"timestamp": timestamp,
							"temperature_c": temperature,
							"precipitation_mm": precipitation,
							"risk_factors": list(risk_factors),
						}
					)

			df = pd.DataFrame(rows)
			LOGGER.debug("MockClimateProvider generated %d rows", len(df))
			return df
		except Exception as exc:  # pragma: no cover - defensive
			LOGGER.exception("MockClimateProvider failed")
			raise DataProviderError("Failed to generate mock climate events") from exc


class MockGeoProvider:
	"""Static region list and simple centroids for UI filters."""

	@st.cache_data(show_spinner=False, ttl=3600)
	def fetch_regions(_self) -> pd.DataFrame:
		try:
			rows = [
				{"region": "Global", "state": "Global", "centroid_lat": 0.0, "centroid_lon": 0.0, "population": None},
				{"region": "Brazil", "state": "BR", "centroid_lat": -14.2350, "centroid_lon": -51.9253, "population": 203080756},
				{"region": "Amazonas", "state": "AM", "centroid_lat": -3.4168, "centroid_lon": -65.8561, "population": 4279229},
				{"region": "Nordeste", "state": "NE", "centroid_lat": -8.28, "centroid_lon": -35.37, "population": 57000000},
				{"region": "Sudeste", "state": "SE", "centroid_lat": -19.92, "centroid_lon": -43.94, "population": 89000000},
			]
			df = pd.DataFrame(rows)
			return df
		except Exception as exc:  # pragma: no cover - defensive
			LOGGER.exception("MockGeoProvider failed")
			raise DataProviderError("Failed to generate mock regions") from exc


class MockFireProvider:
	"""Synthetic fire detection records (e.g., from thermal anomaly products)."""

	@st.cache_data(show_spinner=False, ttl=300)
	def fetch_fires(_self, region: str, period_days: int) -> pd.DataFrame:
		try:
			base = utc_now()
			rng = _deterministic_random(f"fire:{region}:{period_days}")
			rows: list[dict[str, object]] = []
			state = _region_state(region)
			for day in range(period_days):
				timestamp = base - timedelta(days=int(day))
				fires_per_day = int(rng.integers(0, 6))
				for i in range(fires_per_day):
					lat = -3.0 + (rng.random() - 0.5) * 8.0
					lon = -60.0 + (rng.random() - 0.5) * 10.0
					brightness = float(200 + rng.random() * 1500)
					confidence = float(min(1.0, 0.3 + rng.random() * 0.7))
					rows.append(
						{
							"fire_id": f"FIRE-{region[:3].upper()}-{day:04d}-{i}",
							"region": region,
							"state": state,
							"brightness": brightness,
							"confidence": confidence,
							"latitude": lat,
							"longitude": lon,
							"timestamp": timestamp,
							"vegetation_index": float(max(0.0, 1.0 - confidence + rng.random() * 0.2)),
						}
					)

			df = pd.DataFrame(rows)
			LOGGER.debug("MockFireProvider generated %d fire rows", len(df))
			return df
		except Exception as exc:  # pragma: no cover - defensive
			LOGGER.exception("MockFireProvider failed")
			raise DataProviderError("Failed to generate mock fire events") from exc


class MockAirQualityProvider:
	"""Synthetic air quality time-series (PM2.5, PM10, NO2, aggregated AQI)."""

	@st.cache_data(show_spinner=False, ttl=180)
	def fetch_air_quality(_self, region: str, period_days: int) -> pd.DataFrame:
		try:
			base = utc_now()
			rng = _deterministic_random(f"aq:{region}:{period_days}")
			rows: list[dict[str, object]] = []
			samples_per_day = 4
			state = _region_state(region)
			for day in range(period_days):
				for s in range(samples_per_day):
					timestamp = base - timedelta(days=int(day), hours=int(24 / samples_per_day * s))
					pm25 = float(max(0.0, rng.normal(12, 8)))
					pm10 = float(max(0.0, rng.normal(30, 12)))
					no2 = float(max(0.0, rng.normal(15, 6)))
					o3 = float(max(0.0, rng.normal(25, 10)))
					temperature = float(max(10.0, rng.normal(27, 4)))
					humidity = float(min(100.0, max(20.0, rng.normal(65, 15))))
					# simple AQI proxy
					aqi = int(min(500, (pm25 / 12) * 50 + (pm10 / 50) * 25 + (no2 / 40) * 25 + (o3 / 50) * 10))
					rows.append(
						{
							"sample_id": f"AQ-{region[:3].upper()}-{day:04d}-{s}",
							"region": region,
							"state": state,
							"pm25": pm25,
							"pm10": pm10,
							"no2": no2,
							"o3": o3,
							"aqi": aqi,
							"timestamp": timestamp,
							"temperature_c": temperature,
							"humidity_pct": humidity,
						}
					)

			df = pd.DataFrame(rows)
			LOGGER.debug("MockAirQualityProvider generated %d samples", len(df))
			return df
		except Exception as exc:  # pragma: no cover - defensive
			LOGGER.exception("MockAirQualityProvider failed")
			raise DataProviderError("Failed to generate mock air quality data") from exc
