"""Data ingestion pipeline.

Fetches and normalizes climate, fire and air-quality data into a unified
operational dataset ready for cleaning and enrichment.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from pipelines.common import dataframe_cache_key, ensure_columns
from providers.provider_factory import get_provider_container
from utils.exceptions import PipelineError
from utils.logger import get_logger


LOGGER = get_logger(__name__)

BASE_COLUMNS: list[str] = [
	"source",
	"domain",
	"record_type",
	"event_id",
	"region",
	"state",
	"event_type",
	"latitude",
	"longitude",
	"timestamp",
	"severity",
	"confidence",
	"temperature_c",
	"precipitation_mm",
	"brightness",
	"vegetation_index",
	"pm25",
	"pm10",
	"no2",
	"o3",
	"aqi",
	"risk_factors",
	"centroid_lat",
	"centroid_lon",
	"population",
	"payload_weight",
]


def _add_missing_columns(frame: pd.DataFrame, defaults: dict[str, object]) -> pd.DataFrame:
	"""Return a copy with all columns declared in defaults present."""
	result = frame.copy()
	for column, default in defaults.items():
		if column not in result.columns:
			result[column] = default
	return result


def _normalize_climate_frame(frame: pd.DataFrame) -> pd.DataFrame:
	"""Normalize climate provider output into the shared operational schema."""
	required = [
		"event_id",
		"region",
		"state",
		"event_type",
		"severity",
		"confidence",
		"latitude",
		"longitude",
		"timestamp",
	]
	ensure_columns(frame, required, stage="ingest.climate")
	result = frame.copy()
	result.loc[:, "source"] = "climate"
	result.loc[:, "domain"] = "climate_risk"
	result.loc[:, "record_type"] = "event"
	risk_factors_source = result.get("risk_factors", pd.Series([()] * len(result), index=result.index))
	result.loc[:, "risk_factors"] = risk_factors_source.apply(
		lambda value: tuple(value) if isinstance(value, (list, tuple)) else ()
	)
	result = _add_missing_columns(
		result,
		{
			"temperature_c": pd.NA,
			"precipitation_mm": pd.NA,
			"brightness": pd.NA,
			"vegetation_index": pd.NA,
			"pm25": pd.NA,
			"pm10": pd.NA,
			"no2": pd.NA,
			"o3": pd.NA,
			"aqi": pd.NA,
			"centroid_lat": pd.NA,
			"centroid_lon": pd.NA,
			"population": pd.NA,
			"payload_weight": 1.0,
		},
	)
	return result[BASE_COLUMNS]


def _normalize_fire_frame(frame: pd.DataFrame) -> pd.DataFrame:
	"""Normalize fire provider output into the shared operational schema."""
	required = ["fire_id", "region", "state", "brightness", "confidence", "latitude", "longitude", "timestamp"]
	ensure_columns(frame, required, stage="ingest.fire")
	result = frame.copy()
	result.loc[:, "source"] = "fire"
	result.loc[:, "domain"] = "fire_monitoring"
	result.loc[:, "record_type"] = "event"
	result.loc[:, "event_id"] = result["fire_id"].astype(str)
	result.loc[:, "event_type"] = "Queimada"
	result.loc[:, "severity"] = (result["brightness"].astype(float) / 1700.0 * 0.7 + result["confidence"].astype(float) * 0.3).clip(0.0, 1.0)
	result.loc[:, "temperature_c"] = pd.NA
	result.loc[:, "precipitation_mm"] = pd.NA
	result.loc[:, "vegetation_index"] = result.get("vegetation_index", pd.Series([pd.NA] * len(result)))
	result.loc[:, "pm25"] = pd.NA
	result.loc[:, "pm10"] = pd.NA
	result.loc[:, "no2"] = pd.NA
	result.loc[:, "o3"] = pd.NA
	result.loc[:, "aqi"] = pd.NA
	result.loc[:, "risk_factors"] = [("thermal anomaly", "vegetation stress") for _ in range(len(result))]
	result = _add_missing_columns(
		result,
		{"centroid_lat": pd.NA, "centroid_lon": pd.NA, "population": pd.NA, "payload_weight": 1.0},
	)
	return result[BASE_COLUMNS]


def _normalize_air_quality_frame(frame: pd.DataFrame) -> pd.DataFrame:
	"""Normalize air-quality observations into the shared operational schema."""
	required = ["sample_id", "region", "state", "pm25", "pm10", "no2", "aqi", "timestamp"]
	ensure_columns(frame, required, stage="ingest.air_quality")
	result = frame.copy()
	result.loc[:, "source"] = "air_quality"
	result.loc[:, "domain"] = "air_quality_monitoring"
	result.loc[:, "record_type"] = "observation"
	result.loc[:, "event_id"] = result["sample_id"].astype(str)
	result.loc[:, "event_type"] = "Qualidade do Ar"
	result.loc[:, "severity"] = (result["aqi"].astype(float) / 500.0).clip(0.0, 1.0)
	result.loc[:, "confidence"] = (1.0 - (result["severity"] * 0.35)).clip(0.35, 0.95)
	result.loc[:, "latitude"] = pd.NA
	result.loc[:, "longitude"] = pd.NA
	result.loc[:, "temperature_c"] = result.get("temperature_c", pd.Series([pd.NA] * len(result)))
	result.loc[:, "precipitation_mm"] = pd.NA
	result.loc[:, "brightness"] = pd.NA
	result.loc[:, "vegetation_index"] = pd.NA
	result.loc[:, "o3"] = result.get("o3", pd.Series([pd.NA] * len(result)))
	result.loc[:, "risk_factors"] = [("particulate exposure", "urban dispersion") for _ in range(len(result))]
	result = _add_missing_columns(
		result,
		{"centroid_lat": pd.NA, "centroid_lon": pd.NA, "population": pd.NA, "payload_weight": 1.0},
	)
	return result[BASE_COLUMNS]


def _merge_geospatial_metadata(events: pd.DataFrame, regions: pd.DataFrame) -> pd.DataFrame:
	"""Join centroids and population data to the operational dataset."""
	geo = regions[["region", "state", "centroid_lat", "centroid_lon", "population"]].copy()
	merged = events.merge(geo, on=["region", "state"], how="left", suffixes=("", "_geo"))
	centroid_lat_geo = merged["centroid_lat_geo"] if "centroid_lat_geo" in merged.columns else pd.Series(index=merged.index, dtype="float64")
	centroid_lon_geo = merged["centroid_lon_geo"] if "centroid_lon_geo" in merged.columns else pd.Series(index=merged.index, dtype="float64")
	population_geo = merged["population_geo"] if "population_geo" in merged.columns else pd.Series(index=merged.index, dtype="float64")
	merged = merged.assign(
		centroid_lat=merged["centroid_lat"].where(merged["centroid_lat"].notna(), centroid_lat_geo),
		centroid_lon=merged["centroid_lon"].where(merged["centroid_lon"].notna(), centroid_lon_geo),
		population=merged["population"].where(merged["population"].notna(), population_geo),
	)
	merged = merged.drop(columns=[column for column in merged.columns if column.endswith("_geo")], errors="ignore")
	merged = merged.assign(
		latitude=merged["latitude"].where(merged["latitude"].notna(), merged["centroid_lat"]),
		longitude=merged["longitude"].where(merged["longitude"].notna(), merged["centroid_lon"]),
	)
	return merged


@st.cache_data(show_spinner=False, ttl=300, hash_funcs={pd.DataFrame: dataframe_cache_key})
def run_ingest_pipeline(region: str, period_days: int) -> pd.DataFrame:
	"""Ingest and standardize data from all configured providers."""
	try:
		providers = get_provider_container()

		climate = _normalize_climate_frame(providers.climate.fetch_events(region=region, period_days=period_days))
		fire = _normalize_fire_frame(providers.fire.fetch_fires(region=region, period_days=period_days))
		air_quality = _normalize_air_quality_frame(
			providers.air_quality.fetch_air_quality(region=region, period_days=period_days)
		)
		geo_regions = providers.geo.fetch_regions()

		frames = [frame.dropna(axis=1, how="all") for frame in [climate, fire, air_quality] if not frame.empty]
		combined = pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame(columns=BASE_COLUMNS)
		combined = _add_missing_columns(
			combined,
			{
				"source": pd.NA,
				"domain": pd.NA,
				"record_type": pd.NA,
				"event_id": pd.NA,
				"region": pd.NA,
				"state": pd.NA,
				"event_type": pd.NA,
				"latitude": pd.NA,
				"longitude": pd.NA,
				"timestamp": pd.NA,
				"severity": pd.NA,
				"confidence": pd.NA,
				"temperature_c": pd.NA,
				"precipitation_mm": pd.NA,
				"brightness": pd.NA,
				"vegetation_index": pd.NA,
				"pm25": pd.NA,
				"pm10": pd.NA,
				"no2": pd.NA,
				"o3": pd.NA,
				"aqi": pd.NA,
				"risk_factors": pd.NA,
				"centroid_lat": pd.NA,
				"centroid_lon": pd.NA,
				"population": pd.NA,
				"payload_weight": 1.0,
			},
		)
		combined = _merge_geospatial_metadata(combined, geo_regions)
		combined = combined.assign(
			payload_weight=combined["payload_weight"].fillna(1.0),
			timestamp=pd.to_datetime(combined["timestamp"], utc=True, errors="coerce"),
		)
		combined = combined.sort_values(by=["timestamp", "source", "event_type"], ascending=[False, True, True])
		combined = combined.reset_index(drop=True)

		LOGGER.info(
			"Ingested %d records for region=%s period_days=%d",
			len(combined),
			region,
			period_days,
		)
		return combined
	except Exception as exc:  # pragma: no cover - defensive guard
		LOGGER.exception("Ingest pipeline failed")
		raise PipelineError("Failed to ingest operational datasets") from exc
