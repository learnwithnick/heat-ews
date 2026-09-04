import pytest

from app.physics.heat_index import heat_index_c, heat_index_f


@pytest.mark.parametrize(
    "temp_f, rh, expected",
    [
        # Rothfusz regression, no correction branch (13% <= RH <= 85%)
        (90.0, 40.0, 90.58),
        (90.0, 60.0, 99.68),
        # Low-humidity correction (RH < 13%, 80 <= T <= 112)
        (100.0, 10.0, 94.12),
        # High-humidity correction (RH > 85%, 80 <= T <= 87)
        (85.0, 90.0, 101.78),
        # Below the Rothfusz validity range: falls back to the simple formula
        (70.0, 50.0, 69.05),
    ],
)
def test_heat_index_f_reference_values(temp_f, rh, expected):
    assert heat_index_f(temp_f, rh) == pytest.approx(expected, abs=0.1)


def test_low_humidity_branch_reduces_below_unadjusted_rothfusz():
    # Same temperature, dropping RH below 13% should read cooler than a
    # borderline-humid reading once the correction kicks in.
    assert heat_index_f(100.0, 10.0) < heat_index_f(100.0, 13.0)


def test_high_humidity_branch_increases_above_unadjusted_rothfusz():
    assert heat_index_f(85.0, 90.0) > heat_index_f(85.0, 85.0)


def test_simple_formula_used_when_average_below_80():
    # At mild conditions the simple Steadman formula should govern, and it
    # must not accidentally invoke the Rothfusz polynomial.
    temp_f, rh = 70.0, 50.0
    simple = 0.5 * (temp_f + 61.0 + ((temp_f - 68.0) * 1.2) + (rh * 0.094))
    assert heat_index_f(temp_f, rh) == pytest.approx(simple, abs=1e-9)


def test_heat_index_c_matches_f_via_conversion():
    temp_c, rh = 32.2222, 40.0  # 90°F
    expected_c = (heat_index_f(90.0, rh) - 32.0) * 5.0 / 9.0
    assert heat_index_c(temp_c, rh) == pytest.approx(expected_c, abs=0.05)


def test_heat_index_increases_with_humidity_at_fixed_hot_temperature():
    values = [heat_index_f(95.0, rh) for rh in (30.0, 50.0, 70.0)]
    assert values == sorted(values)
