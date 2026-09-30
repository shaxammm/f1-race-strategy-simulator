import pytest

from src.models import Compound
from src.tyres import temperature_factor, tyre_penalty_s


def test_fresh_tyre_equals_compound_offset():
    assert tyre_penalty_s(Compound.SOFT, 0) == pytest.approx(-0.6)
    assert tyre_penalty_s(Compound.HARD, 0) == pytest.approx(0.5)


def test_penalty_grows_with_age():
    assert tyre_penalty_s(Compound.MEDIUM, 20) > tyre_penalty_s(Compound.MEDIUM, 5)


def test_soft_degrades_faster_than_hard():
    soft_growth = tyre_penalty_s(Compound.SOFT, 20) - tyre_penalty_s(Compound.SOFT, 0)
    hard_growth = tyre_penalty_s(Compound.HARD, 20) - tyre_penalty_s(Compound.HARD, 0)
    assert soft_growth > hard_growth


def test_hot_track_wears_more():
    cool = tyre_penalty_s(Compound.MEDIUM, 15, track_temp_c=20)
    hot = tyre_penalty_s(Compound.MEDIUM, 15, track_temp_c=45)
    assert hot > cool


def test_reference_temperature_factor_is_one():
    assert temperature_factor(30.0) == pytest.approx(1.0)


def test_negative_age_rejected():
    with pytest.raises(ValueError):
        tyre_penalty_s(Compound.SOFT, -1)
