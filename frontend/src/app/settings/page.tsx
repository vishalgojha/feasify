"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { Settings, User, Key, Trash2, Check, Moon, Sun } from "lucide-react";

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState(
    typeof window !== "undefined"
      ? localStorage.getItem("feasify_api_url") || "http://localhost:3000"
      : "http://localhost:3000"
  );
  const [theme, setTheme] = useState(
    typeof window !== "undefined"
      ? localStorage.getItem("feasify_theme") || "light"
      : "light"
  );
  const [saved, setSaved] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const handleSave = () => {
    localStorage.setItem("feasify_api_url", apiUrl);
    localStorage.setItem("feasify_theme", theme);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleClearHistory = () => {
    localStorage.removeItem("feasify_history");
    setShowConfirm(false);
  };

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold text-brand-navy mb-8">Settings</h1>

      <div className="space-y-6">
        {/* API URL */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
          <div className="flex items-center gap-3 mb-4">
            <Key size={20} className="text-brand-teal" />
            <h2 className="font-bold text-brand-navy">API Configuration</h2>
          </div>
          <label className="block text-sm text-slate-600 mb-2">API URL</label>
          <input
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-teal/20 outline-none"
            placeholder="http://localhost:3000"
          />
        </div>

        {/* Theme */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
          <div className="flex items-center gap-3 mb-4">
            <Moon size={20} className="text-brand-teal" />
            <h2 className="font-bold text-brand-navy">Appearance</h2>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setTheme("light")}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-xl border",
                theme === "light"
                  ? "border-brand-teal bg-brand-teal/10 text-brand-teal"
                  : "border-slate-200"
              )}
            >
              <Sun size={18} />
              Light
            </button>
            <button
              onClick={() => setTheme("dark")}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-xl border",
                theme === "dark"
                  ? "border-brand-teal bg-brand-teal/10 text-brand-teal"
                  : "border-slate-200"
              )}
            >
              <Moon size={18} />
              Dark
            </button>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-brand-orange/20">
          <div className="flex items-center gap-3 mb-4">
            <Trash2 size={20} className="text-brand-orange" />
            <h2 className="font-bold text-brand-navy">Danger Zone</h2>
          </div>
          <p className="text-sm text-slate-500 mb-4">
            Delete all analysis history. This cannot be undone.
          </p>
          {showConfirm ? (
            <div className="flex gap-2">
              <button
                onClick={handleClearHistory}
                className="px-4 py-2 bg-brand-orange text-white rounded-lg"
              >
                Confirm Delete
              </button>
              <button
                onClick={() => setShowConfirm(false)}
                className="px-4 py-2 border border-slate-200 rounded-lg"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowConfirm(true)}
              className="px-4 py-2 border border-brand-orange text-brand-orange rounded-lg hover:bg-brand-orange/10"
            >
              Clear History
            </button>
          )}
        </div>

        {/* Save */}
        <button
          onClick={handleSave}
          className={cn(
            "px-6 py-3 rounded-xl font-medium flex items-center gap-2",
            saved
              ? "bg-brand-green text-white"
              : "bg-brand-teal text-white hover:opacity-90"
          )}
        >
          {saved ? <Check size={20} /> : null}
          {saved ? "Saved" : "Save Settings"}
        </button>
      </div>
    </div>
  );
}