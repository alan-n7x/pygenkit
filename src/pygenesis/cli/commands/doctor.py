from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Callable
from typing import Any

import typer

from pygenesis import __version__


class DoctorCheck:
    def __init__(self, name: str, check_fn: Callable[[], Any], hint: str = "") -> None:
        self.name = name
        self.check_fn = check_fn
        self.hint = hint

    def run(self) -> dict[str, Any]:
        try:
            result = self.check_fn()
            return {"name": self.name, "ok": True, "detail": str(result), "hint": ""}
        except Exception as exc:
            return {"name": self.name, "ok": False, "detail": str(exc), "hint": self.hint}


def _check_python() -> str:
    return sys.version.split()[0]


def _check_git() -> str:
    r = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=10)
    return r.stdout.strip()


def _check_gh() -> str:
    if not shutil.which("gh"):
        raise RuntimeError("not found")
    r = subprocess.run(["gh", "--version"], capture_output=True, text=True, timeout=10)
    return r.stdout.split("\n")[0] if r.stdout else "found"


def _check_gpg() -> str:
    if not shutil.which("gpg"):
        raise RuntimeError("not found (apt install gnupg)")
    return "found"


def _check_dput() -> str:
    if not shutil.which("dput"):
        raise RuntimeError("not found (apt install dput)")
    return "found"


def _check_debhelper() -> str:
    if not shutil.which("dh"):
        raise RuntimeError("not found (apt install debhelper)")
    return "found"


def _check_twine() -> str:
    r = subprocess.run(
        [sys.executable, "-m", "twine", "--version"],
        capture_output=True, text=True, timeout=10,
    )
    if r.returncode != 0:
        raise RuntimeError("not installed (pip install twine)")
    return r.stdout.strip()


def _check_build_module() -> str:
    r = subprocess.run(
        [sys.executable, "-m", "build", "--version"],
        capture_output=True, text=True, timeout=10,
    )
    if r.returncode != 0:
        raise RuntimeError("not installed (pip install build)")
    return r.stdout.strip()


def doctor_cmd() -> None:
    """Check system for required tools."""
    checks = [
        DoctorCheck("Python", _check_python, "Install Python 3.12+ from python.org"),
        DoctorCheck("Git", _check_git, "apt install git"),
        DoctorCheck("GitHub CLI", _check_gh, "Install from https://cli.github.com"),
        DoctorCheck("GPG", _check_gpg, "apt install gnupg"),
        DoctorCheck("dput", _check_dput, "apt install dput"),
        DoctorCheck("debhelper", _check_debhelper, "apt install debhelper"),
        DoctorCheck(
            "twine", _check_twine, "pip install twine"
        ),
        DoctorCheck(
            "build", _check_build_module, "pip install build"
        ),
    ]

    typer.echo(f"PyGenesis v{__version__} — Doctor")
    typer.echo("")

    all_ok = True
    for check in checks:
        result = check.run()
        if result["ok"]:
            typer.echo(f"  \u2713 {result['name']}: {result['detail']}")
        else:
            all_ok = False
            detail = f" ({result['detail']})" if result["detail"] else ""
            typer.echo(f"  \u2717 {result['name']}: not found{detail}")
            if result["hint"]:
                typer.echo(f"    \u2192 {result['hint']}")

    typer.echo("")
    if all_ok:
        typer.echo("All checks passed!")
    else:
        typer.echo("Some checks failed. Fix the issues above and re-run.")
        raise typer.Exit(code=1)
