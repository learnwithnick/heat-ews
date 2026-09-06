import math
from datetime import datetime

import pytest

from app.physics.wbgt import globe_temperature, solar_zenith_angle


def test_solar_noon_summer_solstice_delhi():
    # 06:50 UTC = 12:20 IST, which is solar noon in Delhi.
    # Sun sits at 23.45 N on the solstice, Delhi is at 28.6 N,
    # so the zenith angle should be about 5.15 degrees.
    z = solar_zenith_angle(28.6, 77.2, datetime(2026, 6, 21, 6, 50))
    assert math.degrees(z) == pytest.approx(5.15, abs=0.3)


def test_sunrise_summer_solstice_delhi():
    # 00:00 UTC = 05:30 IST, close to sunrise in Delhi on the solstice.
    # Zenith just under 90 degrees means the sun is barely above the horizon.
    z = solar_zenith_angle(28.6, 77.2, datetime(2026, 6, 21, 0, 0))
    assert math.degrees(z) == pytest.approx(89.3, abs=1.0)


def test_globe_hotter_than_air_in_strong_sun():
    tg = globe_temperature(40, 2.0, 800, 150, 1000, math.radians(20))
    assert tg > 40


def test_globe_cooler_than_air_at_night():
    # No solar input; the globe radiates to a cold sky.
    tg = globe_temperature(30, 2.0, 0, 0, 1000, math.radians(120))
    assert tg < 30

    