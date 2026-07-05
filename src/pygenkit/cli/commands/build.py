from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import typer


def build_cmd(
    clean: bool = typer.Option(True, "--clean", help="Clean before build"),
) -> None:
    project_dir = Path.cwd()
    pyproject = project_dir / "pyproject.toml"
    if not pyproject.exists():
        typer.echo("No pyproject.toml found. Are you in a Python project?")
        raise typer.Exit(code=1)

    if clean:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "build"],
            capture_output=True,
            timeout=60,
        )

    result = subprocess.run(
        [sys.executable, "-m", "build", "--sdist", "--wheel", str(project_dir)],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        typer.echo(f"Build failed:\n{result.stderr}")
        raise typer.Exit(code=1)

    dist_dir = project_dir / "dist"
    if dist_dir.exists():
        for f in sorted(dist_dir.iterdir()):
            typer.echo(f"  {f.name}")
    typer.echo("Build complete.")
