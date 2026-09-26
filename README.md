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

```text
Client
  â”‚
  â–¼
FastAPI Inference Gateway
  â”‚
  â”œâ”€â”€ Authentication
  â”œâ”€â”€ Rate Limiting
  â”œâ”€â”€ Request ID
  â”‚
  â–¼
Routing Layer
  â”‚
  â”œâ”€â”€ Health-aware
  â”œâ”€â”€ Cost-based
  â””â”€â”€ Round-robin
  â”‚
  â–¼
Reliability Layer
  â”‚
  â”œâ”€â”€ Timeout
  â”œâ”€â”€ Retry
  â””â”€â”€ Circuit Breaker
  â”‚
  â–¼
Provider Abstraction
  â”‚
  â””â”€â”€ Model Providers
  â”‚
  â–¼
Prometheus Metrics
Core capabilities
Inference gateway
FastAPI HTTP API
Structured request and response schemas
Provider abstraction
Model-aware routing
SSE response streaming
Request correlation through X-Request-ID
Reliability engineering
Per-attempt request timeouts
Configurable retries for transient provider failures
Circuit breaker with closed, open, and half_open states
Provider availability awareness
Structured provider error responses
Graceful failure when a requested model is unavailable
Traffic protection
Optional Bearer API-key authentication
Configurable in-process rate limiting
Configurable request limits and windows
Routing
health_aware
cost
round_robin

The routing layer is provider-agnostic and can support multiple providers serving the same model as additional integrations are added.

Observability

Prometheus metrics include:

Request counts
Request latency
Token usage
Provider-related inference metrics

Operational endpoints:

EndpointPurpose
GET /healthLiveness/health
GET /readyReadiness and provider availability
GET /metricsPrometheus metrics
GET /v1/providersProvider health information
POST /v1/chatInference
POST /v1/chat/streamSSE response streaming

Interactive API documentation is available through FastAPI's generated /docs interface.

Reliability behavior

Nexora deliberately treats provider failures as infrastructure events rather than leaking raw exceptions to clients.

Examples:

Provider failure
      â”‚
      â–¼
Retry transient failure
      â”‚
      â”œâ”€â”€ succeeds â”€â”€â–º successful response
      â”‚
      â””â”€â”€ continues failing
                    â”‚
                    â–¼
              Circuit breaker
                    â”‚
                    â–¼
             Provider unavailable
                    â”‚
                    â–¼
             Structured 5xx response

Timeouts are converted into a structured gateway response, while unexpected application exceptions are not blindly retried.

Current provider implementation

Version 1.0.0 includes mock providers for deterministic infrastructure testing:

nexora-mock
mock-429
mock-500
mock-slow

The provider interface is separated from the gateway, routing, and reliability layers so real model-provider integrations can be added without redesigning the core infrastructure.

Configuration

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

Copy .env.example to .env for local configuration.

Local development

Create the environment and install development dependencies:

python -m pip install -e ".[dev]"

Run the API:

uvicorn app.main:app --reload

Open the API documentation at:

http://localhost:8000/docs
Example request
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
Testing

Run the complete test suite:

pytest -q

Current validation:

16 passed

Run static analysis:

ruff check .

Current validation:

All checks passed!

The test suite covers:

Health/readiness
Request validation
Chat inference
Streaming
Circuit breaker behavior
Rate limiting
Provider routing
Retry behavior
Timeout handling
Unexpected-error handling
Docker

Build the production image:

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
CI

GitHub Actions validates the project with automated quality checks.

Workflow:

Push / Pull Request
        â”‚
        â”œâ”€â”€ Install dependencies
        â”œâ”€â”€ Ruff
        â””â”€â”€ Pytest
Architecture

Detailed architecture documentation:

docs/ARCHITECTURE.md
docs/OPERATIONS.md
Project structure
Nexora/
â”œâ”€â”€ app/
â”‚   â”œâ”€â”€ core/
â”‚   â”œâ”€â”€ models/
â”‚   â”œâ”€â”€ observability/
â”‚   â”œâ”€â”€ providers/
â”‚   â”œâ”€â”€ reliability/
â”‚   â”œâ”€â”€ routing/
â”‚   â”œâ”€â”€ security/
â”‚   â””â”€â”€ services/
â”œâ”€â”€ tests/
â”œâ”€â”€ docs/
â”œâ”€â”€ deployments/
â”œâ”€â”€ .github/
â”‚   â””â”€â”€ workflows/
â”œâ”€â”€ Dockerfile
â”œâ”€â”€ docker-compose.yml
â”œâ”€â”€ .env.example
â”œâ”€â”€ pyproject.toml
â””â”€â”€ README.md
Engineering focus

Nexora demonstrates production-oriented AI engineering beyond model development:

API and service architecture
Provider abstraction
Failure isolation
Reliability patterns
Traffic control
Configurable routing
Observability
Automated testing
Containerized deployment
CI validation
Operational documentation

The project intentionally focuses on inference infrastructure rather than duplicating RAG, agent orchestration, or model-training/MLOps functionality.

Release
v1.0.0

Initial production-oriented portfolio release.

Validated locally with:

16 automated tests passing
Ruff checks passing
Docker image build passing
Docker container startup passing
Readiness endpoint returning 4 available providers
GitHub Actions CI configured
Git tag v1.0.0
License

Apache-2.0
