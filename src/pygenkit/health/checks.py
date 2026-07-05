from __future__ import annotations

from pathlib import Path
from typing import Any

from pygenkit.inspector import debian as debian_inspector
from pygenkit.inspector import detect as detect_inspector
from pygenkit.inspector import git as git_inspector
from pygenkit.inspector.pyproject import (
    detect_project_name,
    detect_project_version,
)
from pygenkit.models.health import CategoryScore


def check_versioning(root: Path, pyproject_data: dict[str, Any] | None) -> CategoryScore:
    score = CategoryScore(name="Versioning", weight=0.15)
    pyproject_ver = None

    if pyproject_data:
        pyproject_ver = detect_project_version(pyproject_data)
        if pyproject_ver:
            score.passed += 1
            score.details.append(f"pyproject.toml: {pyproject_ver}")
        else:
            score.issues.append("No version in pyproject.toml")
    score.total += 1

    module = _detect_module(root, pyproject_data)
    init_ver = detect_inspector.detect_version_in_init(root, module)
    if init_ver:
        score.passed += 1
        score.details.append(f"__init__.py: {init_ver}")
    else:
        score.issues.append("No __version__ in module __init__.py")
    score.total += 1

    debian_info = debian_inspector.inspect_debian(root)
    if debian_info.present and debian_info.version_in_changelog:
        score.passed += 1
        score.details.append(f"debian/changelog: {debian_info.version_in_changelog}")
    elif debian_info.present:
        score.issues.append("debian/changelog has no parseable version")
    score.total += 1

    git_tags = git_inspector.detect_git_tags(root)
    if git_tags:
        score.passed += 1
        score.details.append(f"{len(git_tags)} git tag(s)")
    else:
        score.issues.append("No git tags")
    score.total += 1

    consistent = _check_consistent(pyproject_ver, init_ver)
    if consistent:
        score.passed += 1
        score.details.append("Versions are consistent")
    else:
        score.issues.append("Versions are inconsistent")
    score.total += 1

    score.score = score.passed / score.total if score.total > 0 else 0.0
    return score


def check_testing(root: Path) -> CategoryScore:
    score = CategoryScore(name="Testing", weight=0.15)

    has_tests = detect_inspector.detect_tests(root)
    if has_tests:
        score.passed += 1
        score.details.append("Tests directory found")
    else:
        score.issues.append("No tests directory")
    score.total += 1

    if has_tests:
        test_dir = root / "tests"
        if test_dir.is_dir():
            py_files = list(test_dir.rglob("test_*.py"))
            score.details.append(f"{len(py_files)} test file(s)")
            if py_files:
                score.passed += 1
            else:
                score.issues.append("No test_*.py files in tests/")
        score.total += 1

    score.score = score.passed / score.total if score.total > 0 else 0.0
    return score


def check_documentation(root: Path) -> CategoryScore:
    score = CategoryScore(name="Documentation", weight=0.15)

    readme = detect_inspector.detect_readme(root)
    if readme:
        score.passed += 1
        score.details.append(f"README: {readme.name}")
    else:
        score.issues.append("No README file")
    score.total += 1

    changelog = root / "CHANGELOG.md"
    if changelog.exists():
        score.passed += 1
        score.details.append("CHANGELOG.md present")
    else:
        score.issues.append("No CHANGELOG.md")
    score.total += 1

    contributing = root / "CONTRIBUTING.md"
    if contributing.exists():
        score.passed += 1
        score.details.append("CONTRIBUTING.md present")
    score.total += 1

    license_result = detect_inspector.detect_license(root)
    if license_result:
        score.passed += 1
        score.details.append(f"License: {license_result}")
    else:
        score.issues.append("No license file")
    score.total += 1

    score.score = score.passed / score.total if score.total > 0 else 0.0
    return score


def check_cicd(root: Path) -> CategoryScore:
    score = CategoryScore(name="CICD", weight=0.20)

    wf_dir = root / ".github" / "workflows"
    if wf_dir.is_dir():
        wf_files = detect_inspector.workflow_files(root)
        score.details.append(f"{len(wf_files)} workflow file(s)")
        if wf_files:
            score.passed += 1
        score.total += 1

        has_ci = any("ci" in f.name.lower() for f in wf_files)
        has_release = any("release" in f.name.lower() for f in wf_files)
        has_pypi = detect_inspector.has_pypi_publish_workflow(root)

        if has_ci:
            score.passed += 1
            score.details.append("CI workflow present")
        else:
            score.issues.append("No CI workflow")
        score.total += 1

        if has_release:
            score.passed += 1
            score.details.append("Release workflow present")
        else:
            score.issues.append("No release workflow")
        score.total += 1

        if has_pypi:
            score.passed += 1
            score.details.append("PyPI publish workflow present")
        else:
            score.issues.append("No PyPI publish workflow")
        score.total += 1
    else:
        score.issues.append("No GitHub Actions workflows")
        score.total += 3  # ci, release, pypi

    dockerfile = root / "Dockerfile"
    if dockerfile.exists():
        score.passed += 1
        score.details.append("Dockerfile present")
    score.total += 1

    deploy_files = ["fly.toml", "Procfile", "railway.json", "heroku.yml"]
    deploy_count = sum(1 for f in deploy_files if (root / f).exists())
    if deploy_count > 0:
        score.passed += 1
        score.details.append(f"{deploy_count} deploy config(s) present")
    score.total += 1

    score.score = score.passed / score.total if score.total > 0 else 0.0
    return score


