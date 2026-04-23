# Feasify

AI-powered real estate feasibility analysis for Mumbai real estate projects. Analyzes DCPR-2034 compliance, government premiums, clearances, and project costs using multi-agent AI orchestration.

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Launch with guided setup
python -m feasify welcome

# Or just open the web UI
python -m feasify studio
```

## Features

- **DCPR-2034 Analysis** - Full Mumbai Development Control regulations compliance
- **Multi-Agent AI** - 5 specialized agents: Planner, DCPR Expert, Spatial Risk, Cost Engineer, Reviewer
- **Web UI** - Beautiful Streamlit interface for non-technical users
- **Interactive CLI** - Bun-powered CLI with demo mode
- **Cost Stack** - Complete project cost calculation with government premiums
- **Clearance Tracking** - Required clearances with critical path analysis

## Commands

### Web UI (Recommended)
```bash
python -m feasify welcome   # Launch with guided setup + auto-open browser
python -m feasify studio    # Just open the web UI
```

### CLI
```bash
# Feasibility analysis
python -m feasify feasibility 1180 suburbs residential 60 21 --json

# Cost calculation
python -m feasify cost 31754 suburbs 21 residential --finish premium --json

# Clearances
python -m feasify clearances 63 2950 1180 residential --json

# Swarm analysis (multi-agent)
python -m feasify swarm 1234/567 suburbs --json
```

### Bun CLI (Interactive)
```bash
cd cli && bun run start     # Interactive CLI
cd cli && bun run server    # API server (port 3000)
```

## API Endpoints (Bun Server)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API documentation |
| GET | `/api/health` | Health check |
| GET | `/api/feasibility` | DCPR-2034 analysis |
| GET | `/api/clearances` | Required clearances |
| GET | `/api/cost` | Cost calculation |
| POST | `/api/analyze` | Full analysis |

## Project Structure

```
feasify/
├── swarm/              # Multi-agent AI system
│   ├── swarm.py         # Orchestrator
│   ├── state.py         # State management
│   ├── llm.py           # LLM client (Gemini + Groq)
│   ├── prompts.py       # Agent system prompts
│   └── *.py             # Agent implementations
├── studio/              # Web UI (Streamlit)
│   └── app.py           # Feasify Studio
├── cli/                  # Bun CLI
│   ├── index.ts         # Interactive CLI
│   └── server.ts        # API server
├── agents/              # Legacy AI agents
├── knowledge/           # DCPR-2034 knowledge base
└── main.py              # Python CLI
```

## AI Agents

| Agent | Role |
|-------|------|
| **Planner** | Orchestrates workflow, synthesizes reports |
| **DCPR Expert** | FSI calculations, regulation sections |
| **Spatial Risk** | CRZ, aviation, heritage, DP reservations |
| **Cost Engineer** | Full cost stack, revenue model |
| **Reviewer** | Quality control, arithmetic verification |

## API Keys

Get free API keys:

- **Google AI (Gemini)** - [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) (recommended - free tier)
- **Groq** - [console.groq.com/keys](https://console.groq.com/keys) (fast backup)

Set in `.env` file:
```
GOOGLE_API_KEY=your_key_here
```

## Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set API key
export GOOGLE_API_KEY=your_key  # Linux/Mac
set GOOGLE_API_KEY=your_key      # Windows

# Launch
python -m feasify welcome
```

## Requirements

- Python 3.9+
- Rich (CLI formatting)
- Groq or Google AI SDK
- Streamlit (for web UI)
- Bun (optional, for native CLI)

## License

MIT