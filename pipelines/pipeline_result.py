"""Pipeline output structures."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(slots=True)
class PipelineResult:
	"""Standard pipeline result for dashboard consumption."""

	raw_events: pd.DataFrame
	cleaned_events: pd.DataFrame
	enriched_events: pd.DataFrame
	risk_summary: pd.DataFrame
	alert_feed: pd.DataFrame = field(default_factory=pd.DataFrame)
	visualization_frames: dict[str, pd.DataFrame] = field(default_factory=dict)
	storytelling_payload: dict[str, object] = field(default_factory=dict)
