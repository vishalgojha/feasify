# Feasify

Real estate cost estimation tool for Mumbai and Pune regions, integrating MCGM/DP data, zoning analysis, and construction cost estimation.

## Features

- 🏗️ **Cost Estimation**: Calculate construction costs using PWD rates and multipliers
- 🗺️ **Zoning Analysis**: Parse and analyze zoning data from MCGM/DP documents
- 🔍 **Data Fetching**: Scrape property data from official municipal sources
- 💾 **Database Integration**: Store and retrieve property records with SQLAlchemy
- 🚀 **API Ready**: FastAPI layer for future REST API implementation

## Project Structure

```
feasify/
├── feasify/                    # Main Python package
│   ├── core/                   # Business logic (estimator, fetcher, zoning)
│   ├── models/                 # Data models (plot, estimate)
│   ├── db/                     # Database layer (SQLAlchemy)
│   ├── api/                    # FastAPI routes (future)
│   └── utils/                  # Helpers (cache, scraper, rates)
├── data/                       # Local data storage
├── tests/                      # Test suite
├── scripts/                    # Utility scripts
└── docs/                       # Documentation
```

## Setup

1. Create virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Unix
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # Or with dev dependencies:
   pip install -e ".[dev]"
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Usage

```bash
# Run CLI (future)
python -m feasify

# Run API (future)
uvicorn feasify.api.routes:app --reload
```

## Testing

```bash
pytest
# With coverage report:
pytest --cov=feasify --cov-report=html
```

## License

MIT
