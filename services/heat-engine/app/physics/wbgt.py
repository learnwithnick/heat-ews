# Wet Bulb Globe Temperature (WBGT): heat stress metric combining air
# temperature, humidity, wind, and radiant load. Basis for ISO 7243
# work-rest guidance.
#
# Method follows Liljegren et al. (2008), "Modeling the Wet Bulb Globe
# Temperature Using Standard Meteorological Measurements", J. Occup.
# Environ. Hyg. 5(10). Simplifications are noted inline.

import math
from datetime import datetime


# Physical constants
STEFAN_BOLTZMANN = 5.67e-8      # W/m²K⁴
LATENT_HEAT_VAP = 2.45e6        # J/kg, water at ~30°C
CP_AIR = 1005.0                 # J/kg·K, specific heat of air
MW_RATIO = 0.622                # molecular weight water / dry air
LEWIS_NUMBER = 0.85             # air-water vapour

# Instrument properties
GLOBE_EMISSIVITY = 0.95         # matte black paint
GLOBE_ABSORPTIVITY = 0.95
GLOBE_DIAMETER_M = 0.15         # standard 150 mm globe
WICK_EMISSIVITY = 0.95
WICK_ABSORPTIVITY = 0.40        # wet cotton, far less than the black globe
WICK_DIAMETER_M = 0.007         # 7 mm wick

# Environment
GROUND_ALBEDO = 0.15            # typical urban surface
SURFACE_ROUGHNESS_M = 1.0       # dense urban terrain
SKY_EMISSIVITY = 0.75           # clear-sky estimate; ~0.95 under overcast
MIN_WIND_MS = 0.13              # solver floor, per reference implementation

# Air properties (evaluated near 30°C, 1000 hPa)
AIR_CONDUCTIVITY = 0.026        # W/m·K
AIR_VISCOSITY = 1.5e-5          # m²/s, kinematic
PRANDTL = 0.71


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


def saturation_vapour_pressure(temp_c: float) -> float:
    """Saturation vapour pressure in hPa (Magnus formula)."""
    return 6.112 * math.exp(17.67 * temp_c / (temp_c + 243.5))


def _wind_at_2m(wind10m: float) -> float:
    """Log-profile conversion from 10 m forecast wind to 2 m instrument height."""
    wind = max(MIN_WIND_MS, wind10m)
    return wind * (
        math.log(2.0 / SURFACE_ROUGHNESS_M) / math.log(10.0 / SURFACE_ROUGHNESS_M)
    )


def _solar_horizontal(dni: float, diffuse: float, zenith_rad: float) -> float:
    """Global horizontal irradiance in W/m², floored at zero for night hours."""
    return max(0.0, dni * math.cos(zenith_rad) + diffuse)


def _convection_coefficient(wind_2m: float, diameter_m: float) -> float:
    """Convective heat transfer coefficient, W/m²K, for a cylinder or sphere in cross-flow."""
    reynolds = wind_2m * diameter_m / AIR_VISCOSITY
    nusselt = 2 + 0.6 * reynolds**0.5 * PRANDTL**0.33
    return nusselt * AIR_CONDUCTIVITY / diameter_m


def globe_temperature(
    t2m: float,           # air temperature, °C
    wind10m: float,       # wind speed, m/s at 10 m
    dni: float,           # direct normal irradiance, W/m²
    diffuse: float,       # diffuse radiation, W/m²
    pressure_hpa: float,  # surface pressure, hPa
    zenith_rad: float,    # solar zenith angle, radians
) -> float:
    """Black globe temperature in °C.

    Solves the radiative-convective energy balance on a 150 mm matte black
    sphere. Tg appears both as Tg^4 (emission) and linearly (convection),
    so there is no closed form; Newton's method is used.
    """
    ta_k = t2m + 273.15
    solar_total = _solar_horizontal(dni, diffuse, zenith_rad)
    wind_2m = _wind_at_2m(wind10m)
    h = _convection_coefficient(wind_2m, GLOBE_DIAMETER_M)

    # Longwave environment: sky above, ground below, each half the view factor.
    ir_down = SKY_EMISSIVITY * STEFAN_BOLTZMANN * ta_k**4
    ir_up = STEFAN_BOLTZMANN * ta_k**4  # ground assumed at air temperature
    absorbed_ir = GLOBE_EMISSIVITY * 0.5 * (ir_down + ir_up)

    # Sphere absorbs the beam over its cross-section (pi r^2) but radiates
    # from its full surface (4 pi r^2), hence the 1/4 factor. The albedo
    # term adds sunlight reflected up off the ground.
    absorbed_solar = 0.25 * GLOBE_ABSORPTIVITY * solar_total * (1 + GROUND_ALBEDO)

    tg_k = ta_k
    for _ in range(50):
        emitted = GLOBE_EMISSIVITY * STEFAN_BOLTZMANN * tg_k**4
        convection = h * (ta_k - tg_k)
        imbalance = absorbed_solar + absorbed_ir + convection - emitted

        derivative = -4 * GLOBE_EMISSIVITY * STEFAN_BOLTZMANN * tg_k**3 - h
        step = imbalance / derivative
        tg_k -= step

        if abs(step) < 0.01:
            break

    return tg_k - 273.15


