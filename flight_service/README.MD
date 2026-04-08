# Flight Scrapper Service

A flexible flight search service that supports multiple server configurations and provides flight data through various airline scrapers.

## 🛠️ Quick Start

### Using Docker Compose (Recommended)

1. **Set the server type** you want to run:
   ```shell
   export SERVER=rest
   ```
   
   Available options:
   - `rest` - RESTful API server
   - `grpc` - gRPC server  
   - `graphql` - GraphQL server

2. **Start the service** from the parent directory:
   ```shell
   docker compose up flight-scrapper --build
   ```

3. **Verify the service** is running:
   ```shell
   curl http://localhost:8001/
   ```
   
   Expected response:
   ```json
   {
     "status": "alive",
     "timestamp": "Wed, 04 Jun 2025 01:48:17 GMT"
   }
   ```

### Using Docker

Alternatively, you can run the service directly with Docker:

```shell
# Build the container
docker build . -t flight-scraper

# Run the container
docker run -it -p 5000:5000 -e SERVER=rest flight-scraper
```

## 📖 API Documentation

### REST API

The REST API is fully documented using OpenAPI 3.0 specification. You can:

- **View the specification**: Located at `presentations/rest/api.yaml`
- **Interactive documentation**: Copy the content and paste it into [editor.swagger.io](https://editor.swagger.io) for an interactive API explorer
- **Available endpoints**:
  - `GET /` - Health check
  - `POST /get_flights` - Search for flights

### Example Flight Search Request

```bash
curl -X POST http://localhost:8001/get_flights \
  -H "Content-Type: application/json" \
  -d '{
    "airline": "dummy",
    "search_params": {
      "origin": "NYC",
      "destination": "LAX", 
      "departure_date": "2024-07-15",
      "return_date": "2024-07-20",
      "passengers": 1
    }
  }'
```

## 🔧 Configuration

The service uses configuration file `conf.ini` in the root.