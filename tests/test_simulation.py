import numpy as np
import pytest

from src.models import RaceConfig
from src.simulation import fuel_mass_kg, fuel_penalty_s, simulate_race


def test_fuel_mass_first_and_last_lap():
    cfg = RaceConfig()
    assert fuel_mass_kg(cfg, 1) == pytest.approx(100.0)
    assert fuel_mass_kg(cfg, cfg.n_laps) == pytest.approx(100.0 / 57)


def test_fuel_penalty_decreases_over_race():
    cfg = RaceConfig()
    assert fuel_penalty_s(cfg, 1) > fuel_penalty_s(cfg, cfg.n_laps)


def test_invalid_lap_raises():
    with pytest.raises(ValueError):
        fuel_mass_kg(RaceConfig(), 0)


def test_noiseless_total_time_matches_formula():
    result = simulate_race(RaceConfig(), noise_std_s=0.0)
    assert result.total_time_s == pytest.approx(5217.0)
    assert len(result.lap_times_s) == 57


def test_same_seed_is_reproducible():
    a = simulate_race(RaceConfig(), seed=42)
    b = simulate_race(RaceConfig(), seed=42)
    assert np.array_equal(a.lap_times_s, b.lap_times_s)


def test_different_seeds_differ():
    a = simulate_race(RaceConfig(), seed=1)
    b = simulate_race(RaceConfig(), seed=2)
    assert not np.array_equal(a.lap_times_s, b.lap_times_s)


def test_negative_noise_rejected():
    with pytest.raises(ValueError):
        simulate_race(RaceConfig(), noise_std_s=-0.1)
