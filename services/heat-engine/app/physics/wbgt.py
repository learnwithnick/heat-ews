# Wet Bulb Globe Temperature (WBGT): heat stress metric combining air
# temperature, humidity, wind, and radiant load. Basis for ISO 7243
# work-rest guidance.

import math
from datetime import datetime


def solar_zenith_angle(lat_deg: float, lon_deg: float, when_utc: datetime) -> float:
    """Solar zenith angle in radians. Values > pi/2 mean the sun is below the horizon."""
    n = when_utc.timetuple().tm_yday
    declination_deg = 23.45 * math.sin(math.radians(360 * (284 + n) / 365))

    utc_hour = when_utc.hour + when_utc.minute / 60
    solar_hour = utc_hour + lon_deg / 15
    hour_angle_deg = 15 * (solar_hour - 12)

    lat_rad = math.radians(lat_deg)
    dec_rad = math.radians(declination_deg)
    ha_rad = math.radians(hour_angle_deg)

    cos_zenith = (
        math.sin(lat_rad) * math.sin(dec_rad)
        + math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad)
    )
    cos_zenith = max(-1.0, min(1.0, cos_zenith))

    return math.acos(cos_zenith)


def globe_temperature(
    t2m: float,           # air temperature, °C
    wind10m: float,       # wind speed, m/s at 10 m
    dni: float,           # direct normal irradiance, W/m²
    diffuse: float,       # diffuse radiation, W/m²
    pressure_hpa: float,  # surface pressure, hPa
    zenith_rad: float,    # solar zenith angle, radians
) -> float:
    """Black globe temperature in °C (Liljegren et al., 2008)."""
    ...