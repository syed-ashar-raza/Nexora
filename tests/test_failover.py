import pytest

from app.models.schemas import ChatRequest, ChatResponse, Usage
from app.providers.base import Provider, ProviderError
from app.reliability.bulkhead import Bulkhead
from app.reliability.circuit_breaker import CircuitBreaker
from app.services.inference import InferenceService


class FailingProvider(Provider):
    def __init__(self, name: str, model: str) -> None:
        self.name = name
        self.models = {model}
        self.cost = 1.0
        self.calls = 0

    async def chat(self, request: ChatRequest) -> ChatResponse:
        self.calls += 1
        raise ProviderError("simulated provider failure")


class SuccessfulProvider(Provider):
    def __init__(self, name: str, model: str) -> None:
        self.name = name
        self.models = {model}
        self.cost = 1.0
        self.calls = 0

    async def chat(self, request: ChatRequest) -> ChatResponse:
        self.calls += 1
        return ChatResponse(
            id="test-response",
            model=request.model,
            content="fallback success",
            provider=self.name,
            usage=Usage(
                prompt_tokens=1,
                completion_tokens=2,
                total_tokens=3,
            ),
            latency_ms=0.0,
        )


@pytest.mark.asyncio
async def test_inference_fails_over_to_healthy_provider():
    model = "shared-model"
    primary = FailingProvider("provider-a", model)
    fallback = SuccessfulProvider("provider-b", model)

    service = InferenceService()
    service.registry._providers = {
        primary.name: primary,
        fallback.name: fallback,
    }
    service.breakers = {
        primary.name: CircuitBreaker(),
        fallback.name: CircuitBreaker(),
    }
    service.bulkheads = {
        primary.name: Bulkhead(10),
        fallback.name: Bulkhead(10),
    }
    service.router.providers = [primary, fallback]

    request = ChatRequest(
        model=model,
        messages=[{"role": "user", "content": "hello"}],
    )

    response = await service.chat(request)

    assert response.provider == "provider-b"
    assert primary.calls == 3
    assert fallback.calls == 1
    assert service.breakers[primary.name].failures == 1
    assert service.breakers[fallback.name].failures == 0




@pytest.mark.asyncio
async def test_inference_limits_provider_failovers():
    model = "shared-model"
    primary = FailingProvider("provider-a", model)
    fallback = FailingProvider("provider-b", model)
    third = FailingProvider("provider-c", model)

    service = InferenceService()
    service.registry._providers = {
        primary.name: primary,
        fallback.name: fallback,
        third.name: third,
    }
    service.breakers = {
        primary.name: CircuitBreaker(),
        fallback.name: CircuitBreaker(),
        third.name: CircuitBreaker(),
    }
    service.bulkheads = {
        primary.name: Bulkhead(10),
        fallback.name: Bulkhead(10),
        third.name: Bulkhead(10),
    }
    service.router.providers = [primary, fallback, third]

    request = ChatRequest(
        model=model,
        messages=[{"role": "user", "content": "hello"}],
    )

    with pytest.raises(ProviderError):
        await service.chat(request)

    assert primary.calls == 3
    assert fallback.calls == 3
    assert third.calls == 0
