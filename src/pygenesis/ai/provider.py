from __future__ import annotations

import json
import os
import urllib.request
from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, system: str, user: str, **kwargs: Any) -> str:
        ...


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        if not self.api_key:
            msg = "OPENAI_API_KEY is not set"
            raise ValueError(msg)
        self.model = model
        self._base_url = "https://api.openai.com/v1/chat/completions"

    def complete(self, system: str, user: str, **kwargs: Any) -> str:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            **kwargs,
        }
        req = urllib.request.Request(
            self._base_url,
            data=json.dumps(body).encode(),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result: dict[str, Any] = json.loads(resp.read().decode())

        choices = result.get("choices", [])
        if not choices:
            msg = f"OpenAI API returned no choices: {result}"
            raise RuntimeError(msg)
        return str(choices[0]["message"]["content"])


def create_provider(provider_name: str = "openai", **kwargs: Any) -> LLMProvider:
    if provider_name == "openai":
        return OpenAIProvider(**kwargs)
    msg = f"Unknown provider: {provider_name}"
    raise ValueError(msg)
