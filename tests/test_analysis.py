import numpy as np
import pytest

from src.analysis import MonteCarloResult, compare_strategies, run_monte_carlo
from src.models import Compound, RaceConfig, Stint, Strategy


def strat() -> Strategy:
    return Strategy("S-M", (Stint(Compound.SOFT, 20), Stint(Compound.MEDIUM, 37)))


def test_same_seed_reproducible():
    a = run_monte_carlo(RaceConfig(), strat(), n_runs=50, seed=7)
    b = run_monte_carlo(RaceConfig(), strat(), n_runs=50, seed=7)
    assert np.array_equal(a.race_times_s, b.race_times_s)


def test_number_of_runs():
    r = run_monte_carlo(RaceConfig(), strat(), n_runs=30, seed=1)
    assert len(r.race_times_s) == 30


def test_statistics_are_consistent():
    r = run_monte_carlo(RaceConfig(), strat(), n_runs=200, seed=1)
    assert r.fastest_s <= r.median_s <= r.slowest_s
    assert r.std_s > 0


def test_prob_below_extremes():
    r = run_monte_carlo(RaceConfig(), strat(), n_runs=100, seed=1)
    assert r.prob_below(0.0) == 0.0
    assert r.prob_below(1e9) == 1.0


def test_safety_car_increases_spread():
    calm = run_monte_carlo(RaceConfig(safety_car_prob=0.0), strat(), n_runs=200, seed=1)
    chaotic = run_monte_carlo(RaceConfig(safety_car_prob=0.8), strat(), n_runs=200, seed=1)
    assert chaotic.std_s > calm.std_s


def test_invalid_runs_rejected():
    with pytest.raises(ValueError):
        run_monte_carlo(RaceConfig(), strat(), n_runs=0)


def test_compare_returns_row_per_strategy():
    other = Strategy("M-H", (Stint(Compound.MEDIUM, 25), Stint(Compound.HARD, 32)))
    df = compare_strategies(RaceConfig(), [strat(), other], threshold_s=5300, n_runs=20)
    assert len(df) == 2
    assert list(df["Strategy"]) == ["S-M", "M-H"]

