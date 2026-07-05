from __future__ import annotations

import re
from pathlib import Path

_IGNORED_MODULE_DIRS = {
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "env",
    "venv",
}


def _module_name(project_name: str) -> str:
    return project_name.replace("-", "_")


def _is_module_dir(path: Path) -> bool:
    return (
        path.is_dir()
        and path.name not in _IGNORED_MODULE_DIRS
        and not path.name.endswith(".egg-info")
        and not path.name.startswith("_")
        and (path / "__init__.py").is_file()
    )


def detect_module(root: str | Path, project_name: str | None = None) -> str | None:
    root = Path(root)
    src_dir = root / "src"

    # The declared distribution name is the strongest signal. Python package
    # names use underscores where distribution names commonly use hyphens.
    if project_name:
        candidate = _module_name(project_name)
        for base in (src_dir, root):
            module_dir = base / candidate
            if _is_module_dir(module_dir):
                return candidate

    # Fall back to scanning only importable package directories.
    if src_dir.is_dir():
        candidates = sorted(d for d in src_dir.iterdir() if _is_module_dir(d))
        if candidates:
            return candidates[0].name

    python_dirs = sorted(d for d in root.iterdir() if _is_module_dir(d))
    if python_dirs:
        return python_dirs[0].name

    return None


def workflow_files(root: str | Path) -> list[Path]:
    workflow_dir = Path(root) / ".github" / "workflows"
    if not workflow_dir.is_dir():
        return []
    return sorted((*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml")))


def has_pypi_publish_workflow(root: str | Path) -> bool:
    markers = (
        "pypa/gh-action-pypi-publish",
        "twine upload",
        "trusted publishing",
        "publish to pypi",
        "pypi publish",
    )
    for path in workflow_files(root):
        if "pypi" in path.stem.lower():
            return True
        content = path.read_text(encoding="utf-8", errors="replace").lower()
        if any(marker in content for marker in markers):
            return True
    return False


def detect_tests(root: str | Path) -> bool:
    root = Path(root)
    if (root / "tests").is_dir():
        return True
    test_files = list(root.glob("test_*.py")) + list(root.glob("*test*.py"))
    return len(test_files) > 0


def detect_license(root: str | Path) -> str | None:
    root = Path(root)
    for name in ("LICENSE", "LICENSE.txt", "LICENSE.md", "COPYING"):
        path = root / name
        if path.exists():
            content = path.read_text(encoding="utf-8", errors="replace")
            return _classify_license(content)
    return None


def _classify_license(content: str) -> str | None:
    if "MIT" in content and "Permission is hereby granted" in content:
        return "MIT"
    if "Apache License" in content and "Version 2.0" in content:
        return "Apache-2.0"
    if "GNU GENERAL PUBLIC LICENSE" in content and "Version 3" in content:
        return "GPL-3.0"
    if "GNU GENERAL PUBLIC LICENSE" in content and "Version 2" in content:
        return "GPL-2.0"
    if "BSD" in content:
        return "BSD"
    if "Mozilla Public License" in content:
        return "MPL-2.0"
    return "custom"


def detect_version_in_init(root: str | Path, module: str | None = None) -> str | None:
    if not module:
        return None
    for base in (Path(root) / "src", Path(root)):
        init = base / module / "__init__.py"
        if init.exists():
            for line in init.read_text(encoding="utf-8").split("\n"):
                m = re.match(r'__version__\s*=\s*["\']([^"\']+)["\']', line)
                if m:
                    return m.group(1)
    return None


def detect_readme(root: str | Path) -> Path | None:
    root = Path(root)
    for name in ("README.md", "README.rst", "README.txt", "README"):
        path = root / name
        if path.exists():
            return path
    return None
