from __future__ import annotations

from pathlib import Path
from typing import Any

from pygenesis.generators.base import BaseGenerator
from pygenesis.models.config import PyGenesisConfig


class DockerGenerator(BaseGenerator):
    def __init__(self) -> None:
        super().__init__("docker")

    def generate(
        self,
        config: PyGenesisConfig,
        output_dir: str | Path,
        force: bool = False,
    ) -> list[Path]:
        generated: list[Path] = []
        ctx = self._build_context(config)

        out = self.render("Dockerfile.j2", output_dir, "Dockerfile", ctx, force=force)
        if out is not None:
            generated.append(out)

        out = self.render(
            "docker-compose.yml.j2", output_dir, "docker-compose.yml", ctx, force=force
        )
        if out is not None:
            generated.append(out)

        return generated

    def _build_context(self, config: PyGenesisConfig) -> dict[str, Any]:
        return {
            "project": {"name": config.project.name},
            "docker": {
                "base_image": config.docker.base_image,
                "port": config.docker.port,
                "volumes": config.docker.volumes,
            },
        }
