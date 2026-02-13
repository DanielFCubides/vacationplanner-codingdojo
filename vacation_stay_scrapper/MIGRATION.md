# Migration Guide - Clean Architecture Refactoring

## Overview
This document tracks the migration from the old structure to clean architecture.

## Current Status: ✅ Step 1 Complete

### Completed
- ✅ Created src/ directory structure
- ✅ Created shared/ infrastructure
- ✅ Created trips/ domain structure
- ✅ Created stays/ domain structure
- ✅ Created tests/ structure
- ✅ Added __init__.py files to all packages
- ✅ Created architecture documentation

## Migration Progress

### Phase 1: Foundation
- [x] **Step 1**: Create directory structure (COMPLETE)
- [ ] **Step 2**: Move shared infrastructure
- [ ] **Step 3**: Create domain entities

### Phase 2: Application Layer
- [ ] **Step 4**: Create DTOs and schemas
- [ ] **Step 5**: Create use cases
- [ ] **Step 6**: Migrate flight scrapper

### Phase 3: Presentation & Integration
- [ ] **Step 7**: Create API routes
- [ ] **Step 8**: Create new main entry point
- [ ] **Step 9**: Update tests

### Phase 4: Cleanup
- [ ] **Step 10**: Clean up old files

## Next Steps

### Step 2: Move Shared Infrastructure
1. Extract authentication from main.py
2. Move HTTP connector
3. Move circuit breaker
4. Move logger
5. Move exception handler

### Files to Migrate (Step 2)

**From → To**
```
main.py (auth functions) → src/shared/infrastructure/auth/
utils/connector.py → src/shared/infrastructure/http/http_connector.py
utils/circuit_breaker.py → src/shared/infrastructure/http/circuit_breaker.py
utils/logger.py → src/shared/infrastructure/logging/logger.py
utils/exception_handler.py → src/shared/presentation/exception_handlers.py
exceptions.py → src/shared/domain/exceptions.py
```

## Commands Reference

### Verify Structure
