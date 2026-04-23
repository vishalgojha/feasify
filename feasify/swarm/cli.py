"""Swarm CLI command."""
import typer
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(name="swarm", help="Multi-agent Feasify Swarm analysis")
console = Console()


@app.command()
def analyze(
    cts_number: str = typer.Argument(..., help="CTS number to analyze"),
    zone: str = typer.Argument(..., help="Zone: island_city/suburbs/extended_suburbs/barc_area"),
    use: str = typer.Option("residential", help="Use type: residential/commercial/industrial"),
    road_width: float = typer.Option(12.0, help="Road width in meters"),
    plot_area: float = typer.Option(1000.0, help="Plot area in sq.m"),
    land_cost: float = typer.Option(0.0, help="Land cost in INR"),
    lat: float = typer.Option(0.0, help="Latitude for spatial checks"),
    lon: float = typer.Option(0.0, help="Longitude for spatial checks"),
    ward: str = typer.Option("", help="Ward designation"),
    height: float = typer.Option(0.0, help="Proposed building height in meters"),
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
    verbose: bool = typer.Option(False, "--verbose", help="Show agent details"),
):
    """
    Run multi-agent swarm analysis for project feasibility.
    
    Uses 5 agents: Planner, DCPR Expert, Spatial Risk, Cost Engineer, Reviewer.
    """
    from feasify.swarm import FeasifySwarm
    
    with console.status("[bold green]Running Feasify Swarm analysis...") as status:
        try:
            swarm = FeasifySwarm()
            status.update("[bold yellow]Running Spatial Risk check...")
            
            result = swarm.analyze(
                cts_number=cts_number,
                zone=zone,
                road_width_m=road_width,
                use=use,
                plot_area_sqm=plot_area,
                land_cost=land_cost,
                lat=lat,
                lon=lon,
                ward=ward,
                proposed_height_m=height,
            )
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            if json_output:
                console.print(json.dumps({"error": str(e)}))
            raise typer.Exit(1)
    
    if json_output:
        console.print(json.dumps(result, indent=2, default=str))
        return
    
    _display_report(result, verbose)


def _display_report(result: dict, verbose: bool):
    """Display the feasibility report."""
    
    verdict = result.get("verdict", "UNKNOWN")
    verdict_color = {
        "VIABLE": "green",
        "MARGINAL": "yellow",
        "BLOCKED": "red",
        "NEEDS_REVISION": "yellow",
    }.get(verdict, "white")
    
    console.print(Panel.fit(
        f"[bold {verdict_color}]VERDICT: {verdict}[/bold {verdict_color}]",
        title="Feasify Swarm Report",
        border_style=verdict_color
    ))
    
    console.print(f"\n[bold cyan]CTS Number:[/bold cyan] {result.get('cts_number')}")
    
    fsi = result.get("fsi_summary", {})
    if fsi:
        table = Table(title="FSI Analysis")
        table.add_column("Component", style="cyan")
        table.add_column("FSI", style="green", justify="right")
        
        table.add_row("Base FSI", f"{fsi.get('base', 0):.2f}")
        table.add_row("Premium FSI", f"{fsi.get('premium', 0):.2f}")
        table.add_row("TDR FSI", f"{fsi.get('tdr', 0):.2f}")
        table.add_row("Fungible FSI", f"{fsi.get('fungible', 0):.2f}")
        table.add_row("[bold]Total FSI[/bold]", f"[bold]{fsi.get('total', 0):.2f}[/bold]")
        
        console.print(table)
        console.print(f"\nMax Buildable: {fsi.get('max_buildable_sqm', 0):,.0f} sq.m")
        console.print(f"Saleable Area: {fsi.get('saleable_sqm', 0):,.0f} sq.m")
    
    cost = result.get("cost_summary", {})
    if cost:
        console.print(f"\n[bold]Cost Summary:[/bold]")
        console.print(f"  Total: ₹{cost.get('total', 0):,.0f}")
        console.print(f"  Cost/sq.ft: ₹{cost.get('cost_per_sqft', 0):,.0f}")
    
    ratios = result.get("feasibility_ratios", {})
    if ratios:
        console.print(f"\n[bold]Feasibility Ratios:[/bold]")
        console.print(f"  Gross Margin: {ratios.get('gross_margin_pct', 0):.1f}%")
        console.print(f"  ROI: {ratios.get('roi_pct', 0):.1f}%")
        console.print(f"  Breakeven Rate: ₹{ratios.get('breakeven_rate_sqft', 0):,.0f}/sqft")
    
    blockers = result.get('blockers', [])
    if blockers:
        console.print("\n[bold red]BLOCKERS:[/bold red]")
        for b in blockers:
            console.print(f"  • {b.get('type')}: {b.get('description')}")
            console.print(f"    Action: {b.get('recommended_action')}")
    
    risks = result.get('risk_manifest', [])
    if risks and verbose:
        console.print("\n[bold yellow]Risk Manifest:[/bold yellow]")
        for r in risks:
            sev = r.get('severity', 'LOW')
            sev_color = {"BLOCKER": "red", "HIGH": "orange", "MEDIUM": "yellow", "LOW": "green"}.get(sev, "white")
            console.print(f"  [{sev_color}]{sev}[/{sev_color}] {r.get('check')}: {r.get('description')}")
    
    flags = result.get('reviewer_flags', [])
    if flags and verbose:
        console.print("\n[bold yellow]Reviewer Flags:[/bold yellow]")
        for f in flags:
            console.print(f"  • [{f.get('severity')}] {f.get('field')}: {f.get('description')}")
            console.print(f"    Fix: {f.get('recommended_fix')}")
    
    can_proceed = result.get('can_proceed', False)
    if can_proceed:
        console.print("\n[bold green]✓ Project can proceed with development.[/bold green]")
    else:
        console.print("\n[bold red]✗ Project requires further review or has blocking issues.[/bold red]")


if __name__ == "__main__":
    app()