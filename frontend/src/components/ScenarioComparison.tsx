"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { AnalysisResult } from "@/lib/types";
import { runAnalysis } from "@/lib/api";
import { formatCurrency, formatCurrencyCr, cn } from "@/lib/utils";
import { X, GitCompare, Loader2, TrendingUp, TrendingDown, Minus } from "lucide-react";

const scenarioSchema = z.object({
  zone: z.enum(["island_city", "suburbs", "extended_suburbs", "barc_area", "crz_affected"]),
  road_width_m: z.number().positive(),
  floors: z.number().int().min(1).max(60),
  finish: z.enum(["basic", "standard", "premium"]),
  land_cost: z.number().min(0).default(0),
});

type ScenarioFormData = z.infer<typeof scenarioSchema>;

interface Props {
  original: AnalysisResult;
  isOpen: boolean;
  onClose: () => void;
}

const zoneLabels: Record<string, string> = {
  island_city: "Island City",
  suburbs: "Suburbs",
  extended_suburbs: "Extended Suburbs",
  barc_area: "BARC Area",
  crz_affected: "CRZ Affected",
};

const finishLabels: Record<string, string> = {
  basic: "Basic",
  standard: "Standard",
  premium: "Premium",
};

export default function ScenarioComparison({ original, isOpen, onClose }: Props) {
  const router = useRouter();
  const [comparing, setComparing] = useState(false);
  const [scenarioResult, setScenarioResult] = useState<AnalysisResult | null>(null);

  const { register, handleSubmit } = useForm<ScenarioFormData>({
    resolver: zodResolver(scenarioSchema),
    defaultValues: {
      zone: original.inputs.zone as any,
      road_width_m: original.inputs.road_width_m,
      floors: original.inputs.floors,
      finish: original.inputs.finish as any,
      land_cost: original.inputs.land_cost,
    },
  });

  const onSubmit = async (data: ScenarioFormData) => {
    setComparing(true);
    try {
      const inputs = {
        ...original.inputs,
        ...data,
      };
      const result = await runAnalysis(inputs);
      
      const scenario: AnalysisResult = {
        id: crypto.randomUUID(),
        cts_number: original.cts_number + "-B",
        timestamp: new Date().toISOString(),
        inputs,
        feasibility: result.feasibility,
        clearances: result.clearances,
        cost: result.cost,
        verdict: result.cost.cost_per_sqft > 25000 ? "MARGINAL" : "VIABLE",
      };
      setScenarioResult(scenario);
    } catch (e) {
      console.error(e);
    } finally {
      setComparing(false);
    }
  };

  if (!isOpen) return null;

  const diff = (a: number, b: number) => {
    const delta = b - a;
    if (delta > 0) return { color: "text-brand-green", icon: <TrendingUp size={14} />, label: "+" };
    if (delta < 0) return { color: "text-brand-orange", icon: <TrendingDown size={14} />, label: "-" };
    return { color: "text-slate-400", icon: <Minus size={14} />, label: "=" };
  };

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/50 z-50" onClick={onClose} />

      {/* Panel */}
      <div className="fixed right-0 top-0 bottom-0 w-[500px] bg-white z-50 overflow-y-auto shadow-xl">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-brand-navy flex items-center gap-2">
              <GitCompare size={20} />
              Scenario Comparison
            </h2>
            <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-lg">
              <X size={20} />
            </button>
          </div>

          {!scenarioResult ? (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <p className="text-sm text-slate-500 mb-4">
                Modify parameters to compare against original analysis (CTS: {original.cts_number})
              </p>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Zone</label>
                <select {...register("zone")} className="w-full px-3 py-2 rounded-lg border border-slate-200">
                  {Object.entries(zoneLabels).map(([v, l]) => (
                    <option key={v} value={v}>{l}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Road Width (m)</label>
                <input type="number" {...register("road_width_m", { valueAsNumber: true })} className="w-full px-3 py-2 rounded-lg border border-slate-200" />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Floors</label>
                <input type="number" {...register("floors", { valueAsNumber: true })} className="w-full px-3 py-2 rounded-lg border border-slate-200" />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Finish</label>
                <select {...register("finish")} className="w-full px-3 py-2 rounded-lg border border-slate-200">
                  {Object.entries(finishLabels).map(([v, l]) => (
                    <option key={v} value={v}>{l}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Land Cost (₹)</label>
                <input type="number" {...register("land_cost", { valueAsNumber: true })} className="w-full px-3 py-2 rounded-lg border border-slate-200" />
              </div>

              <button type="submit" disabled={comparing} className="w-full py-3 bg-brand-teal text-white rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-2">
                {comparing ? <Loader2 size={18} className="animate-spin" /> : null}
                {comparing ? "Comparing..." : "Run Comparison"}
              </button>
            </form>
          ) : (
            <div className="space-y-6">
              {/* Comparison Table */}
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-slate-500 uppercase">
                    <th className="pb-2">Metric</th>
                    <th className="pb-2 text-brand-navy">Original</th>
                    <th className="pb-2 text-brand-teal">Scenario B</th>
                    <th className="pb-2">Diff</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  <tr>
                    <td className="py-2">Max FSI</td>
                    <td className="py-2 font-medium">{original.feasibility.max_permissible_fsi}</td>
                    <td className="py-2 font-medium">{scenarioResult.feasibility.max_permissible_fsi}</td>
                    <td className={cn("py-2", diff(original.feasibility.max_permissible_fsi, scenarioResult.feasibility.max_permissible_fsi).color)}>
                      {diff(original.feasibility.max_permissible_fsi, scenarioResult.feasibility.max_permissible_fsi).icon}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2">Max BUA (sqft)</td>
                    <td className="py-2 font-medium">{original.feasibility.permissible_bua_sqft.toLocaleString()}</td>
                    <td className="py-2 font-medium">{scenarioResult.feasibility.permissible_bua_sqft.toLocaleString()}</td>
                    <td className={cn("py-2", diff(original.feasibility.permissible_bua_sqft, scenarioResult.feasibility.permissible_bua_sqft).color)}>
                      {diff(original.feasibility.permissible_bua_sqft, scenarioResult.feasibility.permissible_bua_sqft).icon}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2">Construction</td>
                    <td className="py-2 font-medium">{formatCurrencyCr(original.cost.construction.total_construction)}</td>
                    <td className="py-2 font-medium">{formatCurrencyCr(scenarioResult.cost.construction.total_construction)}</td>
                    <td className={cn("py-2", diff(original.cost.construction.total_construction, scenarioResult.cost.construction.total_construction).color)}>
                      {diff(original.cost.construction.total_construction, scenarioResult.cost.construction.total_construction).icon}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2">FSI Premium</td>
                    <td className="py-2 font-medium">{formatCurrencyCr(original.cost.government_premiums.total_government_premiums)}</td>
                    <td className="py-2 font-medium">{formatCurrencyCr(scenarioResult.cost.government_premiums.total_government_premiums)}</td>
                    <td className={cn("py-2", diff(original.cost.government_premiums.total_government_premiums, scenarioResult.cost.government_premiums.total_government_premiums).color)}>
                      {diff(original.cost.government_premiums.total_government_premiums, scenarioResult.cost.government_premiums.total_government_premiums).icon}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2">Grand Total</td>
                    <td className="py-2 font-medium">{formatCurrencyCr(original.cost.grand_total)}</td>
                    <td className="py-2 font-medium">{formatCurrencyCr(scenarioResult.cost.grand_total)}</td>
                    <td className={cn("py-2", diff(original.cost.grand_total, scenarioResult.cost.grand_total).color)}>
                      {diff(original.cost.grand_total, scenarioResult.cost.grand_total).icon}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-2">Cost/sqft</td>
                    <td className="py-2 font-medium">{formatCurrency(original.cost.cost_per_sqft)}</td>
                    <td className="py-2 font-medium">{formatCurrency(scenarioResult.cost.cost_per_sqft)}</td>
                    <td className={cn("py-2", diff(original.cost.cost_per_sqft, scenarioResult.cost.cost_per_sqft).color)}>
                      {diff(original.cost.cost_per_sqft, scenarioResult.cost.cost_per_sqft).icon}
                    </td>
                  </tr>
                </tbody>
              </table>

              <div className="flex gap-2">
                <button onClick={() => setScenarioResult(null)} className="flex-1 py-2 border border-slate-200 rounded-lg text-sm">
                  New Comparison
                </button>
                <button onClick={onClose} className="flex-1 py-2 bg-brand-teal text-white rounded-lg text-sm">
                  Done
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}