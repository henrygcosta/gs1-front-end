"""Shared helpers for pipeline stages.

The functions in this module are intentionally pure and reusable so that
cleaning, enrichment, alerting and storytelling stages can share the same
business rules without duplicating logic.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import pandas as pd

from utils.exceptions import PipelineError

SEVERITY_BANDS = (
	(0.25, "baixa"),
	(0.50, "moderada"),
	(0.75, "alta"),
	(1.01, "critica"),
)

CRITICALITY_BANDS = (
	(0.30, "baixa"),
	(0.55, "media"),
	(0.80, "alta"),
	(1.01, "muito_alta"),
)


@dataclass(frozen=True, slots=True)
class RiskWeights:
	"""Weights used by the climate risk scoring formula."""

	severity: float = 0.42
	confidence_gap: float = 0.16
	indicator_pressure: float = 0.24
	spatial_pressure: float = 0.18


def ensure_columns(frame: pd.DataFrame, required: Iterable[str], *, stage: str) -> None:
	"""Raise a pipeline error if any required column is missing."""
	missing = [column for column in required if column not in frame.columns]
	if missing:
		raise PipelineError(f"{stage}: missing required columns: {', '.join(missing)}")


def dataframe_cache_key(frame: pd.DataFrame) -> str:
	"""Return a stable cache key for DataFrame arguments.

	The key normalizes object columns to string representations so Streamlit
	does not fall back to pickling nested list-like values.
	"""
	normalized = frame.copy()
	for column in normalized.columns:
		if normalized[column].dtype == "object":
			normalized.loc[:, column] = normalized[column].map(
				lambda value: repr(tuple(value)) if isinstance(value, (list, tuple)) else repr(value)
			)
	return f"{tuple(normalized.columns)}|{normalized.shape}|{pd.util.hash_pandas_object(normalized, index=True).sum()}"


def clamp_series(series: pd.Series, minimum: float = 0.0, maximum: float = 1.0) -> pd.Series:
	"""Clamp a numeric series to a range."""
	return series.astype(float).clip(lower=minimum, upper=maximum)


def safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
	"""Return a ratio while protecting against division by zero."""
	denominator = denominator.replace(0, pd.NA)
	return (numerator / denominator).fillna(0.0)


def band_score(value: float) -> str:
	"""Return a band label for a score in the 0-1 range."""
	for threshold, label in SEVERITY_BANDS:
		if value < threshold:
			return label
	return "critica"


def band_geographic_criticality(value: float) -> str:
	"""Return a geographic criticality band for a score in the 0-1 range."""
	for threshold, label in CRITICALITY_BANDS:
		if value < threshold:
			return label
	return "muito_alta"


def risk_alert_level(score: float) -> str:
	"""Map a risk score to a semantic alert level."""
	if score >= 0.85:
		return "critico"
	if score >= 0.70:
		return "alto"
	if score >= 0.45:
		return "moderado"
	return "observacao"


def recommendation_for_event(event_type: str, alert_level: str) -> str:
	"""Return a concise operational recommendation for an event."""
	normalized = event_type.lower()
	if normalized in {"flood", "enchente"}:
		base = "Acionar monitoramento hidrologico e rotas de contingencia."
	elif normalized in {"landslide", "deslizamento"}:
		base = "Revisar encostas, drenagem e areas de ocupacao vulneravel."
	elif normalized in {"drought", "seca"}:
		base = "Priorizar reservas de agua e acompanhamento de estresse hidrico."
	elif normalized in {"fire", "queimada"}:
		base = "Envolver vigilancia territorial e resposta rapida a focos ativos."
	elif normalized in {"airquality", "qualidade do ar"}:
		base = "Avaliar exposicao populacional e comunicados de saude publica."
	else:
		base = "Revisar a area com prioridade operacional e validar o alerta."

	if alert_level == "critico":
		return f"{base} Escalar para comando imediato e notificar a defesa civil."
	if alert_level == "alto":
		return f"{base} Acompanhar de perto nas proximas horas."
	return base


def insight_for_row(event_type: str, region: str, state: str, alert_level: str, criticality: str) -> str:
	"""Generate a short textual insight for one operational record."""
	return (
		f"{event_type} em {region}/{state} com criticidade {criticality} e alerta {alert_level}. "
		"O recorte atual exige priorizacao espacial e acompanhamento temporal."
	)


def operational_headline(total_events: int, critical_events: int, top_region: str) -> str:
	"""Generate a high-level operational headline."""
	return (
		f"Centro em vigilancia: {total_events} eventos analisados, {critical_events} criticos, "
		f"com maior concentracao em {top_region}."
	)
