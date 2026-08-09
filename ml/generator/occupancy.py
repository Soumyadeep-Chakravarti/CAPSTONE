from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np

from .parking import ParkingSlot


@dataclass(frozen=True)
class OccupancyEvent:
    timestamp: datetime
    slot_id: int
    occupied: bool


def occupancy_probability(
    timestamp: datetime,
    slot: ParkingSlot,
) -> float:
    """
    Estimate the probability that a parking slot is occupied
    at a given timestamp.
    """

    hour = timestamp.hour + timestamp.minute / 60.0
    weekday = timestamp.weekday()

    # Base occupancy pattern throughout the day.
    if hour < 7:
        probability = 0.05
    elif hour < 9:
        probability = 0.15 + (hour - 7) * 0.30
    elif hour < 12:
        probability = 0.75
    elif hour < 14:
        probability = 0.65
    elif hour < 17:
        probability = 0.55
    elif hour < 19:
        probability = 0.85
    elif hour < 21:
        probability = 0.60
    else:
        probability = 0.20

    # Weekends are generally less occupied.
    if weekday >= 5:
        probability *= 0.55

    # Different zones have slightly different usage patterns.
    zone_factor = {
        "A": 1.05,
        "B": 1.00,
        "C": 0.95,
        "D": 0.90,
    }.get(slot.zone, 1.0)

    probability *= zone_factor

    return float(np.clip(probability, 0.0, 1.0))


def generate_occupancy_events(
    slots: list[ParkingSlot],
    start: datetime,
    end: datetime,
    interval_minutes: int,
    seed: int,
) -> list[OccupancyEvent]:
    """
    Generate stateful synthetic parking occupancy observations.

    Each slot maintains its occupancy state between observations.
    This produces more realistic parking behavior than independently
    sampling every observation.
    """

    if interval_minutes <= 0:
        raise ValueError(
            "interval_minutes must be greater than 0"
        )

    if end < start:
        raise ValueError(
            "end must be greater than or equal to start"
        )

    rng = np.random.default_rng(seed)

    events: list[OccupancyEvent] = []

    # Current state of every parking slot.
    occupied_state: dict[int, bool] = {
        slot.id: False
        for slot in slots
    }

    timestamp = start

    while timestamp <= end:
        for slot in slots:
            probability = occupancy_probability(
                timestamp,
                slot,
            )

            current_state = occupied_state[slot.id]

            if current_state:
                # Occupied slots usually remain occupied.
                #
                # Higher occupancy probability means a lower
                # chance of the vehicle leaving.
                leave_probability = 0.05 + (
                    1.0 - probability
                ) * 0.15

                if rng.random() < leave_probability:
                    current_state = False

            else:
                # Free slots can become occupied.
                #
                # The probability is based on the expected
                # occupancy level for the current time.
                arrival_probability = probability * 0.25

                if rng.random() < arrival_probability:
                    current_state = True

            occupied_state[slot.id] = current_state

            events.append(
                OccupancyEvent(
                    timestamp=timestamp,
                    slot_id=slot.id,
                    occupied=current_state,
                )
            )

        timestamp += timedelta(
            minutes=interval_minutes
        )

    return events
