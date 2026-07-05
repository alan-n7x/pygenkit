from __future__ import annotations

from pathlib import Path
from typing import Any

from pygenkit.generators.base import BaseGenerator
from pygenkit.models.config import PyGenKitConfig


class DeployGenerator(BaseGenerator):
    def __init__(self) -> None:
        super().__init__("deploy")

    def generate(
        self,
        config: PyGenKitConfig,
        output_dir: str | Path,
        force: bool = False,
    ) -> list[Path]:
        generated: list[Path] = []
        ctx = self._build_context(config)

        targets = {
            "fly.toml": ("fly.toml.j2", config.deploy.fly),
            "Procfile": ("Procfile.j2", config.deploy.heroku),
            "railway.json": ("railway.json.j2", config.deploy.railway),
        }

        for out_name, (template, enabled) in targets.items():
            if not enabled:
                continue
            out = self.render(template, output_dir, out_name, ctx, force=force)
            if out is not None:
                generated.append(out)

        return generated

    def _build_context(self, config: PyGenKitConfig) -> dict[str, Any]:
        return {
            "project": {"name": config.project.name},
            "deploy": {
                "primary_region": config.deploy.primary_region,
                "port": config.deploy.port,
                "memory": config.deploy.memory,
                "cpu_kind": config.deploy.cpu_kind,
                "cpus": config.deploy.cpus,
            },
        }
