from __future__ import annotations

from pathlib import Path

import typer

from pygenkit.config.loader import ConfigLoader
from pygenkit.services.release import ReleaseService


def release_cmd(
    config: Path = typer.Option("pygenkit.yaml", "--config", "-c", help="Config file"),  # noqa: B008
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Print actions without executing"),  # noqa: B008
    bump: str = typer.Option("patch", "--bump", help="Version bump: patch, minor, major"),  # noqa: B008
) -> None:
    config_path = Path(config)
    if not config_path.exists():
        typer.echo(f"Config file not found: {config_path}")
        raise typer.Exit(code=1)

    proj_config = ConfigLoader.load(config_path)
    service = ReleaseService(proj_config)

    if dry_run:
        service.dry_run(bump)
    else:
        result = service.run(bump)
        typer.echo(f"Tag created: {result['tag']}")
        typer.echo(f"Version: {result['version']}")
        if result.get("pushed"):
            typer.echo("Changes pushed to remote.")
            msg = "GitHub Actions will handle PyPI publish, GitHub Release, and Launchpad upload."
            typer.echo(msg)
