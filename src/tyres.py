"""Simplified tyre degradation model (educational, not an official F1 model)."""
from __future__ import annotations

from .models import Compound

# Lap-time offset of a fresh tyre vs Medium (seconds). Negative = faster.
COMPOUND_OFFSET_S = {
    Compound.SOFT: -0.6,
    Compound.MEDIUM: 0.0,
    Compound.HARD: 0.5,
}

# Degradation rate (seconds per lap^DEGRADATION_EXPONENT).
DEGRADATION_RATE = {
    Compound.SOFT: 0.08,
    Compound.MEDIUM: 0.05,
    Compound.HARD: 0.03,
}

DEGRADATION_EXPONENT = 1.3
REFERENCE_TEMP_C = 30.0
TEMP_SENSITIVITY_PER_10C = 0.1


def temperature_factor(track_temp_c: float) -> float:
    """Wear multiplier: hotter track wears tyres faster (never below 0)."""
    factor = 1.0 + TEMP_SENSITIVITY_PER_10C * (track_temp_c - REFERENCE_TEMP_C) / 10.0
    return max(factor, 0.0)


def tyre_penalty_s(compound: Compound, age_laps: int, track_temp_c: float = 30.0) -> float:
    """Lap-time penalty from compound and tyre wear.

    age_laps = number of laps already done on this set (0 = fresh).
    """
    if age_laps < 0:
        raise ValueError("age_laps cannot be negative")
    wear = (
        DEGRADATION_RATE[compound]
        * age_laps ** DEGRADATION_EXPONENT
        * temperature_factor(track_temp_c)
    )
    return COMPOUND_OFFSET_S[compound] + wear
