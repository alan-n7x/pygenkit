from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import typer


def publish_cmd(
    repository: str = typer.Option("pypi", "--repository", "-r", help="PyPI repository"),  # noqa: B008
    dist_dir: Path = typer.Option("dist", "--dist", help="Dist directory"),  # noqa: B008
) -> None:
    dist_path = Path(dist_dir)
    if not dist_path.is_dir() or not list(dist_path.glob("*.whl")):
        typer.echo("No distribution files found. Run 'pygenkit build' first.")
        raise typer.Exit(code=1)

    result = subprocess.run(
        [sys.executable, "-m", "twine", "upload", "--repository", repository, f"{dist_path}/*"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        typer.echo(f"Publish failed:\n{result.stderr}")
        raise typer.Exit(code=1)

    typer.echo("Published to PyPI successfully.")
