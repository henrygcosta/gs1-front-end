"""HTTP climate provider scaffold using `httpx`.

This implementation demonstrates a production-ready shape: accepts an
`httpx.Client` instance and performs requests with retry/timeout behaviors.
The concrete API integration is intentionally left to be configured per
deployment (URLs, auth, schema)."""

from __future__ import annotations

from typing import Any

import pandas as pd
import httpx

from utils.logger import get_logger
from utils.exceptions import DataProviderError


LOGGER = get_logger(__name__)


class ClimateApiProvider:
	"""Simple HTTP-backed climate provider scaffold."""

	def __init__(self, client: httpx.Client) -> None:
		self._client = client

	def fetch_events(self, region: str, period_days: int) -> pd.DataFrame:
		"""Fetch events from remote API and return as pandas DataFrame.

		Must be adapted to the target API's contract.
		"""
		try:
			# Example endpoint composition (override in real implementation)
			url = f"/api/events?region={region}&days={period_days}"
			resp = self._client.get(url)
			resp.raise_for_status()
			payload = resp.json()
			# Convert to DataFrame assuming list-of-dicts payload
			return pd.DataFrame(payload)
		except Exception as exc:  # pragma: no cover - environment dependent
			LOGGER.exception("ClimateApiProvider request failed")
			raise DataProviderError("Failed to fetch climate events from API") from exc
