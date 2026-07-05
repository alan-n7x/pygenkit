from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pygenesis.generators.deploy import DeployGenerator  # noqa: E402
from pygenesis.generators.docker import DockerGenerator  # noqa: E402
from pygenesis.generators.github_actions import GitHubActionsGenerator  # noqa: E402
from pygenesis.generators.orchestrator import generate_all  # noqa: E402
from pygenesis.models.config import (  # noqa: E402
    CIConfig,
    DebianConfig,
    DeployConfig,
    DockerConfig,
    GitHubConfig,
    ProjectConfig,
    PyGenesisConfig,
    PyPIConfig,
    ReleaseConfig,
)


def _make_config(
    project_name: str = "test-app",
    docker_enabled: bool = False,
    deploy_enabled: bool = False,
) -> PyGenesisConfig:
    return PyGenesisConfig(
        project=ProjectConfig(name=project_name, version="1.0.0"),
        ci=CIConfig(python_versions=["3.12", "3.13"]),
        release=ReleaseConfig(),
        pypi=PyPIConfig(),
        debian=DebianConfig(owner="testuser"),
        github=GitHubConfig(),
        docker=DockerConfig(enabled=docker_enabled),
        deploy=DeployConfig(enabled=deploy_enabled),
    )


def test_github_actions_ci(tmp_path: Path) -> None:
    gen = GitHubActionsGenerator()
    config = _make_config()
    gen.generate(config, tmp_path, force=True)

    wf_dir = tmp_path / ".github" / "workflows"
    assert (wf_dir / "ci.yml").exists()
    content = (wf_dir / "ci.yml").read_text()
    assert "CI" in content
    assert "3.12" in content
    assert "3.13" in content
    assert "ruff check" in content
    assert "mypy" in content


def test_github_actions_release(tmp_path: Path) -> None:
    gen = GitHubActionsGenerator()
    config = _make_config()
    gen.generate(config, tmp_path, force=True)

    wf_dir = tmp_path / ".github" / "workflows"
    assert (wf_dir / "release.yml").exists()
    content = (wf_dir / "release.yml").read_text()
    assert "softprops/action-gh-release@v2" in content


def test_github_actions_pypi(tmp_path: Path) -> None:
    gen = GitHubActionsGenerator()
    config = _make_config()
    gen.generate(config, tmp_path, force=True)

    wf_dir = tmp_path / ".github" / "workflows"
    assert (wf_dir / "publish-pypi.yml").exists()
    content = (wf_dir / "publish-pypi.yml").read_text()
    assert "pypa/gh-action-pypi-publish" in content


def test_github_actions_launchpad(tmp_path: Path) -> None:
    gen = GitHubActionsGenerator()
    config = _make_config()
    gen.generate(config, tmp_path, force=True)

    wf_dir = tmp_path / ".github" / "workflows"
    assert (wf_dir / "publish-launchpad.yml").exists()
    content = (wf_dir / "publish-launchpad.yml").read_text()
    assert "testuser" in content
    assert "dput" in content


def test_github_actions_skip_disabled(tmp_path: Path) -> None:
    gen = GitHubActionsGenerator()
    config = _make_config()
    config.github.ci = False
    config.github.release = False
    gen.generate(config, tmp_path, force=True)

    wf_dir = tmp_path / ".github" / "workflows"
    assert not (wf_dir / "ci.yml").exists()
    assert not (wf_dir / "release.yml").exists()


def test_docker_generator(tmp_path: Path) -> None:
    gen = DockerGenerator()
    config = _make_config(docker_enabled=True)
    gen.generate(config, tmp_path, force=True)

    assert (tmp_path / "Dockerfile").exists()
    dockerfile = (tmp_path / "Dockerfile").read_text()
    assert "python:3.12-slim" in dockerfile
    assert "EXPOSE 8000" in dockerfile

    assert (tmp_path / "docker-compose.yml").exists()
    compose = (tmp_path / "docker-compose.yml").read_text()
    assert "8000:8000" in compose


def test_deploy_generator(tmp_path: Path) -> None:
    gen = DeployGenerator()
    config = _make_config(deploy_enabled=True)
    gen.generate(config, tmp_path, force=True)

    assert (tmp_path / "fly.toml").exists()
    fly = (tmp_path / "fly.toml").read_text()
    assert "test-app" in fly
    assert "iad" in fly

    assert (tmp_path / "Procfile").exists()
    proc = (tmp_path / "Procfile").read_text()
    assert "test-app" in proc

    assert (tmp_path / "railway.json").exists()


def test_docker_disabled_via_orchestrator(tmp_path: Path) -> None:
    config = _make_config(docker_enabled=False)
    results = generate_all(config, tmp_path, force=True)
    assert results["docker"] == []


def test_deploy_disabled_via_orchestrator(tmp_path: Path) -> None:
    config = _make_config(deploy_enabled=False)
    results = generate_all(config, tmp_path, force=True)
    assert results["deploy"] == []


def test_generate_all(tmp_path: Path) -> None:
    config = _make_config(docker_enabled=True, deploy_enabled=True)
    results = generate_all(config, tmp_path, force=True)

    assert "github" in results
    assert len(results["github"]) >= 4
    assert "docker" in results
    assert len(results["docker"]) == 2
    assert "deploy" in results
    assert len(results["deploy"]) == 3


def test_generate_all_disabled(tmp_path: Path) -> None:
    config = _make_config(docker_enabled=False, deploy_enabled=False)
    results = generate_all(config, tmp_path, force=True)

    assert len(results["github"]) >= 4
    assert results["docker"] == []
    assert results["deploy"] == []


def test_generate_no_force_skips_existing(tmp_path: Path) -> None:
    config = _make_config(docker_enabled=True)
    (tmp_path / "Dockerfile").write_text("existing", encoding="utf-8")
    (tmp_path / "docker-compose.yml").write_text("existing", encoding="utf-8")
    gen = DockerGenerator()
    files = gen.generate(config, tmp_path, force=False)
    assert files == []
