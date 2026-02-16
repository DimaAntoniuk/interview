"""LLM client interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class LLMMessage:
    """A message in the conversation."""

    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Response from LLM completion."""

    content: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0


class LLMClient(ABC):
    """Abstract interface for LLM clients."""

    @abstractmethod
    async def complete(self, messages: list[LLMMessage], max_tokens: int = 1000) -> LLMResponse:
        """Generate a completion for the given messages."""
        pass

    @abstractmethod
    async def stream(
        self, messages: list[LLMMessage], max_tokens: int = 1000
    ) -> AsyncIterator[str]:
        """Stream a completion for the given messages."""
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in the given text."""
        pass
