from __future__ import annotations

from pathlib import Path
from typing import Any

from pygenkit.health.checks import (
    check_cicd,
    check_documentation,
    check_packaging,
    check_security,
    check_structure,
    check_testing,
    check_versioning,
)
from pygenkit.inspector.pyproject import read_pyproject
from pygenkit.models.health import HealthReport


def calculate_health(root: str | Path = ".") -> HealthReport:
    root_path = Path(root).resolve()
    pyproject_data = _safe_read_pyproject(root_path)

    checks = [
        check_versioning(root_path, pyproject_data),
        check_testing(root_path),
        check_documentation(root_path),
        check_cicd(root_path),
        check_security(root_path),
        check_packaging(root_path, pyproject_data),
        check_structure(root_path),
    ]

    categories = {c.name.lower(): c for c in checks}
    weighted_sum = sum(c.score * c.weight for c in checks)
    total_weight = sum(c.weight for c in checks)
    final_score = int(round(weighted_sum / total_weight * 100)) if total_weight > 0 else 0

    all_issues: list[str] = []
    all_suggestions: list[str] = []
    for c in checks:
        all_issues.extend(c.issues)
        for detail in c.details:
            all_suggestions.append(f"{c.name}: {detail}")

    return HealthReport(
        score=final_score,
        categories=categories,
        issues=all_issues,
        suggestions=all_suggestions,
    )


def _safe_read_pyproject(root: Path) -> dict[str, Any] | None:
    try:
        return read_pyproject(root)
    except (FileNotFoundError, Exception):
        return None
