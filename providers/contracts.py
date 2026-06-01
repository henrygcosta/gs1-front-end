from __future__ import annotations

"""Provider contracts (ports) for external and mock data sources.

Define Protocols to decouple consumers from concrete implementations.
"""

from typing import Protocol

import pandas as pd


class ClimateDataProvider(Protocol):
	"""Port for climate event data retrieval."""

	def fetch_events(self, region: str, period_days: int) -> pd.DataFrame:
		"""Return climate events for the given region and period."""


class GeoDataProvider(Protocol):
	"""Port for geospatial metadata retrieval."""

	def fetch_regions(self) -> pd.DataFrame:
		"""Return available regions and geospatial references."""


class FireDataProvider(Protocol):
	"""Port for fire / queimadas event retrieval."""

	def fetch_fires(self, region: str, period_days: int) -> pd.DataFrame:
		"""Return fire events for the given region and period."""


class AirQualityProvider(Protocol):
	"""Port for air quality measurements and indices."""

	def fetch_air_quality(self, region: str, period_days: int) -> pd.DataFrame:
		"""Return air quality time-series for the given region and period."""
