from __future__ import annotations

from pathlib import Path

from pygenesis.inspector import debian as debian_inspector
from pygenesis.inspector import detect as detect_inspector
from pygenesis.inspector import git as git_inspector
from pygenesis.inspector import pyproject as pyproject_inspector


def validate_version_consistency(root: str | Path = ".") -> list[str]:
    issues: list[str] = []
    root = Path(root).resolve()

    pyproject_ver = _get_pyproject_version(root)
    init_ver = _get_init_version(root)
    changelog_ver = _get_changelog_version(root)
    latest_tag = _get_latest_tag(root)

    if pyproject_ver and init_ver and pyproject_ver != init_ver:
        issues.append(
            f"pyproject.toml: {pyproject_ver} != src/.../__init__.py: {init_ver}"
        )

    if pyproject_ver and changelog_ver and pyproject_ver != changelog_ver:
        issues.append(
            f"pyproject.toml: {pyproject_ver} != debian/changelog: {changelog_ver}"
        )

    if latest_tag and pyproject_ver and latest_tag != pyproject_ver:
        issues.append(
            f"latest git tag v{latest_tag} != pyproject.toml: {pyproject_ver}"
        )

    return issues


def _get_pyproject_version(root: Path) -> str | None:
    try:
        data = pyproject_inspector.read_pyproject(root)
        return pyproject_inspector.detect_project_version(data)
    except (FileNotFoundError, Exception):
        return None


def _get_init_version(root: Path) -> str | None:
    try:
        data = pyproject_inspector.read_pyproject(root)
        name = pyproject_inspector.detect_project_name(data)
        if name:
            module = detect_inspector.detect_module(root, name)
        else:
            module = detect_inspector.detect_module(root)
        if module:
            return detect_inspector.detect_version_in_init(root, module)
    except (FileNotFoundError, Exception):
        pass
    return None


def _get_changelog_version(root: Path) -> str | None:
    try:
        info = debian_inspector.inspect_debian(root)
        return info.version_in_changelog
    except Exception:
        return None


def _get_latest_tag(root: Path) -> str | None:
    try:
        tags = git_inspector.detect_git_tags(root)
        for t in tags:
            if t.startswith("v"):
                return t.lstrip("v")
        return tags[0] if tags else None
    except Exception:
        return None
