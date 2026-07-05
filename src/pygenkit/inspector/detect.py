from __future__ import annotations

import re
from pathlib import Path


def detect_module(root: str | Path, project_name: str | None = None) -> str | None:
    root = Path(root)
    src_dir = root / "src"
    if src_dir.is_dir():
        candidates = sorted(
            d for d in src_dir.iterdir()
            if d.is_dir() and not d.name.startswith("_")
        )
        if candidates:
            return candidates[0].name

    top_dirs = sorted(d for d in root.iterdir() if d.is_dir() and not d.name.startswith("_"))
    python_dirs = [d for d in top_dirs if (d / "__init__.py").exists()]
    if python_dirs:
        return python_dirs[0].name

    if project_name:
        candidate = project_name.replace("-", "_")
        if (src_dir / candidate).is_dir():
            return candidate

    return None


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
