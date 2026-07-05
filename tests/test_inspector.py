import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pygenkit.inspector import debian as debian_inspector  # noqa: E402
from pygenkit.inspector import detect as detect_inspector  # noqa: E402
from pygenkit.inspector import pyproject as pyproject_inspector  # noqa: E402
from pygenkit.inspector.api import inspect_project  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"


def test_inspect_complete_project() -> None:
    with patch("pygenkit.inspector.git.detect_git_tags", return_value=["v1.2.3"]):
        result = inspect_project(FIXTURES / "complete-project")
        assert result.name == "complete-project"
        assert result.version == "1.2.3"
        assert result.python_requires == ">=3.11"
        assert result.module == "my_module"
        assert result.build_backend is not None
        assert result.build_backend.name == "setuptools"
        assert result.has_tests is True
        assert result.license_type == "MIT"
        assert result.has_debian.present is True
        assert result.has_debian.version_in_changelog == "1.2.3"
        assert result.has_workflows.has_ci is True
        assert result.has_workflows.has_pypi_publish is True
        assert result.versions.consistent is True


def test_inspect_no_pyproject(tmp_path: Path) -> None:
    result = inspect_project(tmp_path)
    assert result.errors
    assert "pyproject.toml not found" in result.errors[0]


def test_pyproject_read(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "test"\nversion = "0.1.0"\n', encoding="utf-8")
    data = pyproject_inspector.read_pyproject(tmp_path)
    assert data["project"]["name"] == "test"


def test_pyproject_backend_detect() -> None:
    data = {
        "build-system": {
            "build-backend": "hatchling.build",
            "requires": ["hatchling"],
        }
    }
    backend = pyproject_inspector.detect_build_backend(data)
    assert backend is not None
    assert backend.name == "hatchling"


def test_detect_license_mit(tmp_path: Path) -> None:
    lic = tmp_path / "LICENSE"
    lic.write_text("MIT License\nPermission is hereby granted", encoding="utf-8")
    assert detect_inspector.detect_license(tmp_path) == "MIT"


def test_detect_module(tmp_path: Path) -> None:
    src = tmp_path / "src" / "mypkg"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text("", encoding="utf-8")
    assert detect_inspector.detect_module(tmp_path) == "mypkg"


def test_detect_module_prioritizes_project_name_and_ignores_egg_info(
    tmp_path: Path,
) -> None:
    src = tmp_path / "src"
    package = src / "my_project"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (src / "another_package").mkdir()
    (src / "another_package" / "__init__.py").write_text("", encoding="utf-8")
    (src / "pygenesis.egg-info").mkdir()

    assert detect_inspector.detect_module(tmp_path, "my-project") == "my_project"


def test_detect_module_fallback_ignores_non_packages(tmp_path: Path) -> None:
    src = tmp_path / "src"
    (src / "build").mkdir(parents=True)
    (src / "legacy.egg-info").mkdir()
    package = src / "actual_package"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")

    assert detect_inspector.detect_module(tmp_path) == "actual_package"


def test_inspect_detects_pypi_publish_in_release_yaml(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "sample-app"\nversion = "1.0.0"\n', encoding="utf-8"
    )
    package = tmp_path / "src" / "sample_app"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text('__version__ = "1.0.0"\n', encoding="utf-8")
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "release.yaml").write_text(
        "steps:\n  - uses: pypa/gh-action-pypi-publish@release/v1\n",
        encoding="utf-8",
    )

    result = inspect_project(tmp_path)

    assert result.module == "sample_app"
    assert result.versions.init_version == "1.0.0"
    assert result.has_workflows.has_pypi_publish is True


def test_detect_tests(tmp_path: Path) -> None:
    (tmp_path / "test_foo.py").write_text("", encoding="utf-8")
    assert detect_inspector.detect_tests(tmp_path) is True


def test_inspect_debian(tmp_path: Path) -> None:
    debian = tmp_path / "debian"
    debian.mkdir(parents=True)
    (debian / "control").write_text("", encoding="utf-8")
    (debian / "changelog").write_text("foo (1.0.0-1) unstable;", encoding="utf-8")
    result = debian_inspector.inspect_debian(tmp_path)
    assert result.present is True
    assert result.has_control is True
    assert result.version_in_changelog == "1.0.0"
