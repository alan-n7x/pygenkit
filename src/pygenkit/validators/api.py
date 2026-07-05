from __future__ import annotations

from pathlib import Path

from pygenkit.validators import security as security_validator
from pygenkit.validators import version as version_validator
from pygenkit.validators import workflow as workflow_validator


def validate_project(root: str | Path = ".") -> list[dict[str, object]]:
    results: list[dict[str, object]] = []

    _add_results(results, "version", version_validator.validate_version_consistency(root))
    _add_results(results, "workflow", workflow_validator.validate_workflows(root))
    _add_results(results, "security", security_validator.validate_security(root))

    return results


def _add_results(
    results: list[dict[str, object]],
    category: str,
    issues: list[str],
) -> None:
    for issue in issues:
        results.append({"category": category, "message": issue})


def has_errors(results: list[dict[str, object]]) -> bool:
    return len(results) > 0
