import math
from datetime import datetime

import pytest

from app.physics.wbgt import solar_zenith_angle


def test_solar_noon_summer_solstice_delhi():
    # 06:50 UTC = 12:20 IST, which is solar noon in Delhi.
    # Sun sits at 23.45 N on the solstice, Delhi is at 28.6 N,
    # so the zenith angle should be about 5.15 degrees.
    z = solar_zenith_angle(28.6, 77.2, datetime(2026, 6, 21, 6, 50))
    assert math.degrees(z) == pytest.approx(5.15, abs=0.3)

    