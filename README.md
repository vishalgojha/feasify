# Feasify

Real estate cost estimation tool for Mumbai and Pune regions, integrating MCGM/DP data, zoning analysis, DCPR-2034 compliance, and anti-detection browser automation.

## Features

- 🏗️ **Cost Estimation**: Calculate construction costs using PWD rates and multipliers
- 📋 **DCPR-2034 Knowledge**: Mumbai Development Control regulations with FSI tables, setbacks, parking norms
- 📊 **Feasibility Analysis**: CLI tool for DCPR compliance checking (`feasify feasibility`)
- 🌐 **Anti-Detection Browser**: Integrated Camofox browser for web automation
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
│   ├── utils/                  # Helpers (cache, scraper, rates)
│   ├── browser/                # Camofox anti-detection browser tools
│   └── knowledge/              # DCPR-2034 knowledge base
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

### Cost Estimation
```bash
# CLI estimate
python -m feasify estimate 2400 residential --floors 2

# Output:
# Plot area: 2400 sq.ft | Zone: residential | Floors: 2
# Total Cost: ₹99,36,000
```

### DCPR-2034 Feasibility Analysis
```bash
# Check feasibility for Mumbai suburbs plot
python -m feasify feasibility 500 suburbs residential 15 10

# Output:
# Zonal Basic FSI: 1.0
# Max Permissible FSI: 2.2
# Permissible BUA: 1100 sqm (11840 sqft)
# Building Height: 30m | Floors Feasible: 10
# Setback Side/Rear: 6.0m | Parking Spaces: 7
```

### Browser Automation (Camofox)
```bash
# Search using anti-detection browser
python -m feasify browser-search "Mumbai property rates" --engine google

# Take screenshot
python -m feasify browser-screenshot "https://example.com" --output screenshot.png
```

### Database
```bash
# Initialize database with sample data
python scripts/seed_db.py

# Update PWD rates
python scripts/update_rates.py
```

### API (Future)
```bash
uvicorn feasify.api.routes:app --reload
```

## DCPR-2034 Knowledge Base

Feasify includes comprehensive Mumbai Development Control and Promotion Regulation 2034 knowledge:

- **FSI Tables** (Regulation 30): Island City, Suburbs, BARC, CRZ zones
- **Setback Rules** (Regulation 42): Height-based setbacks for small/large plots
- **Height Regulations** (Regulation 43): 3×(road+setback) rule
- **Parking Norms** (Regulation 44): Residential, Commercial, Industrial
- **Fungible Area** (Regulation 31): Up to 35% bonus area
- **Premium Rules**: Additional FSI on payment

## Testing

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=feasify --cov-report=html

# Run specific test modules
pytest tests/unit/test_dcpr.py -v
pytest tests/unit/test_estimator.py -v
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `estimate <area> <zone> [--floors]` | Cost estimation |
| `feasibility <area> <zone> <use> <road> <floors>` | DCPR-2034 analysis |
| `browser-search <query> [--engine]` | Search with Camofox |
| `browser-screenshot <url> [--output]` | Capture screenshot |
| `browser-start` | Start Camofox server |
| `fetch <plot_id> [--source]` | Fetch plot details |
| `version` | Show version |

## License

MIT