def natural_wet_bulb(
    t2m: float,           # air temperature, °C
    rh: float,            # relative humidity, %
    wind10m: float,       # wind speed, m/s at 10 m
    dni: float,           # direct normal irradiance, W/m²
    diffuse: float,       # diffuse radiation, W/m²
    pressure_hpa: float,  # surface pressure, hPa
    zenith_rad: float,    # solar zenith angle, radians
) -> float:
    """Natural wet bulb temperature in °C.

    Energy balance on a wetted cotton wick exposed to sun and wind. Unlike
    the psychrometric wet bulb, this instrument is unshielded, so it absorbs
    solar and longwave radiation as well as losing heat to evaporation.

    Simplification vs Liljegren: air properties are evaluated at a fixed
    reference state rather than iterated with wick temperature, and the
    wick is treated as isothermal. Both are small effects at Delhi
    conditions but should be noted in the methodology.
    """
    ta_k = t2m + 273.15
    solar_total = _solar_horizontal(dni, diffuse, zenith_rad)
    wind_2m = _wind_at_2m(wind10m)
    h = _convection_coefficient(wind_2m, WICK_DIAMETER_M)

    # Actual vapour pressure of the ambient air.
    ea = saturation_vapour_pressure(t2m) * rh / 100.0

    ir_down = SKY_EMISSIVITY * STEFAN_BOLTZMANN * ta_k**4
    ir_up = STEFAN_BOLTZMANN * ta_k**4
    absorbed_ir = WICK_EMISSIVITY * 0.5 * (ir_down + ir_up)

    # Cylinder, not sphere: absorbs over diameter x length, radiates over
    # the full circumference, so the geometric factor is 1/pi rather than 1/4.
    absorbed_solar = (
        (1 / math.pi) * WICK_ABSORPTIVITY * solar_total * (1 + GROUND_ALBEDO)
    )

    # Evaporative coefficient from the Lewis relation. Converts a vapour
    # pressure difference (hPa) into a heat flux (W/m²).
    evap_coeff = (
        h * MW_RATIO * LATENT_HEAT_VAP
        / (CP_AIR * pressure_hpa * LEWIS_NUMBER ** (2 / 3))
    )

    tnw_k = ta_k - 5.0  # wet bulb always sits below air temperature
    for _ in range(50):
        tnw_c = tnw_k - 273.15
        es_wick = saturation_vapour_pressure(tnw_c)

        emitted = WICK_EMISSIVITY * STEFAN_BOLTZMANN * tnw_k**4
        convection = h * (ta_k - tnw_k)
        latent = evap_coeff * (es_wick - ea)

        imbalance = absorbed_solar + absorbed_ir + convection - emitted - latent

        # d(es)/dT for the Magnus formula, needed for Newton's method.
        des_dt = es_wick * 17.67 * 243.5 / (tnw_c + 243.5) ** 2
        derivative = (
            -4 * WICK_EMISSIVITY * STEFAN_BOLTZMANN * tnw_k**3
            - h
            - evap_coeff * des_dt
        )

        step = imbalance / derivative
        tnw_k -= step

        if abs(step) < 0.01:
            break

    return tnw_k - 273.15


def wbgt_outdoor(tnw: float, tg: float, ta: float) -> float:
    """WBGT for outdoor conditions with solar load, °C (ISO 7243)."""
    return 0.7 * tnw + 0.2 * tg + 0.1 * ta


def wbgt_from_weather(
    t2m: float,
    rh: float,
    wind10m: float,
    dni: float,
    diffuse: float,
    pressure_hpa: float,
    lat_deg: float,
    lon_deg: float,
    when_utc: datetime,
) -> float:
    """Full pipeline: weather variables in, WBGT in °C out."""
    zenith_rad = solar_zenith_angle(lat_deg, lon_deg, when_utc)

    tg = globe_temperature(t2m, wind10m, dni, diffuse, pressure_hpa, zenith_rad)
    tnw = natural_wet_bulb(
        t2m, rh, wind10m, dni, diffuse, pressure_hpa, zenith_rad
    )

    return wbgt_outdoor(tnw, tg, t2m)

