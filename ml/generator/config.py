from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class GeneratorConfig:
    """Configuration for synthetic parking data generation."""

    # Parking topology
    lot_count: int = 1
    slots_per_lot: int = 1000

    floors_per_lot: int = 3
    zones_per_floor: int = 4

    # Historical data range
    start_date: datetime = datetime(2026, 1, 1)
    end_date: datetime = datetime(2026, 3, 31)

    # Occupancy sampling
    occupancy_interval_minutes: int = 5

    # Reproducibility
    random_seed: int = 42
