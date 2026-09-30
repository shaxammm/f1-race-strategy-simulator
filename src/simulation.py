"""Race simulation: fuel, tyres, pit stops, weather, Safety Car, noise."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .models import RaceConfig, Strategy
from .safety_car import SC_LAP_TIME_FACTOR, SC_PIT_LOSS_FACTOR, draw_safety_car_laps
from .tyres import tyre_penalty_s
from .weather import Weather, weather_penalty_s


@dataclass(frozen=True, eq=False)
class RaceResult:
    """Outcome of one simulated race."""
    lap_times_s: np.ndarray
    pit_stops: int = 0
    pit_loss_total_s: float = 0.0
    safety_car_laps: frozenset = field(default_factory=frozenset)

    @property
    def total_time_s(self) -> float:
        return float(self.lap_times_s.sum())

    @property
    def average_lap_time_s(self) -> float:
        return float(self.lap_times_s.mean())


def fuel_mass_kg(config: RaceConfig, lap: int) -> float:
    """Fuel on board at the start of a 1-based lap number."""
    if not 1 <= lap <= config.n_laps:
        raise ValueError(f"lap must be in [1, {config.n_laps}]")
    return config.initial_fuel_kg - config.fuel_burn_kg_per_lap * (lap - 1)


def fuel_penalty_s(config: RaceConfig, lap: int) -> float:
    """Extra lap time caused by fuel weight."""
    return config.fuel_effect_s_per_kg * fuel_mass_kg(config, lap)


def lap_time_s(config: RaceConfig, lap: int, noise_s: float = 0.0) -> float:
    """Base lap time + fuel effect + externally supplied noise."""
    return config.base_lap_time_s + fuel_penalty_s(config, lap) + noise_s


def simulate_race(
    config: RaceConfig,
    noise_std_s: float = 0.2,
    seed: int | None = None,
) -> RaceResult:
    """Simple race without tyres or pit stops (stage 4 version)."""
    if noise_std_s < 0:
        raise ValueError("noise_std_s cannot be negative")

    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, noise_std_s, size=config.n_laps)
    times = np.array(
        [lap_time_s(config, lap, noise[lap - 1])
         for lap in range(1, config.n_laps + 1)]
    )
    return RaceResult(lap_times_s=times)


def simulate_strategy(
    config: RaceConfig,
    strategy: Strategy,
    noise_std_s: float = 0.2,
    seed: int | None = None,
    weather: Weather = Weather.DRY,
) -> RaceResult:
    """Simulate a race following a tyre/pit-stop strategy."""
    if noise_std_s < 0:
        raise ValueError("noise_std_s cannot be negative")
    strategy.validate_against(config)

    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, noise_std_s, size=config.n_laps)
    sc_laps = draw_safety_car_laps(config.n_laps, config.safety_car_prob, rng)

    times: list[float] = []
    pit_loss_total = 0.0
    lap = 0
    last_stint = len(strategy.stints) - 1
    for stint_index, stint in enumerate(strategy.stints):
        for tyre_age in range(stint.laps):  # 0 = fresh tyres
            lap += 1
            lap_time = (
                lap_time_s(config, lap, noise[lap - 1])
                + tyre_penalty_s(stint.compound, tyre_age, config.track_temp_c)
                + weather_penalty_s(weather, lap, config.n_laps)
            )
            if lap in sc_laps:
                lap_time *= SC_LAP_TIME_FACTOR
            times.append(lap_time)
        if stint_index < last_stint:
            loss = config.pit_loss_s
            if lap in sc_laps:
                loss *= SC_PIT_LOSS_FACTOR
            times[-1] += loss
            pit_loss_total += loss

    return RaceResult(
        lap_times_s=np.array(times),
        pit_stops=strategy.pit_stops,
        pit_loss_total_s=pit_loss_total,
        safety_car_laps=frozenset(sc_laps),
    )
