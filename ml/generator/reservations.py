from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np

from .config import GeneratorConfig
from .parking import ParkingSlot


@dataclass(frozen=True)
class ReservationEvent:
    id: int
    slot_id: int
    start_time: datetime
    end_time: datetime
    vehicle_type: str
    status: str


VEHICLE_TYPES = (
    "car",
    "motorcycle",
    "suv",
    "electric",
)


def generate_reservations(
    slots: list[ParkingSlot],
    config: GeneratorConfig,
) -> list[ReservationEvent]:
    """Generate synthetic parking reservations."""

    rng = np.random.default_rng(config.random_seed)

    reservations: list[ReservationEvent] = []

    reservation_id = 1
    timestamp = config.start_date

    while timestamp < config.end_date:
        # Number of reservations generated at this time.
        reservation_count = int(
            rng.integers(
                low=max(1, len(slots) // 500),
                high=max(2, len(slots) // 100),
            )
        )

        selected_slots = rng.choice(
            slots,
            size=min(reservation_count, len(slots)),
            replace=False,
        )

        for slot in selected_slots:
            duration_minutes = int(
                rng.integers(
                    low=30,
                    high=181,
                )
            )

            start_time = timestamp
            end_time = start_time + timedelta(
                minutes=duration_minutes
            )

            if end_time > config.end_date:
                continue

            vehicle_type = str(
                rng.choice(VEHICLE_TYPES)
            )

            status = str(
                rng.choice(
                    ["completed", "confirmed", "cancelled"],
                    p=[0.70, 0.25, 0.05],
                )
            )

            reservations.append(
                ReservationEvent(
                    id=reservation_id,
                    slot_id=slot.id,
                    start_time=start_time,
                    end_time=end_time,
                    vehicle_type=vehicle_type,
                    status=status,
                )
            )

            reservation_id += 1

        timestamp += timedelta(
            minutes=config.occupancy_interval_minutes
        )

    return reservations
