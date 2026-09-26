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

`GET /metrics` exposes Prometheus metrics.

## Security

Set `NEXORA_API_KEY` in the environment. Never commit `.env`.
