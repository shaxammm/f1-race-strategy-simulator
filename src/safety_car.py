"""Simplified Safety Car model (educational)."""
from __future__ import annotations

import numpy as np

SC_LAP_TIME_FACTOR = 1.35   # laps under SC are ~35% slower
SC_PIT_LOSS_FACTOR = 0.5    # pit stop costs about half under SC
SC_DURATION_LAPS = 4


def draw_safety_car_laps(
    n_laps: int,
    probability: float,
    rng: np.random.Generator,
) -> set[int]:
    """Return the set of 1-based laps run under Safety Car.

    With the given probability, one SC period of SC_DURATION_LAPS starts
    on a random lap (not the first lap, and it must fit in the race).
    """
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be in [0, 1]")
    if rng.random() >= probability or n_laps < SC_DURATION_LAPS + 2:
        return set()
    start = int(rng.integers(2, n_laps - SC_DURATION_LAPS + 2))
    return set(range(start, start + SC_DURATION_LAPS))
