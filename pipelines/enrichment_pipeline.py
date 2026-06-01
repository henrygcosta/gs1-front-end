"""Data enrichment pipeline stage.

Adds risk indicators, spatial criticality, semantic alerts and textual
insights to the cleaned operational dataset.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from pipelines.common import (
	RiskWeights,
	band_geographic_criticality,
	band_score,
	clamp_series,
	dataframe_cache_key,
	insight_for_row,
	risk_alert_level,
	recommendation_for_event,
)
from utils.exceptions import PipelineError
from utils.logger import get_logger


LOGGER = get_logger(__name__)
RISK_WEIGHTS = RiskWeights()


def _normalized(series: pd.Series, maximum: float) -> pd.Series:
	"""Normalize a series to the 0-1 range using a fixed maximum."""
	return clamp_series(series.astype(float) / maximum)


def _source_indicator_pressure(frame: pd.DataFrame) -> pd.Series:
	"""Compute a domain-specific indicator pressure score."""
	temperature_pressure = clamp_series(((pd.to_numeric(frame["temperature_c"], errors="coerce").fillna(26.0) - 30.0) / 15.0).clip(lower=0.0))
	precipitation_pressure = _normalized(pd.to_numeric(frame["precipitation_mm"], errors="coerce").fillna(0.0), 120.0)
	dryness_pressure = clamp_series(1.0 - precipitation_pressure)
	fire_pressure = clamp_series(
		_normalized(pd.to_numeric(frame["brightness"], errors="coerce").fillna(0.0), 1700.0) * 0.75
		+ (1.0 - pd.to_numeric(frame["vegetation_index"], errors="coerce").fillna(0.55)) * 0.25
	)
	aqi_numeric = pd.to_numeric(frame["aqi"], errors="coerce").fillna(0.0)
	hair_pressure = _normalized(aqi_numeric, 500.0)

	pressure = pd.Series(np.zeros(len(frame)), index=frame.index, dtype=float)
	pressure = pressure.where(~frame["event_type"].eq("Flood"), clamp_series(precipitation_pressure + temperature_pressure * 0.15))
	pressure = pressure.where(~frame["event_type"].eq("Storm"), clamp_series(precipitation_pressure * 0.9 + temperature_pressure * 0.2))
	pressure = pressure.where(~frame["event_type"].eq("Heatwave"), clamp_series(temperature_pressure * 0.95 + dryness_pressure * 0.20))
	pressure = pressure.where(~frame["event_type"].eq("Landslide"), clamp_series(precipitation_pressure * 0.85 + (1.0 - pd.to_numeric(frame["vegetation_index"], errors="coerce").fillna(0.5)) * 0.35))
	pressure = pressure.where(~frame["event_type"].eq("Drought"), clamp_series(dryness_pressure * 0.90 + temperature_pressure * 0.30))
	pressure = pressure.where(~frame["source"].eq("fire"), fire_pressure)
	pressure = pressure.where(~frame["source"].eq("air_quality"), hair_pressure)
	return clamp_series(pressure.fillna(precipitation_pressure))


def _population_pressure(frame: pd.DataFrame) -> pd.Series:
	"""Return a normalized spatial pressure based on population density proxy."""
	population = pd.to_numeric(frame["population"], errors="coerce").fillna(0.0)
	max_population = float(population.max()) if float(population.max()) > 0 else 1.0
	return clamp_series(population / max_population)


@st.cache_data(show_spinner=False, ttl=300, hash_funcs={pd.DataFrame: dataframe_cache_key})
def run_enrichment_pipeline(events: pd.DataFrame) -> pd.DataFrame:
	"""Add derived metrics, predictions and textual insights."""
	try:
		enriched = events.copy()
		enriched.loc[:, "timestamp"] = pd.to_datetime(enriched["timestamp"], utc=True, errors="coerce")
		enriched.loc[:, "date"] = enriched["timestamp"].dt.date
		enriched.loc[:, "hour"] = enriched["timestamp"].dt.hour
		enriched.loc[:, "day_of_week"] = enriched["timestamp"].dt.day_name()
		enriched.loc[:, "month"] = enriched["timestamp"].dt.month
		enriched.loc[:, "severity_band"] = enriched["severity"].apply(band_score)
		enriched.loc[:, "indicator_pressure"] = _source_indicator_pressure(enriched)
		enriched.loc[:, "population_pressure"] = _population_pressure(enriched)
		enriched.loc[:, "confidence_gap"] = clamp_series(1.0 - pd.to_numeric(enriched["confidence"], errors="coerce"))
		enriched.loc[:, "risk_score"] = clamp_series(
			(pd.to_numeric(enriched["severity"], errors="coerce") * RISK_WEIGHTS.severity)
			+ (enriched["confidence_gap"] * RISK_WEIGHTS.confidence_gap)
			+ (enriched["indicator_pressure"] * RISK_WEIGHTS.indicator_pressure)
			+ (enriched["population_pressure"] * RISK_WEIGHTS.spatial_pressure)
		)
		enriched.loc[:, "climate_severity_index"] = clamp_series(
			(pd.to_numeric(enriched["severity"], errors="coerce") * 0.55) + (enriched["indicator_pressure"] * 0.45)
		)
		enriched.loc[:, "flood_risk_probability"] = clamp_series(
			(enriched["indicator_pressure"] * 0.70)
			+ (pd.to_numeric(enriched["severity"], errors="coerce") * 0.20)
			+ (enriched["population_pressure"] * 0.10)
		)
		enriched.loc[:, "landslide_risk_probability"] = clamp_series(
			(enriched["indicator_pressure"] * 0.55)
			+ ((1.0 - pd.to_numeric(enriched["vegetation_index"], errors="coerce").fillna(0.5)) * 0.25)
			+ (pd.to_numeric(enriched["severity"], errors="coerce") * 0.20)
		)
		enriched.loc[:, "drought_risk_probability"] = clamp_series(
			((1.0 - pd.to_numeric(enriched["precipitation_mm"], errors="coerce").fillna(0.0).clip(0, 120) / 120.0) * 0.60)
			+ ((pd.to_numeric(enriched["temperature_c"], errors="coerce").fillna(28.0) - 26.0).clip(lower=0.0) / 20.0 * 0.25)
			+ (pd.to_numeric(enriched["severity"], errors="coerce") * 0.15)
		)
		enriched.loc[:, "fire_risk_probability"] = clamp_series(
			(enriched["indicator_pressure"] * 0.68)
			+ ((1.0 - pd.to_numeric(enriched["vegetation_index"], errors="coerce").fillna(0.55)) * 0.20)
			+ (pd.to_numeric(enriched["severity"], errors="coerce") * 0.12)
		)
		enriched.loc[:, "air_quality_risk_probability"] = clamp_series(
			(pd.to_numeric(enriched["aqi"], errors="coerce").fillna(0.0) / 500.0 * 0.75)
			+ (pd.to_numeric(enriched["severity"], errors="coerce") * 0.25)
		)
		enriched.loc[:, "geographic_criticality_score"] = clamp_series(
			(enriched["risk_score"] * 0.70) + (enriched["population_pressure"] * 0.30)
		)
		enriched.loc[:, "severity_class"] = enriched["risk_score"].apply(band_score)
		enriched.loc[:, "geographic_criticality_class"] = enriched["geographic_criticality_score"].apply(
			band_geographic_criticality
		)
		enriched.loc[:, "alert_level"] = enriched["risk_score"].apply(risk_alert_level)
		enriched.loc[:, "is_critical"] = (enriched["risk_score"] >= 0.85) | (enriched["geographic_criticality_score"] >= 0.80)
		enriched.loc[:, "priority_score"] = clamp_series(
			(enriched["risk_score"] * 0.65) + (enriched["geographic_criticality_score"] * 0.35)
		)
		enriched.loc[:, "operational_priority"] = pd.cut(
			enriched["priority_score"],
			bins=[-0.01, 0.35, 0.55, 0.75, 1.0],
			labels=["baixa", "moderada", "alta", "critica"],
		)
		enriched.loc[:, "semantic_alert"] = enriched.apply(
			lambda row: f"{str(row['alert_level']).upper()} | {row['event_type']} em {row['region']}/{row['state']}",
			axis=1,
		)
		enriched.loc[:, "recommended_action"] = enriched.apply(
			lambda row: recommendation_for_event(str(row["event_type"]), str(row["alert_level"])), axis=1
		)
		enriched.loc[:, "insight_text"] = enriched.apply(
			lambda row: insight_for_row(
				str(row["event_type"]), str(row["region"]), str(row["state"]), str(row["alert_level"]), str(row["geographic_criticality_class"])
			),
			axis=1,
		)
		enriched.loc[:, "alert_title"] = enriched.apply(
			lambda row: f"{str(row['alert_level']).upper()} - {row['event_type']} em {row['region']}", axis=1
		)

		LOGGER.debug("Enriched dataset: %d rows", len(enriched))
		return enriched.sort_values(by=["priority_score", "timestamp"], ascending=[False, False]).reset_index(drop=True)
	except Exception as exc:  # pragma: no cover - defensive guard
		LOGGER.exception("Enrichment pipeline failed")
		raise PipelineError("Failed to enrich operational dataset") from exc
