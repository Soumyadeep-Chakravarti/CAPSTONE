from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import DWHBase

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dimensions import (
        DimDate,
        DimTime,
        DimParkingLot,
        DimParkingSlot,
        DimVehicleType,
    )

class FactOccupancy(DWHBase):
    """
    Atomic occupancy fact.

    Grain:
        One parking slot observed at one point in time.
    """

    __tablename__ = "fact_occupancy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    date_id: Mapped[int] = mapped_column(
        ForeignKey("dim_date.id"),
        nullable=False,
        index=True,
    )

    time_id: Mapped[int] = mapped_column(
        ForeignKey("dim_time.id"),
        nullable=False,
        index=True,
    )

    parking_lot_id: Mapped[int] = mapped_column(
        ForeignKey("dim_parking_lot.id"),
        nullable=False,
        index=True,
    )

    parking_slot_id: Mapped[int] = mapped_column(
        ForeignKey("dim_parking_slot.id"),
        nullable=False,
        index=True,
    )

    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    is_occupied: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    is_reserved: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    occupancy_confidence: Mapped[float | None] = mapped_column(Float)

    date: Mapped["DimDate"] = relationship(
        back_populates="occupancy_records"
    )

    time: Mapped["DimTime"] = relationship(
        back_populates="occupancy_records"
    )

    parking_lot: Mapped["DimParkingLot"] = relationship(
        back_populates="occupancy_records"
    )

    parking_slot: Mapped["DimParkingSlot"] = relationship(
        back_populates="occupancy_records"
    )

    __table_args__ = (
        UniqueConstraint(
            "parking_slot_id",
            "observed_at",
            name="uq_occupancy_slot_timestamp",
        ),
    )


class FactReservation(DWHBase):
    """
    Historical reservation fact.

    Grain:
        One reservation.
    """

    __tablename__ = "fact_reservation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    source_reservation_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True,
    )

    date_id: Mapped[int] = mapped_column(
        ForeignKey("dim_date.id"),
        nullable=False,
        index=True,
    )

    time_id: Mapped[int] = mapped_column(
        ForeignKey("dim_time.id"),
        nullable=False,
        index=True,
    )

    parking_lot_id: Mapped[int] = mapped_column(
        ForeignKey("dim_parking_lot.id"),
        nullable=False,
        index=True,
    )

    parking_slot_id: Mapped[int] = mapped_column(
        ForeignKey("dim_parking_slot.id"),
        nullable=False,
        index=True,
    )

    vehicle_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("dim_vehicle_type.id"),
        index=True,
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    date: Mapped["DimDate"] = relationship(
        back_populates="reservations"
    )

    time: Mapped["DimTime"] = relationship(
        back_populates="reservations"
    )

    parking_lot: Mapped["DimParkingLot"] = relationship(
        back_populates="reservations"
    )

    parking_slot: Mapped["DimParkingSlot"] = relationship(
        back_populates="reservations"
    )

    vehicle_type: Mapped["DimVehicleType | None"] = relationship(
        back_populates="reservations"
    )
