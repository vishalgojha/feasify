"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { AnalysisResult } from "@/lib/types";
import { formatCurrency, formatCurrencyCr, formatSqft, formatSqM, cn } from "@/lib/utils";
import ScenarioComparison from "@/components/ScenarioComparison";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { ArrowLeft, Download, GitCompare, AlertTriangle } from "lucide-react";

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [showJson, setShowJson] = useState(false);
  const [showScenario, setShowScenario] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("feasify_history");
    if (stored && params.id) {
      const data = JSON.parse(stored) as AnalysisResult[];
      const found = data.find((a) => a.id === params.id);
      if (found) setResult(found);
      else router.push("/history");
    }
  }, [params.id, router]);

  if (!result) return <div className="p-8">Loading...</div>;

  const verdictColors: Record<string, string> = {
    VIABLE: "bg-brand-green text-white",
    MARGINAL: "bg-brand-yellow text-brand-navy",
    BLOCKED: "bg-brand-orange text-white",
  };

  const fsiData = [
    { name: "Base", value: result.feasibility.zonal_basic_fsi || 1.0, fill: "#1D3557" },
    { name: "Premium", value: result.feasibility.max_permissible_fsi - (result.feasibility.zonal_basic_fsi || 1.0), fill: "#0A9396" },
  ];

  const costData = [
    { name: "Land", value: result.cost.land_cost / 1e7, fill: "#1D3557" },
    { name: "Construction", value: result.cost.construction.total_construction / 1e7, fill: "#0A9396" },
    { name: "Gov Premiums", value: result.cost.government_premiums.total_government_premiums / 1e7, fill: "#2D6A4F" },
    { name: "Professional", value: result.cost.professional_fees.total_professional_fees / 1e7, fill: "#E9C46A" },
    { name: "Statutory", value: result.cost.statutory.total_statutory / 1e7, fill: "#E76F51" },
  ];

  const hasLandCost = result.inputs.land_cost > 0;

  return (
    <div className="max-w-5xl pb-24">
      <div className="flex items-center gap-4 mb-6">
        <Link
          href="/history"
          className="p-2 hover:bg-slate-100 rounded-lg"
        >
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-2xl font-bold text-brand-navy">
          {result.cts_number || "Analysis Result"}
        </h1>
      </div>

      {/* Verdict Banner */}
      <div className={cn("p-6 rounded-2xl mb-6", verdictColors[result.verdict])}>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm opacity/70 mb-1">Verdict</div>
            <div className="text-4xl font-bold">{result.verdict}</div>
          </div>
          <div className="text-right">
            <div className="text-sm opacity/70">Cost/sqft</div>
            <div className="text-2xl font-bold">{formatCurrency(result.cost.cost_per_sqft)}</div>
          </div>
        </div>
      </div>

      {/* FSI Breakdown */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 mb-6">
        <h2 className="font-bold text-brand-navy mb-4"> FSI Breakdown</h2>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={fsiData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis type="category" dataKey="name" width={80} />
            <Tooltip />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-4 text-center font-medium text-brand-navy">
          Max Buildable: {formatSqM(result.feasibility.permissible_bua_sqm)} ({formatSqft(result.feasibility.permissible_bua_sqft)})
        </div>
      </div>

      {/* Cost Stack */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 mb-6">
        <h2 className="font-bold text-brand-navy mb-4">Cost Stack</h2>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={costData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip formatter={(v: number) => formatCurrencyCr(v * 1e7)} />
            <Bar dataKey="value" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-4 text-center">
          <div className="text-sm text-slate-500">Grand Total</div>
          <div className="text-3xl font-bold text-brand-navy">
            {formatCurrencyCr(result.cost.grand_total)}
          </div>
          <div className="text-sm text-slate-500">
            {formatCurrency(result.cost.cost_per_sqft)}/sqft • {formatCurrency(result.cost.cost_per_sqm)}/sqm
          </div>
        </div>
      </div>

      {/* Feasibility Ratios */}
      {hasLandCost && (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 mb-6">
          <h2 className="font-bold text-brand-navy mb-4">Feasibility Ratios</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-slate-50 rounded-xl">
              <div className="text-sm text-slate-500 mb-1">Gross Margin</div>
              <div className="text-2xl font-bold text-brand-green">25%</div>
            </div>
            <div className="text-center p-4 bg-slate-50 rounded-xl">
              <div className="text-sm text-slate-500 mb-1">ROI</div>
              <div className="text-2xl font-bold text-brand-teal">18%</div>
            </div>
            <div className="text-center p-4 bg-slate-50 rounded-xl">
              <div className="text-sm text-slate-500 mb-1">Breakeven</div>
              <div className="text-2xl font-bold text-brand-navy">
                {formatCurrency(result.cost.cost_per_sqft * 1.2)}
              </div>
            </div>
          </div>
        </div>
      )}

      {!hasLandCost && (
        <div className="bg-slate-50 rounded-xl p-4 text-center text-slate-500 mb-6">
          Land cost not provided — P&L ratios not available
        </div>
      )}

      {/* Warnings */}
      {result.feasibility.warnings?.length > 0 && (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 mb-6">
          <h2 className="font-bold text-brand-navy mb-4 flex items-center gap-2">
            <AlertTriangle size={18} className="text-brand-yellow" />
            Warnings
          </h2>
          <div className="space-y-2">
            {result.feasibility.warnings.map((w, i) => (
              <div key={i} className="p-3 bg-brand-yellow/10 rounded-lg text-sm">
                {w}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Clearances */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 mb-6">
        <h2 className="font-bold text-brand-navy mb-4">Clearances</h2>
        <table className="w-full">
          <thead>
            <tr className="text-left text-xs text-slate-500 uppercase">
              <th className="pb-2">Name</th>
              <th className="pb-2">Timeline</th>
              <th className="pb-2">Fee</th>
              <th className="pb-2">Risk</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {result.clearances.clearances?.map((c, i) => (
              <tr key={i}>
                <td className="py-3">{c.name}</td>
                <td className="py-3">{c.timeline_days} days</td>
                <td className="py-3">{formatCurrency(c.fee)}</td>
                <td className="py-3">
                  <span
                    className={cn(
                      "px-2 py-1 rounded-full text-xs",
                      c.risk_level === "low"
                        ? "bg-brand-green/10 text-brand-green"
                        : c.risk_level === "medium"
                        ? "bg-brand-yellow/10 text-brand-yellow"
                        : "bg-brand-orange/10 text-brand-orange"
                    )}
                  >
                    {c.risk_level}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {result.clearances.critical_path_days && (
          <div className="mt-4 pt-4 border-t text-sm text-slate-500">
            Critical Path: {result.clearances.critical_path_days} days •{" "}
            Bottleneck: {result.clearances.bottleneck}
          </div>
        )}
      </div>

      {/* Raw JSON */}
      <details className="bg-slate-900 text-slate-100 rounded-xl p-4 mb-6">
        <summary className="cursor-pointer text-sm">Raw JSON</summary>
        <pre className="mt-4 text-xs overflow-x-auto">
          {JSON.stringify(result, null, 2)}
        </pre>
      </details>

      {/* Actions */}
      <div className="fixed bottom-0 left-64 right-0 p-4 bg-white border-t flex justify-between">
        <Link
          href="/history"
          className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg"
        >
          Back
        </Link>
        <div className="flex gap-2">
          <button 
          onClick={async () => {
            try {
              const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000"}/api/report`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id: result.id, result }),
              });
              if (res.ok) {
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `feasify_${result.cts_number}.pdf`;
                a.click();
              }
            } catch (e) {
              console.error(e);
            }
          }}
          className="px-4 py-2 bg-brand-teal text-white rounded-lg flex items-center gap-2 hover:opacity-90"
        >
          <Download size={18} />
          Export PDF
        </button>
        <button 
          onClick={() => setShowScenario(true)}
          className="px-4 py-2 bg-brand-navy text-white rounded-lg flex items-center gap-2 hover:opacity-90"
        >
          <GitCompare size={18} />
          New Scenario
        </button>
      </div>
      </div>

      <ScenarioComparison 
        original={result} 
        isOpen={showScenario} 
        onClose={() => setShowScenario(false)} 
      />
    </div>
  );
}