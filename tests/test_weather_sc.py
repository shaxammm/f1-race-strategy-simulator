import numpy as np
import pytest

from src.models import Compound, RaceConfig, Stint, Strategy
from src.safety_car import draw_safety_car_laps
from src.simulation import simulate_strategy
from src.weather import Weather, weather_penalty_s


def strategy() -> Strategy:
    return Strategy("S-M", (Stint(Compound.SOFT, 20), Stint(Compound.MEDIUM, 37)))


def test_dry_has_no_penalty():
    assert weather_penalty_s(Weather.DRY, 10, 57) == 0.0


def test_heavy_rain_slower_than_light_rain():
    assert weather_penalty_s(Weather.HEAVY_RAIN, 10, 57) > weather_penalty_s(Weather.LIGHT_RAIN, 10, 57)


def test_changing_weather_rains_only_in_middle():
    assert weather_penalty_s(Weather.CHANGING, 5, 57) == 0.0
    assert weather_penalty_s(Weather.CHANGING, 30, 57) > 0.0
    assert weather_penalty_s(Weather.CHANGING, 55, 57) == 0.0


def test_rain_makes_race_slower():
    dry = simulate_strategy(RaceConfig(), strategy(), noise_std_s=0.0)
    wet = simulate_strategy(RaceConfig(), strategy(), noise_std_s=0.0, weather=Weather.HEAVY_RAIN)
    assert wet.total_time_s > dry.total_time_s


def test_zero_probability_gives_no_safety_car():
    rng = np.random.default_rng(1)
    assert draw_safety_car_laps(57, 0.0, rng) == set()


def test_certain_probability_gives_safety_car():
    rng = np.random.default_rng(1)
    laps = draw_safety_car_laps(57, 1.0, rng)
    assert len(laps) == 4
    assert min(laps) >= 2 and max(laps) <= 57


def test_invalid_probability_rejected():
    with pytest.raises(ValueError):
        draw_safety_car_laps(57, 1.5, np.random.default_rng(0))


def test_safety_car_laps_are_recorded():
    cfg = RaceConfig(safety_car_prob=1.0)
    result = simulate_strategy(cfg, strategy(), noise_std_s=0.0, seed=3)
    assert len(result.safety_car_laps) == 4
