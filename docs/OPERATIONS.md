# Operations

## Local

```powershell
uvicorn app.main:app --reload
```

## Docker

```powershell
docker compose up --build
```

## Checks

```powershell
pytest -q
ruff check app tests
```

## Health

`GET /health` verifies process health.

`GET /ready` verifies the service has registered providers.

`GET /metrics` exposes Prometheus-compatible metrics.

## Observability

Nexora exposes:

- `nexora_requests_total` - inference request count by model and status.
- `nexora_request_latency_seconds` - inference latency histogram by model.
- `nexora_tokens_total` - prompt and completion token counters by model.

Prometheus collects these metrics using `monitoring/prometheus.yml`.

Prometheus runs on port `9090` in Docker Compose.

A healthy Nexora scrape should report `up = 1` for the `nexora` job.

## Security

Set `NEXORA_API_KEY` in the environment. Never commit `.env`.
