from dataclasses import dataclass

from .config import GeneratorConfig


@dataclass(frozen=True)
class ParkingLot:
    id: int
    name: str
    location: str
    total_capacity: int


@dataclass(frozen=True)
class ParkingSlot:
    id: int
    lot_id: int
    slot_number: str
    floor: int
    zone: str


def generate_parking_lots(
    config: GeneratorConfig,
) -> list[ParkingLot]:
    """Generate parking lot definitions."""

    return [
        ParkingLot(
            id=lot_id,
            name=f"Parking Lot {lot_id}",
            location=f"Campus Zone {lot_id}",
            total_capacity=config.slots_per_lot,
        )
        for lot_id in range(1, config.lot_count + 1)
    ]


def generate_parking_slots(
    config: GeneratorConfig,
) -> list[ParkingSlot]:
    """Generate exactly slots_per_lot slots for every parking lot."""

    slots: list[ParkingSlot] = []
    slot_id = 1

    total_groups = config.floors_per_lot * config.zones_per_floor

    for lot_id in range(1, config.lot_count + 1):
        for slot_index in range(config.slots_per_lot):
            group_index = slot_index % total_groups

            floor = (group_index // config.zones_per_floor) + 1
            zone_index = group_index % config.zones_per_floor
            zone = chr(ord("A") + zone_index)

            position = (slot_index // total_groups) + 1

            slot_number = f"{floor}-{zone}-{position:03d}"

            slots.append(
                ParkingSlot(
                    id=slot_id,
                    lot_id=lot_id,
                    slot_number=slot_number,
                    floor=floor,
                    zone=zone,
                )
            )

            slot_id += 1

    return slots
