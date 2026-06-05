"""Satellite provider scaffold for future integration with raster/vector APIs.

Currently a placeholder to keep the providers surface consistent.
"""

from __future__ import annotations

import pandas as pd

from utils.logger import get_logger

LOGGER = get_logger(__name__)


class SatelliteApiProvider:
	"""Placeholder for satellite-derived signals.

	Real implementations should return DataFrame with appropriate columns
	such as `feature_id`, `region`, `signal_type`, `value`, `timestamp`.
	"""

	def fetch_satellite_signals(self, region: str, period_days: int) -> pd.DataFrame:
		raise NotImplementedError("SatelliteApiProvider is not implemented yet.")
