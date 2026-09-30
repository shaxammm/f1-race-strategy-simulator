import pytest

from src.models import Compound, RaceConfig, Stint, Strategy
from src.simulation import simulate_strategy


def make_strategy() -> Strategy:
    return Strategy(
        "Soft-Medium",
        (Stint(Compound.SOFT, 20), Stint(Compound.MEDIUM, 37)),
    )


def test_pit_laps_and_count():
    s = make_strategy()
    assert s.pit_stops == 1
    assert s.pit_laps == [20]


def test_wrong_lap_total_rejected():
    bad = Strategy("Bad", (Stint(Compound.SOFT, 10),))
    with pytest.raises(ValueError):
        simulate_strategy(RaceConfig(), bad)


def test_lap_count_matches_race():
    result = simulate_strategy(RaceConfig(), make_strategy(), noise_std_s=0.0)
    assert len(result.lap_times_s) == 57


def test_pit_loss_adds_exactly_to_total():
    s = make_strategy()
    no_pit_cost = simulate_strategy(RaceConfig(pit_loss_s=0.0), s, noise_std_s=0.0)
    with_pit_cost = simulate_strategy(RaceConfig(pit_loss_s=22.0), s, noise_std_s=0.0)
    assert with_pit_cost.total_time_s - no_pit_cost.total_time_s == pytest.approx(22.0)
    assert with_pit_cost.pit_loss_total_s == pytest.approx(22.0)


def test_pit_lap_is_slower_than_next_lap():
    result = simulate_strategy(RaceConfig(), make_strategy(), noise_std_s=0.0)
    # lap 20 (index 19) contains the pit stop
    assert result.lap_times_s[19] > result.lap_times_s[20] + 10
