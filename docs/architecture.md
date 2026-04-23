# Feasify Architecture

## Overview
Feasify is a real estate cost estimation tool targeting Mumbai and Pune markets, integrating municipal data (MCGM/DP), zoning analysis, and construction cost estimation.

## System Components

### 1. Core Layer (`feasify/core/`)
- **estimator.py**: Cost calculation engine using PWD rates and multipliers
- **fetcher.py**: Web scrapers for MCGM and DP portals
- **zoning.py**: Zoning data models and parsers

### 2. Models Layer (`feasify/models/`)
- **plot.py**: Plot, CTS, and zoning data structures
- **estimate.py**: Cost estimate dataclass with serialization

### 3. Database Layer (`feasify/db/`)
- **models.py**: SQLAlchemy ORM models
- **session.py**: Database session management

### 4. API Layer (`feasify/api/`)
- **routes.py**: FastAPI endpoints (future)
- **schemas.py**: Pydantic request/response models

### 5. Utilities (`feasify/utils/`)
- **cache.py**: File-based caching with TTL
- **scraper_helpers.py**: HTTP request utilities
- **rates.py**: PWD rates and multipliers

## Data Flow

```
User Input → CLI/API → Estimator → Fetcher (if plot data needed) → Cost Calculation → Output
                                    ↓
                              Zoning Parser (for zone info)
                                    ↓
                              Database (optional storage)
```

## External Integrations
- **MCGM Portal**: Property tax and plot details
- **DP Portal**: Development Plan zoning data
- **PWD Maharashtra**: Standard construction rates

## Future Enhancements
- Machine learning model for price prediction
- GIS integration for map visualization
- Mobile app support via API
- Integration with real estate platforms
