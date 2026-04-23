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

if __name__ == "__main__":
    app()
