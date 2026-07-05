from __future__ import annotations

from pathlib import Path

import typer

from pygenkit.inspector.api import inspect_project


def _fmt(val: object) -> str:
    if val is None:
        return "—"
    return str(val)


def inspect_cmd() -> None:
    """Analyze project structure, versions, and metadata."""
    project_dir = Path.cwd()

    typer.echo(f"  Inspecting {project_dir}")
    typer.echo("")

    result = inspect_project(project_dir)

    typer.echo(f"  Project:       {_fmt(result.name)}")
    typer.echo(f"  Version:       {_fmt(result.version)}")
    typer.echo(f"  Module:        {_fmt(result.module)}")
    backend = result.build_backend
    typer.echo(f"  Build backend: {_fmt(backend.name if backend else None)}")
    typer.echo(f"  Python req:    {_fmt(result.python_requires)}")
    typer.echo(f"  License:       {_fmt(result.license_type)}")
    typer.echo(f"  Tests:         {'yes' if result.has_tests else 'no'}")
    typer.echo(f"  Debian:        {'yes' if result.has_debian.present else 'no'}")
    typer.echo(f"  GitHub:        {_fmt(result.github_remote)}")
    typer.echo("")

    if result.versions.issues:
        typer.echo("  Version issues:")
        for issue in result.versions.issues:
            typer.echo(f"    \u2717 {issue}")

    if result.warnings:
        typer.echo("  Warnings:")
        for w in result.warnings:
            typer.echo(f"    ! {w}")

    if result.errors:
        typer.echo("  Errors:")
        for e in result.errors:
            typer.echo(f"    \u2717 {e}")
        raise typer.Exit(code=1)

    typer.echo("")
    if result.versions.consistent:
        typer.echo("  Versions: consistent")
    else:
        typer.echo("  Versions: inconsistent")
        raise typer.Exit(code=1)
