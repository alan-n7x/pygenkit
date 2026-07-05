from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pygenkit.ai.prompts import SYSTEM_PROMPT, build_user_prompt  # noqa: E402
from pygenkit.ai.provider import LLMProvider, OpenAIProvider, create_provider  # noqa: E402
from pygenkit.ai.review import (  # noqa: E402
    ReviewResult,
    get_pr_diff_from_file,
    review_diff,
)


class MockProvider(LLMProvider):
    def __init__(self, response: str = "mock response") -> None:
        self.response = response
        self.last_system = ""
        self.last_user = ""

    def complete(self, system: str, user: str, **kwargs: Any) -> str:  # noqa: ARG002
        self.last_system = system
        self.last_user = user
        return self.response


def test_create_provider_openai_no_key() -> None:
    import os
    key = os.environ.pop("OPENAI_API_KEY", None)
    try:
        raised = False
        try:
            create_provider("openai")
        except ValueError:
            raised = True
        assert raised
    finally:
        if key:
            os.environ["OPENAI_API_KEY"] = key


def test_mock_provider() -> None:
    provider = MockProvider("fixed response")
    result = provider.complete("sys", "usr")
    assert result == "fixed response"
    assert provider.last_system == "sys"
    assert provider.last_user == "usr"


def test_review_diff_with_mock() -> None:
    provider = MockProvider("## Summary\nLooks good.")
    result = review_diff("diff --git a/file.py b/file.py", provider=provider)
    assert isinstance(result, ReviewResult)
    assert result.raw == "## Summary\nLooks good."
    assert result.error == ""


def test_review_diff_error() -> None:
    provider = MockProvider()
    def _raise(*_a: object, **_kw: object) -> str:  # type: ignore[no-untyped-def]
        raise RuntimeError("API error")
    provider.complete = _raise  # type: ignore[method-assign]
    result = review_diff("some diff", provider=provider)
    assert result.error != ""


def test_review_diff_empty_diff() -> None:
    provider = MockProvider("review")
    result = review_diff("", provider=provider)
    assert result.raw == "review"


def test_build_user_prompt() -> None:
    prompt = build_user_prompt("my diff content", filename_hint="test.py")
    assert "my diff content" in prompt
    assert "test.py" in prompt

    prompt_no_hint = build_user_prompt("diff")
    assert "diff" in prompt_no_hint


def test_system_prompt_content() -> None:
    assert "correctness" in SYSTEM_PROMPT.lower() or "Correctness" in SYSTEM_PROMPT
    assert "security" in SYSTEM_PROMPT.lower()
    assert "maintainability" in SYSTEM_PROMPT.lower()


def test_get_pr_diff_from_file(tmp_path: Path) -> None:
    f = tmp_path / "diff.txt"
    f.write_text("--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old\n+new\n", encoding="utf-8")
    diff = get_pr_diff_from_file(f)
    assert "old" in diff
    assert "new" in diff


def test_openai_provider_no_key() -> None:
    import os
    key = os.environ.pop("OPENAI_API_KEY", None)
    try:
        raised = False
        try:
            OpenAIProvider(api_key="")
        except ValueError:
            raised = True
        assert raised
    finally:
        if key:
            os.environ["OPENAI_API_KEY"] = key


def test_openai_provider_with_key() -> None:
    p = OpenAIProvider(api_key="sk-test123")
    assert p.api_key == "sk-test123"
    assert p.model == "gpt-4o-mini"


def test_review_diff_kwargs_passthrough() -> None:
    class KwargCheckProvider(LLMProvider):
        def __init__(self) -> None:
            self.kwargs: dict[str, Any] = {}

        def complete(self, _system: str, _user: str, **kwargs: Any) -> str:
            self.kwargs = kwargs
            return "ok"

    provider = KwargCheckProvider()
    review_diff("diff", provider=provider, temperature=0.5, max_tokens=100)
    assert provider.kwargs.get("temperature") == 0.5
    assert provider.kwargs.get("max_tokens") == 100
