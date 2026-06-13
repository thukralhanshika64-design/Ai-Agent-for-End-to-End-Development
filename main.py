"""
AI Agent for End-to-End App Development
========================================

Main entry point. Run this script to start the multi-agent pipeline.

Usage:
    python main.py                          # Interactive mode (prompts for idea)
    python main.py "Your app idea here"     # Direct mode (pass idea as argument)

Prerequisites:
    1. Install Ollama: https://ollama.com
    2. Pull a model:   ollama pull llama3
    3. Install deps:   pip install -r requirements.txt
"""

import sys
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from orchestrator import build_app

console = Console()

# ─── Banner ──────────────────────────────────────────────
BANNER = r"""
   _    ___    ___                 __     ____        _ __   __
  / \  |_ _|  / _ \  ___  _   _  / _|   | __ ) _   _(_) | __\ \
 / _ \  | |  | | | |/ _ \| | | || |_    |  _ \| | | | | |/ __| |
/ ___ \ | |  | |_| |  __/| |_| ||  _|   | |_) | |_| | | | (__| |
/_/   \_\___|  \___/ \___| \__,_||_|     |____/ \__,_|_|_|\___| |
                                                             /_/
"""


def main():
    """Main entry point for the AI Agent pipeline."""
    console.print(f"[bold bright_cyan]{BANNER}[/bold bright_cyan]")
    console.print(Panel(
        "[bold white]Multi-Agent System for End-to-End Application Development[/bold white]\n"
        "[dim]Planner → Developer → Tester → Reviewer[/dim]\n\n"
        "[dim italic]Powered by Ollama (local LLM) + LangChain + Rich[/dim italic]",
        border_style="bright_cyan",
        padding=(1, 3),
    ))

    # Get the app idea
    if len(sys.argv) > 1:
        # Idea provided as command-line argument
        app_idea = " ".join(sys.argv[1:])
        console.print(f"\n[bold]App Idea:[/bold] {app_idea}\n")
    else:
        # Interactive prompt
        console.print()
        app_idea = Prompt.ask(
            "[bold bright_cyan]🚀 Describe the app you want to build[/bold bright_cyan]",
            default="Build a simple REST API for a todo app using FastAPI",
        )

    if not app_idea.strip():
        console.print("[bold red]❌ No app idea provided. Exiting.[/bold red]")
        sys.exit(1)

    # Run the pipeline
    try:
        final_code = build_app(app_idea)
        console.print("\n[bold bright_green]🎉 Done! Your application has been generated.[/bold bright_green]\n")
    except KeyboardInterrupt:
        console.print("\n[bold yellow]⚠ Pipeline interrupted by user.[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]❌ Pipeline failed: {e}[/bold red]")
        console.print("[dim]Make sure Ollama is running: `ollama serve`[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
