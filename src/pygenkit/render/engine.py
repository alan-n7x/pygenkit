from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from pygenkit.utils.filters import TemplateFilters


class RenderEngine:
    def __init__(self, templates_dir: str | Path) -> None:
        self.templates_dir = Path(templates_dir)
        self._env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
        self._env.filters.update(TemplateFilters.get_filters())

    def render_string(self, template: str, context: dict[str, Any]) -> str:
        t = self._env.from_string(template)
        return t.render(**context)

    def render_file(self, template_path: str, context: dict[str, Any]) -> str:
        t = self._env.get_template(template_path)
        return t.render(**context)

    def render_to_file(
        self,
        template_path: str,
        output_path: str | Path,
        context: dict[str, Any],
    ) -> Path:
        content = self.render_file(template_path, context)
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        return out
