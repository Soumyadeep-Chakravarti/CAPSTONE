from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SlotStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


class ReservationStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class SlotEventType(str, Enum):
    OCCUPIED = "occupied"
    AVAILABLE = "available"
    RESERVED = "reserved"
    RELEASED = "released"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    vehicles: Mapped[list["Vehicle"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="user",
    )


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )

    registration_number: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        index=True,
    )

    vehicle_type: Mapped[str] = mapped_column(String(32))

    user: Mapped["User"] = relationship(
        back_populates="vehicles",
    )

    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="vehicle",
    )


class ParkingLot(Base):
    __tablename__ = "parking_lots"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(255))

    total_capacity: Mapped[int] = mapped_column(Integer)

    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    slots: Mapped[list["ParkingSlot"]] = relationship(
        back_populates="parking_lot",
        cascade="all, delete-orphan",
    )


class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    id: Mapped[int] = mapped_column(primary_key=True)

    lot_id: Mapped[int] = mapped_column(
        ForeignKey("parking_lots.id"),
        index=True,
    )

    slot_number: Mapped[str] = mapped_column(String(32))

    status: Mapped[SlotStatus] = mapped_column(
        SQLEnum(SlotStatus),
        default=SlotStatus.AVAILABLE,
        index=True,
    )

    floor: Mapped[int | None] = mapped_column(Integer)
    zone: Mapped[str | None] = mapped_column(String(32))

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    parking_lot: Mapped["ParkingLot"] = relationship(
        back_populates="slots",
    )

    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="slot",
    )

    events: Mapped[list["SlotEvent"]] = relationship(
        back_populates="slot",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "lot_id",
            "slot_number",
            name="uq_slot_lot_number",
        ),
    )


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )

    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id"),
        index=True,
    )

    slot_id: Mapped[int] = mapped_column(
        ForeignKey("parking_slots.id"),
        index=True,
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime,
        index=True,
    )

    end_time: Mapped[datetime] = mapped_column(
        DateTime,
        index=True,
    )

    status: Mapped[ReservationStatus] = mapped_column(
        SQLEnum(ReservationStatus),
        default=ReservationStatus.PENDING,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(
        back_populates="reservations",
    )

    vehicle: Mapped["Vehicle"] = relationship(
        back_populates="reservations",
    )

    slot: Mapped["ParkingSlot"] = relationship(
        back_populates="reservations",
    )


class SlotEvent(Base):
    __tablename__ = "slot_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    slot_id: Mapped[int] = mapped_column(
        ForeignKey("parking_slots.id"),
        index=True,
    )

    event_type: Mapped[SlotEventType] = mapped_column(
        SQLEnum(SlotEventType),
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    reservation_id: Mapped[int | None] = mapped_column(
        ForeignKey("reservations.id"),
        nullable=True,
        index=True,
    )

    slot: Mapped["ParkingSlot"] = relationship(
        back_populates="events",
    )
