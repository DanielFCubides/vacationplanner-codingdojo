# Vacation Stay Scrapper API

A REST API for vacation planning with flight search and accommodation services.

## 🚀 Current Status

### ✅ Implemented (Phase 0)
- Health check endpoint
- Basic flight search via external service
- OpenAPI documentation with Swagger UI

### 🔄 In Development (Phase 1-5)
- Complete vacation plan management
- Accommodation search with real/fake data
- User authentication
- Advanced filtering and recommendations

## 📖 API Documentation

### View Interactive Documentation

1. **Start the service**:
   ```bash
   cd vacation_stay_scrapper
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access Swagger UI**:
   ```
   http://localhost:8000/docs
   ```

3. **Access ReDoc**:
   ```
   http://localhost:8000/redoc
   ```

4. **Get OpenAPI JSON**:
   ```
   http://localhost:8000/openapi.json
   ```

## 🔧 Current Endpoints

### Health Check
```http
GET /
```
Returns service health status.

### Flight Search
```http
POST /vacation-plan
Content-Type: application/json

{
  "origin": "BOG",
  "destination": "MIA", 
  "arrival_date": "2025-09-15",
  "return_date": "2025-09-22",
  "passengers": 2,
  "checked_baggage": 1,
  "carry_on_baggage": 1
}
```

## 🛠️ Configuration

### Environment Variables
```bash
# Service URLs
FLIGHT_SERVICE_URL=localhost:8001

# Feature flags (planned)
USE_FAKE_FLIGHTS=false
USE_FAKE_STAYS=false

# Storage options (planned)
VACATION_STORAGE=memory
VACATION_FILE_PATH=/data/plans.json
```

## 📋 Planned Endpoints (Phases 1-5)

### Vacation Plan Management
```http
POST   /vacation-plans              # Create vacation plan
GET    /vacation-plans              # List user's plans
GET    /vacation-plans/{plan_id}    # Get specific plan
PUT    /vacation-plans/{plan_id}    # Update plan
DELETE /vacation-plans/{plan_id}    # Delete plan
```

### Accommodation Search
```http
GET /stays/search?location=Miami&check_in_date=2025-09-15&check_out_date=2025-09-22&guests=2&use_fake_data=true
```

## 🧪 Testing with Fake Data

Once implemented, you'll be able to use fake data for development:

```bash
# Enable fake data mode
export USE_FAKE_FLIGHTS=true
export USE_FAKE_STAYS=true

# Test accommodation search
curl "http://localhost:8000/stays/search?location=Miami&check_in_date=2025-09-15&check_out_date=2025-09-22&guests=2&use_fake_data=true"
```

## 🏗️ Architecture

This API follows Clean Architecture principles:

- **Domain Layer**: Business entities and rules
- **Application Layer**: Use cases and orchestration  
- **Infrastructure Layer**: External services and data access
- **Presentation Layer**: REST API controllers

## 📦 Dependencies

```bash
pip install fastapi uvicorn pydantic
```

For development phases:
```bash
pip install faker pytest httpx
```

## 🔗 Related Services

- **Flight Scrapper Service**: `localhost:8001` - Provides flight search data
- **Recommendations Service**: `localhost:3000` - AI-powered recommendations (planned)
- **Knowledge Base**: Prolog rules for vacation planning logic

## 📝 Development Notes

### Phase 1-2: Foundation
- Domain models implemented ✅
- Repository interfaces defined ✅
- Configuration structure ready

### Phase 3-4: Core Features
- Use cases implementation
- API controllers
- Dependency injection setup

### Phase 5: Production Ready
- End-to-end testing
- Docker integration
- Production deployment

## 🤝 Contributing

Follow the iterative development plan:

1. Implement one phase at a time
2. Start with simple functionality
3. Add complexity incrementally
4. Maintain clean architecture boundaries
5. Focus on business value delivery

## 📋 API Standards

- RESTful endpoints
- JSON request/response format
- Standard HTTP status codes
- Comprehensive error handling
- OpenAPI 3.0 specification
- Pydantic models for validation

## 🔍 Monitoring

Health check endpoint provides service status:
```bash
curl http://localhost:8000/
# Response: {"message": "health-check"}
```
