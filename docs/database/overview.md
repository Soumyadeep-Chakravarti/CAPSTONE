# Database Architecture

The Smart Parking Reservation System uses a dual-database architecture consisting of an **Online Transaction Processing (OLTP)** database and a **Data Warehouse (DWH)**.

The separation allows the system to handle real-time transactional workloads independently from analytical and machine-learning workloads.

## Architecture

```text
                    Smart Parking System
                            │
             ┌──────────────┴──────────────┐
             │                             │
          OLTP DB                         DWH
             │                             │
       PostgreSQL                    PostgreSQL
             │                             │
     Transactional Data             Analytical Data
             │                             │
     ┌───────┴────────┐          ┌─────────┴─────────┐
     │                │          │                   │
 Reservations     Slot State   Facts             Dimensions
 Users            Vehicles     Occupancy          Date
 Parking Lots     Slot Events  Reservations        Time
                                                     Lot
                                                     Slot
                                                     Vehicle Type
```

## OLTP Database

The OLTP database is responsible for the application's operational data.

It handles:

- User information
- Vehicle registration
- Parking lot configuration
- Individual parking slots
- Reservations
- Real-time slot state
- Slot state events

The OLTP database is optimized for frequent inserts, updates, and transactional consistency.

### Current OLTP tables

```text
users
vehicles
parking_lots
parking_slots
reservations
slot_events
```

PostgreSQL is used as the database engine.

SQLAlchemy is used as the ORM and Alembic is used for schema migrations.

## Data Warehouse

The Data Warehouse is intended for historical analysis and machine-learning workloads.

Unlike the OLTP database, the DWH will retain historical observations rather than only the current operational state.

The DWH will contain:

- Historical parking occupancy
- Historical slot availability
- Reservation history
- Parking lot usage patterns
- Time-based dimensions
- Parking lot dimensions
- Parking slot dimensions
- Vehicle-related dimensions

The warehouse will follow a dimensional modelling approach using **fact and dimension tables**.

## Why Two Databases?

Keeping OLTP and DWH separate prevents analytical workloads from interfering with real-time application operations.

For example, an ML training query may scan millions of historical occupancy records. That workload should not negatively affect a user's attempt to reserve a parking slot.

The separation also provides a clean data pipeline:

```text
OLTP
 │
 │ Historical events
 ▼
ETL / ELT Pipeline
 │
 ▼
DWH
 │
 ├── Analytics
 │
 └── ML Dataset
       │
       ▼
   ML Training
       │
       ▼
   Predictions
       │
       ▼
     Backend
```

## Migration Strategy

Both databases have independent Alembic environments.

```text
backend/
├── alembic.ini
├── alembic_dwh.ini
│
├── migrations/
│   └── versions/
│
└── migrations_dwh/
    └── versions/
```

The OLTP and DWH schemas can therefore evolve independently.

## Development Environment

PostgreSQL instances are managed using Docker Compose.

Python dependencies are managed using `uv`.

The backend and ML environments maintain separate dependency configurations to prevent unnecessary coupling between application and machine-learning dependencies.

## Current Status

### Completed

- PostgreSQL OLTP database
- PostgreSQL DWH database
- SQLAlchemy database models
- Database connections
- Docker Compose configuration
- OLTP Alembic environment
- DWH Alembic environment
- Initial OLTP migration
- Database documentation

### Next

- Finalize DWH dimensional model
- Implement DWH fact tables
- Implement DWH dimension tables
- Build OLTP → DWH data pipeline
- Define ML training dataset
- Generate/collect historical parking occupancy data
