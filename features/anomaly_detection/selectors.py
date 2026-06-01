"""Selectors for the anomaly detection feature."""

from __future__ import annotations

import pandas as pd

from features.common import FeatureContext, NarrativeBlock, narrative_blocks_from_findings, top_findings, top_records


def select_low_confidence(context: FeatureContext) -> pd.DataFrame:
	"""Return the low-confidence events used in anomaly inspection."""
	if context.enriched_events.empty:
		return context.enriched_events.head(0).copy()
	return top_records(context.enriched_events[context.enriched_events["confidence"] < 0.6], sort_by="risk_score", limit=20)


def select_confidence_bands(context: FeatureContext) -> pd.DataFrame:
	"""Return a confidence band distribution."""
	if context.enriched_events.empty:
		return context.enriched_events.head(0).copy()
	bins = pd.cut(context.enriched_events["confidence"], bins=[-0.01, 0.4, 0.6, 0.8, 1.0], labels=["muito_baixa", "baixa", "media", "alta"])
	return bins.value_counts(dropna=False).rename_axis("confidence_band").reset_index(name="total_events")


def select_text_analysis(context: FeatureContext) -> list[NarrativeBlock]:
	"""Build narrative text blocks for anomaly review."""
	return narrative_blocks_from_findings(top_findings(context.enriched_events[context.enriched_events["confidence"] < 0.7], limit=4), prefix="Anomalias")


def select_recommendations(context: FeatureContext) -> list[str]:
	"""Return concise recommendations for the anomaly panel."""
	findings = top_findings(context.enriched_events[context.enriched_events["confidence"] < 0.7], limit=4)
	return [finding.description for finding in findings]

