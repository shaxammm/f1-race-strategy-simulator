from src.analysis import compare_strategies
from src.models import Compound, RaceConfig, Stint, Strategy

cfg = RaceConfig(safety_car_prob=0.3)
strategies = [
    Strategy("Soft-Medium", (Stint(Compound.SOFT, 20), Stint(Compound.MEDIUM, 37))),
    Strategy("Medium-Hard", (Stint(Compound.MEDIUM, 25), Stint(Compound.HARD, 32))),
    Strategy(
        "Soft-Medium-Soft",
        (Stint(Compound.SOFT, 15), Stint(Compound.MEDIUM, 27), Stint(Compound.SOFT, 15)),
    ),
]

df = compare_strategies(cfg, strategies, threshold_s=5340, n_runs=1000)
print(df.to_string(index=False))


