from __future__ import annotations

from pathlib import Path

import typer


def release_check_cmd(
    config: Path = typer.Option("pygenesis.toml", "--config", "-c", help="Config file"),  # noqa: B008
) -> None:
    """Verify that the project is ready for release."""
    if not config.exists():
        typer.echo(f"  Config not found: {config}")
        typer.echo("  Run: pygenesis init <name>")
        raise typer.Exit(code=1)

    typer.echo("  [release-check] Readiness check coming in Stage 5.")
