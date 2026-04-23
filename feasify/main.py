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
    pdf: bool = typer.Option(False, help="Generate PDF report")
):
    """Run AI-powered project feasibility analysis using Claude."""
    from feasify.agents import run_agent
    from feasify.agents.project_intelligence import run_agent as run_agent_direct
    
    with console.status("[bold green]Running Project Intelligence Agent with Claude..."):
        try:
            report = run_agent_direct(
                cts_number=cts_number,
                use_type=use_type,
                land_cost=land_cost,
                finish_grade=finish,
                output_dir=output_dir,
                generate_pdf=pdf
            )
            console.print("\n[bold green]✓ Analysis complete![/bold green]")
        except Exception as e:
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

if __name__ == "__main__":
    app()
