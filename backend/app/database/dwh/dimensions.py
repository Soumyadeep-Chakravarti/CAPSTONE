from datetime import date,  time

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import DWHBase

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .facts import FactOccupancy, FactReservation

class DimDate(DWHBase):
    __tablename__ = "dim_date"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    full_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)

    day: Mapped[int] = mapped_column(Integer, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    day_name: Mapped[str] = mapped_column(String(16), nullable=False)

    week: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    month_name: Mapped[str] = mapped_column(String(16), nullable=False)

    quarter: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    is_weekend: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_holiday: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    occupancy_records: Mapped[list["FactOccupancy"]] = relationship(
        back_populates="date"
    )

    reservations: Mapped[list["FactReservation"]] = relationship(
        back_populates="date"
    )


class DimTime(DWHBase):
    __tablename__ = "dim_time"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    full_time: Mapped[time] = mapped_column(Time, nullable=False, unique=True)

    hour: Mapped[int] = mapped_column(Integer, nullable=False)
    minute: Mapped[int] = mapped_column(Integer, nullable=False)

    time_of_day: Mapped[str] = mapped_column(String(16), nullable=False)

    is_peak: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    occupancy_records: Mapped[list["FactOccupancy"]] = relationship(
        back_populates="time"
    )

    reservations: Mapped[list["FactReservation"]] = relationship(
        back_populates="time"
    )


class DimParkingLot(DWHBase):
    __tablename__ = "dim_parking_lot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    source_lot_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)

    total_capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    slots: Mapped[list["DimParkingSlot"]] = relationship(
        back_populates="parking_lot"
    )

    occupancy_records: Mapped[list["FactOccupancy"]] = relationship(
        back_populates="parking_lot"
    )

    reservations: Mapped[list["FactReservation"]] = relationship(
        back_populates="parking_lot"
    )


class DimParkingSlot(DWHBase):
    __tablename__ = "dim_parking_slot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    source_slot_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)

    parking_lot_id: Mapped[int] = mapped_column(
        ForeignKey("dim_parking_lot.id"),
        nullable=False,
        index=True,
    )

    slot_number: Mapped[str] = mapped_column(String(32), nullable=False)

    floor: Mapped[int | None] = mapped_column(Integer)
    zone: Mapped[str | None] = mapped_column(String(32))

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    parking_lot: Mapped["DimParkingLot"] = relationship(
        back_populates="slots"
    )

    occupancy_records: Mapped[list["FactOccupancy"]] = relationship(
        back_populates="parking_slot"
    )

    reservations: Mapped[list["FactReservation"]] = relationship(
        back_populates="parking_slot"
    )

    __table_args__ = (
        UniqueConstraint(
            "parking_lot_id",
            "slot_number",
            name="uq_dwh_slot_lot_number",
        ),
    )


class DimVehicleType(DWHBase):
    __tablename__ = "dim_vehicle_type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    vehicle_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        unique=True,
    )

    reservations: Mapped[list["FactReservation"]] = relationship(
        back_populates="vehicle_type"
    )
