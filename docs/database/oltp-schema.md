# OLTP Schema

The OLTP database stores the operational state of the Smart Parking Reservation System.

It is designed around normalized transactional entities and maintains referential integrity through PostgreSQL foreign keys and constraints.

## Tables

```text
users
  │
  ├── vehicles
  │      │
  │      └── reservations
  │             │
parking_lots ─ parking_slots
                  │
                  ├── reservations
                  │
                  └── slot_events
```

## `users`

Stores registered users.

| Column       | Description                |
| ------------ | -------------------------- |
| `id`         | Unique user identifier     |
| `name`       | User name                  |
| `email`      | User email address         |
| `created_at` | Account creation timestamp |

The email field is indexed to support efficient user lookup.

## `vehicles`

Stores vehicles associated with users.

| Column                | Description                 |
| --------------------- | --------------------------- |
| `id`                  | Unique vehicle identifier   |
| `user_id`             | Owner of the vehicle        |
| `registration_number` | Vehicle registration number |
| `vehicle_type`        | Type/category of vehicle    |

A vehicle belongs to one user.

## `parking_lots`

Stores parking facility information.

| Column           | Description                            |
| ---------------- | -------------------------------------- |
| `id`             | Unique parking lot identifier          |
| `name`           | Parking lot name                       |
| `location`       | Human-readable location                |
| `total_capacity` | Total number of slots                  |
| `latitude`       | Geographic latitude                    |
| `longitude`      | Geographic longitude                   |
| `is_active`      | Whether the parking lot is operational |

A parking lot contains multiple parking slots.

## `parking_slots`

Represents individual parking spaces.

| Column        | Description                          |
| ------------- | ------------------------------------ |
| `id`          | Unique slot identifier               |
| `lot_id`      | Parent parking lot                   |
| `slot_number` | Human-readable slot identifier       |
| `status`      | Current slot status                  |
| `floor`       | Floor number                         |
| `zone`        | Parking zone                         |
| `is_active`   | Whether the slot is currently usable |

A unique constraint is enforced on:

```text
(lot_id, slot_number)
```

This prevents two slots within the same parking lot from having the same slot number.

## `reservations`

Stores parking reservations.

| Column       | Description                    |
| ------------ | ------------------------------ |
| `id`         | Unique reservation identifier  |
| `user_id`    | User making the reservation    |
| `vehicle_id` | Vehicle being parked           |
| `slot_id`    | Reserved parking slot          |
| `start_time` | Reservation start              |
| `end_time`   | Reservation end                |
| `status`     | Current reservation status     |
| `created_at` | Reservation creation timestamp |

Indexes are maintained on frequently queried fields such as user, vehicle, slot, status, start time, and end time.

## `slot_events`

Stores events associated with parking slots.

| Column           | Description                          |
| ---------------- | ------------------------------------ |
| `id`             | Unique event identifier              |
| `slot_id`        | Associated parking slot              |
| `event_type`     | Type of slot event                   |
| `timestamp`      | Event timestamp                      |
| `reservation_id` | Related reservation, when applicable |

This table is particularly important for the future data pipeline because it provides historical information about changes in parking-slot state.

## Relationships

```text
User
 │
 └──< Vehicle
       │
       └──< Reservation >── ParkingSlot >── ParkingLot
                              │
                              └──< SlotEvent
```

The database uses foreign-key constraints to maintain referential integrity.

## Indexing

Indexes are currently used on fields that are expected to be frequently queried:

- User email
- Vehicle registration number
- Vehicle user ID
- Parking slot lot ID
- Parking slot status
- Reservation user ID
- Reservation vehicle ID
- Reservation slot ID
- Reservation status
- Reservation start time
- Reservation end time
- Slot event slot ID
- Slot event event type
- Slot event timestamp
- Slot event reservation ID

## Role in the ML Pipeline

The OLTP database is not intended to be used directly as the primary ML training store.

Instead, operational information will be extracted from the OLTP database and transformed into historical analytical records in the DWH.

```text
OLTP
 │
 ├── reservations
 ├── slot_events
 ├── parking_slots
 └── parking_lots
       │
       ▼
   Data Pipeline
       │
       ▼
      DWH
       │
       ▼
  ML Training Data
```
