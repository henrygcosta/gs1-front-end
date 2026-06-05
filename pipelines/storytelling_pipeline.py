"""Storytelling pipeline stage.

Builds text-based outputs that explain the operational state to humans.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
import streamlit as st

from pipelines.common import operational_headline
from utils.exceptions import PipelineError
from utils.logger import get_logger

LOGGER = get_logger(__name__)


@dataclass(slots=True)
class StorytellingPayload:
	"""Narrative payload used by the dashboard and human-in-the-loop pages."""

	headline: str = ""
	summary: str = ""
	key_findings: list[str] = field(default_factory=list)
	recommendations: list[str] = field(default_factory=list)
	top_regions: list[str] = field(default_factory=list)
	top_event_types: list[str] = field(default_factory=list)
	alert_highlights: pd.DataFrame = field(default_factory=pd.DataFrame)


def _top_values(frame: pd.DataFrame, column: str, limit: int = 3) -> list[str]:
	"""Return the most frequent values for a column."""
	return frame[column].value_counts().head(limit).index.astype(str).tolist()


@st.cache_data(show_spinner=False, ttl=300)
def build_storytelling_payload(
	enriched_events: pd.DataFrame,
	risk_summary: pd.DataFrame,
	alert_feed: pd.DataFrame | None = None,
) -> StorytellingPayload:
	"""Create a narrative payload from operational metrics and alerts."""
	try:
		if enriched_events.empty:
			return StorytellingPayload(
				headline="Nenhum evento disponivel para narrar.",
				summary="Os filtros atuais nao retornaram dados suficientes para gerar narrativa.",
			)

		total_events = len(enriched_events)
		critical_events = int(enriched_events["is_critical"].sum())
		top_region = enriched_events["region"].value_counts().idxmax()
		top_state = enriched_events["state"].value_counts().idxmax()
		top_event_types = _top_values(enriched_events, "event_type", limit=4)
		top_regions = _top_values(enriched_events, "region", limit=4)
		alert_rows = alert_feed if alert_feed is not None and not alert_feed.empty else enriched_events.loc[
			enriched_events["is_critical"]
		, ["event_id", "event_type", "region", "state", "semantic_alert", "recommended_action"]
		]
		alert_preview = alert_rows.head(12).copy()

		headline = operational_headline(total_events, critical_events, top_region)
		primary_risk = risk_summary.sort_values(by="avg_risk_score", ascending=False).head(1)
		primary_event_type = primary_risk["event_type"].iloc[0] if not primary_risk.empty else "eventos diversos"
		avg_risk = float(risk_summary["avg_risk_score"].mean()) if not risk_summary.empty else 0.0
		criticality_text = "alta" if critical_events else "moderada"
		summary = (
			f"O centro de monitoramento acompanha {total_events} registros, com {critical_events} pontos criticos "
			f"e concentracao principal em {top_region}/{top_state}. O evento com maior risco agregado foi {primary_event_type}, "
			f"enquanto o risco medio consolidado do recorte permanece em {avg_risk:.2f} ({criticality_text})."
		)
		key_findings = [
			f"Maior concentracao operacional em {top_region}/{top_state}.",
			f"Top 4 categorias de evento: {', '.join(top_event_types)}.",
			f"{critical_events} eventos classificados como criticos.",
		]
		recommendations = [
			"Reforcar monitoramento espacial nas regioes com maior prioridade.",
			"Manter revisao humana para alertas criticos antes da notificacao externa.",
			"Acompanhar tendencia temporal para identificar escalada de severidade.",
		]

		LOGGER.debug("Storytelling payload built: total=%d critical=%d", total_events, critical_events)
		return StorytellingPayload(
			headline=headline,
			summary=summary,
			key_findings=key_findings,
			recommendations=recommendations,
			top_regions=top_regions,
			top_event_types=top_event_types,
			alert_highlights=alert_preview,
		)
	except Exception as exc:  # pragma: no cover - defensive guard
		LOGGER.exception("Storytelling pipeline failed")
		raise PipelineError("Failed to build storytelling payload") from exc
