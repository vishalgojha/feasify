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

if __name__ == "__main__":
    app()
