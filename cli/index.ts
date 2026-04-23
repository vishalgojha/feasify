#!/usr/bin/env bun

import inquirer from "inquirer";
import chalk from "chalk";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const FEASIFY_ROOT = resolve(__dirname, "..");

interface FeasibilityData {
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

interface ClearanceItem {
  name: string;
  description: string;
  timeline_days: number;
  fee: number;
  risk_level: string;
}

interface ClearancesData {
  clearances: ClearanceItem[];
  critical_path_days: number;
  bottleneck: string;
}

interface CostData {
  land_cost: number;
  construction: { total_construction: number; rate_source: string };
  government_premiums: { total_government_premiums: number };
  professional_fees: { total_professional_fees: number };
  statutory: { total_statutory: number };
  financing: { financing_cost: number };
  grand_total: number;
  cost_per_sqft: number;
}

const ZONES = [
  { name: "Island City (South Mumbai)", value: "island_city" },
  { name: "Suburbs", value: "suburbs" },
  { name: "Extended Suburbs", value: "extended_suburbs" },
  { name: "BARC Area (M Ward)", value: "barc_area" },
];

const USES = [
  { name: "Residential", value: "residential" },
  { name: "Commercial", value: "commercial" },
];

const GRADES = [
  { name: "Basic (Economy)", value: "basic" },
  { name: "Standard (Mid-market)", value: "standard" },
  { name: "Premium (Luxury)", value: "premium" },
];

async function runPythonCommand(args: string[]): Promise<{ stdout: string; stderr: string; exitCode: number }> {
  const cmd = args.join(" ");
  const proc = Bun.spawn({
    cmd: ["python", "-m", "feasify", ...args],
    cwd: FEASIFY_ROOT,
    stdout: "pipe",
    stderr: "pipe",
  });

  const [stdout, stderr] = await Promise.all([
    proc.stdout.text(),
    proc.stderr.text(),
  ]);

  const exitCode = await proc.exitCode;
  return { stdout, stderr, exitCode };
}

function extractJson(text: string): any {
  // Normalize line endings and remove Python noise
  const normalized = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  
  const lines = normalized.split("\n").filter((l) => 
    !l.includes("python :") && 
    !l.includes("Traceback") &&
    !l.includes('File "') &&
    !l.includes("reportlab")
  );
  
  let combined = lines.join("\n");
  
  // Fix newlines INSIDE string values - apply multiple times for multi-line strings
  let prev = "";
  while (prev !== combined) {
    prev = combined;
    combined = combined.replace(/"([^"]*)\n([^"]*)"/g, (match, p1, p2) => `"${p1}${p2}"`);
  }
  
  // Find first "{"
  const startIdx = combined.indexOf("{");
  if (startIdx === -1) return null;
  
  // Find the end by counting braces
  let depth = 0;
  let endIdx = -1;
  for (let i = startIdx; i < combined.length; i++) {
    if (combined[i] === "{") depth++;
    else if (combined[i] === "}") {
      depth--;
      if (depth === 0) {
        endIdx = i + 1;
        break;
      }
    }
  }
  
  if (endIdx === -1) return null;
  
  const jsonText = combined.substring(startIdx, endIdx);
  
  try {
    return JSON.parse(jsonText);
  } catch (e) {
    return null;
  }
}

function formatCurrency(value: number | undefined): string {
  if (!value && value !== 0) return "N/A";
  return "₹" + value.toLocaleString("en-IN", { maximumFractionDigits: 0 });
}

async function main() {
  const args = process.argv.slice(2);
  
  // Demo mode if no TTY
  if (!process.stdin.isTTY) {
    console.clear();
    console.log(chalk.bold.cyan("\n=== FEASIFY FSI FEASIBILITY CLI ===\n"));
    console.log(chalk.yellow("Demo Mode - Using sample values:\n"));
    
    // Sample values for demo
    const plotArea = 1180;
    const zone = "suburbs";
    const use = "residential";
    const roadWidth = 60;
    const floors = 21;
    const finish = "premium";
    const landCost = 500000000;
    
    console.log(`  Plot Area: ${plotArea} sq.m`);
    console.log(`  Zone: ${zone}`);
    console.log(`  Use: ${use}`);
    console.log(`  Road Width: ${roadWidth}m`);
    console.log(`  Floors: ${floors}`);
    console.log(`  Grade: ${finish}`);
    console.log(`  Land Cost: ₹${(landCost/10000000).toFixed(0)} Cr\n`);
    
    // Run same analysis
    process.stdout.write(chalk.gray("  → DCPR-2034 feasibility... "));
    const feaResult = await runPythonCommand([
      "feasibility", plotArea.toString(), zone, use, roadWidth.toString(), floors.toString(), "--json"
    ]);
    const feasibility = extractJson(feaResult.stdout + feaResult.stderr);
    if (!feasibility) { 
      console.error(chalk.red("FAILED"));
      return; 
    }
    console.log(chalk.green("✓"));

    process.stdout.write(chalk.gray("  → Calculating clearances... "));
    const clearResult = await runPythonCommand([
      "clearances", feasibility.approx_height_m.toFixed(1), feasibility.permissible_bua_sqm.toFixed(1),
      plotArea.toString(), use, "--json"
    ]);
    const clearances = extractJson(clearResult.stdout + clearResult.stderr);
    console.log(chalk.green("✓"));

    process.stdout.write(chalk.gray("  → Building cost stack... "));
    const costResult = await runPythonCommand([
      "cost", feasibility.permissible_bua_sqft.toFixed(1), zone, floors.toString(), use,
      "--finish", finish, "--land-cost", landCost.toString(), "--json"
    ]);
    const cost = extractJson(costResult.stdout + costResult.stderr);
    console.log(chalk.green("✓"));

    displayResults(feasibility, clearances, cost);
    
    console.log(chalk.gray("\nRun with terminal for interactive mode:\n"));
    console.log(chalk.cyan("  cd cli && bun run start\n"));
    return;
  }
  
  // Interactive mode
  console.clear();
  console.log(chalk.bold.cyan("\n=== FEASIFY FSI FEASIBILITY CLI ===\n"));

  const answers = await inquirer.prompt([
    {
      type: "input",
      name: "plot_area",
      message: "Plot Area (sq.m):",
      default: "1000",
    },
    { type: "list", name: "zone", message: "Select Zone:", choices: ZONES, default: 1 },
    { type: "list", name: "use", message: "Proposed Use:", choices: USES, default: 0 },
    {
      type: "input",
      name: "road_width",
      message: "Road Width (meters):",
      default: "12",
    },
    {
      type: "input",
      name: "floors",
      message: "Number of Floors (G=1):",
      default: "10",
    },
    { type: "list", name: "finish", message: "Construction Grade:", choices: GRADES, default: 1 },
    { type: "input", name: "land_cost", message: "Land Cost (₹) [optional]:", default: "" },
  ]);

  const plotArea = parseFloat(answers.plot_area) || 1000;
  const zone = answers.zone;
  const use = answers.use;
  const roadWidth = parseFloat(answers.road_width) || 12;
  const floors = parseInt(answers.floors) || 10;
  const finish = answers.finish;
  const landCost = parseFloat(answers.land_cost) || 0;

  console.log(chalk.yellow("\n⚙ Running feasibility analysis...\n"));

  // Step 1: Feasibility
  process.stdout.write(chalk.gray("  → DCPR-2034 feasibility... "));
  const feaResult = await runPythonCommand([
    "feasibility", plotArea.toString(), zone, use, roadWidth.toString(), floors.toString(), "--json"
  ]);
  const feasibility = extractJson(feaResult.stdout + feaResult.stderr);
  
  if (!feasibility || feaResult.exitCode !== 0) {
    console.error(chalk.red("FAILED"));
    console.error("STDOUT:", feaResult.stdout.substring(0, 500));
    console.error("STDERR:", feaResult.stderr.substring(0, 500));
    return;
  }
  console.log(chalk.green("✓"));

  // Step 2: Clearances
  process.stdout.write(chalk.gray("  → Calculating clearances... "));
  const clearResult = await runPythonCommand([
    "clearances",
    feasibility.approx_height_m.toFixed(1),
    feasibility.permissible_bua_sqm.toFixed(1),
    plotArea.toString(),
    use,
    "--json"
  ]);
  const clearances = extractJson(clearResult.stdout + clearResult.stderr);
  console.log(chalk.green("✓"));

  // Step 3: Cost
  process.stdout.write(chalk.gray("  → Building cost stack... "));
  const costResult = await runPythonCommand([
    "cost",
    feasibility.permissible_bua_sqft.toFixed(1),
    zone,
    floors.toString(),
    use,
    "--finish", finish,
    "--land-cost", landCost.toString(),
    "--json"
  ]);
  const cost = extractJson(costResult.stdout + costResult.stderr);
  console.log(chalk.green("✓"));

  // Display Results
  displayResults(feasibility, clearances, cost);
}

function displayResults(
  feasibility: FeasibilityData,
  clearances: ClearancesData,
  cost: CostData
) {
  console.log(chalk.bold.green("\n✓ FEASIBILITY REPORT\n"));
  console.log(chalk.cyan("═".repeat(60)));

  // Design Parameters
  console.log(chalk.bold("\n🏗️ Design Parameters:"));
  console.log(`  Zone Basic FSI:     ${chalk.cyan(feasibility.zonal_basic_fsi.toFixed(2))}`);
  console.log(`  Max Permissible FSI: ${chalk.yellow(feasibility.max_permissible_fsi.toFixed(2))}`);
  console.log(`  Permissible BUA:     ${chalk.green(feasibility.permissible_bua_sqft.toLocaleString())} sq.ft.`);
  console.log(`  Building Height:     ${feasibility.approx_height_m.toFixed(1)}m (${feasibility.floors_feasible} floors)`);
  console.log(`  Setbacks:           Side/Rear ${feasibility.setback_side_rear_m}m, Dead Wall ${feasibility.setback_dead_wall_m}m`);
  console.log(`  Parking Required:   ${feasibility.parking_spaces_required} spaces`);
  console.log(`  Max Tenements:      ${feasibility.max_tenements}`);

  if (feasibility.high_rise) {
    console.log(chalk.yellow("\n  ⚠ HIGH-RISE: Fire NOC from Mumbai Fire Brigade mandatory"));
  }

  if (feasibility.warnings?.length > 0) {
    console.log(chalk.yellow("\n⚠ Warnings:"));
    feasibility.warnings.forEach((w: string) => console.log(`  • ${w}`));
  }

  // Clearances
  if (clearances?.clearances?.length > 0) {
    console.log(chalk.bold("\n📋 Required Clearances:"));
    console.log("  " + "-".repeat(50));
    clearances.clearances.forEach((c: ClearanceItem) => {
      const risk = c.risk_level === "high" ? chalk.red("HIGH") : c.risk_level === "medium" ? chalk.yellow("MED") : chalk.green("LOW");
      console.log(`  ${c.name.padEnd(15)} ${String(c.timeline_days + "d").padEnd(6)} ${formatCurrency(c.fee).padStart(12)} ${risk}`);
    });
    console.log("  " + "-".repeat(50));
    console.log(`  ${chalk.yellow("Critical Path:")} ${clearances.critical_path_days} days  ${chalk.red("Bottleneck:")} ${clearances.bottleneck}`);
  }

  // Cost Stack
  if (cost) {
    console.log(chalk.bold("\n💰 Cost Stack:"));
    console.log("  " + "-".repeat(50));
    console.log(`  ${"Land Cost:".padEnd(20)} ${formatCurrency(cost.land_cost).padStart(15)}`);
    console.log(`  ${"Construction:".padEnd(20)} ${formatCurrency(cost.construction?.total_construction).padStart(15)}`);
    console.log(`  ${"Gov Premiums:".padEnd(20)} ${formatCurrency(cost.government_premiums?.total_government_premiums).padStart(15)}`);
    console.log(`  ${"Professional Fees:".padEnd(20)} ${formatCurrency(cost.professional_fees?.total_professional_fees).padStart(15)}`);
    console.log(`  ${"Statutory:".padEnd(20)} ${formatCurrency(cost.statutory?.total_statutory).padStart(15)}`);
    console.log(`  ${"Financing:".padEnd(20)} ${formatCurrency(cost.financing?.financing_cost).padStart(15)}`);
    console.log("  " + "-".repeat(50));
    console.log(chalk.bold(`  ${"GRAND TOTAL:".padEnd(20)} ${formatCurrency(cost.grand_total).padStart(15)}`));
    console.log(`  ${"Cost/sq.ft:".padEnd(20)} ${formatCurrency(cost.cost_per_sqft).padStart(15)}`);
  }

  console.log(chalk.cyan("\n" + "═".repeat(60)));
  console.log(chalk.gray("\nAnalysis complete.\n"));
}

main().catch((error) => {
  console.error(chalk.red(`\nFatal error: ${error.message}`));
  process.exit(1);
});