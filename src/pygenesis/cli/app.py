from __future__ import annotations

import typer

from pygenesis import __version__
from pygenesis.cli.commands import (
    doctor_cmd,
    generate_cmd,
    health_cmd,
    init_cmd,
    inspect_cmd,
    new_cmd,
    release_check_cmd,
    review_cmd,
    validate_cmd,
)

cli = typer.Typer(
    name="pygenesis",
    help="Analyze Python projects and generate CI/CD pipelines for PyPI and Debian/Launchpad",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"PyGenesis v{__version__}")
        raise typer.Exit()


@cli.callback()
def _main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    pass


cli.command(name="init")(init_cmd)
cli.command(name="new")(new_cmd)
cli.command(name="inspect")(inspect_cmd)
cli.command(name="validate")(validate_cmd)
cli.command(name="generate")(generate_cmd)
cli.command(name="release-check")(release_check_cmd)
cli.command(name="health")(health_cmd)
cli.command(name="review")(review_cmd)
cli.command(name="doctor")(doctor_cmd)
