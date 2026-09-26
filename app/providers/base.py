from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.models.schemas import ChatRequest, ChatResponse


class ProviderError(Exception):
    pass


class ProviderUnavailable(ProviderError):
    pass


class ProviderTimeout(Exception):
    pass


class Provider(ABC):
    name: str
    models: set[str]

    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        ...

    async def stream(self, request: ChatRequest) -> AsyncIterator[str]:
        response = await self.chat(request)
        for token in response.content.split():
            yield token + " "
