import time

from app.core.config import settings
from app.models.schemas import ChatRequest, ChatResponse
from app.observability.metrics import LATENCY, REQUESTS, RETRIES, TOKENS
from app.providers.base import ProviderError, ProviderTimeout, ProviderUnavailable
from app.providers.registry import ProviderRegistry
from app.reliability.bulkhead import Bulkhead, BulkheadFull
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
        self.bulkheads = {
            p.name: Bulkhead(settings.provider_concurrency_limit) 
            for p in self.registry.all()
        }

    async def chat(self, request: ChatRequest) -> ChatResponse:
        healthy = {
            p.name
            for p in self.registry.all()
            if self.breakers[p.name].allow()
        }
        attempted: set[str] = set()
        failover_count = 0

        while True:
            available = healthy - attempted
            if not available:
                raise ProviderUnavailable(
                    f"Requested model '{request.model}' is unavailable"
                )

            provider = self.router.choose(request.model, available)
            attempted.add(provider.name)

            breaker = self.breakers[provider.name]
            bulkhead = self.bulkheads[provider.name]
            started = time.perf_counter()
            acquired = False

            try:
                await bulkhead.acquire()
                acquired = True
                response = await with_retry(
                    lambda provider=provider: provider.chat(request),
                    settings.max_retries,
                    settings.request_timeout_seconds,
                    settings.retry_backoff_seconds,
                    settings.retry_max_backoff_seconds,
                    settings.retry_jitter_seconds,
                    lambda _: RETRIES.labels(request.model).inc(),
                    settings.retry_budget_seconds,
                )
                breaker.success()
                elapsed = time.perf_counter() - started
                response.latency_ms = elapsed * 1000
                REQUESTS.labels(request.model, "success").inc()
                LATENCY.labels(request.model).observe(elapsed)
                TOKENS.labels(request.model, "prompt").inc(
                    response.usage.prompt_tokens
                )
                TOKENS.labels(request.model, "completion").inc(
                    response.usage.completion_tokens
                )
                return response
            except BulkheadFull:
                REQUESTS.labels(request.model, "bulkhead_full").inc()
                raise
            except (ProviderError, ProviderTimeout):
                breaker.failure()
                REQUESTS.labels(request.model, "error").inc()
                if not (healthy - attempted):
                    raise
                if failover_count >= settings.max_provider_failovers:
                    raise
                failover_count += 1
            finally:
                if acquired:
                    await bulkhead.release()




