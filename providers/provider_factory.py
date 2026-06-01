"""Provider factory and dependency composition."""

from __future__ import annotations

"""Factory to compose provider implementations.

Returns a `ProviderContainer` with concrete provider instances. Uses
`st.cache_resource` to keep long-lived clients and providers in memory.
"""

from dataclasses import dataclass

import httpx
import streamlit as st

from providers.contracts import ClimateDataProvider, GeoDataProvider, FireDataProvider, AirQualityProvider
from providers.mock_provider import (
	MockClimateProvider,
	MockGeoProvider,
	MockFireProvider,
	MockAirQualityProvider,
)
from providers.climate_provider import ClimateApiProvider
from providers.geo_provider import GeoApiProvider
from providers.satellite_provider import SatelliteApiProvider
from utils.config import get_settings
from utils.logger import get_logger


LOGGER = get_logger(__name__)


@dataclass(slots=True)
class ProviderContainer:
	"""Container holding provider instances used by the application."""

	climate: ClimateDataProvider
	geo: GeoDataProvider
	fire: FireDataProvider
	air_quality: AirQualityProvider
	satellite: object | None = None


@st.cache_resource
def get_provider_container() -> ProviderContainer:
	"""Create and cache provider instances according to configuration."""
	settings = get_settings()

	if settings.use_mock_provider:
		LOGGER.info("Using mock providers for all data sources")
		return ProviderContainer(
			climate=MockClimateProvider(),
			geo=MockGeoProvider(),
			fire=MockFireProvider(),
			air_quality=MockAirQualityProvider(),
			satellite=None,
		)

	# Example of how a real provider could be composed. Real implementations
	# must be added to providers/* and handle authentication, backoff and errors.
	client = httpx.Client(timeout=10.0)
	LOGGER.info("Using HTTP providers with shared client")
	return ProviderContainer(
		climate=ClimateApiProvider(client),
		geo=GeoApiProvider(client),
		fire=MockFireProvider(),
		air_quality=MockAirQualityProvider(),
		satellite=SatelliteApiProvider(),
	)
