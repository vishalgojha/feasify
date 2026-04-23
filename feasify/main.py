"""Feasify CLI entry point."""
import typer
from rich.console import Console
from rich.table import Table
from feasify.config import settings

app = typer.Typer(name="feasify", help="Real estate cost estimation tool")
console = Console()

@app.command()
def estimate(
    area: float = typer.Argument(..., help="Plot area in sq.ft."),
    zone: str = typer.Argument(..., help="Zoning type (residential/commercial/industrial)"),
    floors: int = typer.Option(1, help="Number of floors")
):
    """Estimate construction cost for a plot."""
    from feasify.core.estimator import estimate_cost
    from feasify.utils.rates import get_current_rates
    
    rates = get_current_rates()
    result = estimate_cost(area, zone, floors, rates)
    
    table = Table(title="Cost Estimate")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in result.items():
        table.add_row(key, str(value))
    
    console.print(table)

@app.command()
def analyze(
    cts_number: str = typer.Argument(..., help="CTS number to analyze"),
    use_type: str = typer.Argument(..., help="Proposed use: residential/commercial/industrial"),
    land_cost: float = typer.Option(None, help="Land cost in ₹ (optional)"),
    finish: str = typer.Option("standard", help="Construction grade: basic/standard/premium"),
    output_dir: str = typer.Option("data/reports", help="Output directory for reports"),
    pdf: bool = typer.Option(False, help="Generate PDF report"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON for CLI integration")
):
    """Run AI-powered project feasibility analysis using Groq."""
    from feasify.agents import run_agent
    from feasify.agents.project_intelligence import run_agent as run_agent_direct
    
    try:
        report = run_agent_direct(
            cts_number=cts_number,
            use_type=use_type,
            land_cost=land_cost,
            finish_grade=finish,
            output_dir=output_dir,
            generate_pdf=pdf
        )
        
        if json_output:
            # Output JSON for Bun CLI
            import json
            console.print(json.dumps({
                "cts_number": report.cts_number,
                "plot_details": report.plot_details,
                "spatial_context": report.spatial_context,
                "design": report.design,
                "clearances": report.clearances,
                "cost_stack": report.cost_stack,
                "recommendation": report.recommendation,
                "risks": report.risks,
            }, default=str, indent=2))
        else:
            console.print("\n[bold green]✓ Analysis complete![/bold green]")
    except Exception as e:
        if json_output:
            import json
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"\n[bold red]Error: {e}[/bold red]")
        raise typer.Exit(1)

@app.command()
def fetch(
    plot_id: str = typer.Argument(..., help="Plot ID or CTS number"),
    source: str = typer.Option("mcgm", help="Data source (mcgm/dp)")
):
    """Fetch plot details from municipal sources."""
    from feasify.core.fetcher import fetch_plot_data
    
    with console.status(f"Fetching data for {plot_id}..."):
        data = fetch_plot_data(plot_id, source)
    
    console.print_json(data=data)

@app.command()
def version():
    """Show Feasify version."""
    from feasify import __version__
    console.print(f"Feasify version: {__version__}")


