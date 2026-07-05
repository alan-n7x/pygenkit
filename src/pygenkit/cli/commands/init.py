from __future__ import annotations

from pathlib import Path

import typer

from pygenkit.models.config import PyGenKitConfig


def init_cmd(
    name: str = typer.Argument(..., help="Project name"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config"),  # noqa: B008
) -> None:
    """Create pygenkit.toml in the current directory."""
    config_path = Path("pygenkit.toml").resolve()
    if config_path.exists() and not force:
        typer.echo("  pygenkit.toml already exists. Use --force to overwrite.")
        raise typer.Exit(code=1)

    content = PyGenKitConfig.generate_default(name)
    config_path.write_text(content, encoding="utf-8")
    typer.echo(f"  Created {config_path}")
    typer.echo("  Edit it with your project info, then run: pygenkit inspect")
