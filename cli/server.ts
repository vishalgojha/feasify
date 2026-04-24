#!/usr/bin/env bun

import { serve } from "bun";
import chalk from "chalk";

const PORT = 3000;

const HTML = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Feasify - FSI Feasibility API</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, system-ui, sans-serif; background: #0a0a0a; color: #fff; min-height: 100vh; padding: 2rem; }
    .container { max-width: 900px; margin: 0 auto; }
    h1 { color: #00ff88; margin-bottom: 0.5rem; font-size: 2rem; }
    .subtitle { color: #888; margin-bottom: 2rem; }
    .endpoints { display: grid; gap: 1rem; }
    .endpoint { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 1.5rem; }
    .method { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 4px; font-weight: bold; font-size: 0.8rem; }
    .get { background: #00ff8820; color: #00ff88; }
    .post { background: #00ff0020; color: #00ff00; }
    .path { font-family: monospace; font-size: 1.1rem; margin: 0.5rem 0; color: #fff; }
    .desc { color: #888; font-size: 0.9rem; }
    .example { background: #0a0a0a; padding: 1rem; border-radius: 4px; margin-top: 1rem; font-family: monospace; font-size: 0.85rem; color: #00ff88; white-space: pre-wrap; overflow-x: auto; }
    code { color: #ff6b6b; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Feasify API</h1>
    <p class="subtitle">FSI Feasibility Analysis for Mumbai Real Estate</p>
    
    <div class="endpoints">
      <div class="endpoint">
        <span class="method get">GET</span>
        <div class="path">/api/feasibility</div>
        <p class="desc">DCPR-2034 feasibility analysis</p>
        <div class="example">curl "http://localhost:${PORT}/api/feasibility?plot_area=1000&zone=suburbs&use=residential&road_width=12&floors=10"</div>
      </div>
      
      <div class="endpoint">
        <span class="method get">GET</span>
        <div class="path">/api/clearances</div>
        <p class="desc">Calculate required clearances and critical path</p>
        <div class="example">curl "http://localhost:${PORT}/api/clearances?height_m=30&bua_sqm=2200&plot_area_sqm=1000&use=residential"</div>
      </div>
      
      <div class="endpoint">
        <span class="method get">GET</span>
        <div class="path">/api/cost</div>
        <p class="desc">Calculate complete project cost stack</p>
        <div class="example">curl "http://localhost:${PORT}/api/cost?bua_sqft=23681&zone=suburbs&floors=10&use=residential&finish=standard"</div>
      </div>
      
      <div class="endpoint">
        <span class="method post">POST</span>
        <div class="path">/api/analyze</div>
        <p class="desc">Full project analysis (all three endpoints combined)</p>
        <div class="example">curl -X POST "http://localhost:${PORT}/api/analyze" \\
  -H "Content-Type: application/json" \\
  -d '{"plot_area_sqm":1000,"zone":"suburbs","use":"residential","road_width_m":12,"floors":10,"finish":"standard","land_cost":0}'</div>
      </div>
    </div>
  </div>
</body>
</html>
`;

interface AnalyzeRequest {
  cts_number?: string;
  plot_area_sqm: number;
  zone: string;
  use: string;
  road_width_m: number;
  floors: number;
  finish?: string;
  land_cost?: number;
}

const COST_ARGS = {
  zone: ["island_city", "suburbs", "extended_suburbs", "barc_area"],
  use: ["residential", "commercial"],
  finish: ["basic", "standard", "premium"],
};

async function runPythonCommand(args: string[]): Promise<{ data: any; error?: string; stderr?: string }> {
  const proc = Bun.spawn({
    cmd: ["python", "-m", "feasify", ...args],
    cwd: import.meta.dir + "/..",
    stdout: "pipe",
    stderr: "pipe",
  });

  const [stdout, stderr] = await Promise.all([
    proc.stdout.text(),
    proc.stderr.text(),
  ]);

  const exitCode = await proc.exitCode;

  if (exitCode === 0) {
    try {
      const lines = stdout.split("\n");
      const jsonStart = lines.findIndex((l) => l.trim().startsWith("{"));
      if (jsonStart >= 0) {
        const jsonLines = lines.slice(jsonStart).join("\n");
        const jsonMatch = jsonLines.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          return { data: JSON.parse(jsonMatch[0]) };
        }
      }
      return { data: stdout.trim() };
    } catch {
      return { data: stdout.trim() };
    }
  } else {
    return { data: null, error: stderr || `Exit code ${exitCode}`, stderr };
  }
}

function parseQueryParam(value: string | string[] | undefined, defaultValue: string | number): string | number {
  if (!value) return defaultValue;
  if (Array.isArray(value)) return value[0] || defaultValue;
  const parsed = Number(value);
  return isNaN(parsed) ? String(value) : parsed;
}

const server = serve({
  port: PORT,
  async fetch(req) {
    const url = new URL(req.url);

    if (url.pathname === "/" || url.pathname === "/index.html") {
      return new Response(HTML, {
        headers: { "Content-Type": "text/html" },
      });
    }

    if (url.pathname === "/api/feasibility") {
      const plot_area = parseQueryParam(url.searchParams.get("plot_area"), 1000);
      const zone = parseQueryParam(url.searchParams.get("zone"), "suburbs");
      const use = parseQueryParam(url.searchParams.get("use"), "residential");
      const road_width = parseQueryParam(url.searchParams.get("road_width"), 12);
      const floors = parseQueryParam(url.searchParams.get("floors"), 10);

      console.log(chalk.cyan(`[GET] /api/feasibility`));
      const result = await runPythonCommand([
        "feasibility", String(plot_area), String(zone), String(use), String(road_width), String(floors), "--json"
      ]);

      if (result.error) {
        return Response.json({ error: result.error }, { status: 500 });
      }
      return Response.json(result.data);
    }

    if (url.pathname === "/api/clearances") {
      const height_m = parseQueryParam(url.searchParams.get("height_m"), 30);
      const bua_sqm = parseQueryParam(url.searchParams.get("bua_sqm"), 2200);
      const plot_area_sqm = parseQueryParam(url.searchParams.get("plot_area_sqm"), 1000);
      const use = parseQueryParam(url.searchParams.get("use"), "residential");

      console.log(chalk.cyan(`[GET] /api/clearances`));
      const result = await runPythonCommand([
        "clearances", String(height_m), String(bua_sqm), String(plot_area_sqm), use as string, "--json"
      ]);

      if (result.error) {
        return Response.json({ error: result.error }, { status: 500 });
      }
      return Response.json(result.data);
    }

    if (url.pathname === "/api/cost") {
      const bua_sqft = parseQueryParam(url.searchParams.get("bua_sqft"), 10000);
      const zone = parseQueryParam(url.searchParams.get("zone"), "suburbs");
      const floors = parseQueryParam(url.searchParams.get("floors"), 5);
      const use = parseQueryParam(url.searchParams.get("use"), "residential");
      const finish = parseQueryParam(url.searchParams.get("finish"), "standard");
      const land_cost = parseQueryParam(url.searchParams.get("land_cost"), 0);

      console.log(chalk.cyan(`[GET] /api/cost`));
      const result = await runPythonCommand([
        "cost", String(bua_sqft), String(zone), String(floors), use as string, "--finish", String(finish), "--land-cost", String(land_cost), "--json"
      ]);

if (result.error) {
          return Response.json({ error: result.error }, { status: 500 });
        }
        return Response.json(result.data);
      }
    }

    if (url.pathname === "/api/analyze" && req.method === "POST") {
      try {
        const body: AnalyzeRequest = await req.json();
        console.log(chalk.cyan(`[POST] /api/analyze`), chalk.gray(JSON.stringify(body)));

        const feaResult = await runPythonCommand([
          "feasibility",
          String(body.plot_area_sqm || 1000),
          body.zone || "suburbs",
          body.use || "residential",
          String(body.road_width_m || 12),
          String(body.floors || 10),
          "--json"
        ]);

        if (feaResult.error) {
          return Response.json({ error: feaResult.error }, { status: 500 });
        }

        const feasibility = feaResult.data;
        const clearancesResult = await runPythonCommand([
          "clearances",
          feasibility.approx_height_m.toFixed(1),
          feasibility.permissible_bua_sqm.toFixed(1),
          String(body.plot_area_sqm || 1000),
          body.use || "residential",
          "--json"
        ]);

        const costResult = await runPythonCommand([
          "cost",
          feasibility.permissible_bua_sqft.toFixed(1),
          body.zone || "suburbs",
          String(body.floors || 10),
          body.use || "residential",
          "--finish", body.finish || "standard",
          "--land-cost", String(body.land_cost || 0),
          "--json"
        ]);

        const result = {
          feasibility,
          clearances: clearancesResult.data,
          cost: costResult.data,
        };

        // Save to database
        const analysisId = crypto.randomUUID();
        const saveData = {
          id: analysisId,
          cts_number: body.cts_number || "",
          inputs: body,
          ...result,
          verdict: "VIABLE",
        };
        
        runPythonCommand(["db-save", "--json", JSON.stringify(saveData)]);

        return Response.json(result);
      } catch (e: any) {
        return Response.json({ error: e.message }, { status: 400 });
      }
    }

    if (url.pathname === "/api/report" && req.method === "POST") {
      try {
        const body = await req.json();
        const result = await runPythonCommand([
          "report", "--json", JSON.stringify(body.result), "--output", `/tmp/feasify_${body.id}.pdf`
        ]);
        if (result.error) {
          return Response.json({ error: result.error }, { status: 500 });
        }
        const pdfPath = `/tmp/feasify_${body.id}.pdf`;
        const pdfFile = Bun.file(pdfPath);
        if (await pdfFile.exists()) {
          return new Response(pdfFile, {
            headers: { "Content-Type": "application/pdf" },
          });
        }
        return Response.json({ message: "PDF generated", path: pdfPath });
      } catch (e: any) {
        return Response.json({ error: e.message }, { status: 400 });
      }
    }

    if (url.pathname === "/api/history") {
      const limit = parseQueryParam(url.searchParams.get("limit"), 50);
      const result = await runPythonCommand(["db-list", "--limit", String(limit), "--json"]);
      if (result.error) {
        return Response.json({ error: result.error }, { status: 500 });
      }
      try {
        return Response.json(JSON.parse(result.data));
      } catch {
        return Response.json(result.data);
      }
    }

    if (url.pathname === "/api/health") {
      return Response.json({ status: "ok", timestamp: new Date().toISOString() });
    }

    return Response.json({ error: "Not found" }, { status: 404 });
  },
});

console.log(chalk.bold.cyan(`\n=== FEASIFY API SERVER ===\n`));
console.log(`🌐 Server running at ${chalk.green(`http://localhost:${PORT}`)}`);
console.log(`📖 API docs at ${chalk.green(`http://localhost:${PORT}`)}\n`);
console.log(`Endpoints:`);
console.log(`  ${chalk.yellow("GET")}  /api/feasibility  - DCPR-2034 analysis`);
console.log(`  ${chalk.yellow("GET")}  /api/clearances    - Required clearances`);
console.log(`  ${chalk.yellow("GET")}  /api/cost          - Cost calculation`);
console.log(`  ${chalk.yellow("POST")} /api/analyze        - Full analysis\n`);