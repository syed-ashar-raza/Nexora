# Nexora Architecture

Nexora separates transport, authentication, inference orchestration, provider integration, reliability, and observability.

## Request lifecycle

1. FastAPI validates the request.
2. Authentication runs when an API key is configured.
3. A request ID is propagated in the response.
4. The inference service determines healthy providers.
5. The router selects the requested model/provider.
6. The circuit breaker prevents calls to repeatedly failing providers.
7. Retry logic handles transient provider errors.
8. The provider returns a normalized response.
9. Prometheus records request, latency, and token metrics.

This separation keeps provider-specific implementation out of the HTTP layer and makes reliability behavior independently testable.
