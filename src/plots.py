"""Matplotlib charts for the race strategy simulator (educational)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from .analysis import MonteCarloResult
from .models import Compound
from .simulation import RaceResult
from .tyres import tyre_penalty_s


def plot_lap_times(
    results: dict[str, RaceResult],
    pit_laps: dict[str, list[int]] | None = None,
):
    """Lap time vs lap number, one line per strategy, pit stops marked."""
    fig, ax = plt.subplots(figsize=(10, 5))
    for name, result in results.items():
        laps = np.arange(1, len(result.lap_times_s) + 1)
        line, = ax.plot(laps, result.lap_times_s, label=name)
        if pit_laps and name in pit_laps:
            for pit_lap in pit_laps[name]:
                ax.axvline(pit_lap, color=line.get_color(), linestyle=":", alpha=0.5)
    ax.set_xlabel("Lap")
    ax.set_ylabel("Lap time (s)")
    ax.set_title("Lap time vs lap number (dotted lines = pit stops)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def plot_tyre_degradation(max_age: int = 40, track_temp_c: float = 30.0):
    """Tyre penalty vs tyre age for each compound."""
    ages = np.arange(0, max_age + 1)
    fig, ax = plt.subplots(figsize=(8, 5))
    for compound in Compound:
        penalty = [tyre_penalty_s(compound, int(a), track_temp_c) for a in ages]
        ax.plot(ages, penalty, label=compound.value)
    ax.set_xlabel("Tyre age (laps)")
    ax.set_ylabel("Lap-time penalty vs fresh Medium (s)")
    ax.set_title(f"Tyre degradation model (track {track_temp_c:.0f} C)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def plot_race_time_distribution(results: list[MonteCarloResult]):
    """Overlaid histograms of Monte Carlo race times."""
    fig, ax = plt.subplots(figsize=(10, 5))
    for r in results:
        ax.hist(r.race_times_s, bins=40, alpha=0.5, label=r.strategy_name)
        ax.axvline(r.mean_s, linestyle="--", linewidth=1)
    ax.set_xlabel("Total race time (s)")
    ax.set_ylabel("Number of simulations")
    ax.set_title("Race-time distribution (dashed lines = mean)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig
