from __future__ import annotations

from pathlib import Path

from pygenesis.generators.deploy import DeployGenerator
from pygenesis.generators.docker import DockerGenerator
from pygenesis.generators.github_actions import GitHubActionsGenerator
from pygenesis.models.config import PyGenesisConfig


def generate_all(
    config: PyGenesisConfig,
    output_dir: str | Path = ".",
    force: bool = False,
) -> dict[str, list[Path]]:
    results: dict[str, list[Path]] = {}

    gh = GitHubActionsGenerator()
    results["github"] = gh.generate(config, output_dir, force=force)

    if config.docker.enabled:
        dkr = DockerGenerator()
        results["docker"] = dkr.generate(config, output_dir, force=force)
    else:
        results["docker"] = []

    if config.deploy.enabled:
        dep = DeployGenerator()
        results["deploy"] = dep.generate(config, output_dir, force=force)
    else:
        results["deploy"] = []

    return results
