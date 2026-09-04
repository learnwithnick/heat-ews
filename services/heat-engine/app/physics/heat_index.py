"""NWS Rothfusz regression heat index.

Reference: Rothfusz, L.P. (1990), NWS Technical Attachment SR 90-23.
"""

import math


def heat_index_f(temp_f: float, rh: float) -> float:
    """Heat index in °F given air temperature in °F and relative humidity in %."""
    simple = 0.5 * (temp_f + 61.0 + ((temp_f - 68.0) * 1.2) + (rh * 0.094))

    if (simple + temp_f) / 2.0 < 80.0:
        return simple

    hi = (
        -42.379
        + 2.04901523 * temp_f
        + 10.14333127 * rh
        - 0.22475541 * temp_f * rh
        - 0.00683783 * temp_f * temp_f
        - 0.05481717 * rh * rh
        + 0.00122874 * temp_f * temp_f * rh
        + 0.00085282 * temp_f * rh * rh
        - 0.00000199 * temp_f * temp_f * rh * rh
    )

    if rh < 13.0 and 80.0 <= temp_f <= 112.0:
        hi -= ((13.0 - rh) / 4.0) * math.sqrt((17.0 - abs(temp_f - 95.0)) / 17.0)
    elif rh > 85.0 and 80.0 <= temp_f <= 87.0:
        hi += ((rh - 85.0) / 10.0) * ((87.0 - temp_f) / 5.0)

    return hi


def heat_index_c(temp_c: float, rh: float) -> float:
    """Heat index in °C given air temperature in °C and relative humidity in %."""
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    hi_f = heat_index_f(temp_f, rh)
    return (hi_f - 32.0) * 5.0 / 9.0
