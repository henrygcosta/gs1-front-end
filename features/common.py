"""Shared helpers for feature modules.

The feature layer builds business-oriented view models on top of the pipeline
outputs without depending on Streamlit widgets or page code.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from pipelines.common import dataframe_cache_key, insight_for_row, operational_headline, recommendation_for_event, risk_alert_level


@dataclass(frozen=True, slots=True)
class FeatureContext:
	"""Container with the canonical datasets consumed by feature modules."""

	region: str
	period_days: int
	event_types: list[str]
	raw_events: pd.DataFrame
	cleaned_events: pd.DataFrame
	enriched_events: pd.DataFrame
	risk_summary: pd.DataFrame
	alert_feed: pd.DataFrame


@dataclass(frozen=True, slots=True)
class MetricCard:
	"""Simple KPI-like metric used across feature modules."""

	label: str
	value: str
	helper: str | None = None
	kind: str = "info"


@dataclass(frozen=True, slots=True)
class NarrativeBlock:
	"""Textual insight used for executive summaries and storytelling."""

	title: str
	text: str
	kind: str = "info"


@dataclass(frozen=True, slots=True)
class FeatureSection:
	"""Generic section wrapper for a reusable feature output."""

	title: str
	subtitle: str
	metrics: list[MetricCard]
	frames: dict[str, pd.DataFrame]
	narratives: list[NarrativeBlock]


@dataclass(frozen=True, slots=True)
class TopFinding:
	"""Compact record used to highlight a relevant operational item."""

	label: str
	region: str
	state: str
	alert_level: str
	risk_score: float
	description: str


FEATURE_CACHE_KWARGS = {pd.DataFrame: dataframe_cache_key}


def top_records(frame: pd.DataFrame, *, sort_by: str, limit: int = 5, ascending: bool = False) -> pd.DataFrame:
	"""Return the most relevant records from a frame.

	The function always returns a copy to protect the cached source frame.
	"""
	if frame.empty or sort_by not in frame.columns:
		return frame.head(0).copy()
	return frame.sort_values(sort_by, ascending=ascending).head(limit).copy()


def top_findings(frame: pd.DataFrame, *, label_column: str = "event_type", limit: int = 5) -> list[TopFinding]:
	"""Build a list of reusable operational findings from a frame."""
	if frame.empty:
		return []
	selected = top_records(frame, sort_by="risk_score", limit=limit)
	findings: list[TopFinding] = []
	for _, row in selected.iterrows():
		findings.append(
			TopFinding(
				label=str(row.get(label_column, row.get("event_type", "Evento"))),
				region=str(row.get("region", "Global")),
				state=str(row.get("state", "")),
				alert_level=str(row.get("alert_level", risk_alert_level(float(row.get("risk_score", 0.0))))),
				risk_score=float(row.get("risk_score", 0.0)),
				description=insight_for_row(
					str(row.get("event_type", "Evento")),
					str(row.get("region", "Global")),
					str(row.get("state", "")),
					str(row.get("alert_level", risk_alert_level(float(row.get("risk_score", 0.0))))),
					str(row.get("geographic_criticality_class", "media")),
				),
			)
		)
	return findings


def narrative_blocks_from_findings(findings: list[TopFinding], *, prefix: str) -> list[NarrativeBlock]:
	"""Convert top findings into short narrative blocks."""
	blocks: list[NarrativeBlock] = []
	for finding in findings[:3]:
		blocks.append(
			NarrativeBlock(
				title=f"{prefix}: {finding.label}",
				text=f"{finding.region}/{finding.state} | alerta {finding.alert_level} | risco {finding.risk_score:.2f}",
				kind=finding.alert_level,
			)
		)
	return blocks


def executive_headline(context: FeatureContext, *, top_region: str | None = None) -> str:
	"""Generate a standard executive headline for the dashboard."""
	region = top_region or context.region
	return operational_headline(len(context.enriched_events), int((context.enriched_events.get("is_critical", pd.Series(dtype=bool)).fillna(False)).sum()), region)
