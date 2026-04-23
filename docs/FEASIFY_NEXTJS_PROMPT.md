# Feasify - Next.js UI Generation Prompt

## Project Overview

**Feasify** is an AI-powered real estate feasibility analysis tool for Mumbai real estate projects. It analyzes DCPR-2034 compliance, government premiums, clearances, and project costs using multi-agent AI orchestration.

## Tech Stack for Next.js UI

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **State**: React hooks + Zustand (optional)
- **Forms**: React Hook Form + Zod validation
- **Charts**: Recharts or ApexCharts
- **API**: Call existing Python backend via REST API

## Existing Backend Tools

### CLI Commands (already implemented)
```bash
# Feasibility analysis
python -m feasify feasibility 1180 suburbs residential 60 21 --json

# Cost calculation  
python -m feasify cost 31754 suburbs 21 residential --finish premium --json

# Clearances
python -m feasify clearances 63 2950 1180 residential --json

# Full Swarm analysis (5-agent)
python -m feasify swarm 1234/567 suburbs --json
```

### API Endpoints (Bun server at port 3000)
- `GET /api/feasibility?plot_area=1000&zone=suburbs&use=residential&road_width=12&floors=10`
- `GET /api/clearances?height_m=30&bua_sqm=2200&plot_area_sqm=1000&use=residential`
- `GET /api/cost?bua_sqft=23681&zone=suburbs&floors=10&use=residential&finish=standard`
- `POST /api/analyze` - Full analysis

## Required Screens

### 1. Dashboard (Home)
- Summary cards: Total Projects, Viable Projects, Blocked Projects, Average Cost/sqft
- Recent analyses list
- Quick action buttons

### 2. New Project Analysis
- Form inputs:
  - CTS Number (text)
  - Zone (select: island_city, suburbs, extended_suburbs, barc_area, crz_affected)
  - Use Type (select: residential, commercial, industrial)
  - Plot Area (number, sq.m)
  - Road Width (number, meters)
  - Floors (number)
  - Finish Grade (select: basic, standard, premium)
  - Land Cost (number, optional)
- Submit button → calls `/api/analyze`

### 3. Results Display
- Verdict banner (VIABLE/MARGINAL/BLOCKED with colors)
- FSI Breakdown (bar chart)
  - Base FSI, Premium FSI, TDR, Fungible
- Cost Summary
  - Total Cost, Cost/sqft, Cost/sq.m
- Feasibility Ratios
  - Gross Margin %, ROI %, Breakeven Rate
- Risk Manifest
  - List with severity badges (BLOCKER/HIGH/MEDIUM/LOW)
- Clearances Table
  - Name, Timeline (days), Fee (₹), Risk Level
- Full JSON expandable section

### 4. Project History
- Table with columns: CTS, Zone, Verdict, Date, Actions
- Search/filter functionality
- View details button

### 5. Settings
- API Key configuration
- Theme toggle (light/dark)
- Export options

## UI/UX Requirements

### Color Scheme
- Primary: #0A9396 (teal)
- Secondary: #1D3557 (dark blue)
- Success: #2D6A4F (green)
- Warning: #E9C46A (yellow)
- Error: #E76F51 (red)
- Background: #F8F9FA (light) / #0D1117 (dark)

### Components (shadcn/ui)
- Sidebar navigation
- Cards for metrics
- Tables with sorting/filtering
- Forms with validation
- Badges for status
- Charts (bar, line)
- Buttons (primary, secondary, ghost)
- Input fields
- Select dropdowns
- Dialogs/modals
- Toast notifications

### Responsive
- Mobile-friendly sidebar (collapsible)
- Responsive cards and tables

## Example API Response Structure

```json
{
  "project_id": "uuid",
  "cts_number": "1234/567",
  "verdict": "VIABLE",
  "fsi_summary": {
    "base": 1.0,
    "premium": 1.5,
    "tdr": 0,
    "fungible": 0,
    "total": 2.5,
    "max_buildable_sqm": 2950,
    "saleable_sqm": 2212
  },
  "cost_summary": {
    "total": 2056756133,
    "cost_per_sqft": 64772,
    "cost_per_sqm": 697201
  },
  "feasibility_ratios": {
    "gross_margin_pct": 25,
    "roi_pct": 18,
    "breakeven_rate_sqft": 48000
  },
  "risk_manifest": [
    {
      "check": "FIRE_NOC",
      "severity": "HIGH",
      "description": "High-rise building requires fire NOC"
    }
  ],
  "clearances": [
    {"name": "IOD", "timeline_days": 30, "fee": 5000, "risk_level": "low"},
    {"name": "CC", "timeline_days": 60, "fee": 10000, "risk_level": "low"}
  ]
}
```

## Deliverables

1. **Project structure** - Next.js 14 App Router with shadcn/ui
2. **Layout** - Sidebar + main content area
3. **Pages** - Dashboard, New Analysis, Results, History, Settings
4. **Components** - Reusable UI components
5. **API integration** - Service layer to call backend
6. **State** - Form state, results state, history state

## Instructions for Gemini

Generate the complete Next.js project structure with:
- `app/layout.tsx` - Root layout with sidebar
- `app/page.tsx` - Dashboard
- `app/analyze/page.tsx` - New analysis form
- `app/results/[id]/page.tsx` - Results display
- `app/history/page.tsx` - Project history
- `app/settings/page.tsx` - Settings
- `components/ui/*` - shadcn/ui components (use standard imports)
- `lib/api.ts` - API service layer
- `lib/types.ts` - TypeScript interfaces
- Tailwind config with Feasify colors
