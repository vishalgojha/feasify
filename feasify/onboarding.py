#!/usr/bin/env python3
"""Feasify Welcome & Setup - Interactive onboarding for non-technical users."""

import os
import sys
import json
import subprocess
import webbrowser
from pathlib import Path

# Check rich
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
except ImportError:
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "rich", "-q"], check=True)
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm

console = Console()


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def check_keys():
    return {
        "GOOGLE_API_KEY": bool(os.getenv("GOOGLE_API_KEY")),
        "GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY")),
    }


def main():
    clear()
    
    console.print(Panel.fit(
        """
        [bold cyan]🏠 Welcome to Feasify![/bold cyan]
        
        Your AI-powered real estate feasibility assistant for Mumbai projects.
        """,
        border_style="cyan",
        padding=(2, 4),
    ))
    console.print()
    
    # Check existing keys
    keys = check_keys()
    
    if keys["GOOGLE_API_KEY"] and keys["GROQ_API_KEY"]:
        console.print("[green]✓ API keys configured[/green]")
        console.print("  • Google AI (Gemini)")
        console.print("  • Groq")
    elif keys["GOOGLE_API_KEY"]:
        console.print("[green]✓ Google AI configured[/green]")
    elif keys["GROQ_API_KEY"]:
        console.print("[green]✓ Groq configured[/green]")
    else:
        console.print("[yellow]⚠ No API keys found[/yellow]")
        console.print()
        console.print("[cyan]To set up, add your API key to .env file:[/cyan]")
        console.print()
        console.print("  GOOGLE_API_KEY=your_key_here")
        console.print()
        console.print("[dim]Get free key at: https://aistudio.google.com/app/apikey[/dim]")
    
    console.print()
    
    # Launch Studio
    if Confirm.ask("Launch Feasify Studio?", default=True):
        console.print("\n[yellow]🚀 Starting Feasify Studio...[/yellow]")
        console.print("[dim]Open http://localhost:8501 in your browser[/dim]\n")
        
        studio_path = Path(__file__).parent / "studio" / "app.py"
        
        if studio_path.exists():
            webbrowser.open("http://localhost:8501")
            subprocess.Popen([
                sys.executable, "-m", "streamlit", "run",
                str(studio_path),
                "--browser.gatherUsageStats", "false",
                "--server.headless", "true",
                "--server.port", "8501"
            ])
        else:
            console.print("[red]Studio not found![/red]")
            console.print("[dim]Run: pip install streamlit[/dim]")


if __name__ == "__main__":
    main()