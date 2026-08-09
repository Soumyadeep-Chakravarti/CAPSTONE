from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime, time

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from backend.app.database.dwh.dimensions import (
    DimDate,
    DimParkingLot,
    DimParkingSlot,
    DimTime,
    DimVehicleType,
)
from backend.app.database.dwh.facts import (
    FactOccupancy,
    FactReservation,
)

from ..generator.occupancy import OccupancyEvent
from ..generator.parking import ParkingLot, ParkingSlot
from ..generator.reservations import ReservationEvent

def get_time_of_day(hour: int) -> str:
    if hour < 6:
        return "night"

    if hour < 12:
        return "morning"

    if hour < 17:
        return "afternoon"

    if hour < 21:
        return "evening"

    return "night"


def is_peak_hour(hour: int) -> bool:
    return hour in {8, 9, 17, 18}


def load_dates(
    session: Session,
    timestamps: Iterable[datetime],
) -> dict[date, int]:
    dates = {timestamp.date() for timestamp in timestamps}

    if not dates:
        return {}

    existing = session.execute(
        select(DimDate).where(DimDate.full_date.in_(dates))
    ).scalars()

    result = {
        row.full_date: row.id
        for row in existing
    }

    for current_date in sorted(dates):
        if current_date in result:
            continue

        row = DimDate(
            full_date=current_date,
            day=current_date.day,
            day_of_week=current_date.weekday(),
            day_name=current_date.strftime("%A"),
            week=current_date.isocalendar().week,
            month=current_date.month,
            month_name=current_date.strftime("%B"),
            quarter=(current_date.month - 1) // 3 + 1,
            year=current_date.year,
            is_weekend=current_date.weekday() >= 5,
            is_holiday=False,
        )

        session.add(row)
        session.flush()

        result[current_date] = row.id

    return result


def load_times(
    session: Session,
    timestamps: Iterable[datetime],
) -> dict[time, int]:
    times = {
        timestamp.time().replace(
            second=0,
            microsecond=0,
        )
        for timestamp in timestamps
    }

    if not times:
        return {}

    existing = session.execute(
        select(DimTime).where(DimTime.full_time.in_(times))
    ).scalars()

    result = {
        row.full_time: row.id
        for row in existing
    }

    for current_time in sorted(times):
        if current_time in result:
            continue

        row = DimTime(
            full_time=current_time,
            hour=current_time.hour,
            minute=current_time.minute,
            time_of_day=get_time_of_day(current_time.hour),
            is_peak=is_peak_hour(current_time.hour),
        )

        session.add(row)
        session.flush()

        result[current_time] = row.id

    return result


def load_parking_lots(
    session: Session,
    lots: list[ParkingLot],
) -> dict[int, int]:
    result: dict[int, int] = {}

    for lot in lots:
        row = session.execute(
            select(DimParkingLot).where(
                DimParkingLot.source_lot_id == lot.id
            )
        ).scalar_one_or_none()

        if row is None:
            row = DimParkingLot(
                source_lot_id=lot.id,
                name=lot.name,
                location=lot.location,
                total_capacity=lot.total_capacity,
                latitude=None,
                longitude=None,
                is_active=True,
            )

            session.add(row)
            session.flush()

        result[lot.id] = row.id

    return result


def load_parking_slots(
    session: Session,
    slots: list[ParkingSlot],
    lot_ids: dict[int, int],
) -> dict[int, int]:
    result: dict[int, int] = {}

    for slot in slots:
        row = session.execute(
            select(DimParkingSlot).where(
                DimParkingSlot.source_slot_id == slot.id
            )
        ).scalar_one_or_none()

        if row is None:
            row = DimParkingSlot(
                source_slot_id=slot.id,
                parking_lot_id=lot_ids[slot.lot_id],
                slot_number=slot.slot_number,
                floor=slot.floor,
                zone=slot.zone,
                is_active=True,
            )

            session.add(row)
            session.flush()

        result[slot.id] = row.id

    return result

def load_vehicle_types(
    session: Session,
    reservations: Iterable[ReservationEvent],
) -> dict[str, int]:
    """Load vehicle types and return vehicle_type -> DWH id mapping."""

    vehicle_types = {
        reservation.vehicle_type
        for reservation in reservations
    }

    if not vehicle_types:
        return {}

    existing = session.execute(
        select(DimVehicleType).where(
            DimVehicleType.vehicle_type.in_(vehicle_types)
        )
    ).scalars()

    result = {
        row.vehicle_type: row.id
        for row in existing
    }

    for vehicle_type in sorted(vehicle_types):
        if vehicle_type in result:
            continue

        row = DimVehicleType(
            vehicle_type=vehicle_type,
        )

        session.add(row)
        session.flush()

        result[vehicle_type] = row.id

    return result

def load_occupancy(
    session: Session,
    events: Iterable[OccupancyEvent],
    date_ids: dict[date, int],
    time_ids: dict[time, int],
    lot_ids: dict[int, int],
    slot_ids: dict[int, int],
    slot_lot_ids: dict[int, int],
    batch_size: int = 10_000,
) -> int:
    """Load occupancy events into the DWH in batches."""

    batch: list[dict[str, object]] = []
    inserted = 0

    for event in events:
        observed_at = event.timestamp

        event_time = observed_at.time().replace(
            second=0,
            microsecond=0,
        )

        batch.append(
            {
                "date_id": date_ids[observed_at.date()],
                "time_id": time_ids[event_time],
                "parking_lot_id": lot_ids[
                    slot_lot_ids[event.slot_id]
                ],
                "parking_slot_id": slot_ids[event.slot_id],
                "observed_at": observed_at,
                "is_occupied": event.occupied,
                "is_reserved": False,
                "occupancy_confidence": 1.0,
            }
        )

        if len(batch) >= batch_size:
            session.execute(
                insert(FactOccupancy),
                batch,
            )

            inserted += len(batch)
            batch.clear()

    if batch:
        session.execute(
            insert(FactOccupancy),
            batch,
        )

        inserted += len(batch)

    return inserted

def load_reservations(
    session: Session,
    reservations: Iterable[ReservationEvent],
    date_ids: dict[date, int],
    time_ids: dict[time, int],
    lot_ids: dict[int, int],
    slot_ids: dict[int, int],
    slot_lot_ids: dict[int, int],
    vehicle_type_ids: dict[str, int],
    batch_size: int = 10_000,
) -> int:
    """Load reservation events into the DWH in batches."""

    batch: list[dict[str, object]] = []
    inserted = 0

    for reservation in reservations:
        start_time = reservation.start_time

        event_time = start_time.time().replace(
            second=0,
            microsecond=0,
        )

        duration_minutes = int(
            (reservation.end_time - start_time).total_seconds() // 60
        )

        batch.append(
            {
                "source_reservation_id": reservation.id,
                "date_id": date_ids[start_time.date()],
                "time_id": time_ids[event_time],
                "parking_lot_id": lot_ids[
                    slot_lot_ids[reservation.slot_id]
                ],
                "parking_slot_id": slot_ids[
                    reservation.slot_id
                ],
                "vehicle_type_id": vehicle_type_ids[
                    reservation.vehicle_type
                ],
                "start_time": reservation.start_time,
                "end_time": reservation.end_time,
                "duration_minutes": duration_minutes,
                "status": reservation.status,
            }
        )

        if len(batch) >= batch_size:
            session.execute(
                insert(FactReservation),
                batch,
            )

            inserted += len(batch)
            batch.clear()

    if batch:
        session.execute(
            insert(FactReservation),
            batch,
        )

        inserted += len(batch)

    return inserted
