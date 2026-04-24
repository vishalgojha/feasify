"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { runAnalysis } from "@/lib/api";
import { AnalysisResult } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Send, Loader2, AlertCircle } from "lucide-react";

const schema = z.object({
  cts_number: z.string().min(1, "Required"),
  zone: z.enum(["island_city", "suburbs", "extended_suburbs", "barc_area", "crz_affected"]),
  use: z.enum(["residential", "commercial", "industrial"]),
  plot_area_sqm: z.number().positive(),
  road_width_m: z.number().positive(),
  floors: z.number().int().min(1).max(60),
  finish: z.enum(["basic", "standard", "premium"]),
  land_cost: z.number().min(0).default(0),
});

type FormData = z.infer<typeof schema>;

const zoneLabels: Record<string, string> = {
  island_city: "Island City",
  suburbs: "Suburbs",
  extended_suburbs: "Extended Suburbs",
  barc_area: "BARC Area",
  crz_affected: "CRZ Affected",
};

const useLabels: Record<string, string> = {
  residential: "Residential",
  commercial: "Commercial",
  industrial: "Industrial",
};

const finishLabels: Record<string, string> = {
  basic: "Basic",
  standard: "Standard",
  premium: "Premium",
};

export default function AnalyzePage() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<"dcpr" | "clearances" | "cost" | "done">("dcpr");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      cts_number: "",
      zone: "suburbs",
      use: "residential",
      plot_area_sqm: 1000,
      road_width_m: 9,
      floors: 10,
      finish: "standard",
      land_cost: 0,
    },
  });

  const onSubmit = async (data: FormData) => {
    setSubmitting(true);
    setError(null);
    setStep("dcpr");

    try {
      setStep("clearances");
      const result = await runAnalysis(data);

      setStep("cost");
      const inputs = { ...data, cts_number: data.cts_number };

      let verdict: "VIABLE" | "MARGINAL" | "BLOCKED" = "VIABLE";
      if (result.cost.cost_per_sqft > 25000) verdict = "MARGINAL";
      if (result.feasibility.warnings?.length > 3) verdict = "BLOCKED";

      const analysis: AnalysisResult = {
        id: crypto.randomUUID(),
        cts_number: data.cts_number,
        timestamp: new Date().toISOString(),
        inputs,
        feasibility: result.feasibility,
        clearances: result.clearances,
        cost: result.cost,
        verdict,
      };

      // Save to localStorage
      const stored = localStorage.getItem("feasify_history");
      const history = stored ? JSON.parse(stored) : [];
      history.push(analysis);
      localStorage.setItem("feasify_history", JSON.stringify(history));

      setStep("done");
      router.push(`/results/${analysis.id}`);
    } catch (e: any) {
      setError(e.message || "Analysis failed");
    } finally {
      setSubmitting(false);
    }
  };

  const steps = [
    { key: "dcpr", label: "DCPR Analysis" },
    { key: "clearances", label: "Clearances" },
    { key: "cost", label: "Cost Stack" },
  ];

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold text-brand-navy mb-2">New Analysis</h1>
      <p className="text-slate-500 mb-8">Enter project details for DCPR-2034 compliance</p>

      {submitting && (
        <div className="mb-6 p-4 bg-brand-teal/10 rounded-xl border border-brand-teal/20">
          <div className="flex items-center gap-3 mb-3">
            <Loader2 size={18} className="animate-spin text-brand-teal" />
            <span className="font-medium text-brand-teal">Analyzing...</span>
          </div>
          <div className="flex gap-2">
            {steps.map((s, i) => (
              <div
                key={s.key}
                className={cn(
                  "px-3 py-1 rounded-full text-xs font-medium",
                  step === s.key
                    ? "bg-brand-teal text-white"
                    : steps.findIndex((x) => x.key === step) > i
                    ? "bg-brand-green text-white"
                    : "bg-slate-200 text-slate-600"
                )}
              >
                {s.label}
              </div>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 bg-brand-orange/10 rounded-xl border border-brand-orange/20 flex items-center gap-3">
          <AlertCircle size={18} className="text-brand-orange" />
          <span className="text-brand-orange">{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-1">
              CTS Number
            </label>
            <input
              {...register("cts_number")}
              placeholder="e.g. 918/1"
              className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-teal/20 focus:border-brand-teal outline-none"
            />
            {errors.cts_number && (
              <p className="text-sm text-brand-orange mt-1">{errors.cts_number.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Zone
            </label>
            <select
              {...register("zone")}
              className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-teal/20 focus:border-brand-teal outline-none"
            >
              {Object.entries(zoneLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Use Type
            </label>
            <select
              {...register("use")}
              className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-teal/20 focus:border-teal outline-none"
            >
              {Object.entries(useLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Plot Area (sq.m)
            </label>
            <input
              type="number"
              {...register("plot_area_sqm", { valueAsNumber: true })}
              className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-teal/20 focus:border-brand-teal outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Road Width (meters)
            </label>
            <input
              type="number"
              {...register("road_width_m", { valueAsNumber: true })}
              className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-teal/20 focus:border-brand-teal outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Floors
            </label>
            <input
              type="number"
              {...register("floors", { valueAsNumber: true })}
              className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-teal/20 focus:border-brand-teal outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Finish Grade
            </label>
            <select
              {...register("finish")}
              className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-teal/20 focus:border-brand-teal outline-none"
            >
              {Object.entries(finishLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div className="col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Land Cost (₹) <span className="text-slate-400">(optional)</span>
            </label>
            <input
              type="number"
              {...register("land_cost", { valueAsNumber: true })}
              placeholder="0 for society redevelopment"
              className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-teal/20 focus:border-brand-teal outline-none"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full py-4 bg-brand-teal text-white rounded-xl font-medium disabled:opacity-50 hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
        >
          {submitting ? (
            <>
              <Loader2 size={20} className="animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Send size={20} />
              Run Analysis
            </>
          )}
        </button>
      </form>
    </div>
  );
}