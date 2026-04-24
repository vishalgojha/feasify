export interface FeasibilityResult {
  zonal_basic_fsi: number;
  max_permissible_fsi: number;
  permissible_bua_sqm: number;
  permissible_bua_sqft: number;
  approx_height_m: number;
  floors_feasible: number;
  setback_side_rear_m: number;
  setback_dead_wall_m: number;
  high_rise: boolean;
  fire_noc_required: boolean;
  parking_spaces_required: number;
  max_tenements: number;
  warnings: string[];
}

export interface CostResult {
  land_cost: number;
  construction: {
    base_construction: number;
    total_construction: number;
    rate_source: string;
    material_prices?: Record<string, number>;
  };
  government_premiums: {
    additional_fsi_premium: number;
    fungible_premium: number;
    development_cess: number;
    infrastructure_levy: number;
    total_government_premiums: number;
  };
  professional_fees: { total_professional_fees: number };
  clearances: { total_clearance_fees: number };
  statutory: { labour_cess: number; gst: number; total_statutory: number };
  financing: { financing_cost: number };
  grand_total: number;
  cost_per_sqft: number;
  cost_per_sqm: number;
}

export interface ClearanceItem {
  name: string;
  description: string;
  timeline_days: number;
  fee: number;
  risk_level: "low" | "medium" | "high";
  depends_on: string[];
  notes: string;
}

export interface ClearancesResult {
  clearances: ClearanceItem[];
  critical_path_days: number;
  critical_sequence: string[];
  bottleneck: string;
}

export interface AnalysisInputs {
  plot_area_sqm: number;
  zone: string;
  use: string;
  road_width_m: number;
  floors: number;
  finish: string;
  land_cost: number;
  cts_number?: string;
}

export interface AnalysisResult {
  id: string;
  cts_number: string;
  timestamp: string;
  inputs: AnalysisInputs;
  feasibility: FeasibilityResult;
  clearances: ClearancesResult;
  cost: CostResult;
  verdict: "VIABLE" | "MARGINAL" | "BLOCKED";
}