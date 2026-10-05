import time

from app.core.config import settings
from app.models.schemas import ChatRequest, ChatResponse
from app.observability.metrics import LATENCY, REQUESTS, RETRIES, TOKENS
from app.providers.registry import ProviderRegistry
from app.reliability.circuit_breaker import CircuitBreaker
from app.reliability.retry import with_retry
from app.routing.policy import Router


class InferenceService:
    def __init__(self) -> None:
        self.registry = ProviderRegistry()
        self.breakers = {
            p.name: CircuitBreaker(
                settings.circuit_failure_threshold,
                settings.circuit_recovery_seconds,
            )
            for p in self.registry.all()
        }
        self.router = Router(self.registry.all(), settings.routing_policy)

    async def chat(self, request: ChatRequest) -> ChatResponse:
        healthy = {p.name for p in self.registry.all() if self.breakers[p.name].allow()}
        provider = self.router.choose(request.model, healthy)
        breaker = self.breakers[provider.name]
        started = time.perf_counter()

        try:
            response = await with_retry(
                lambda: provider.chat(request),
                settings.max_retries,
                settings.request_timeout_seconds,
                settings.retry_backoff_seconds,
                settings.retry_max_backoff_seconds,
                settings.retry_jitter_seconds,
                lambda _: RETRIES.labels(request.model).inc(),
            )
            breaker.success()
            elapsed = time.perf_counter() - started
            response.latency_ms = elapsed * 1000
            REQUESTS.labels(request.model, "success").inc()
            LATENCY.labels(request.model).observe(elapsed)
            TOKENS.labels(request.model, "prompt").inc(response.usage.prompt_tokens)
            TOKENS.labels(request.model, "completion").inc(response.usage.completion_tokens)
            return response
        except Exception:
            breaker.failure()
            REQUESTS.labels(request.model, "error").inc()
            raise
