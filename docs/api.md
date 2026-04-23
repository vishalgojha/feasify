# Feasify API Documentation

## Base URL
`http://localhost:8000` (development)

## Endpoints

### Health Check
```
GET /health
```
Response:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### Generate Cost Estimate
```
POST /estimate
```
Request:
```json
{
  "area_sqft": 2400.0,
  "zone_type": "residential",
  "num_floors": 1,
  "plot_id": "PLOT-001"
}
```
Response:
```json
{
  "plot_area_sqft": 2400.0,
  "built_up_area_sqft": 2400.0,
  "zone_type": "residential",
  "num_floors": 1,
  "rate_per_sqft": 1800.0,
  "base_cost": 4320000.0,
  "contingency": 216000.0,
  "overhead": 432000.0,
  "total_cost": 4968000.0
}
```

### Fetch Plot Details
```
GET /plot/{plot_id}?source=mcgm
```
Response:
```json
{
  "plot_id": "1234/567",
  "source": "MCGM",
  "area_sqft": 2400.0,
  "zone_type": "residential",
  "owner": "John Doe",
  "address": "123, ABC Road, Andheri West"
}
```

### List Zoning Types
```
GET /zones
```
Response:
```json
{
  "zones": ["residential", "commercial", "industrial", "public", "green", "special"]
}
```

## Authentication
Currently not implemented. Future versions will use API keys or JWT.

## Rate Limiting
Not implemented in v0.1.0.

## Error Responses
All errors return JSON with `error` field:
```json
{
  "error": "Failed to fetch data"
}
```
