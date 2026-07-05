from __future__ import annotations

from pathlib import Path

from pygenkit.models.inspection import DebianInspection


def inspect_debian(root: str | Path) -> DebianInspection:
    debian_dir = Path(root) / "debian"
    result = DebianInspection(present=debian_dir.is_dir())

    if not result.present:
        return result

    control = debian_dir / "control"
    changelog = debian_dir / "changelog"

    result.has_control = control.exists()
    result.has_changelog = changelog.exists()

    if result.has_changelog:
        ver = _parse_changelog_version(changelog)
        result.version_in_changelog = ver

    issues = _check_issues(debian_dir, result)
    result.issues = issues

    return result


def _parse_changelog_version(path: Path) -> str | None:
    try:
        first_line = path.read_text(encoding="utf-8").split("\n")[0]
        if "(" in first_line and ")" in first_line:
            return first_line.split("(")[1].split(")")[0].split("-")[0]
    except (IndexError, OSError):
        pass
    return None


def _check_issues(debian_dir: Path, result: DebianInspection) -> list[str]:
    issues: list[str] = []
    if not result.has_control:
        issues.append("debian/control is missing")
    if not result.has_changelog:
        issues.append("debian/changelog is missing")
    if result.present and not (debian_dir / "rules").exists():
        issues.append("debian/rules is missing (dh_make?)")
    if result.present and not (debian_dir / "source" / "format").exists():
        issues.append("debian/source/format is missing (use '3.0 (quilt)')")
    return issues
