"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  MessagesSquare,
  History,
  Settings,
  BarChart3,
} from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: BarChart3 },
  { href: "/analyze", label: "New Analysis", icon: MessagesSquare },
  { href: "/history", label: "Vault", icon: History },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-64 bg-brand-navy text-white flex flex-col z-50">
      <div className="p-6 flex items-center gap-3">
        <div className="w-10 h-10 bg-brand-teal rounded-xl flex items-center justify-center font-bold text-xl italic">
          F
        </div>
        <span className="text-2xl font-bold">Feasify</span>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors",
                isActive
                  ? "bg-brand-teal text-white"
                  : "text-slate-400 hover:text-white hover:bg-white/5"
              )}
            >
              <Icon size={20} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4">
        <div className="p-4 rounded-2xl bg-white/5">
          <div className="text-xs font-medium">Feasify</div>
          <div className="text-xs text-slate-500">DCPR-2034 AI</div>
        </div>
      </div>
    </aside>
  );
}