@app.command()
def swarm(
    cts_number: str = typer.Argument(..., help="CTS number to analyze"),
    zone: str = typer.Argument(..., help="Zone: island_city/suburbs/extended_suburbs/barc_area"),
    use: str = typer.Option("residential", help="Use type: residential/commercial/industrial"),
    road_width: float = typer.Option(12.0, help="Road width in meters"),
    plot_area: float = typer.Option(1000.0, help="Plot area in sq.m"),
    land_cost: float = typer.Option(0.0, help="Land cost in INR"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
):
    """Run multi-agent swarm analysis (Planner, DCPR, Spatial, Cost, Reviewer)."""
    from feasify.swarm import FeasifySwarm
    
    with console.status("[bold green]Running Feasify Swarm..."):
        try:
            swarm = FeasifySwarm()
            result = swarm.analyze(
                cts_number=cts_number,
                zone=zone,
                road_width_m=road_width,
                use=use,
                plot_area_sqm=plot_area,
                land_cost=land_cost,
            )
        except Exception as e:
            if json_output:
                console.print(json.dumps({"error": str(e)}))
            else:
                console.print(f"[bold red]Error:[/bold red] {e}")
            raise typer.Exit(1)
    
    if json_output:
        import json
        console.print(json.dumps(result, indent=2, default=str))
        return
    
    from rich.panel import Panel
    
    verdict = result.get("verdict", "UNKNOWN")
    verdict_color = {"VIABLE": "green", "MARGINAL": "yellow", "BLOCKED": "red"}.get(verdict, "white")
    
    console.print(Panel.fit(
        f"[bold {verdict_color}]VERDICT: {verdict}[/bold {verdict_color}]",
        title="Feasify Swarm Report",
        border_style=verdict_color
    ))
    
    fsi = result.get("fsi_summary", {})
    if fsi:
        table = Table(title="FSI Analysis")
        table.add_column("Component", style="cyan")
        table.add_column("FSI", style="green", justify="right")
        table.add_row("Base", f"{fsi.get('base', 0):.2f}")
        table.add_row("Premium", f"{fsi.get('premium', 0):.2f}")
        table.add_row("TDR", f"{fsi.get('tdr', 0):.2f}")
        table.add_row("Total", f"{fsi.get('total', 0):.2f}")
        console.print(table)
        console.print(f"Max Buildable: {fsi.get('max_buildable_sqm', 0):,.0f} sq.m")
    
    cost = result.get("cost_summary", {})
    if cost:
        console.print(f"\nTotal Cost: ₹{cost.get('total', 0):,.0f}")
        console.print(f"Cost/sq.ft: ₹{cost.get('cost_per_sqft', 0):,.0f}")
    
    if result.get('can_proceed'):
        console.print("\n[bold green]✓ Project can proceed[/bold green]")
    else:
        console.print("\n[bold red]✗ Project has issues[/bold red]")


# Browser automation commands
@app.command()
def browser_start():
    """Start Camofox browser server."""
    from feasify.browser.client import CamofoxClient
    client = CamofoxClient()
    result = client.start_browser()
    console.print_json(data=result)

@app.command()
def browser_search(
    query: str = typer.Argument(..., help="Search query"),
    engine: str = typer.Option("google", help="Search engine (google/youtube/amazon/reddit)")
):
    """Search using Camofox browser."""
    from feasify.browser.tools import google_search, youtube_search, amazon_search, reddit_search
    
    with console.status(f"Searching {engine} for: {query}"):
        if engine == "google":
            result = google_search(query)
        elif engine == "youtube":
            result = youtube_search(query)
        elif engine == "amazon":
            result = amazon_search(query)
        elif engine == "reddit":
            result = reddit_search(query)
        else:
            console.print(f"[red]Unknown search engine: {engine}[/red]")
            raise typer.Exit(1)
    
    console.print_json(data=result)

@app.command()
def browser_screenshot(
    url: str = typer.Argument(..., help="URL to screenshot"),
    output: str = typer.Option("screenshot.png", help="Output file path")
):
    """Take a screenshot of a URL using Camofox."""
    import base64
    from pathlib import Path
    from feasify.browser.tools import browser_create_tab, browser_screenshot as screenshot_tool
    
    tab = browser_create_tab(url)
    screenshot_data = screenshot_tool(tab["tab_id"])
    
    if "screenshot" in screenshot_data:
        img_data = base64.b64decode(screenshot_data["screenshot"])
        Path(output).write_bytes(img_data)
        console.print(f"[green]Screenshot saved to: {output}[/green]")
    else:
        console.print("[red]Failed to capture screenshot[/red]")
    
    from feasify.browser.tools import browser_close_tab
    browser_close_tab(tab["tab_id"])


@app.command()
def feasibility(
    plot_area: float = typer.Argument(..., help="Plot area in sq.m"),
    zone: str = typer.Argument(..., help="Zone: island_city/suburbs/extended_suburbs/barc_area/crz_affected"),
    use: str = typer.Argument(..., help="Use: residential/commercial/industrial"),
    road_width: float = typer.Argument(..., help="Road width in meters"),
    floors: int = typer.Argument(..., help="Number of floors (G=1)"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON for CLI integration")
):
    """Run DCPR-2034 feasibility analysis."""
    from feasify.knowledge.dcpr import (
        MumbaiZone, BuildingUse, calculate_feasibility, FeasibilityInput
    )
    
    zone_map = {
        "island_city": MumbaiZone.ISLAND_CITY,
        "suburbs": MumbaiZone.SUBURBS,
        "extended_suburbs": MumbaiZone.EXTENDED_SUBURBS,
        "barc_area": MumbaiZone.BARC_AREA,
        "crz_affected": MumbaiZone.CRZ_AFFECTED,
    }
    
    use_map = {
        "residential": BuildingUse.RESIDENTIAL,
        "commercial": BuildingUse.COMMERCIAL,
        "industrial": BuildingUse.INDUSTRIAL,
    }
    
    zone_enum = zone_map.get(zone.lower())
    use_enum = use_map.get(use.lower())
    
    if not zone_enum:
        console.print(f"[red]Invalid zone: {zone}[/red]")
        raise typer.Exit(1)
    if not use_enum:
        console.print(f"[red]Invalid use: {use}[/red]")
        raise typer.Exit(1)
    
    inp = FeasibilityInput(
        plot_area_sqm=plot_area,
        zone=zone_enum,
        use=use_enum,
        road_width_m=road_width,
        floors=floors,
    )
    
    result = calculate_feasibility(inp)
    
    if json_output:
        import json
        console.print(json.dumps({
            "zonal_basic_fsi": result.zonal_basic_fsi,
            "max_permissible_fsi": result.max_permissible_fsi,
            "permissible_bua_sqm": result.permissible_bua_sqm,
            "permissible_bua_sqft": result.permissible_bua_sqft,
            "total_max_bua_sqm": result.total_max_bua_sqm,
            "approx_height_m": result.approx_height_m,
            "floors_feasible": result.floors_feasible,
            "setback_side_rear_m": result.setback_side_rear_m,
            "setback_dead_wall_m": result.setback_dead_wall_m,
            "high_rise": result.high_rise,
            "fire_noc_required": result.fire_noc_required,
            "parking_spaces_required": result.parking_spaces_required,
            "max_tenements": result.max_tenements,
            "warnings": result.warnings or [],
        }, default=str, indent=2))
        return
    
    table = Table(title="DCPR-2034 Feasibility Analysis")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Zonal Basic FSI", str(result.zonal_basic_fsi))
    table.add_row("Max Permissible FSI", str(result.max_permissible_fsi))
    table.add_row("Permissible BUA (sqm)", str(result.permissible_bua_sqm))
    table.add_row("Permissible BUA (sqft)", str(result.permissible_bua_sqft))
    table.add_row("Total Max BUA (sqm)", str(result.total_max_bua_sqm))
    table.add_row("Building Height (m)", str(result.approx_height_m))
    table.add_row("Floors Feasible", str(result.floors_feasible))
    table.add_row("Setback Side/Rear (m)", str(result.setback_side_rear_m))
    table.add_row("Dead Wall Setback (m)", str(result.setback_dead_wall_m))
    table.add_row("High-Rise", str(result.high_rise))
    table.add_row("Fire NOC Required", str(result.fire_noc_required))
    table.add_row("Parking Spaces", str(result.parking_spaces_required))
    table.add_row("Max Tenements", str(result.max_tenements))
    
    console.print(table)
    
    if result.warnings:
        console.print("\n[yellow]⚠ WARNINGS:[/yellow]")
        for w in result.warnings:
            console.print(f"  • {w}")


@app.command()
def cost(
    bua_sqft: float = typer.Argument(..., help="Built-up area in sq.ft."),
    zone: str = typer.Argument(..., help="Zone type: island_city/suburbs/extended_suburbs/barc_area"),
    floors: int = typer.Argument(..., help="Number of floors"),
    use: str = typer.Argument("residential", help="Use type: residential/commercial"),
    finish: str = typer.Option("standard", help="Finish grade: basic/standard/premium"),
    land_cost: float = typer.Option(0.0, help="Land cost in ₹"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON for CLI integration")
):
    """Calculate complete project cost stack."""
    from feasify.agents.cost_engine import build_cost_stack
    
    result = build_cost_stack(
        bua_sqft=bua_sqft,
        zone_type=zone,
        num_floors=floors,
        base_construction_cost=0.0,
        clearance_fees=0.0,
        land_cost=land_cost,
        finish_grade=finish,
        use=use,
        use_live_rates=True
    )
    
    if json_output:
        import json
        console.print(json.dumps(result, default=str, indent=2))
        return
    
    table = Table(title="Cost Stack")
    table.add_column("Category", style="cyan")
    table.add_column("Amount (₹)", style="green", justify="right")
    
    table.add_row("Land Cost", f"₹{result['land_cost']:,.0f}")
    table.add_row("Construction", f"₹{result['construction']['total_construction']:,.0f}")
    table.add_row("Government Premiums", f"₹{result['government_premiums']['total_government_premiums']:,.0f}")
    table.add_row("Professional Fees", f"₹{result['professional_fees']['total_professional_fees']:,.0f}")
    table.add_row("Statutory", f"₹{result['statutory']['total_statutory']:,.0f}")
    table.add_row("Financing", f"₹{result['financing']['financing_cost']:,.0f}")
    table.add_row("Grand Total", f"₹{result['grand_total']:,.0f}")
    
    console.print(table)
    console.print(f"\nCost per sq.ft: ₹{result['cost_per_sqft']:,.0f}")


@app.command()
def clearances(
    height_m: float = typer.Argument(..., help="Building height in meters"),
    bua_sqm: float = typer.Argument(..., help="Built-up area in sq.m"),
    plot_area_sqm: float = typer.Argument(..., help="Plot area in sq.m"),
    use: str = typer.Argument("residential", help="Use type: residential/commercial"),
    zone: str = typer.Option("suburbs", help="Zone type"),
    csia_km: float = typer.Option(999.0, help="Distance to CSIA airport in km"),
    coast_km: float = typer.Option(999.0, help="Distance to coast in km"),
    ward: str = typer.Option("", help="Ward designation"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON for CLI integration")
):
    """Calculate required clearances for a project."""
    from feasify.agents.clearance_engine import resolve_clearances, calculate_critical_path
    
    clearances = resolve_clearances(
        height_m=height_m,
        bua_sqm=bua_sqm,
        plot_area_sqm=plot_area_sqm,
        distance_to_csia_km=csia_km,
        distance_to_coast_km=coast_km,
        ward=ward,
        use=use
    )
    
    critical_path = calculate_critical_path(clearances)
    
    if json_output:
        import json
        console.print(json.dumps({
            "clearances": clearances,
            "critical_path_days": critical_path["total_days"],
            "critical_sequence": critical_path["critical_sequence"],
            "bottleneck": critical_path["bottleneck"],
        }, default=str, indent=2))
        return
    
    table = Table(title="Required Clearances")
    table.add_column("Clearance", style="cyan")
    table.add_column("Timeline", style="yellow", justify="right")
    table.add_column("Fee (₹)", style="green", justify="right")
    table.add_column("Risk", style="magenta")
    
    for c in clearances:
        risk = c.get("risk_level", "medium")
        risk_color = "red" if risk == "high" else "yellow" if risk == "medium" else "green"
        table.add_row(
            c.get("name", "Unknown"),
            f"{c.get('timeline_days', 0)} days",
            f"₹{c.get('fee', 0):,.0f}",
            f"[{risk_color}]{risk}[/{risk_color}]"
        )
    
    console.print(table)
    console.print(f"\n[bold]Critical Path:[/bold] {critical_path['total_days']} days")


if __name__ == "__main__":
    app()
