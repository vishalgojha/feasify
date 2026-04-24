"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  flexRender,
  createColumnHelper,
} from "@tanstack/react-table";
import { AnalysisResult } from "@/lib/types";
import { formatCurrency, formatDate, cn } from "@/lib/utils";
import { Search, Trash2, ChevronRight } from "lucide-react";

const columnHelper = createColumnHelper<AnalysisResult>();

interface HistoryItem {
  project_id: string;
  cts_number: string;
  zone: string;
  verdict: string;
  created_at: string;
}

export default function HistoryPage() {
  const router = useRouter();
  const [data, setData] = useState<HistoryItem[]>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [verdictFilter, setVerdictFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000"}/api/history`);
        if (res.ok) {
          const json = await res.json();
          setData(Array.isArray(json) ? json : []);
        }
      } catch {
        // Fallback to localStorage
        const stored = localStorage.getItem("feasify_history");
        if (stored) {
          const arr = JSON.parse(stored);
          setData(arr.map((a: AnalysisResult) => ({
            project_id: a.id,
            cts_number: a.cts_number,
            zone: a.inputs?.zone,
            verdict: a.verdict,
            created_at: a.timestamp,
          })));
        }
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const filteredData = data.filter(
    (a) => verdictFilter === "all" || a.verdict === verdictFilter
  );

  const columns = [
    columnHelper.accessor("cts_number", {
      header: "CTS",
      cell: (info) => info.getValue() || "-",
    }),
    columnHelper.accessor("zone", {
      header: "Zone",
      cell: (info) => info.getValue() || "-",
    }),
    columnHelper.accessor("verdict", {
      header: "Verdict",
      cell: (info) => {
        const v = info.getValue();
        return (
          <span
            className={cn(
              "px-2 py-1 rounded-full text-xs font-medium",
              v === "VIABLE"
                ? "bg-brand-green/10 text-brand-green"
                : v === "MARGINAL"
                ? "bg-brand-yellow/10 text-brand-yellow"
                : "bg-brand-orange/10 text-brand-orange"
            )}
          >
            {v}
          </span>
        );
      },
    }),
    columnHelper.accessor("created_at", {
      header: "Date",
      cell: (info) => info.getValue() ? formatDate(info.getValue()) : "-",
    }),
    columnHelper.display({
      id: "actions",
      header: "",
      cell: ({ row }) => (
        <div className="flex gap-2 justify-end">
          <button
            onClick={() => router.push(`/results/${row.original.project_id}`)}
            className="p-2 hover:bg-slate-100 rounded-lg"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      ),
    }),
  ];

  const table = useReactTable({
    data: filteredData,
    columns,
    state: { globalFilter },
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  return (
    <div className="max-w-6xl">
      <h1 className="text-3xl font-bold text-brand-navy mb-2">Vault</h1>
      <p className="text-slate-500 mb-8">Analysis history</p>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex gap-4">
          <div className="relative flex-1 max-w-xs">
            <Search
              size={18}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
            />
            <input
              value={globalFilter ?? ""}
              onChange={(e) => setGlobalFilter(e.target.value)}
              placeholder="Search CTS..."
              className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-teal/20 outline-none"
            />
          </div>
          <select
            value={verdictFilter}
            onChange={(e) => setVerdictFilter(e.target.value)}
            className="px-4 py-2 rounded-xl border border-slate-200"
          >
            <option value="all">All Verdicts</option>
            <option value="VIABLE">Viable</option>
            <option value="MARGINAL">Marginal</option>
            <option value="BLOCKED">Blocked</option>
          </select>
        </div>

        <table className="w-full">
          <thead className="bg-slate-50/50">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase"
                  >
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-slate-100">
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id} className="hover:bg-slate-50/50">
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-4">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>

        {filteredData.length === 0 && (
          <div className="p-8 text-center text-slate-500">
            No analyses found
          </div>
        )}
      </div>
    </div>
  );
}