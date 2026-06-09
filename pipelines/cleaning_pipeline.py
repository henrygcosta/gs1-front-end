"""Data cleaning pipeline stage."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from pipelines.common import clamp_series, dataframe_cache_key, ensure_columns
from utils.exceptions import PipelineError
from utils.logger import get_logger

LOGGER = get_logger(__name__)

REQUIRED_COLUMNS = [
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
]


@st.cache_data(show_spinner=False, ttl=300, hash_funcs={pd.DataFrame: dataframe_cache_key})
def run_cleaning_pipeline(events: pd.DataFrame) -> pd.DataFrame:
	"""Normalize values, remove duplicates and eliminate invalid rows."""
	try:
		ensure_columns(events, REQUIRED_COLUMNS, stage="cleaning")
		cleaned = events.copy()
		cleaned = cleaned.assign(
			event_id=cleaned["event_id"].astype(str),
			region=cleaned["region"].astype(str),
			state=cleaned["state"].astype(str),
			event_type=cleaned["event_type"].astype(str),
			timestamp=pd.to_datetime(cleaned["timestamp"], utc=True, errors="coerce"),
		)
		cleaned = cleaned.dropna(subset=["event_id", "timestamp"])
		cleaned = cleaned.drop_duplicates(subset=["source", "event_id"])
		cleaned.loc[:, "severity"] = clamp_series(cleaned["severity"])
		cleaned.loc[:, "confidence"] = clamp_series(cleaned["confidence"])
		has_coords = cleaned["latitude"].notna() & cleaned["longitude"].notna()
		invalid_coords = has_coords & (
			~cleaned["latitude"].between(-90, 90, inclusive="both")
			| ~cleaned["longitude"].between(-180, 180, inclusive="both")
		)
		cleaned = cleaned.loc[~invalid_coords].copy()
		risk_factors_source = cleaned.get("risk_factors", pd.Series([()] * len(cleaned), index=cleaned.index))
		cleaned.loc[:, "risk_factors"] = risk_factors_source.apply(
			lambda value: tuple(value) if isinstance(value, list | tuple) else ()
		)
		cleaned = cleaned.sort_values(by=["timestamp", "severity", "confidence"], ascending=[False, False, False])
		cleaned = cleaned.reset_index(drop=True)
		LOGGER.debug("Cleaned dataset: %d rows", len(cleaned))
		return cleaned
	except Exception as exc:  # pragma: no cover - defensive guard
		LOGGER.exception("Cleaning pipeline failed")
		raise PipelineError("Failed to clean operational dataset") from exc
