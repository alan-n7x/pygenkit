from __future__ import annotations

import subprocess
from pathlib import Path


def detect_github_remote(root: str | Path) -> str | None:
    try:
        r = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=10,
            cwd=str(root),
        )
        if r.returncode != 0:
            return None
        url = r.stdout.strip()
        if "github.com" in url:
            return url
        return url
    except (subprocess.SubprocessError, FileNotFoundError):
        return None


def detect_git_tags(root: str | Path) -> list[str]:
    try:
        r = subprocess.run(
            ["git", "tag", "--sort=-version:refname"],
            capture_output=True, text=True, timeout=10,
            cwd=str(root),
        )
        if r.returncode != 0:
            return []
        return [t.strip() for t in r.stdout.strip().split("\n") if t.strip()]
    except (subprocess.SubprocessError, FileNotFoundError):
        return []


def extract_github_owner_repo(url: str) -> tuple[str, str] | None:
    if "github.com" not in url:
        return None
    parts = url.rstrip("/").replace(".git", "").split("/")
    if len(parts) >= 2:
        return (parts[-2], parts[-1])
    return None


def is_git_repo(root: str | Path) -> bool:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True, timeout=5, cwd=str(root),
        )
        return r.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False
