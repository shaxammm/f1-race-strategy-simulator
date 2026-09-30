from src.models import Compound, RaceConfig, Stint, Strategy
from src.simulation import simulate_strategy

cfg = RaceConfig()
strategies = [
    Strategy("Soft-Medium", (Stint(Compound.SOFT, 20), Stint(Compound.MEDIUM, 37))),
    Strategy("Medium-Hard", (Stint(Compound.MEDIUM, 25), Stint(Compound.HARD, 32))),
    Strategy(
        "Soft-Medium-Soft",
        (Stint(Compound.SOFT, 15), Stint(Compound.MEDIUM, 27), Stint(Compound.SOFT, 15)),
    ),
]

for s in strategies:
    r = simulate_strategy(cfg, s, noise_std_s=0.0)
    print(f"{s.name:18} total={r.total_time_s:8.1f} s  pits={r.pit_stops}  avg={r.average_lap_time_s:.2f} s")
