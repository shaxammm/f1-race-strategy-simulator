"""Simplified weather model (educational)."""
from __future__ import annotations

from enum import Enum


class Weather(str, Enum):
    DRY = "Dry"
    LIGHT_RAIN = "Light Rain"
    HEAVY_RAIN = "Heavy Rain"
    CHANGING = "Changing"


# Extra seconds per lap on dry-weather tyres.
WEATHER_PENALTY_S = {
    Weather.DRY: 0.0,
    Weather.LIGHT_RAIN: 4.0,
    Weather.HEAVY_RAIN: 12.0,
}


def weather_penalty_s(weather: Weather, lap: int, n_laps: int) -> float:
    """Lap-time penalty for a given weather and 1-based lap.

    CHANGING: dry for the first third, light rain in the middle third,
    dry again in the last third.
    """
    if weather is Weather.CHANGING:
        third = n_laps / 3
        if third < lap <= 2 * third:
            return WEATHER_PENALTY_S[Weather.LIGHT_RAIN]
        return 0.0
    return WEATHER_PENALTY_S[weather]
