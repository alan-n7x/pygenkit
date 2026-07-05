from __future__ import annotations

import typer

from pygenesis.health.api import calculate_health


def _bar(pct: int, width: int = 20) -> str:
    filled = int(pct / 100 * width)
    empty = width - filled
    return "[" + "#" * filled + "-" * empty + "]"


def health_cmd() -> None:
    """Assess project health across 7 categories."""
    report = calculate_health(".")

    score = report.score
    bar = _bar(score)
    grade = _grade(score)

    typer.echo(f"  Health Score: {bar} {score}/100 ({grade})")
    typer.echo("")

    cat_keys = (
        "versioning", "testing", "documentation",
        "cicd", "security", "packaging", "structure",
    )
    for cat_key in cat_keys:
        cat = report.categories.get(cat_key)
        if not cat:
            continue
        pct = int(cat.score * 100)
        cb = _bar(pct, 10)
        label = cat.name.ljust(14)
        typer.echo(f"  {label} {cb} {pct}%  ({cat.passed}/{cat.total})")

    if report.issues:
        typer.echo("")
        typer.echo("  Issues:")
        for issue in report.issues[:10]:
            typer.echo(f"    \u2717 {issue}")
        if len(report.issues) > 10:
            typer.echo(f"    ... and {len(report.issues) - 10} more")

    typer.echo("")
    if score >= 80:
        typer.echo("  Great shape!")
    elif score >= 50:
        typer.echo("  Room for improvement.")
    else:
        typer.echo("  Needs significant work.")


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 65:
        return "C"
    if score >= 50:
        return "D"
    return "F"
