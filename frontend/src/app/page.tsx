"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AnalysisResult } from "@/lib/types";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Plus, Building2, AlertTriangle, CheckCircle, TrendingUp } from "lucide-react";

export default function Dashboard() {
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    viable: 0,
    blocked: 0,
    avgCostSqft: 0,
  });

  useEffect(() => {
    const stored = localStorage.getItem("feasify_history");
    if (stored) {
      const data = JSON.parse(stored) as AnalysisResult[];
      setAnalyses(data.slice(-5).reverse());
      const viable = data.filter((a) => a.verdict === "VIABLE").length;
      const blocked = data.filter((a) => a.verdict === "BLOCKED").length;
      const avg =
        data.length > 0
          ? data.reduce((sum, a) => sum + a.cost.cost_per_sqft, 0) / data.length
          : 0;
      setStats({ total: data.length, viable, blocked, avgCostSqft: avg });
    }
  }, []);

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case "VIABLE":
        return "bg-brand-green/10 text-brand-green";
      case "MARGINAL":
        return "bg-brand-yellow/10 text-brand-yellow";
      case "BLOCKED":
        return "bg-brand-orange/10 text-brand-orange";
      default:
        return "bg-slate-100 text-slate-600";
    }
  };

  return (
    <div className="max-w-6xl">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-brand-navy">Dashboard</h1>
          <p className="text-slate-500">Mumbai real estate feasibility</p>
        </div>
        <Link
          href="/analyze"
          className="flex items-center gap-2 px-5 py-3 bg-brand-teal text-white rounded-xl font-medium hover:opacity-90 transition-opacity"
        >
          <Plus size={20} />
          New Analysis
        </Link>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
          <div className="flex items-center gap-3 text-slate-500 mb-2">
            <Building2 size={18} />
            <span className="text-sm">Total Analyses</span>
          </div>
          <div className="text-3xl font-bold text-brand-navy">{stats.total}</div>
        </div>

        <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
          <div className="flex items-center gap-3 text-brand-green mb-2">
            <CheckCircle size={18} />
            <span className="text-sm">Viable</span>
          </div>
          <div className="text-3xl font-bold text-brand-green">{stats.viable}</div>
        </div>

        <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
          <div className="flex items-center gap-3 text-brand-orange mb-2">
            <AlertTriangle size={18} />
            <span className="text-sm">Blocked</span>
          </div>
          <div className="text-3xl font-bold text-brand-orange">{stats.blocked}</div>
        </div>

        <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100">
          <div className="flex items-center gap-3 text-slate-500 mb-2">
            <TrendingUp size={18} />
            <span className="text-sm">Avg Cost/sqft</span>
          </div>
          <div className="text-3xl font-bold text-brand-navy">
            {formatCurrency(stats.avgCostSqft)}
          </div>
        </div>
      </div>

      {/* Recent */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 bg-slate-50/50">
          <h2 className="font-medium text-brand-navy">Recent Analyses</h2>
        </div>

        {analyses.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            No analyses yet.{" "}
            <Link href="/analyze" className="text-brand-teal hover:underline">
              Start your first analysis
            </Link>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-slate-50/50">
              <tr>
                <th className="px-5 py-3 text-left text-xs font-medium text-slate-500 uppercase">
                  CTS
                </th>
                <th className="px-5 py-3 text-left text-xs font-medium text-slate-500 uppercase">
                  Zone
                </th>
                <th className="px-5 py-3 text-left text-xs font-medium text-slate-500 uppercase">
                  Verdict
                </th>
                <th className="px-5 py-3 text-left text-xs font-medium text-slate-500 uppercase">
                  Date
                </th>
                <th className="px-5 py-3 text-right text-xs font-medium text-slate-500 uppercase">
                  Cost/sqft
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {analyses.map((a) => (
                <tr key={a.id} className="hover:bg-slate-50/50">
                  <td className="px-5 py-4 font-medium">{a.cts_number || "-"}</td>
                  <td className="px-5 py-4 text-slate-600">{a.inputs.zone}</td>
                  <td className="px-5 py-4">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getVerdictColor(
                        a.verdict
                      )}`}
                    >
                      {a.verdict}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-slate-500 text-sm">
                    {formatDate(a.timestamp)}
                  </td>
                  <td className="px-5 py-4 text-right font-medium">
                    {formatCurrency(a.cost.cost_per_sqft)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}