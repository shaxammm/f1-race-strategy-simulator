import matplotlib

matplotlib.use("Agg")  # save to files, no window

from src.analysis import run_monte_carlo
from src.models import Compound, RaceConfig, Stint, Strategy
from src.plots import (
    plot_lap_times,
    plot_race_time_distribution,
    plot_tyre_degradation,
)
from src.simulation import simulate_strategy

cfg = RaceConfig(safety_car_prob=0.3)
strategies = [
    Strategy("Soft-Medium", (Stint(Compound.SOFT, 20), Stint(Compound.MEDIUM, 37))),
    Strategy("Medium-Hard", (Stint(Compound.MEDIUM, 25), Stint(Compound.HARD, 32))),
    Strategy(
        "Soft-Medium-Soft",
        (Stint(Compound.SOFT, 15), Stint(Compound.MEDIUM, 27), Stint(Compound.SOFT, 15)),
    ),
]

# Lap times without safety car, so the curves are easy to read
clean_cfg = RaceConfig(safety_car_prob=0.0)
single = {s.name: simulate_strategy(clean_cfg, s, noise_std_s=0.0) for s in strategies}
pits = {s.name: s.pit_laps for s in strategies}

plot_lap_times(single, pits).savefig("screenshots/lap_times.png", dpi=150)
plot_tyre_degradation().savefig("screenshots/tyre_degradation.png", dpi=150)

mc = [run_monte_carlo(cfg, s, n_runs=1000) for s in strategies]
plot_race_time_distribution(mc).savefig("screenshots/distribution.png", dpi=150)

print("Saved 3 charts to screenshots/")
