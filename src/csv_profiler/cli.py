"""
Command-line interface for CSV Profiler using Typer.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Fix Windows console encoding for Unicode support
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

from .io import read_csv_rows
from .profiling import profile_rows
from .render import render_markdown

app = typer.Typer(
    name="csv-profiler",
    help="📊 CSV Profiler - Analyze CSV files and generate detailed reports",
    add_completion=False
)
console = Console()


@app.command()
def profile(
    input_path: Path = typer.Argument(
        ...,
        help="Path to the CSV file to profile",
        exists=True,
        dir_okay=False,
        readable=True
    ),
    out_dir: Path = typer.Option(
        "outputs",
        "--out-dir", "-o",
        help="Output directory for reports"
    ),
    report_name: str = typer.Option(
        "report",
        "--name", "-n",
        help="Base name for report files"
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet", "-q",
        help="Suppress progress messages"
    )
):
    """
    Profile a CSV file and generate comprehensive reports.

    Generates JSON and Markdown reports with statistics and quality warnings.
    """
    if not quiet:
        console.print("\n[bold cyan]📊 CSV Profiler[/bold cyan]")
        console.print("=" * 60)
        console.print(f"[blue]Input file:[/blue] {input_path}")
        console.print(f"[blue]Output directory:[/blue] {out_dir}")
        console.print(f"[blue]Report name:[/blue] {report_name}")
        console.print()

    # Start timing
    start_time = time.perf_counter_ns()

    try:
        # Read CSV file
        if not quiet:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(description="Reading CSV file...", total=None)
                rows = read_csv_rows(input_path)
            console.print(f"[green]✓[/green] Read {len(rows):,} rows\n")
        else:
            rows = read_csv_rows(input_path)

        # Profile the data
        if not quiet:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(description="Profiling data...", total=None)
                report = profile_rows(rows)
            console.print(f"[green]✓[/green] Profiled {report['n_cols']} columns\n")
        else:
            report = profile_rows(rows)

        # Calculate timing
        end_time = time.perf_counter_ns()
        timing_ms = (end_time - start_time) / 1_000_000
        report["timing_ms"] = round(timing_ms, 2)

        # Create output directory
        out_dir.mkdir(parents=True, exist_ok=True)

        # Write JSON report
        json_path = out_dir / f"{report_name}.json"
        if not quiet:
            console.print(f"[yellow]💾[/yellow] Writing JSON report to {json_path}...")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        if not quiet:
            console.print(f"[green]✓[/green] JSON report saved\n")

        # Write Markdown report
        md_path = out_dir / f"{report_name}.md"
        if not quiet:
            console.print(f"[yellow]📝[/yellow] Writing Markdown report to {md_path}...")
        markdown = render_markdown(report)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        if not quiet:
            console.print(f"[green]✓[/green] Markdown report saved\n")

        # Summary
        if not quiet:
            console.print("=" * 60)
            console.print(f"[bold green]✅ Profiling complete![/bold green]")
            console.print(f"[cyan]⏱️  Processing time:[/cyan] {timing_ms:.2f} ms")
            console.print(f"[cyan]📁 Reports saved to:[/cyan] {out_dir.absolute()}")
            console.print("=" * 60 + "\n")

    except FileNotFoundError as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}", file=sys.stderr)
        raise typer.Exit(code=1)
    except ValueError as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}", file=sys.stderr)
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]❌ Unexpected error:[/bold red] {e}", file=sys.stderr)
        raise typer.Exit(code=1)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == '__main__':
    main()
