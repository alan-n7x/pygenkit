import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pygenkit.models.config import PyGenKitConfig  # noqa: E402

SAMPLE_TOML = """[project]
name = "hello-world"
version = "0.2.0"

[ci]
python_versions = ["3.12", "3.13"]
runner = "ubuntu-latest"
lint = true
type_check = true

[release]
branch = "main"
tag_prefix = "v"
changelog = "CHANGELOG.md"

[pypi]
enabled = true
environment = "pypi"
trusted_publishing = true

[debian]
enabled = true
email = "dev@example.com"
name = "Dev Name"
ppa = "tools"
distributions = ["noble"]
revision = "1"
"""


def test_config_load_from_toml(tmp_path: Path) -> None:
    config_path = tmp_path / "pygenkit.toml"
    config_path.write_text(SAMPLE_TOML, encoding="utf-8")

    cfg = PyGenKitConfig.load(config_path)
    assert cfg.project.name == "hello-world"
    assert cfg.project.version == "0.2.0"
    assert cfg.ci.python_versions == ["3.12", "3.13"]
    assert cfg.ci.runner == "ubuntu-latest"
    assert cfg.pypi.enabled is True
    assert cfg.debian.enabled is True
    assert cfg.debian.email == "dev@example.com"
    assert cfg.debian.ppa == "tools"
    assert cfg.debian.distributions == ["noble"]


def test_config_generate_default() -> None:
    content = PyGenKitConfig.generate_default("my-app")
    assert 'name = "my-app"' in content
    assert 'version = "0.1.0"' in content
    assert "python_versions" in content


def test_config_roundtrip(tmp_path: Path) -> None:
    config_path = tmp_path / "pygenkit.toml"
    config_path.write_text(SAMPLE_TOML, encoding="utf-8")

    cfg1 = PyGenKitConfig.load(config_path)
    cfg1.save(config_path)
    cfg2 = PyGenKitConfig.load(config_path)

    assert cfg2.project.name == cfg1.project.name
    assert cfg2.project.version == cfg1.project.version
    assert cfg2.debian.email == cfg1.debian.email
    assert cfg2.ci.python_versions == cfg1.ci.python_versions
