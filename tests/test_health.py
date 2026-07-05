from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pygenkit.health.api import calculate_health  # noqa: E402
from pygenkit.health.checks import (  # noqa: E402
    check_cicd,
    check_documentation,
    check_packaging,
    check_security,
    check_structure,
    check_testing,
    check_versioning,
)
from pygenkit.models.health import CategoryScore  # noqa: E402


def _write_pyproject(path: Path, name: str = "test-app", version: str = "1.0.0") -> None:
    content = f"""[project]
name = "{name}"
version = "{version}"
description = "A test project"
dependencies = ["requests>=2.0"]
"""
    (path / "pyproject.toml").write_text(content, encoding="utf-8")


def _write_init(path: Path, name: str, version: str = "1.0.0") -> None:
    src_dir = path / "src" / name
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "__init__.py").write_text(f'__version__ = "{version}"\n', encoding="utf-8")


def test_health_score_perfect(tmp_path: Path) -> None:
    _write_pyproject(tmp_path)
    _write_init(tmp_path, "test_app")

    (tmp_path / "README.md").write_text("# Test", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("MIT License", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("__pycache__/", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_app.py").write_text("def test(): pass", encoding="utf-8")

    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    (wf_dir / "ci.yml").write_text(
        "name: CI\non: [push]\npermissions: read-all\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - uses: actions/checkout@v6\n",
        encoding="utf-8",
    )
    (wf_dir / "release.yml").write_text(
        "name: Release\non: [push]\npermissions: write-all\n"
        "jobs:\n  rel:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - uses: actions/checkout@v6\n",
        encoding="utf-8",
    )
    (wf_dir / "publish-pypi.yml").write_text(
        "name: PyPI\non: [push]\npermissions: id-token\njobs:\n  pub:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - uses: actions/checkout@v6\n",
        encoding="utf-8",
    )

    (tmp_path / "Dockerfile").write_text("FROM python:3.12", encoding="utf-8")

    report = calculate_health(tmp_path)
    assert report.score >= 60


def test_health_score_minimal(tmp_path: Path) -> None:
    report = calculate_health(tmp_path)
    assert isinstance(report.score, int)
    assert 0 <= report.score <= 100
    assert len(report.categories) == 7


def test_check_versioning(tmp_path: Path) -> None:
    _write_pyproject(tmp_path)
    _write_init(tmp_path, "test_app")

    from pygenkit.inspector.pyproject import read_pyproject
    data = read_pyproject(tmp_path)
    result = check_versioning(tmp_path, data)
    assert isinstance(result, CategoryScore)
    assert result.score > 0


def test_check_versioning_no_data(tmp_path: Path) -> None:
    result = check_versioning(tmp_path, None)
    assert isinstance(result, CategoryScore)


def test_check_testing(tmp_path: Path) -> None:
    result = check_testing(tmp_path)
    assert isinstance(result, CategoryScore)
    assert result.score == 0.0

    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("", encoding="utf-8")
    result = check_testing(tmp_path)
    assert result.score > 0


def test_check_documentation(tmp_path: Path) -> None:
    result = check_documentation(tmp_path)
    assert result.score < 0.5

    (tmp_path / "README.md").write_text("# H", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("# C", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("MIT", encoding="utf-8")
    result = check_documentation(tmp_path)
    assert result.score >= 0.5


def test_check_cicd(tmp_path: Path) -> None:
    result = check_cicd(tmp_path)
    assert result.score < 1.0

    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    (wf_dir / "ci.yml").write_text("", encoding="utf-8")
    (wf_dir / "release.yml").write_text("", encoding="utf-8")
    (wf_dir / "publish-pypi.yml").write_text("", encoding="utf-8")
    result = check_cicd(tmp_path)
    assert result.score > 0


def test_check_security(tmp_path: Path) -> None:
    result = check_security(tmp_path)
    assert isinstance(result, CategoryScore)


def test_check_packaging(tmp_path: Path) -> None:
    result = check_packaging(tmp_path, None)
    assert result.score == 0.0

    _write_pyproject(tmp_path)
    from pygenkit.inspector.pyproject import read_pyproject

    data = read_pyproject(tmp_path)
    result = check_packaging(tmp_path, data)
    assert result.score > 0


def test_check_structure(tmp_path: Path) -> None:
    result = check_structure(tmp_path)
    assert isinstance(result, CategoryScore)

    (tmp_path / ".gitignore").write_text("", encoding="utf-8")
    result = check_structure(tmp_path)
    assert result.score > 0


def test_health_cli() -> None:
    from typer.testing import CliRunner

    from pygenkit.cli.app import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["health"])
    assert result.exit_code == 0