def check_security(root: Path) -> CategoryScore:
    score = CategoryScore(name="Security", weight=0.15)

    license_type = detect_inspector.detect_license(root)
    if license_type:
        score.passed += 1
        score.details.append(f"License: {license_type}")
    else:
        score.issues.append("No license")
    score.total += 1

    git_dir = root / ".git"
    if git_dir.is_dir():
        score.passed += 1
    else:
        score.issues.append("Not a git repository")
    score.total += 1

    github_remote = git_inspector.detect_github_remote(root)
    if github_remote:
        score.passed += 1
    else:
        score.issues.append("No GitHub remote configured")
    score.total += 1

    wf_dir = root / ".github" / "workflows"
    has_permissions = False
    if wf_dir.is_dir():
        for f in detect_inspector.workflow_files(root):
            content = f.read_text(encoding="utf-8", errors="replace")
            if "permissions:" in content:
                has_permissions = True
                break

    if has_permissions or not wf_dir.is_dir():
        score.passed += 1
    else:
        score.issues.append("Workflows missing permissions block")
    score.total += 1

    score.score = score.passed / score.total if score.total > 0 else 0.0
    return score


def check_packaging(root: Path, pyproject_data: dict[str, Any] | None) -> CategoryScore:
    score = CategoryScore(name="Packaging", weight=0.10)

    if pyproject_data:
        score.passed += 1
        score.details.append("pyproject.toml present")
    else:
        score.issues.append("No pyproject.toml")
    score.total += 1

    if pyproject_data:
        pkg_data = pyproject_data.get("project", {})
        if pkg_data.get("name"):
            score.passed += 1
        else:
            score.issues.append("pyproject.toml missing project name")
        score.total += 1

        if pkg_data.get("version"):
            score.passed += 1
        else:
            score.issues.append("pyproject.toml missing version")
        score.total += 1

        if pkg_data.get("description"):
            score.passed += 1
        else:
            score.issues.append("pyproject.toml missing description")
        score.total += 1

    src_dir = root / "src"
    if src_dir.is_dir():
        score.passed += 1
        score.details.append("src/ layout detected")
    else:
        score.issues.append("Not using src/ layout (recommended)")
    score.total += 1

    score.score = score.passed / score.total if score.total > 0 else 0.0
    return score


def check_structure(root: Path) -> CategoryScore:
    score = CategoryScore(name="Structure", weight=0.10)

    gitignore = root / ".gitignore"
    if gitignore.exists():
        score.passed += 1
    else:
        score.issues.append("No .gitignore")
    score.total += 1

    editorconfig = root / ".editorconfig"
    if editorconfig.exists():
        score.passed += 1
    score.total += 1

    ruff_toml = root / "ruff.toml"
    pyproject_toml = root / "pyproject.toml"
    ruff_configured = False
    if ruff_toml.exists():
        ruff_configured = True
    elif pyproject_toml.exists():
        data = _try_read_pyproject(pyproject_toml)
        if data and "tool" in data and "ruff" in data["tool"]:
            ruff_configured = True
    if ruff_configured:
        score.passed += 1
        score.details.append("Ruff configured")
    else:
        score.issues.append("Ruff not configured")
    score.total += 1

    mypy_configured = False
    mypy_ini = root / "mypy.ini"
    if mypy_ini.exists():
        mypy_configured = True
    elif pyproject_toml.exists():
        data = _try_read_pyproject(pyproject_toml)
        if data and "tool" in data and "mypy" in data["tool"]:
            mypy_configured = True
    if mypy_configured:
        score.passed += 1
        score.details.append("Mypy configured")
    else:
        score.issues.append("Mypy not configured")
    score.total += 1

    precommit = root / ".pre-commit-config.yaml"
    if precommit.exists():
        score.passed += 1
        score.details.append("pre-commit configured")
    score.total += 1

    score.score = score.passed / score.total if score.total > 0 else 0.0
    return score


def _detect_module(root: Path, pyproject_data: dict[str, Any] | None) -> str | None:
    name = detect_project_name(pyproject_data) if pyproject_data else None
    return detect_inspector.detect_module(root, name)


def _check_consistent(pyproject_ver: str | None, init_ver: str | None) -> bool:
    if pyproject_ver and init_ver:
        return pyproject_ver == init_ver
    return bool(pyproject_ver or init_ver)


def _try_read_pyproject(path: Path) -> dict[str, Any] | None:
    try:
        import tomllib
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
