# Data Warehouse Schema

The Data Warehouse stores historical parking information for analytics and machine-learning workloads.

The DWH will use a **dimensional modelling** approach based on fact and dimension tables.

## Objective

The warehouse should allow the system to answer questions such as:

- How many vehicles were parked in a lot at a given time?
- What percentage of a parking lot was occupied?
- Which parking slots are most frequently occupied?
- What are the peak parking hours?
- How does occupancy vary by day of the week?
- How long are parking slots typically occupied?
- How many slots are expected to be available at a future time?

These historical records will eventually form the training dataset for the parking availability prediction model.

## Proposed Star Schema

```text
                         dim_date
                            │
                            │
dim_time ─────────── fact_occupancy ───────── dim_parking_lot
                            │
                            │
                     dim_parking_slot
                            │
                            │
                    dim_vehicle_type
```

## Dimensions

### `dim_date`

Provides calendar information for historical observations.

Possible attributes include:

- Date key
- Full date
- Day
- Day of week
- Week
- Month
- Quarter
- Year
- Weekend indicator
- Holiday indicator

This allows occupancy to be analyzed by calendar patterns.

### `dim_time`

Represents the time component of an observation.

Possible attributes include:

- Time key
- Hour
- Minute
- Time of day
- Peak/off-peak indicator

The granularity may be configured around the system's observation interval.

For example:

```text
00:00
00:15
00:30
00:45
...
23:45
```

### `dim_parking_lot`

Contains analytical information about a parking facility.

Possible attributes:

- Parking lot key
- Source parking lot ID
- Parking lot name
- Location
- Capacity
- Latitude
- Longitude
- Active status

### `dim_parking_slot`

Contains analytical information about individual slots.

Possible attributes:

- Parking slot key
- Source slot ID
- Parking lot key
- Slot number
- Floor
- Zone
- Active status

### `dim_vehicle_type`

Describes vehicle categories used for analysis.

Possible categories could include:

```text
car
motorcycle
suv
other
```

The exact categories will depend on the final OLTP model and available data.

## Facts

### `fact_occupancy`

This is the primary fact table for the ML pipeline.

Each record represents the observed state of a parking slot or parking facility at a particular point in time.

A slot-level record may contain:

| Field                 | Description                                |
| --------------------- | ------------------------------------------ |
| Date key              | Observation date                           |
| Time key              | Observation time                           |
| Parking lot key       | Associated parking lot                     |
| Parking slot key      | Associated parking slot                    |
| Occupied              | Whether the slot was occupied              |
| Reservation indicator | Whether the slot had an active reservation |

Aggregated measures can additionally provide:

- Total capacity
- Occupied slots
- Available slots
- Occupancy percentage

The exact grain of this fact table will be finalized before implementation.

## `fact_reservation`

Stores historical reservation activity for analytical purposes.

Possible measures and attributes include:

- Reservation date
- Start time
- End time
- Parking lot
- Parking slot
- Vehicle type
- Reservation duration
- Reservation status

## Data Flow

```text
                    OLTP
                     │
                     │
             Slot events
             Reservations
             Slot metadata
                     │
                     ▼
                ETL / ELT
                     │
          ┌──────────┴──────────┐
          │                     │
     Transform             Validate
          │                     │
          └──────────┬──────────┘
                     ▼
                    DWH
                     │
              ┌──────┴──────┐
              │             │
           Analytics        ML
                            │
                            ▼
                     Training Dataset
                            │
                            ▼
                       ML Model
```

## ML Target

The warehouse is being designed around two related prediction problems.

### Lot-level prediction

Given a parking lot and future timestamp:

```text
Input:
    parking_lot = LOT-001
    timestamp = 2026-08-10 14:30

Prediction:
    expected_available_slots = 237
```

### Slot-level prediction

Given a parking slot and future timestamp:

```text
Input:
    parking_lot = LOT-001
    slot = A-237
    timestamp = 2026-08-10 14:30

Prediction:
    probability_available = 0.87
```

The final ML formulation will be determined after sufficient historical data is available.

## Current Status

The DWH database and migration environment are configured.

The dimensional schema is currently being designed and has **not yet been finalized or migrated**.

The next implementation step is to define the final grain and relationships of the fact tables before generating the initial DWH Alembic migration.
