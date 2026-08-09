from datetime import date, time, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import DWHBase


# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------


class DimDate(DWHBase):
    __tablename__ = "dim_date"

    date_key: Mapped[int] = mapped_column(Integer, primary_key=True)

    date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)

    day: Mapped[int] = mapped_column(Integer, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)

    week: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    quarter: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    is_weekend: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    is_holiday: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )


class DimTime(DWHBase):
    __tablename__ = "dim_time"

    time_key: Mapped[int] = mapped_column(Integer, primary_key=True)

    time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
        unique=True,
    )

    hour: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    minute: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    time_bucket: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    period_of_day: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )


class DimParkingLot(DWHBase):
    __tablename__ = "dim_parking_lot"

    lot_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    lot_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    location: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    parking_type: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    floors: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "lot_id",
            name="uq_dwh_lot_id",
        ),
    )


class DimParkingSlot(DWHBase):
    __tablename__ = "dim_parking_slot"

    slot_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    slot_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    lot_key: Mapped[int] = mapped_column(
        ForeignKey("dim_parking_lot.lot_key"),
        nullable=False,
    )

    slot_number: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    floor: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    zone: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    slot_type: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    is_covered: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    near_entrance: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "slot_id",
            name="uq_dwh_slot_id",
        ),
    )


class DimUser(DWHBase):
    __tablename__ = "dim_user"

    user_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    user_type: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            name="uq_dwh_user_id",
        ),
    )


class DimVehicle(DWHBase):
    __tablename__ = "dim_vehicle"

    vehicle_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    vehicle_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    vehicle_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "vehicle_id",
            name="uq_dwh_vehicle_id",
        ),
    )


# ---------------------------------------------------------------------------
# Fact tables
# ---------------------------------------------------------------------------


class FactOccupancy(DWHBase):
    __tablename__ = "fact_occupancy"

    occupancy_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    date_key: Mapped[int] = mapped_column(
        ForeignKey("dim_date.date_key"),
        nullable=False,
    )

    time_key: Mapped[int] = mapped_column(
        ForeignKey("dim_time.time_key"),
        nullable=False,
    )

    lot_key: Mapped[int] = mapped_column(
        ForeignKey("dim_parking_lot.lot_key"),
        nullable=False,
    )

    total_slots: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    occupied_slots: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    available_slots: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reserved_slots: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    occupancy_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class FactSlotOccupancy(DWHBase):
    __tablename__ = "fact_slot_occupancy"

    slot_occupancy_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    date_key: Mapped[int] = mapped_column(
        ForeignKey("dim_date.date_key"),
        nullable=False,
    )

    time_key: Mapped[int] = mapped_column(
        ForeignKey("dim_time.time_key"),
        nullable=False,
    )

    lot_key: Mapped[int] = mapped_column(
        ForeignKey("dim_parking_lot.lot_key"),
        nullable=False,
    )

    slot_key: Mapped[int] = mapped_column(
        ForeignKey("dim_parking_slot.slot_key"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class FactReservation(DWHBase):
    __tablename__ = "fact_reservation"

    reservation_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    date_key: Mapped[int] = mapped_column(
        ForeignKey("dim_date.date_key"),
        nullable=False,
    )

    start_time_key: Mapped[int] = mapped_column(
        ForeignKey("dim_time.time_key"),
        nullable=False,
    )

    end_time_key: Mapped[int] = mapped_column(
        ForeignKey("dim_time.time_key"),
        nullable=False,
    )

    user_key: Mapped[int] = mapped_column(
        ForeignKey("dim_user.user_key"),
        nullable=False,
    )

    vehicle_key: Mapped[int] = mapped_column(
        ForeignKey("dim_vehicle.vehicle_key"),
        nullable=False,
    )

    lot_key: Mapped[int] = mapped_column(
        ForeignKey("dim_parking_lot.lot_key"),
        nullable=False,
    )

    slot_key: Mapped[int] = mapped_column(
        ForeignKey("dim_parking_slot.slot_key"),
        nullable=False,
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    actual_arrival: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    actual_departure: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
