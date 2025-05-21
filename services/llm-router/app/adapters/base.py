from abc import ABC, abstractmethod
from typing import Dict, List, Any, AsyncIterator

class BaseAdapter(ABC):
    """All providers implement both chat() and chat_stream()."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    @abstractmethod
    async def chat(                 # full response
        self,
        messages: List[Dict[str, str]],
        temperature: float | None,
        max_tokens: int | None,
    ) -> Any: ...

    @abstractmethod
    async def chat_stream(          # generator of chunks
        self,
        messages: List[Dict[str, str]],
        temperature: float | None,
        max_tokens: int | None,
    ) -> AsyncIterator[str]: ...
