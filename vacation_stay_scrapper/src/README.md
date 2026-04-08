# Clean Architecture Structure

This project follows Clean Architecture principles with clear separation of concerns.

## Directory Structure

```
src/
├── shared/              # Shared components across domains
├── trips/               # Trip Management Domain
└── stays/               # Stay Management Domain
```

## Layers (Inside each domain)

### 1. Domain Layer (`domain/`)
**Purpose:** Core business logic, completely isolated from external concerns

- `entities/` - Domain entities (aggregate roots and entities)
- `value_objects/` - Immutable value objects
- `repositories/` - Repository interfaces (ports)
- `services/` - Domain services for complex business logic

**Rules:**
- No dependencies on other layers
- No framework dependencies
- Pure business logic only
- Uses only standard Python libraries

### 2. Application Layer (`application/`)
**Purpose:** Application-specific business rules and use cases

- `dtos/` - Data Transfer Objects for application layer
- `use_cases/` - Application use cases (orchestrates domain logic)

**Rules:**
- Depends only on domain layer
- No dependencies on infrastructure or presentation
- Coordinates domain objects
- Implements application-specific workflows

### 3. Infrastructure Layer (`infrastructure/`)
**Purpose:** External concerns and implementation details

- `persistence/` - Database implementations, repositories
- `external/` - External API clients, third-party integrations

**Rules:**
- Implements domain repository interfaces
- Can depend on domain and application layers
- Contains all external dependencies
- Framework-specific code goes here

### 4. Presentation Layer (`presentation/`)
**Purpose:** User interface concerns (REST API in our case)

- `api/` - FastAPI routes and endpoints
  - `routes.py` - API route definitions
  - `schemas.py` - Pydantic request/response models
  - `dependencies.py` - FastAPI dependencies
- `mappers/` - Convert between API schemas and domain entities

**Rules:**
- Depends on application layer
- Framework-specific (FastAPI) code
- Handles HTTP concerns
- Maps external data to internal DTOs

## Shared Components (`shared/`)

Contains code shared across all domains:

- `infrastructure/` - Shared infrastructure (auth, http, logging)
- `domain/` - Shared domain concepts (exceptions, value objects)
- `presentation/` - Shared API concerns (middleware, exception handlers)

## Dependency Rule

**Dependencies point inward:**
```
Presentation → Application → Domain
Infrastructure → Domain
```

The domain layer has no dependencies.
All dependencies point toward the domain.

## Example: Adding a New Feature

1. **Define domain entity** in `trips/domain/entities/`
2. **Create repository interface** in `trips/domain/repositories/`
3. **Implement use case** in `trips/application/use_cases/`
4. **Implement repository** in `trips/infrastructure/persistence/`
5. **Create API endpoint** in `trips/presentation/api/routes.py`
6. **Add request/response schemas** in `trips/presentation/api/schemas.py`

## Benefits

✅ **Testability** - Easy to test each layer independently
✅ **Maintainability** - Changes are localized
✅ **Flexibility** - Easy to swap implementations
✅ **Scalability** - Easy to add new features
✅ **Domain Focus** - Business logic is isolated and protected
