import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pygenkit.validators.api import has_errors, validate_project  # noqa: E402
from pygenkit.validators.security import validate_security  # noqa: E402
from pygenkit.validators.version import validate_version_consistency  # noqa: E402
from pygenkit.validators.workflow import validate_workflows  # noqa: E402


def test_validate_version_consistent(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "x"\nversion = "1.0.0"\n', encoding="utf-8")
    src = tmp_path / "src" / "x"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text('__version__ = "1.0.0"\n', encoding="utf-8")
    issues = validate_version_consistency(tmp_path)
    assert issues == []


def test_validate_version_inconsistent(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "x"\nversion = "1.0.0"\n', encoding="utf-8")
    src = tmp_path / "src" / "x"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text('__version__ = "2.0.0"\n', encoding="utf-8")
    issues = validate_version_consistency(tmp_path)
    assert len(issues) >= 1
    assert "1.0.0" in issues[0]
    assert "2.0.0" in issues[0]


def test_validate_workflow_no_dir(tmp_path: Path) -> None:
    issues = validate_workflows(tmp_path)
    assert issues == []


def test_validate_workflow_with_file(tmp_path: Path) -> None:
    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    wf = wf_dir / "ci.yml"
    content = (
        "name: CI\non: [push]\njobs:\n"
        "  test:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - uses: actions/checkout@v6\n"
    )
    wf.write_text(content, encoding="utf-8")
    issues = validate_workflows(tmp_path)
    assert isinstance(issues, list)


def test_validate_security_no_dir(tmp_path: Path) -> None:
    issues = validate_security(tmp_path)
    assert issues == []


def test_validate_project_api(tmp_path: Path) -> None:
    results = validate_project(tmp_path)
    assert isinstance(results, list)


def test_has_errors() -> None:
    assert has_errors([{"category": "version", "message": "test"}]) is True
    assert has_errors([]) is False


def test_validate_outdated_action(tmp_path: Path) -> None:
    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    wf = wf_dir / "ci.yml"
    content = (
        "name: CI\non: [push]\njobs:\n"
        "  test:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - uses: actions/checkout@v3\n"
    )
    wf.write_text(content, encoding="utf-8")
    issues = validate_workflows(tmp_path)
    outdated = [i for i in issues if "outdated" in i.lower()]
    assert len(outdated) >= 1
