from __future__ import annotations

from pathlib import Path
from typing import Any

from pygenesis.generators.base import BaseGenerator
from pygenesis.models.config import PyGenesisConfig


class GitHubActionsGenerator(BaseGenerator):
    def __init__(self) -> None:
        super().__init__("github/workflows")

    def generate(
        self,
        config: PyGenesisConfig,
        output_dir: str | Path,
        force: bool = False,
    ) -> list[Path]:
        generated: list[Path] = []
        ctx = self._build_context(config)
        wf_dir = Path(output_dir) / ".github" / "workflows"
        wf_dir.mkdir(parents=True, exist_ok=True)

        workflows = {
            "ci.yml": ("ci.yml.j2", config.github.ci),
            "release.yml": ("release.yml.j2", config.github.release),
            "publish-pypi.yml": ("publish-pypi.yml.j2", config.github.publish_pypi),
            "publish-launchpad.yml": (
                "publish-launchpad.yml.j2",
                config.github.publish_launchpad,
            ),
        }

        for out_name, (template, enabled) in workflows.items():
            if not enabled:
                continue
            out = self.render(template, wf_dir, out_name, ctx, force=force)
            if out is not None:
                generated.append(out)

        return generated

    def _build_context(self, config: PyGenesisConfig) -> dict[str, Any]:
        return {
            "project": {
                "name": config.project.name,
                "extras": config.project.extras,
            },
            "ci": {
                "python_versions": config.ci.python_versions,
                "runner": config.ci.runner,
                "lint": config.ci.lint,
                "type_check": config.ci.type_check,
            },
            "release": {
                "branch": config.release.branch,
                "tag_prefix": config.release.tag_prefix,
            },
            "pypi": {
                "environment": config.pypi.environment,
                "trusted_publishing": config.pypi.trusted_publishing,
            },
            "debian": {
                "owner": config.debian.owner,
                "ppa": config.debian.ppa,
            },
        }
