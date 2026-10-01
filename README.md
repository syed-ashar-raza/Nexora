# Nexora

**Production AI inference infrastructure platform**

Nexora is a FastAPI-based inference gateway designed around the reliability and operational concerns of production AI serving: provider abstraction, configurable routing, retries, timeouts, circuit breaking, authentication, rate limiting, request tracing, streaming responses, and Prometheus observability.

> **Version:** 1.0.0
> **Status:** Portfolio-ready
> **License:** Apache-2.0
> **Python:** 3.14+

## Why Nexora

AI applications often depend on external or local model providers whose availability, latency, and failure behavior cannot be assumed.

Nexora places an infrastructure layer between an application and model providers:

    Client
      |
      v
    FastAPI Inference Gateway
      |
      +-- Authentication
      +-- Rate Limiting
      +-- Request ID
      |
      v
    Routing Layer
      |
      +-- Health-aware
      +-- Cost-based
      +-- Round-robin
      |
      v
    Reliability Layer
      |
      +-- Timeout
      +-- Retry
      +-- Circuit Breaker
      |
      v
    Provider Abstraction
      |
      +-- Model Providers
      |
      v
    Prometheus Metrics

## Core Capabilities

### Inference Gateway

- FastAPI HTTP API
- Structured request and response schemas
- Provider abstraction
- Model-aware routing
- SSE response streaming
- Request correlation through `X-Request-ID`

### Reliability Engineering

- Per-attempt request timeouts
- Configurable retries for transient provider failures
- Circuit breaker with `closed`, `open`, and `half_open` states
- Provider availability awareness
- Structured provider error responses
- Graceful failure when a requested model is unavailable

### Traffic Protection

- Optional Bearer API-key authentication
- Configurable in-process rate limiting
- Configurable request limits and windows

### Routing

Nexora supports configurable provider-routing policies:

- `health_aware`
- `cost`
- `round_robin`

The routing layer is provider-agnostic and can support multiple providers serving the same model as additional integrations are added.

### Observability

Prometheus metrics include:

- Request counts
- Request latency
- Token usage
- Provider-related inference metrics

Operational endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /health` | Liveness and health |
| `GET /ready` | Readiness and provider availability |
| `GET /metrics` | Prometheus metrics |
| `GET /v1/providers` | Provider health information |
| `POST /v1/chat` | Inference |
| `POST /v1/chat/stream` | SSE response streaming |

Interactive API documentation is available through FastAPI's generated `/docs` interface.

## Reliability Behavior

Nexora deliberately treats provider failures as infrastructure events rather than leaking raw exceptions to clients.

Example failure flow:

    Provider failure
          |
          v
    Retry transient failure
          |
          +-- succeeds ----------> successful response
          |
          +-- continues failing
                        |
                        v
                  Circuit breaker
                        |
                        v
                 Provider unavailable
                        |
                        v
                 Structured 5xx response

Timeouts are converted into a structured gateway response, while unexpected application exceptions are not blindly retried.

## Current Provider Implementation

Version 1.0.0 includes mock providers for deterministic infrastructure testing:

- `nexora-mock`
- `mock-429`
- `mock-500`
- `mock-slow`

The provider interface is separated from the gateway, routing, and reliability layers so real model-provider integrations can be added without redesigning the core infrastructure.

## Configuration

Configuration is environment-driven through Pydantic Settings.

Example:

    NEXORA_APP_NAME=Nexora
    NEXORA_ENVIRONMENT=development
    NEXORA_API_KEY=
    NEXORA_RATE_LIMIT=60
    NEXORA_RATE_WINDOW_SECONDS=60
    NEXORA_REQUEST_TIMEOUT_SECONDS=30
    NEXORA_MAX_RETRIES=2
    NEXORA_CIRCUIT_FAILURE_THRESHOLD=5
    NEXORA_CIRCUIT_RECOVERY_SECONDS=30
    NEXORA_ROUTING_POLICY=health_aware
    NEXORA_LOG_LEVEL=INFO

Copy `.env.example` to `.env` for local configuration.

## Local Development

Install development dependencies:

    python -m pip install -e ".[dev]"

Run the API:

    uvicorn app.main:app --reload

Open the API documentation:

    http://localhost:8000/docs

## Example Request

    Invoke-RestMethod `
      -Method Post `
      -Uri http://localhost:8000/v1/chat `
      -ContentType "application/json" `
      -Body '{"model":"nexora-mock","messages":[{"role":"user","content":"Hello Nexora"}]}'

Example response shape:

    {
      "id": "nex-...",
      "model": "nexora-mock",
      "content": "Nexora response: Hello Nexora",
      "provider": "nexora-mock",
      "usage": {
        "prompt_tokens": 2,
        "completion_tokens": 4,
        "total_tokens": 6
      },
      "latency_ms": 1.2
    }

## Testing

Run the complete test suite:

    pytest -q

Current validation:

    16 passed

Run static analysis:

    ruff check .

Current validation:

    All checks passed!

The test suite covers:

- Health and readiness
- Request validation
- Chat inference
- Streaming
- Circuit breaker behavior
- Rate limiting
- Provider routing
- Retry behavior
- Timeout handling
- Unexpected-error handling

## Docker

Build the image:

    docker build -t nexora:1.0.0 .

Run the container:

    docker run --rm -d --name nexora -p 8000:8000 nexora:1.0.0

Verify readiness:

    Invoke-RestMethod http://localhost:8000/ready

Expected:

    status    providers
    ------    ---------
    ready     4

Stop the container:

    docker stop nexora

## ☸️ Kubernetes

Nexora includes a Kubernetes deployment manifest under `k8s/`.

The deployment was validated locally with Minikube and Docker using:

- Kubernetes deployment
- Nexora container image
- Liveness probe on `/health`
- Readiness probe on `/ready`
- Kubernetes Service exposure
- Running pod verification
- API health and inference verification

Local validation confirmed the application running successfully inside Kubernetes with the configured health and readiness probes.

This demonstrates container orchestration and operational deployment patterns in addition to the core inference gateway implementation.

## CI

GitHub Actions validates the project with automated quality checks.

Workflow:

    Push / Pull Request
            |
            +-- Install dependencies
            +-- Ruff
            +-- Pytest

## Architecture

Detailed architecture documentation:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/OPERATIONS.md`](docs/OPERATIONS.md)

## Project Structure

    Nexora/
    ├── app/
    │   ├── core/
    │   ├── models/
    │   ├── observability/
    │   ├── providers/
    │   ├── reliability/
    │   ├── routing/
    │   ├── security/
    │   └── services/
    ├── tests/
    ├── docs/
    ├── deployments/
    ├── .github/
    │   └── workflows/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── .env.example
    ├── pyproject.toml
    └── README.md

## Engineering Focus

Nexora demonstrates production-oriented AI engineering beyond model development:

- API and service architecture
- Provider abstraction
- Failure isolation
- Reliability patterns
- Traffic control
- Configurable routing
- Observability
- Automated testing
- Containerized deployment
- CI validation
- Operational documentation

The project intentionally focuses on **inference infrastructure** rather than duplicating RAG, agent orchestration, or model-training/MLOps functionality.

## Release

### v1.0.0

Initial production-oriented portfolio release.

Validated locally with:

- 16 automated tests passing
- Ruff checks passing
- Docker image build passing
- Docker container startup passing
- Readiness endpoint returning 4 available providers
- GitHub Actions CI configured
- Git tag `v1.0.0`

## License

Apache-2.0
