from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def validate_security(root: str | Path = ".") -> list[str]:
    issues: list[str] = []
    wf_dir = Path(root) / ".github" / "workflows"

    if not wf_dir.is_dir():
        return []

    for yml_file in sorted(wf_dir.glob("*.yml")):
        issues.extend(_check_workflow_security(yml_file))

    secrets_file = Path(root) / ".github" / "secrets"
    if secrets_file.exists():
        issues.append(".github/secrets file should not be versioned")

    return issues


def _check_workflow_security(path: Path) -> list[str]:
    issues: list[str] = []
    name = path.name

    try:
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        return issues

    if not isinstance(data, dict):
        return issues

    jobs = data.get("jobs", {})
    if not isinstance(jobs, dict):
        return issues

    for job_id, job in jobs.items():
        if not isinstance(job, dict):
            continue
        issues.extend(_check_job_permissions(name, job_id, job))
        issues.extend(_check_job_secrets(name, job_id, job))
        issues.extend(_check_job_environment(name, job_id, job))

    return issues


def _check_job_permissions(wf_name: str, job_id: str, job: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    prefix = f"{wf_name}/{job_id}"

    if "permissions" not in job:
        issues.append(
            f"{prefix}: no explicit permissions block"
        )

    steps = job.get("steps", [])
    if isinstance(steps, list):
        for i, step in enumerate(steps):
            if isinstance(step, dict) and step.get("uses", "").startswith("actions/checkout"):
                token = step.get("with", {}).get("token", "")
                if token and "secrets." not in str(token):
                    issues.append(f"{prefix}/step{i}: hardcoded token in checkout action")

    return issues


def _check_job_secrets(wf_name: str, job_id: str, job: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    raw_yml = yaml.dump(job)

    hardcoded_patterns = ["password=", "api_key=", "secret=", "token="]
    for pattern in hardcoded_patterns:
        if pattern in raw_yml.lower():
            prefix = f"{wf_name}/{job_id}"
            issues.append(f"{prefix}: possible hardcoded secret ('{pattern}') in workflow")

    return issues


def _check_job_environment(wf_name: str, job_id: str, job: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    env = job.get("environment")

    if env and isinstance(env, str) and env == "pypi":
        return issues

    steps = job.get("steps", [])
    if isinstance(steps, list):
        for step in steps:
            if isinstance(step, dict):
                uses = step.get("uses", "")
                if ("pypi-publish" in uses or "pypa/gh-action-pypi-publish" in uses) and not env:
                        prefix = f"{wf_name}/{job_id}"
                        issues.append(f"{prefix}: PyPI publish should use a protected environment")

    return issues
