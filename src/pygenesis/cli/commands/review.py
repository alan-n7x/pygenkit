from __future__ import annotations

from pathlib import Path

import typer

from pygenesis.ai.review import get_pr_diff, get_pr_diff_from_file, review_diff


def review_cmd(
    pr: str = typer.Argument("", help="PR number (e.g. 42) or path to diff file"),  # noqa: B008
    repo: str = typer.Option("", "--repo", help="GitHub repo (owner/repo)"),  # noqa: B008
    model: str = typer.Option("gpt-4o-mini", "--model", "-m", help="LLM model"),  # noqa: B008
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show diff without reviewing"),  # noqa: B008
) -> None:
    """Review a GitHub PR diff using AI."""
    diff: str = ""

    if not pr:
        typer.echo("  Error: PR number or path to diff file required")
        raise typer.Exit(code=1)

    diff_path = Path(pr)
    if diff_path.exists():
        diff = get_pr_diff_from_file(diff_path)
        source = pr
    else:
        try:
            diff = get_pr_diff(pr, repo or None)
            source = f"PR #{pr}" + (f" ({repo})" if repo else "")
        except RuntimeError as exc:
            typer.echo(f"  Error: {exc}")
            raise typer.Exit(code=1) from exc

    if not diff.strip():
        typer.echo("  Empty diff — nothing to review.")
        return

    if dry_run:
        typer.echo(f"  Diff from {source}:")
        typer.echo("")
        typer.echo(diff[:2000] + ("..." if len(diff) > 2000 else ""))
        return

    typer.echo(f"  Reviewing {source}...")
    typer.echo("")

    try:
        result = review_diff(diff, filename_hint=source, model=model)
    except ValueError as exc:
        typer.echo(f"  Error: {exc}")
        raise typer.Exit(code=1) from exc

    if result.error:
        typer.echo(f"  Review failed: {result.error}")
        raise typer.Exit(code=1)

    typer.echo(result.raw)
