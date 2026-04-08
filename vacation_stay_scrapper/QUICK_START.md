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
