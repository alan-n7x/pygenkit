from __future__ import annotations

from pathlib import Path

import typer

from pygenesis.generators.project import ProjectGenerator


def new_cmd(
    name: str = typer.Argument(..., help="Project name"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output directory"),  # noqa: B008
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing directory"),  # noqa: B008
) -> None:
    """Scaffold a new Python project with CI/CD, tests, and tooling ready."""
    gen = ProjectGenerator()
    output_dir = output or Path.cwd()
    try:
        root = gen.generate(
            name=name,
            output_dir=output_dir,
            force=force,
        )
    except FileExistsError as exc:
        typer.echo(f"  Error: {exc}")
        raise typer.Exit(code=1) from exc

    typer.echo(f"  Created {root}")
    typer.echo("")
    typer.echo("  Next steps:")
    typer.echo(f"    cd {name}")
    typer.echo("    git add . && git commit -m 'Initial commit'")
    typer.echo("    git remote add origin <repo-url>")
    typer.echo("    git push -u origin main")
    typer.echo("")
    typer.echo("  Edit pygenesis.toml with your info, then run:")
    typer.echo("    pygenesis generate")
