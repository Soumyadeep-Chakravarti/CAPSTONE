from .config import GeneratorConfig
from .occupancy import generate_occupancy_events
from .parking import (
    generate_parking_lots,
    generate_parking_slots,
)


def main() -> None:
    config = GeneratorConfig()

    # Generate parking topology.
    lots = generate_parking_lots(config)
    slots = generate_parking_slots(config)

    print(f"Generated lots: {len(lots)}")
    print(f"Generated slots: {len(slots)}")

    print("\nFirst lot:")
    print(lots[0])

    print("\nFirst five slots:")
    for slot in slots[:5]:
        print(slot)

    # Validate parking topology.
    assert len(lots) == config.lot_count
    assert len(slots) == config.lot_count * config.slots_per_lot

    for lot in lots:
        lot_slots = [
            slot
            for slot in slots
            if slot.lot_id == lot.id
        ]

        assert len(lot_slots) == lot.total_capacity
        assert len({slot.slot_number for slot in lot_slots}) == lot.total_capacity

    # Generate synthetic occupancy observations.
    events = generate_occupancy_events(
        slots=slots,
        start=config.start_date,
        end=config.end_date,
        interval_minutes=config.occupancy_interval_minutes,
        seed=config.random_seed,
    )

    occupied_count = sum(
        event.occupied
        for event in events
    )

    free_count = len(events) - occupied_count

    occupancy_rate = (
        occupied_count / len(events)
        if events
        else 0.0
    )

    print("\nOccupancy:")
    print(f"Generated events: {len(events)}")
    print(f"Occupied observations: {occupied_count}")
    print(f"Free observations: {free_count}")
    print(f"Overall occupancy rate: {occupancy_rate:.2%}")

    print("\nFirst five occupancy events:")
    for event in events[:5]:
        print(event)

    # Validate occupancy generation.
    total_seconds = (
        config.end_date - config.start_date
    ).total_seconds()

    expected_timestamps = (
        int(
            total_seconds
            // (config.occupancy_interval_minutes * 60)
        )
        + 1
    )

    expected_events = expected_timestamps * len(slots)

    assert len(events) == expected_events
    assert all(event.slot_id > 0 for event in events)


if __name__ == "__main__":
    main()
