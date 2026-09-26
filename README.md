# Nexora

**Production AI inference infrastructure platform.**

Nexora provides a unified FastAPI inference gateway with provider abstraction, health-aware routing, retries, timeouts, circuit breakers, fallback behavior, API-key authentication, request IDs, Prometheus metrics, and streaming responses.

## Architecture

```text
Client
  │
  ▼
FastAPI Gateway
  ├── Authentication / Request ID
  ├── Rate Limiting
  ▼
Inference Service
  ├── Routing Policy
  ├── Provider Health
  ├── Timeout / Retry
  ├── Circuit Breaker
  └── Fallback
  ▼
Provider Abstraction
  ├── Mock Provider
  └── HTTP Provider Adapter
  ▼
Response / Stream
  │
  └── Prometheus Metrics
```

## Quick start

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
pytest
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

If `NEXORA_API_KEY` is set, send `Authorization: Bearer <key>`.

## API

`POST /v1/chat`

```json
{
  "model": "nexora-mock",
  "messages": [
    {"role": "user", "content": "Hello Nexora"}
  ],
  "stream": false
}
```

Useful endpoints:

- `GET /health`
- `GET /ready`
- `GET /metrics`
- `GET /v1/providers`
- `POST /v1/chat`
- `POST /v1/chat/stream`

## Design principles

- Keep provider-specific behavior behind an interface.
- Prefer explicit reliability controls over hidden magic.
- Fail fast on invalid requests.
- Keep observability available on every request.
- Avoid introducing orchestration frameworks without measurable ROI.
- Never claim production provider support until an adapter is configured and tested.

## License

Apache-2.0
