from __future__ import annotations

import typer

from pygenesis.validators.api import has_errors, validate_project


def validate_cmd() -> None:
    project_dir = "."

    results = validate_project(project_dir)

    if not results:
        typer.echo("  No issues found.")
        return

    categories = {"version": "Version", "workflow": "Workflow", "security": "Security"}
    for cat_key, cat_label in categories.items():
        cat_issues = [r["message"] for r in results if r["category"] == cat_key]
        if cat_issues:
            typer.echo(f"  {cat_label}:")
            for msg in cat_issues:
                typer.echo(f"    \u2717 {msg}")

    if has_errors(results):
        typer.echo("")
        typer.echo("  Validation failed.")
        raise typer.Exit(code=1)
