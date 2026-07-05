from __future__ import annotations

from pathlib import Path

from pygenkit.inspector import debian as debian_inspector
from pygenkit.inspector import detect as detect_inspector
from pygenkit.inspector import git as git_inspector
from pygenkit.inspector.pyproject import (
    detect_build_backend,
    detect_project_name,
    detect_project_version,
    detect_python_requires,
    read_pyproject,
)
from pygenkit.models.inspection import (
    DebianInspection,
    ProjectInspection,
    VersionInspection,
    WorkflowInspection,
)


def inspect_project(root: str | Path = ".") -> ProjectInspection:
    root = Path(root).resolve()
    result = ProjectInspection(root=str(root))

    try:
        data = read_pyproject(root)
    except FileNotFoundError:
        result.errors.append("pyproject.toml not found")
        return result
    except Exception as exc:
        result.errors.append(f"Failed to parse pyproject.toml: {exc}")
        return result

    result.name = detect_project_name(data)
    result.version = detect_project_version(data)
    result.python_requires = detect_python_requires(data)
    result.build_backend = detect_build_backend(data)

    if result.name:
        result.module = detect_inspector.detect_module(root, result.name)
    else:
        result.module = detect_inspector.detect_module(root)

    result.has_tests = detect_inspector.detect_tests(root)
    result.license_type = detect_inspector.detect_license(root)
    result.has_license = result.license_type is not None

    init_ver = detect_inspector.detect_version_in_init(root, result.module)
    pyproject_ver = result.version
    debian_info = debian_inspector.inspect_debian(root)
    result.has_debian = debian_info

    github_remote = git_inspector.detect_github_remote(root)
    result.github_remote = github_remote
    git_tags = git_inspector.detect_git_tags(root)

    workflows = _inspect_workflows(root)
    result.has_workflows = workflows

    result.versions = VersionInspection(
        pyproject_version=pyproject_ver,
        init_version=init_ver,
        changelog_version=debian_info.version_in_changelog,
        git_tags=git_tags,
        consistent=_check_version_consistency(
            pyproject_ver, init_ver, debian_info.version_in_changelog, git_tags
        ),
        issues=_collect_version_issues(
            pyproject_ver, init_ver, debian_info.version_in_changelog, git_tags
        ),
    )

    result.warnings = _collect_warnings(result, debian_info)

    return result


def _inspect_workflows(root: Path) -> WorkflowInspection:
    wf = WorkflowInspection()
    wf_dir = root / ".github" / "workflows"
    if not wf_dir.is_dir():
        return wf

    for f in wf_dir.glob("*.yml"):
        wf.files.append(f.name)
        content = f.read_text(encoding="utf-8", errors="replace")
        if "pypi" in content.lower() or "publish" in content.lower():
            wf.has_pypi_publish = True
        if "launchpad" in content.lower() or "ppa" in content.lower():
            wf.has_launchpad = True
        if "test" in content.lower() or "lint" in content.lower():
            wf.has_ci = True

    return wf


def _check_version_consistency(
    pyproject_ver: str | None,
    init_ver: str | None,
    changelog_ver: str | None,
    git_tags: list[str],
) -> bool:
    versions = [v for v in [pyproject_ver, init_ver, changelog_ver] if v]
    if not versions:
        return True
    if len(set(versions)) > 1:
        return False
    latest_tag = _latest_tag(git_tags)
    if latest_tag and pyproject_ver and latest_tag != pyproject_ver:
        return bool(not git_tags)
    return True


def _latest_tag(tags: list[str]) -> str | None:
    for t in tags:
        if t.startswith("v"):
            return t.lstrip("v")
    return tags[0] if tags else None


def _collect_version_issues(
    pyproject_ver: str | None,
    init_ver: str | None,
    changelog_ver: str | None,
    git_tags: list[str],
) -> list[str]:
    issues: list[str] = []
    if pyproject_ver and init_ver and pyproject_ver != init_ver:
        issues.append(f"pyproject.toml version ({pyproject_ver}) != __init__.py ({init_ver})")
    if pyproject_ver and changelog_ver and pyproject_ver != changelog_ver:
        issues.append(
            f"pyproject.toml ({pyproject_ver}) != debian/changelog ({changelog_ver})"
        )
    latest = _latest_tag(git_tags)
    if latest and pyproject_ver and latest != pyproject_ver:
        issues.append(f"latest git tag (v{latest}) != pyproject.toml version ({pyproject_ver})")
    return issues


def _collect_warnings(result: ProjectInspection, debian_info: DebianInspection) -> list[str]:
    warnings: list[str] = []
    if not result.has_tests:
        warnings.append("No tests directory found")
    if not result.has_license:
        warnings.append("No license file found")
    if not result.build_backend:
        warnings.append("No build backend detected in pyproject.toml")
    if not result.github_remote:
        warnings.append("No GitHub remote configured")
    if result.has_debian.present and debian_info.issues:
        warnings.extend(f"Debian: {i}" for i in debian_info.issues)
    return warnings
