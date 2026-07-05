from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BuildBackend:
    name: str
    backend: str  # setuptools, hatchling, poetry, etc.
    requires: list[str] = field(default_factory=list)


@dataclass
class DebianInspection:
    present: bool = False
    has_control: bool = False
    has_changelog: bool = False
    version_in_changelog: str | None = None
    issues: list[str] = field(default_factory=list)


@dataclass
class WorkflowInspection:
    has_ci: bool = False
    has_pypi_publish: bool = False
    has_launchpad: bool = False
    files: list[str] = field(default_factory=list)


@dataclass
class VersionInspection:
    pyproject_version: str | None = None
    init_version: str | None = None
    changelog_version: str | None = None
    git_tags: list[str] = field(default_factory=list)
    consistent: bool = False
    issues: list[str] = field(default_factory=list)


@dataclass
class ProjectInspection:
    name: str | None = None
    version: str | None = None
    python_requires: str | None = None
    module: str | None = None
    root: str = ""
    build_backend: BuildBackend | None = None
    has_tests: bool = False
    has_license: bool = False
    license_type: str | None = None
    has_debian: DebianInspection = field(default_factory=DebianInspection)
    has_workflows: WorkflowInspection = field(default_factory=WorkflowInspection)
    versions: VersionInspection = field(default_factory=VersionInspection)
    github_remote: str | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
