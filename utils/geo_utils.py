"""Geospatial helper functions."""

from __future__ import annotations

from math import radians, sin, cos, sqrt, atan2


def haversine_distance_km(
	lat_a: float,
	lon_a: float,
	lat_b: float,
	lon_b: float,
) -> float:
	"""Compute distance in kilometers between two coordinates."""
	earth_radius_km = 6371.0

	d_lat = radians(lat_b - lat_a)
	d_lon = radians(lon_b - lon_a)

	a = (
		sin(d_lat / 2) ** 2
		+ cos(radians(lat_a)) * cos(radians(lat_b)) * sin(d_lon / 2) ** 2
	)
	c = 2 * atan2(sqrt(a), sqrt(1 - a))
	return earth_radius_km * c
