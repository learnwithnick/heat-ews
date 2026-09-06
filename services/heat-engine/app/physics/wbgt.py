# Wet Bulb Globe Temperature (WBGT): heat stress metric combining air
# temperature, humidity, wind, and radiant load. Basis for ISO 7243
# work-rest guidance.

import math
from datetime import datetime


STEFAN_BOLTZMANN = 5.67e-8   # W/m²K⁴
GLOBE_EMISSIVITY = 0.95      # matte black paint
GLOBE_DIAMETER_M = 0.15      # standard 150 mm globe
GROUND_ALBEDO = 0.15         # typical urban surface
SURFACE_ROUGHNESS_M = 1.0    # dense urban terrain
AIR_CONDUCTIVITY = 0.026     # W/m·K
AIR_VISCOSITY = 1.5e-5       # m²/s, kinematic
PRANDTL = 0.71               # dimensionless, air


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
    ta_k = t2m + 273.15

    # Global horizontal irradiance, floored at zero for night hours.
    solar_total = max(0.0, dni * math.cos(zenith_rad) + diffuse)

    # Wind at globe height (2 m) from the 10 m forecast value,
    # log profile over dense urban roughness.
    wind = max(0.13, wind10m)
    wind_2m = wind * (
        math.log(2.0 / SURFACE_ROUGHNESS_M)
        / math.log(10.0 / SURFACE_ROUGHNESS_M)
    )

    # Convective heat transfer coefficient for a sphere in cross-flow.
    reynolds = wind_2m * GLOBE_DIAMETER_M / AIR_VISCOSITY
    nusselt = 2 + 0.6 * reynolds**0.5 * PRANDTL**0.33
    h = nusselt * AIR_CONDUCTIVITY / GLOBE_DIAMETER_M

    # Sky emissivity: crude clear-sky estimate. Overcast pushes this toward 1.
    sky_emissivity = 0.75
    ir_down = sky_emissivity * STEFAN_BOLTZMANN * ta_k**4
    ir_up = STEFAN_BOLTZMANN * ta_k**4  # ground assumed at air temperature

    # Absorbed solar: quarter factor from sphere cross-section / surface area,
    # plus the ground-reflected component.
    absorbed_solar = 0.25 * (1 - 0.05) * solar_total * (1 + GROUND_ALBEDO)

    # Iterate: energy in = energy out. Tg appears as Tg^4 and linearly,
    # so there is no closed form.
    tg_k = ta_k
    for _ in range(50):
        emitted = GLOBE_EMISSIVITY * STEFAN_BOLTZMANN * tg_k**4
        absorbed_ir = GLOBE_EMISSIVITY * 0.5 * (ir_down + ir_up)
        convection = h * (ta_k - tg_k)

        imbalance = absorbed_solar + absorbed_ir + convection - emitted

        # Derivative of imbalance with respect to tg_k, for Newton's method.
        derivative = -4 * GLOBE_EMISSIVITY * STEFAN_BOLTZMANN * tg_k**3 - h
        step = imbalance / derivative

        tg_k -= step
        if abs(step) < 0.01:
            break

    return tg_k - 273.15