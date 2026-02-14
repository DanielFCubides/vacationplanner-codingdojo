# ✅ Application Running - Quick Start Guide

## Current Status: WORKING ✅

The application now has a **single unified `main.py`** at the project root with all endpoints loaded.

---

## 🚀 How to Start the Server

```bash
cd /Users/m4_dfcc/workspace/vacationplanner-codingdojo/vacation_stay_scrapper
source .venv/bin/activate
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

---

## 📋 Available Endpoints

Visit: **http://127.0.0.1:8000/docs**

### Clean Architecture Endpoints (New)

**Trip Management:**
- `POST /api/trips` - Create a new trip
- `GET /api/trips` - List all trips  
- `GET /api/trips/{trip_id}` - Get trip by ID
- `PUT /api/trips/{trip_id}` - Update trip
- `DELETE /api/trips/{trip_id}` - Delete trip

### Legacy Endpoints

- `GET /` - Health check (requires auth)
- `POST /vacation-plan` - Search vacation plans (requires auth)

---

## 🧪 Testing Without Authentication

The new `/api/trips` endpoints **do NOT require authentication** (for now), so you can test them immediately in the Swagger UI.

### Create a Trip
```json
POST /api/trips
{
  "name": "Summer Vacation",
  "destination": "Bali, Indonesia",
  "start_date": "2026-07-01",
  "end_date": "2026-07-15",
  "status": "planning"
}
```

### Get All Trips
```
GET /api/trips
```

### Get Specific Trip
```
GET /api/trips/{trip_id}
```

---

## 📊 What's Loaded

```
✅ Clean architecture routes from src/trips/
✅ Legacy routes (health check, vacation-plan)
✅ Swagger UI documentation
✅ Middleware (CORS, logging, exception handling)
✅ Dependency injection for use cases
✅ In-memory repository (data resets on restart)
```

---

## 🏗️ Architecture

```
main.py (root)
  ├── Imports trips router
  ├── Registers with app.include_router(trips_router)
  └── Loads all endpoints

src/trips/
  ├── presentation/api/routes.py → Defines endpoints
  ├── application/use_cases/ → Business logic
  ├── domain/entities/ → Domain models
  └── infrastructure/persistence/ → In-memory storage
```

---

## ✅ Verification

Run this to see all available routes:
```bash
cd /Users/m4_dfcc/workspace/vacationplanner-codingdojo/vacation_stay_scrapper
source .venv/bin/activate
python -c "from main import app; [print(f'{list(route.methods)[0]:6} {route.path}') for route in app.routes if hasattr(route, 'methods')]"
```

Expected output:
```
GET    /openapi.json
GET    /docs
GET    /docs/oauth2-redirect
GET    /redoc
POST   /api/trips
GET    /api/trips
GET    /api/trips/{trip_id}
PUT    /api/trips/{trip_id}
DELETE /api/trips/{trip_id}
GET    /
POST   /vacation-plan
```

---

## 🎯 Summary

**Problem:** Two separate main.py files, routes not loading
**Solution:** Merged into single main.py at root with `app.include_router(trips_router)`
**Result:** All endpoints available at http://127.0.0.1:8000/docs

✅ **Application is now fully functional!**
