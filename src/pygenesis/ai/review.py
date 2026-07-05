from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pygenesis.ai.prompts import SYSTEM_PROMPT, build_user_prompt
from pygenesis.ai.provider import LLMProvider, create_provider


@dataclass
class ReviewResult:
    raw: str
    summary: str = ""
    issues: list[dict[str, str]] = field(default_factory=list)
    positives: list[str] = field(default_factory=list)
    error: str = ""


def get_pr_diff(pr_number: str, repo: str | None = None) -> str:
    cmd = ["gh", "pr", "diff", pr_number]
    if repo:
        cmd.extend(["--repo", repo])
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode != 0:
            msg = f"gh command failed: {r.stderr.strip()}"
            raise RuntimeError(msg)
        return r.stdout
    except FileNotFoundError:
        msg = "GitHub CLI (gh) is not installed"
        raise RuntimeError(msg)  # noqa: B904


def get_pr_diff_from_file(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def review_diff(
    diff: str,
    provider: LLMProvider | None = None,
    filename_hint: str = "",
    **llm_kwargs: Any,
) -> ReviewResult:
    if provider is None:
        provider = create_provider()

    try:
        user = build_user_prompt(diff, filename_hint)
        raw = provider.complete(SYSTEM_PROMPT, user, **llm_kwargs)
        return ReviewResult(raw=raw)
    except Exception as exc:
        return ReviewResult(raw="", error=str(exc))
