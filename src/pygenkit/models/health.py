from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CategoryScore:
    name: str
    weight: float  # contribution to total (0.0 to 1.0, sum = 1.0)
    score: float = 0.0  # 0.0 to 1.0
    passed: int = 0
    total: int = 0
    details: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


@dataclass
class HealthReport:
    score: int  # 0-100
    categories: dict[str, CategoryScore] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
