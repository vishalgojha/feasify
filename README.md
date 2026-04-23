# Feasify

Real estate FSI feasibility analysis tool for Mumbai, integrating DCPR-2034 compliance, government premiums, clearance tracking, and project cost estimation.

## Features

- **DCPR-2034 Feasibility** - Full Mumbai Development Control regulations analysis
- **Clearance Engine** - Required clearances, timelines, fees, and critical path
- **Cost Stack** - Complete project cost calculation with government premiums
- **Interactive CLI** - User-friendly Bun-powered command-line interface
- **REST API** - HTTP server for programmatic access
- **Groq AI Agent** - Optional AI-powered analysis (requires API key)

## Quick Start

### Python CLI
```bash
# Feasibility analysis
python -m feasify feasibility 1180 suburbs residential 60 21

# Get JSON output
python -m feasify feasibility 1180 suburbs residential 60 21 --json
```

### Bun Interactive CLI
```bash
cd cli
bun run start
```

### API Server
```bash
cd cli
bun run server
# Opens at http://localhost:3000
```

## CLI Commands

### Core Analysis

```bash
# 1. Feasibility (DCPR-2034)
python -m feasify feasibility PLOT_AREA ZONE USE ROAD_WIDTH FLOORS [--json]
python -m feasify feasibility 1180 suburbs residential 60 21 --json

# 2. Cost Stack
python -m feasify cost BUA_SQFT ZONE FLOORS [USE] [--finish] [--land-cost] [--json]
python -m feasify cost 31754 suburbs 21 residential --finish premium --json

# 3. Clearances
python -m feasify clearances HEIGHT_M BUA_SQM PLOT_AREA [USE] [--json]
python -m feasify clearances 63 2950 1180 residential --json

# 4. Quick Estimate
python -m feasify estimate AREA ZONE [--floors]
python -m feasify estimate 10000 residential --floors 10

# 5. Fetch Plot Data
python -m feasify fetch CTS_NUMBER [--source mcgm|dp]

# 6. AI Analysis (requires GROQ_API_KEY)
python -m feasify analyze CTS_NUMBER USE_TYPE [--json]
```

### Options

| Command | Description |
|---------|-------------|
| `--json` | Output JSON for CLI integration |
| `--finish` | Construction grade: basic/standard/premium |
| `--land-cost` | Land cost in ₹ for financing calculation |
| `--floors` | Number of floors |
| `--pdf` | Generate PDF report |
| `--source` | Data source: mcgm or dp |

## Bun CLI Commands

```bash
cd cli

bun run start      # Interactive CLI with prompts
bun run server     # HTTP API server on port 3000
bun run dev        # Watch mode for development
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API documentation |
| GET | `/api/health` | Health check |
| GET | `/api/feasibility` | DCPR-2034 analysis |
| GET | `/api/clearances` | Required clearances |
| GET | `/api/cost` | Cost calculation |
| POST | `/api/analyze` | Full project analysis |

### API Example
```bash
curl -X POST "http://localhost:3000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"plot_area_sqm":1180,"zone":"suburbs","use":"residential","road_width_m":60,"floors":21}'
```

## Project Structure

```
feasify/
├── cli/                    # Bun CLI (interactive + API server)
│   ├── index.ts           # Interactive CLI
│   └── server.ts          # HTTP API server
├── feasify/               # Python package
│   ├── agents/            # AI agent and cost engine
│   ├── core/              # Estimator, fetcher
│   ├── knowledge/         # DCPR-2034 knowledge base
│   └── main.py            # CLI entry point
├── data/                   # Local data storage
└── tests/                  # Test suite
```

## Setup

```bash
# Clone and setup
cd feaisfy
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY=your_key_here  # Optional, for AI analysis

# Run CLI
python -m feasify feasibility 1180 suburbs residential 60 21
```

## DCPR-2034 Coverage

- **FSI Tables**: Island City, Suburbs, Extended Suburbs, BARC Area
- **Setback Rules**: Height-based for small/large plots
- **Height Regulations**: 3×(road+setback) rule
- **Parking Norms**: Residential, Commercial, Industrial
- **Fungible Area**: Up to 35% bonus area
- **Premium FSI**: 50% for residential, 60% for commercial

## Testing

```bash
# Python tests
pytest tests/ -v

# CLI build test
cd cli && bun build index.ts --target=bun
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key for AI agent |
| `PYTHONIOENCODING` | Set to `utf-8` for Unicode support |

## License

MIT