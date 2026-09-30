"""Core data structures for the F1 Race Strategy Simulator.

Educational simplified model; not an official Formula 1 model.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Compound(str, Enum):
    """Available tyre compounds."""
    SOFT = "Soft"
    MEDIUM = "Medium"
    HARD = "Hard"


@dataclass(frozen=True)
class RaceConfig:
    """Static race parameters."""
    n_laps: int = 57
    base_lap_time_s: float = 90.0
    pit_loss_s: float = 22.0
    initial_fuel_kg: float = 100.0
    fuel_effect_s_per_kg: float = 0.03
    track_temp_c: float = 30.0
    safety_car_prob: float = 0.0

    def __post_init__(self) -> None:
        if self.n_laps <= 0:
            raise ValueError("n_laps must be positive")
        if self.base_lap_time_s <= 0:
            raise ValueError("base_lap_time_s must be positive")
        if self.pit_loss_s < 0:
            raise ValueError("pit_loss_s cannot be negative")
        if not 0.0 <= self.safety_car_prob <= 1.0:
            raise ValueError("safety_car_prob must be in [0, 1]")

    @property
    def fuel_burn_kg_per_lap(self) -> float:
        """Fuel burns linearly to ~0 at the flag."""
        return self.initial_fuel_kg / self.n_laps


@dataclass(frozen=True)
class Stint:
    """A continuous run on one set of tyres."""
    compound: Compound
    laps: int

    def __post_init__(self) -> None:
        if self.laps <= 0:
            raise ValueError("Stint must have at least one lap")


@dataclass(frozen=True)
class Strategy:
    """An ordered sequence of stints."""
    name: str
    stints: tuple[Stint, ...]

    def __post_init__(self) -> None:
        if not self.stints:
            raise ValueError("Strategy needs at least one stint")

    @property
    def total_laps(self) -> int:
        return sum(s.laps for s in self.stints)

    @property
    def pit_stops(self) -> int:
        return len(self.stints) - 1

    @property
    def pit_laps(self) -> list[int]:
        """Lap numbers (1-based) at the end of which a pit stop occurs."""
        laps, total = [], 0
        for stint in self.stints[:-1]:
            total += stint.laps
            laps.append(total)
        return laps

    def validate_against(self, config: RaceConfig) -> None:
        if self.total_laps != config.n_laps:
            raise ValueError(
                f"Strategy '{self.name}' covers {self.total_laps} laps, "
                f"race has {config.n_laps}"
            )
