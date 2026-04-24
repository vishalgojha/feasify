import { AnalysisInputs, AnalysisResult, FeasibilityResult, ClearancesResult, CostResult } from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3000";

export async function runAnalysis(
  inputs: AnalysisInputs
): Promise<{
  feasibility: FeasibilityResult;
  clearances: ClearancesResult;
  cost: CostResult;
}> {
  const res = await fetch(`${BASE}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(inputs),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getFeasibility(
  plotArea: number,
  zone: string,
  use: string,
  roadWidth: number,
  floors: number
): Promise<FeasibilityResult> {
  const params = new URLSearchParams({
    plot_area: String(plotArea),
    zone,
    use,
    road_width: String(roadWidth),
    floors: String(floors),
  });
  const res = await fetch(`${BASE}/api/feasibility?${params}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getClearances(
  heightM: number,
  buaSqM: number,
  plotAreaSqM: number,
  use: string
): Promise<ClearancesResult> {
  const params = new URLSearchParams({
    height_m: String(heightM),
    bua_sqm: String(buaSqM),
    plot_area_sqm: String(plotAreaSqM),
    use,
  });
  const res = await fetch(`${BASE}/api/clearances?${params}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getCost(
  buaSqFt: number,
  zone: string,
  floors: number,
  use: string,
  finish: string,
  landCost?: number
): Promise<CostResult> {
  const params = new URLSearchParams({
    bua_sqft: String(buaSqFt),
    zone,
    floors: String(floors),
    use,
    finish,
    ...(landCost ? { land_cost: String(landCost) } : {}),
  });
  const res = await fetch(`${BASE}/api/cost?${params}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}