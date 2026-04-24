import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatCurrencyCr(amount: number): string {
  return `₹${(amount / 1e7).toFixed(2)} Cr`;
}

export function formatSqft(sqft: number): string {
  return new Intl.NumberFormat("en-IN").format(Math.round(sqft)) + " sqft";
}

export function formatSqM(sqm: number): string {
  return new Intl.NumberFormat("en-IN").format(Math.round(sqm)) + " sqm";
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}