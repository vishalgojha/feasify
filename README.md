# Feasify

AI-powered real estate feasibility analysis for Mumbai real estate projects. Analyzes DCPR-2034 compliance, government premiums, clearances, and project costs using multi-agent AI orchestration.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from feasify.db.session import init_db; init_db()"

# Start API server (port 3000)
cd cli && bun run server

# Start Next.js frontend (port 3000)
cd frontend && npm run dev
```

## Features

- **DCPR-2034 Analysis** - Full Mumbai Development Control regulations compliance
- **Multi-Agent AI** - 5 specialized agents: Planner, DCPR Expert, Spatial Risk, Cost Engineer, Reviewer
- **Next.js Web UI** - Beautiful React frontend with chat interface
- **Interactive CLI** - Bun-powered CLI with demo mode
- **Cost Stack** - Complete project cost calculation with government premiums
- **Clearance Tracking** - Required clearances with critical path analysis
- **PDF Reports** - Export feasibility reports as PDF
- **Scenario Comparison** - Compare two scenarios side-by-side
- **SQLite Persistence** - All analyses saved to database

## Commands

### Python CLI
```bash
# Feasibility analysis
python -m feasify feasibility 1180 suburbs residential 60 21 --json

# Cost calculation
python -m feasify cost 31754 suburbs 21 residential --finish premium --json

# Clearances
python -m feasify clearances 63 2950 1180 residential --json

# Full Swarm analysis (multi-agent)
python -m feasify swarm 1234/567 suburbs --json

# Generate PDF report
python -m feasify report --json '<result_json>' --output report.pdf

# Database commands
python -m feasify db-save --json '<result_json>'
python -m feasify db-list --limit 50 --json
```

### Bun CLI
```bash
cd cli && bun run start     # Interactive CLI
cd cli && bun run server  # API server (port 3000)
```

## API Endpoints (Bun Server)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API documentation |
| GET | `/api/health` | Health check |
| GET | `/api/feasibility` | DCPR-2034 analysis |
| GET | `/api/clearances` | Required clearances |
| GET | `/api/cost` | Cost calculation |
| POST | `/api/analyze` | Full analysis + save to DB |
| POST | `/api/report` | Generate PDF |
| GET | `/api/history` | List saved analyses |

## Frontend

Next.js 14 App Router with:

- **Dashboard** - Metrics and recent analyses
- **Analyze** - Project input form
- **Results** - Full analysis with charts, FSI breakdown, cost stack, clearances
- **Vault** - History table with search/filter
- **Settings** - API config, theme, clear history
- **Scenario Comparison** - Side-by-side scenario analysis

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
feasify/
├── frontend/             # Next.js 14 frontend
│   ├── src/
│   │   ├── app/        # App router pages
│   │   ├── components/  # UI components
│   │   └── lib/       # API, types, utils
│   └── package.json
├── cli/                 # Bun CLI & server
│   ├── index.ts         # Interactive CLI
│   └── server.ts        # API server
├── feasify/             # Python backend
│   ├── swarm/          # Multi-agent AI
│   ├── agents/         # AI agents
│   ├── knowledge/      # DCPR-2034
│   ├── db/           # Database models
│   └── main.py         # Python CLI
└── docs/
```

## AI Agents

| Agent | Role |
|-------|------|
| **Planner** | Orchestrates workflow, synthesizes reports |
| **DCPR Expert** | FSI calculations, regulation sections |
| **Spatial Risk** | CRZ, aviation, heritage, DP reservations |
| **Cost Engineer** | Full cost stack, revenue model |
| **Reviewer** | Quality control, arithmetic verification |

## Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install
pip install -r requirements.txt

# Initialize database
python -c "from feasify.db.session import init_db; init_db()"

# Set API key (in .env)
GOOGLE_API_KEY=your_key_here

# Start servers
cd cli && bun run server  # Backend (port 3000)
cd frontend && npm run dev  # Frontend (port 3000)
```

## Tech Stack

- **Python 3.9+** - Backend
- **Next.js 14** - Frontend
- **Bun** - CLI & API server
- **SQLite** - Database
- **Tailwind CSS** - Styling
- **Recharts** - Charts
- **reportlab** - PDF generation

## API Keys

Get free API keys:

- **Google AI (Gemini)** - [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) (recommended)
- **Groq** - [console.groq.com/keys](https://console.groq.com/keys) (backup)

## License

MIT