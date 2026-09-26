import asyncio
import time
import uuid

from app.models.schemas import ChatRequest, ChatResponse, Usage
from app.providers.base import Provider, ProviderError


class MockProvider(Provider):
    def __init__(
        self,
        name: str = "nexora-mock",
        cost: float = 1.0,
    ):
        self.name = name
        self.models = {name}
        self.cost = cost

    async def chat(self, request: ChatRequest) -> ChatResponse:
        text = request.messages[-1].content

        if request.model == "mock-429":
            raise ProviderError("simulated rate limit")

        if request.model == "mock-500":
            raise ProviderError("simulated provider failure")

        if request.model == "mock-slow":
            await asyncio.sleep(0.25)

        started = time.perf_counter()
        content = f"Nexora response: {text}"
        prompt_tokens = max(
            1,
            sum(len(message.content.split()) for message in request.messages),
        )
        completion_tokens = len(content.split())

        return ChatResponse(
            id=f"nex-{uuid.uuid4().hex[:12]}",
            model=request.model,
            content=content,
            provider=self.name,
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            latency_ms=(time.perf_counter() - started) * 1000,
        )
