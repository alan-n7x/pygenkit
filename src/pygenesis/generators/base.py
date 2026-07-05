from __future__ import annotations

from pathlib import Path
from typing import Any

from pygenesis.render.engine import RenderEngine


class BaseGenerator:
    def __init__(self, subdir: str) -> None:
        templates_dir = Path(__file__).resolve().parent.parent / "templates" / subdir
        self._engine = RenderEngine(templates_dir)

    def render(
        self,
        template_name: str,
        output_dir: str | Path,
        output_name: str,
        context: dict[str, Any],
        force: bool = False,
    ) -> Path | None:
        out = Path(output_dir) / output_name
        if out.exists() and not force:
            return None
        return self._engine.render_to_file(template_name, out, context)

    def list_templates(self) -> list[str]:
        d = Path(self._engine.templates_dir)
        if not d.is_dir():
            return []
        return sorted(f.name for f in d.glob("**/*.j2"))
