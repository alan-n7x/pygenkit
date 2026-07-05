from __future__ import annotations

import re


class TemplateFilters:
    @staticmethod
    def snake_case(value: str) -> str:
        s = re.sub(r"[-\s]+", "_", value)
        return s.lower().strip("_")

    @staticmethod
    def kebab_case(value: str) -> str:
        s = re.sub(r"[_\s]+", "-", value)
        return s.lower().strip("-")

    @staticmethod
    def pascal_case(value: str) -> str:
        return "".join(word.capitalize() for word in re.split(r"[-_\\s]", value))

    @staticmethod
    def camel_case(value: str) -> str:
        s = TemplateFilters.pascal_case(value)
        return s[0].lower() + s[1:] if s else s

    @staticmethod
    def module_name(value: str) -> str:
        return TemplateFilters.snake_case(value)

    @staticmethod
    def capitalise(value: str) -> str:
        return value.capitalize()

    @staticmethod
    def get_filters() -> dict[str, object]:
        return {
            "snake_case": TemplateFilters.snake_case,
            "kebab_case": TemplateFilters.kebab_case,
            "pascal_case": TemplateFilters.pascal_case,
            "camel_case": TemplateFilters.camel_case,
            "module_name": TemplateFilters.module_name,
            "capitalise": TemplateFilters.capitalise,
        }
