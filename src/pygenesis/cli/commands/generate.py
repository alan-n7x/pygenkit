from __future__ import annotations

from pathlib import Path

import typer

from pygenesis.generators.orchestrator import generate_all
from pygenesis.models.config import PyGenesisConfig


def generate_cmd(
    config: Path = typer.Option("pygenesis.toml", "--config", "-c", help="Config file"),  # noqa: B008
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show changes without writing"),  # noqa: B008
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),  # noqa: B008
) -> None:
    if not config.exists():
        typer.echo(f"  Config not found: {config}")
        typer.echo("  Run: pygenesis init <name>")
        raise typer.Exit(code=1)

    cfg = PyGenesisConfig.load(config)
    results = generate_all(cfg, force=force)

    if dry_run:
        _report_dry(results)
        return

    total = sum(len(v) for v in results.values())
    if total == 0:
        typer.echo("  Nothing to generate (enable docker/deploy in config, or files already exist).")  # noqa: E501
        typer.echo("  Use --force to overwrite existing files.")
        return

    typer.echo(f"  Generated {total} file(s):")
    cwd = Path.cwd().resolve()
    for category, paths in results.items():
        for p in paths:
            rel = p.resolve().relative_to(cwd)
            typer.echo(f"    \u2713 {category}: {rel}")

    typer.echo("")
    typer.echo("  Done.")


def _report_dry(results: dict[str, list[Path]]) -> None:
    total = sum(len(v) for v in results.values())
    typer.echo(f"  Would generate {total} file(s):")
    for category, paths in results.items():
        for p in paths:
            typer.echo(f"    {category}: {p}")
