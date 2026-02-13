# Architecture Diagram

## High-Level Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
│                         (main.py)                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
┌───────────────▼──────────────┐   ┌───────────▼──────────────┐
│      Trips Domain             │   │      Stays Domain         │
│                               │   │                           │
│  ┌─────────────────────────┐ │   │  ┌─────────────────────┐ │
│  │   Presentation Layer    │ │   │  │  Presentation Layer │ │
│  │   - API Routes          │ │   │  │  - API Routes       │ │
│  │   - Request/Response    │ │   │  │  - Request/Response │ │
│  │   - Mappers             │ │   │  │  - Mappers          │ │
│  └──────────┬──────────────┘ │   │  └──────────┬──────────┘ │
│             │                 │   │             │            │
│  ┌──────────▼──────────────┐ │   │  ┌──────────▼──────────┐ │
│  │   Application Layer     │ │   │  │  Application Layer  │ │
│  │   - Use Cases           │ │   │  │  - Use Cases        │ │
│  │   - DTOs                │ │   │  │  - DTOs             │ │
│  └──────────┬──────────────┘ │   │  └──────────┬──────────┘ │
│             │                 │   │             │            │
│  ┌──────────▼──────────────┐ │   │  ┌──────────▼──────────┐ │
│  │   Domain Layer          │ │   │  │  Domain Layer       │ │
│  │   - Entities            │ │   │  │  - Entities         │ │
│  │   - Value Objects       │ │   │  │  - Value Objects    │ │
│  │   - Repository Ports    │ │   │  │  - Repository Ports │ │
│  │   - Domain Services     │ │   │  │  - Domain Services  │ │
│  └──────────▲──────────────┘ │   │  └──────────▲──────────┘ │
│             │                 │   │             │            │
│  ┌──────────┴──────────────┐ │   │  ┌──────────┴──────────┐ │
│  │  Infrastructure Layer   │ │   │  │ Infrastructure Layer│ │
│  │  - Repositories         │ │   │  │ - Repositories      │ │
│  │  - External APIs        │ │   │  │ - External APIs     │ │
│  │  - DB Implementations   │ │   │  │ - DB Implementations│ │
│  └─────────────────────────┘ │   │  └─────────────────────┘ │
└──────────────────────────────┘   └──────────────────────────┘
                │                               │
                └───────────────┬───────────────┘
                                │
                ┌───────────────▼──────────────┐
                │     Shared Components        │
                │                              │
                │  - Auth (JWT, Keycloak)      │
                │  - HTTP Client               │
                │  - Circuit Breaker           │
                │  - Logger                    │
                │  - Exception Handlers        │
                │  - Common Value Objects      │
                └──────────────────────────────┘
```

## Domain Structure (Trips Example)

```
trips/
│
├── presentation/           ┌──────────────────┐
│   ├── api/               │  HTTP Layer      │
│   │   ├── routes.py      │  FastAPI Routes  │
│   │   ├── schemas.py     │  Pydantic Models │
│   │   └── dependencies   └──────────────────┘
│   └── mappers/                    │
│       └── trip_mapper.py          │
│                                   ▼
├── application/            ┌──────────────────┐
│   ├── dtos/              │  Use Cases       │
│   │   └── *.py           │  Orchestration   │
│   └── use_cases/         └──────────────────┘
│       ├── create_trip.py          │
│       ├── get_trip.py             │
│       └── search_flights.py       ▼
│                           ┌──────────────────┐
├── domain/                │  Business Logic  │
│   ├── entities/          │  Pure Python     │
│   │   ├── trip.py        │  No Dependencies │
│   │   ├── flight.py      └──────────────────┘
│   │   └── traveler.py             ▲
│   ├── value_objects/              │
│   │   ├── trip_id.py              │
│   │   └── airport.py              │
│   ├── repositories/               │
│   │   └── trip_repository.py (interface)
│   └── services/                   │
│       └── flight_searcher.py      │
│                                   │
└── infrastructure/         ┌──────────────────┐
    ├── persistence/        │  External Stuff  │
    │   └── in_memory_*     │  Databases       │
    └── external/           │  APIs            │
        └── flight_api_*    └──────────────────┘
```

## Dependency Flow

```
┌────────────────────────────────────────────┐
│  Dependency Rule: All dependencies point  │
│  inward toward the domain layer            │
└────────────────────────────────────────────┘

     Infrastructure  ────────────┐
                                 │
                                 ▼
     Presentation    ────────────┐
                                 │
                                 ▼
     Application     ────────────┐
                                 │
                                 ▼
     ╔═══════════════════════════╗
     ║         DOMAIN            ║
     ║    (No dependencies)      ║
     ╚═══════════════════════════╝
```

## Request Flow Example

```
1. HTTP Request arrives
   │
   ▼
2. FastAPI Route (presentation/api/routes.py)
   │
   ▼
3. Validate with Pydantic Schema (presentation/api/schemas.py)
   │
   ▼
4. Map to DTO (presentation/mappers/)
   │
   ▼
5. Call Use Case (application/use_cases/)
   │
   ▼
6. Use Case orchestrates Domain Logic
   ├──> Domain Services (domain/services/)
   ├──> Domain Entities (domain/entities/)
   └──> Repository Interface (domain/repositories/)
        │
        ▼
7. Infrastructure implements Repository
   └──> External API Call (infrastructure/external/)
   │
   ▼
8. Domain Entities returned
   │
   ▼
9. Map to Response Schema
   │
   ▼
10. HTTP Response
```
