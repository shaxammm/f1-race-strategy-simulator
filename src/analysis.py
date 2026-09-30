"""Monte Carlo analysis of race strategies (educational)."""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

from .models import RaceConfig, Strategy
from .simulation import simulate_strategy
from .weather import Weather


@dataclass(frozen=True, eq=False)
class MonteCarloResult:
    """Statistics over many simulated races for one strategy."""
    strategy_name: str
    pit_stops: int
    race_times_s: np.ndarray

    @property
    def mean_s(self) -> float:
        return float(self.race_times_s.mean())

    @property
    def median_s(self) -> float:
        return float(np.median(self.race_times_s))

    @property
    def std_s(self) -> float:
        return float(self.race_times_s.std(ddof=1)) if len(self.race_times_s) > 1 else 0.0

    @property
    def fastest_s(self) -> float:
        return float(self.race_times_s.min())

    @property
    def slowest_s(self) -> float:
        return float(self.race_times_s.max())

    def prob_below(self, threshold_s: float) -> float:
        """Share of simulations finishing faster than threshold_s (0..1)."""
        return float((self.race_times_s < threshold_s).mean())


def run_monte_carlo(
    config: RaceConfig,
    strategy: Strategy,
    n_runs: int = 1000,
    noise_std_s: float = 0.2,
    temp_std_c: float = 3.0,
    weather: Weather = Weather.DRY,
    seed: int | None = 42,
) -> MonteCarloResult:
    """Run many races with random noise, SC and track temperature."""
    if n_runs <= 0:
        raise ValueError("n_runs must be positive")
    if temp_std_c < 0:
        raise ValueError("temp_std_c cannot be negative")

    master_rng = np.random.default_rng(seed)
    times = np.empty(n_runs)
    for i in range(n_runs):
        temp = config.track_temp_c + master_rng.normal(0.0, temp_std_c)
        run_config = replace(config, track_temp_c=temp)
        run_seed = int(master_rng.integers(0, 2**31 - 1))
        result = simulate_strategy(
            run_config, strategy, noise_std_s=noise_std_s,
            seed=run_seed, weather=weather,
        )
        times[i] = result.total_time_s
    return MonteCarloResult(strategy.name, strategy.pit_stops, times)


def compare_strategies(
    config: RaceConfig,
    strategies: list[Strategy],
    threshold_s: float,
    n_runs: int = 1000,
    weather: Weather = Weather.DRY,
    seed: int | None = 42,
) -> pd.DataFrame:
    """Side-by-side table of Monte Carlo statistics."""
    rows = []
    for s in strategies:
        r = run_monte_carlo(config, s, n_runs=n_runs, weather=weather, seed=seed)
        rows.append({
            "Strategy": r.strategy_name,
            "Pit stops": r.pit_stops,
            "Mean (s)": round(r.mean_s, 1),
            "Median (s)": round(r.median_s, 1),
            "Std (s)": round(r.std_s, 2),
            "Fastest (s)": round(r.fastest_s, 1),
            "Slowest (s)": round(r.slowest_s, 1),
            f"P(< {threshold_s:.0f} s)": f"{r.prob_below(threshold_s) * 100:.1f}%",
        })
    return pd.DataFrame(rows)
