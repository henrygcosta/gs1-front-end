"""Tests for provider composition and mock data providers."""

from __future__ import annotations

from providers import provider_factory
from providers.mock_provider import (
	MockAirQualityProvider,
	MockClimateProvider,
	MockFireProvider,
	MockGeoProvider,
)
from utils.config import Settings


def test_get_provider_container_uses_mock_providers(monkeypatch) -> None:
	monkeypatch.setattr(provider_factory, "get_settings", lambda: Settings(use_mock_provider=True))
	clear = getattr(provider_factory.get_provider_container, "clear", None)
	if callable(clear):
		clear()

	container = provider_factory.get_provider_container()
	again = provider_factory.get_provider_container()

	assert type(container.climate) is MockClimateProvider
	assert type(container.geo) is MockGeoProvider
	assert type(container.fire) is MockFireProvider
	assert type(container.air_quality) is MockAirQualityProvider
	assert container is again


def test_mock_climate_provider_generates_reproducible_daily_events() -> None:
	provider = MockClimateProvider()
	frame = provider.fetch_events("Brazil", 4)

	assert len(frame) == 20
	assert {"event_id", "region", "state", "event_type", "severity", "confidence", "latitude", "longitude", "timestamp"}.issubset(frame.columns)
	assert frame["region"].eq("Brazil").all()


def test_mock_geo_provider_returns_centroids_and_population() -> None:
	frame = MockGeoProvider().fetch_regions()

	assert not frame.empty
	assert {"region", "state", "centroid_lat", "centroid_lon", "population"}.issubset(frame.columns)


def test_mock_air_quality_provider_generates_expected_samples() -> None:
	frame = MockAirQualityProvider().fetch_air_quality("Brazil", 3)

	assert len(frame) == 12
	assert {"sample_id", "region", "state", "pm25", "pm10", "no2", "aqi", "timestamp"}.issubset(frame.columns)


def test_mock_fire_provider_returns_fire_schema() -> None:
	frame = MockFireProvider().fetch_fires("Brazil", 10)

	assert {"fire_id", "region", "state", "brightness", "confidence", "latitude", "longitude", "timestamp"}.issubset(frame.columns)
	assert frame["region"].dropna().isin(["Brazil"]).all()
