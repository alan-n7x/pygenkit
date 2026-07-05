from __future__ import annotations

from pathlib import Path

from pygenkit.generators.deploy import DeployGenerator
from pygenkit.generators.docker import DockerGenerator
from pygenkit.generators.github_actions import GitHubActionsGenerator
from pygenkit.models.config import PyGenKitConfig


def generate_all(
    config: PyGenKitConfig,
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
