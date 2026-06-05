"""Geospatial provider scaffold using `httpx`.

Provides an example shape for real geospatial API integration. Real
implementations should return a pandas.DataFrame with region metadata.
"""

from __future__ import annotations

import httpx
import pandas as pd

from utils.exceptions import DataProviderError
from utils.logger import get_logger

LOGGER = get_logger(__name__)


class GeoApiProvider:
	"""HTTP-backed geospatial provider scaffold."""

	def __init__(self, client: httpx.Client) -> None:
		self._client = client

	def fetch_regions(self) -> pd.DataFrame:
		"""Fetch regions metadata from a remote service."""
		try:
			url = "/api/regions"
			resp = self._client.get(url)
			resp.raise_for_status()
			return pd.DataFrame(resp.json())
		except Exception as exc:  # pragma: no cover - depends on external service
			LOGGER.exception("GeoApiProvider request failed")
			raise DataProviderError("Failed to fetch region metadata from API") from exc
