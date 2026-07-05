from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def validate_workflows(root: str | Path = ".") -> list[str]:
    issues: list[str] = []
    wf_dir = Path(root) / ".github" / "workflows"

    if not wf_dir.is_dir():
        return []

    for yml_file in sorted(wf_dir.glob("*.yml")):
        issues.extend(_validate_single_workflow(yml_file))

    return issues


def _validate_single_workflow(path: Path) -> list[str]:
    issues: list[str] = []
    name = path.name

    try:
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        issues.append(f"{name}: invalid YAML — {exc}")
        return issues

    if not isinstance(data, dict):
        issues.append(f"{name}: not a mapping")
        return issues

    if "name" not in data:
        issues.append(f"{name}: missing 'name' field")

    triggers = _collect_triggers(data)
    if not triggers:
        issues.append(f"{name}: no triggers defined (on:)")

    jobs = data.get("jobs", {})
    if not jobs:
        issues.append(f"{name}: no jobs defined")
        return issues

    for job_id, job in jobs.items():
        if not isinstance(job, dict):
            continue
        issues.extend(_validate_job(name, job_id, job))

    return issues


def _collect_triggers(data: dict[str, Any]) -> list[str]:
    triggers: list[str] = []
    on = data.get("on", {})
    if isinstance(on, str):
        triggers.append(on)
    elif isinstance(on, dict):
        triggers.extend(on.keys())
    elif isinstance(on, list):
        triggers.extend(str(t) for t in on)
    return triggers


def _validate_job(wf_name: str, job_id: str, job: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    prefix = f"{wf_name}/{job_id}"

    if "runs-on" not in job:
        issues.append(f"{prefix}: missing runs-on")

    steps = job.get("steps", [])
    if not steps:
        issues.append(f"{prefix}: no steps")
        return issues

    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        if "uses" in step:
            issues.extend(_check_action_version(prefix, i, step["uses"]))
        if "run" in step:
            issues.extend(_check_shell_injection(prefix, i, step["run"]))

    return issues


def _check_action_version(prefix: str, step_idx: int, uses: str) -> list[str]:
    issues: list[str] = []
    if not isinstance(uses, str):
        return issues

    if "@" not in uses:
        issues.append(f"{prefix}/step{step_idx}: action '{uses}' has no version pin")
        return issues

    action, version = uses.rsplit("@", 1)
    known_outdated = {
        "actions/checkout@v3": "use actions/checkout@v4 or newer",
        "actions/checkout@v2": "use actions/checkout@v4 or newer",
        "actions/setup-python@v4": "use actions/setup-python@v5 or newer",
        "actions/setup-python@v3": "use actions/setup-python@v5 or newer",
        "actions/upload-artifact@v3": "use actions/upload-artifact@v4 or newer",
        "actions/download-artifact@v3": "use actions/download-artifact@v4 or newer",
    }

    full = f"{action}@{version}"
    if full in known_outdated:
        issues.append(f"{prefix}/step{step_idx}: {full} is outdated — {known_outdated[full]}")

    if not _is_sha_pin(version):
        issues.append(
            f"{prefix}/step{step_idx}: '{full}' uses tag '{version}' instead of SHA pin"
        )

    return issues


def _is_sha_pin(version: str) -> bool:
    return len(version) == 40 and all(c in "0123456789abcdef" for c in version)


def _check_shell_injection(prefix: str, step_idx: int, run: str) -> list[str]:
    issues: list[str] = []
    if not isinstance(run, str):
        return issues

    dangerous = ["${{ github.event.issue.title }}", "${{ github.event.pull_request.title }}"]
    for pattern in dangerous:
        if pattern in run:
            issues.append(
                f"{prefix}/step{step_idx}: possible script injection via {pattern}"
            )

    return issues
