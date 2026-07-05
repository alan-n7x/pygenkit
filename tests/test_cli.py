import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from typer.testing import CliRunner  # noqa: E402

from pygenkit.cli.app import cli  # noqa: E402

runner = CliRunner()


def test_help_output() -> None:
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "pygenkit" in result.stdout


def test_version_output() -> None:
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.2.4" in result.stdout


def test_doctor_runs() -> None:
    result = runner.invoke(cli, ["doctor"])
    assert result.exit_code in (0, 1)
    assert "PyGenKit" in result.stdout


def test_init_creates_config() -> None:
    result = runner.invoke(cli, ["init", "my-app"], standalone_mode=False)
    assert result.exit_code == 0
    config = Path("pygenkit.toml")
    assert config.exists()
    config.unlink()


def test_init_requires_name() -> None:
    result = runner.invoke(cli, ["init"])
    assert result.exit_code != 0


def test_inspect_runs() -> None:
    result = runner.invoke(cli, ["inspect"])
    assert result.exit_code in (0, 1)
    assert "Inspecting" in result.stdout


def test_validate_runs() -> None:
    result = runner.invoke(cli, ["validate"])
    assert result.exit_code in (0, 1)
    assert "No issues" in result.stdout or "Version" in result.stdout or "Security" in result.stdout


def test_generate_fails_without_config(tmp_path: Path) -> None:
    result = runner.invoke(cli, ["generate", "--config", str(tmp_path / "nonexistent.toml")])
    assert result.exit_code == 1
    assert "not found" in result.stdout


def test_release_check_fails_without_config(tmp_path: Path) -> None:
    result = runner.invoke(cli, ["release-check", "--config", str(tmp_path / "nonexistent.toml")])
    assert result.exit_code == 1
    assert "not found" in result.stdout
