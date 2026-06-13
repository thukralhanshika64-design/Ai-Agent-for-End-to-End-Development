"""
Orchestrator — Controls the end-to-end pipeline flow.

Executes each agent in sequence:
  Planner → Developer → Tester → Reviewer

Displays progress with rich formatting and saves artifacts to disk.
"""

import os
import time
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule

from agents import planner_agent, developer_agent, tester_agent, reviewer_agent
from config import (
    ENABLE_PLANNING,
    ENABLE_DEVELOPMENT,
    ENABLE_TESTING,
    ENABLE_REVIEW,
    SAVE_OUTPUT_TO_FILE,
    OUTPUT_DIR,
)

console = Console()


def _save_artifact(filename: str, content: str, run_dir: str) -> str:
    """Save a pipeline artifact to the output directory."""
    filepath = os.path.join(run_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def _run_stage(stage_name: str, emoji: str, color: str, agent_fn, *args) -> str:
    """
    Execute a single pipeline stage with progress display.

    Args:
        stage_name: Human-readable name of the stage.
        emoji: Emoji to display.
        color: Rich color for the stage header.
        agent_fn: The agent function to call.
        *args: Arguments to pass to the agent function.

    Returns:
        The agent's response string.
    """
    console.print()
    console.print(Rule(f"[bold {color}]{emoji}  {stage_name}[/bold {color}]"))
    console.print()

    start = time.time()

    with Progress(
        SpinnerColumn(style=color),
        TextColumn(f"[{color}]{{task.description}}[/{color}]"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"Running {stage_name}...", total=None)
        result = agent_fn(*args)
        progress.update(task, completed=True)

    elapsed = time.time() - start

    console.print(Panel(
        Markdown(result),
        title=f"[bold {color}]{stage_name} Output[/bold {color}]",
        border_style=color,
        padding=(1, 2),
    ))
    console.print(f"  [dim]⏱ Completed in {elapsed:.1f}s[/dim]")

    return result


def build_app(app_idea: str) -> str:
    """
    Orchestrate the full AI agent pipeline.

    Takes an app idea through planning, development, testing,
    and review stages to produce production-ready code.

    Args:
        app_idea: A natural-language description of the app to build.

    Returns:
        The final reviewed and improved code.
    """
    # Create output directory for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(OUTPUT_DIR, f"run_{timestamp}")

    if SAVE_OUTPUT_TO_FILE:
        os.makedirs(run_dir, exist_ok=True)

    # ── Header ──────────────────────────────────
    console.print()
    console.print(Panel(
        f"[bold white]{app_idea}[/bold white]",
        title="[bold bright_cyan]🤖 AI Agent — End-to-End App Builder[/bold bright_cyan]",
        subtitle="[dim]Powered by Ollama + LangChain[/dim]",
        border_style="bright_cyan",
        padding=(1, 3),
    ))

    pipeline_start = time.time()
    plan = ""
    code = ""
    test_report = ""
    final_code = ""

    # ── Stage 1: Planning ───────────────────────
    if ENABLE_PLANNING:
        plan = _run_stage(
            "Stage 1 · Planning", "📋", "cyan",
            planner_agent, app_idea,
        )
        if SAVE_OUTPUT_TO_FILE:
            _save_artifact("01_plan.md", plan, run_dir)
    else:
        console.print("[dim]⏭ Planning stage skipped[/dim]")
        plan = app_idea  # Pass raw idea to developer if planning is skipped

    # ── Stage 2: Development ────────────────────
    if ENABLE_DEVELOPMENT:
        code = _run_stage(
            "Stage 2 · Development", "💻", "green",
            developer_agent, plan,
        )
        if SAVE_OUTPUT_TO_FILE:
            _save_artifact("02_code.py", code, run_dir)
    else:
        console.print("[dim]⏭ Development stage skipped[/dim]")

    # ── Stage 3: Testing ────────────────────────
    if ENABLE_TESTING and code:
        test_report = _run_stage(
            "Stage 3 · Testing", "🧪", "yellow",
            tester_agent, code,
        )
        if SAVE_OUTPUT_TO_FILE:
            _save_artifact("03_test_report.md", test_report, run_dir)
    else:
        console.print("[dim]⏭ Testing stage skipped[/dim]")

    # ── Stage 4: Code Review ────────────────────
    if ENABLE_REVIEW and code:
        final_code = _run_stage(
            "Stage 4 · Code Review", "🔍", "magenta",
            reviewer_agent, code, test_report,
        )
        if SAVE_OUTPUT_TO_FILE:
            _save_artifact("04_final_code.py", final_code, run_dir)
    else:
        console.print("[dim]⏭ Review stage skipped[/dim]")
        final_code = code

    # ── Summary ─────────────────────────────────
    total_time = time.time() - pipeline_start

    console.print()
    console.print(Rule("[bold bright_cyan]✅  Pipeline Complete[/bold bright_cyan]"))
    console.print()

    summary_lines = [
        f"  [bold]Total time:[/bold]  {total_time:.1f}s",
        f"  [bold]Stages run:[/bold]  {sum([ENABLE_PLANNING, ENABLE_DEVELOPMENT, ENABLE_TESTING, ENABLE_REVIEW])}/4",
    ]
    if SAVE_OUTPUT_TO_FILE:
        abs_path = os.path.abspath(run_dir)
        summary_lines.append(f"  [bold]Artifacts:[/bold]   {abs_path}")

    console.print(Panel(
        "\n".join(summary_lines),
        title="[bold bright_cyan]📊 Run Summary[/bold bright_cyan]",
        border_style="bright_cyan",
        padding=(1, 2),
    ))

    return final_code
