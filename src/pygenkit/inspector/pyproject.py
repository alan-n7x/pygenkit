from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from pygenkit.models.inspection import BuildBackend

BACKEND_MAP: dict[str, str] = {
    "setuptools.build_meta": "setuptools",
    "hatchling.build": "hatchling",
    "poetry.core.masonry.api": "poetry",
    "flit_core.buildapi": "flit",
    "pdm.buildapi": "pdm",
    "maturin": "maturin",
    "mesonpy": "meson-python",
    "scikit_build_core.build": "scikit-build-core",
}


def read_pyproject(root: str | Path) -> dict[str, Any]:
    path = Path(root) / "pyproject.toml"
    if not path.exists():
        raise FileNotFoundError(f"pyproject.toml not found in {root}")
    raw = path.read_bytes()
    return tomllib.loads(raw.decode("utf-8"))


def detect_build_backend(data: dict[str, Any]) -> BuildBackend | None:
    build_system = data.get("build-system", {})
    backend_path = build_system.get("build-backend", "")
    requires = build_system.get("requires", [])

    name = BACKEND_MAP.get(backend_path, backend_path.split(".")[0] if backend_path else "unknown")
    if not backend_path:
        return None

    return BuildBackend(name=name, backend=backend_path, requires=requires)


def _get_project_field(data: dict[str, Any], field: str) -> str | None:
    project = data.get("project", {})
    if not isinstance(project, dict):
        return None
    val = project.get(field)
    return str(val) if val is not None else None


def detect_project_name(data: dict[str, Any]) -> str | None:
    return _get_project_field(data, "name")


def detect_project_version(data: dict[str, Any]) -> str | None:
    return _get_project_field(data, "version")


def detect_python_requires(data: dict[str, Any]) -> str | None:
    return _get_project_field(data, "requires-python")


def detect_dependencies(data: dict[str, Any]) -> list[str]:
    project = data.get("project", {})
    if not isinstance(project, dict):
        return []
    deps = project.get("dependencies", [])
    return [str(d) for d in deps] if isinstance(deps, list) else []


def detect_test_deps(data: dict[str, Any]) -> list[str]:
    optional = data.get("project", {}).get("optional-dependencies", {})
    deps: list[str] = []
    for group in optional.values():
        deps.extend(group)
    return deps
