import uuid

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.core.config import settings
from app.models.schemas import ChatRequest, ProviderInfo
from app.providers.base import (
    ProviderError,
    ProviderTimeout,
    ProviderUnavailable,
)
from app.security.auth import authenticate
from app.services.inference import InferenceService

app = FastAPI(
    title="Nexora",
    version="1.0.0",
    description="Production AI inference infrastructure platform.",
)
service = InferenceService()


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(ProviderUnavailable)
async def provider_unavailable_handler(
    request: Request,
    exc: ProviderUnavailable,
):
    request_id = getattr(request.state, "request_id", "")
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "type": "provider_unavailable",
                "message": str(exc),
            },
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


@app.exception_handler(ProviderTimeout)
async def provider_timeout_handler(
    request: Request,
    exc: ProviderTimeout,
):
    request_id = getattr(request.state, "request_id", "")
    return JSONResponse(
        status_code=504,
        content={
            "error": {
                "type": "provider_timeout",
                "message": str(exc),
            },
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


@app.exception_handler(ProviderError)
async def provider_error_handler(
    request: Request,
    exc: ProviderError,
):
    request_id = getattr(request.state, "request_id", "")
    return JSONResponse(
        status_code=502,
        content={
            "error": {
                "type": "provider_error",
                "message": str(exc),
            },
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "1.0.0",
    }


@app.get("/ready")
async def ready():
    return {
        "status": "ready",
        "providers": len(service.registry.all()),
    }


@app.get("/metrics")
async def metrics():
    return StreamingResponse(
        iter([generate_latest()]),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.get(
    "/v1/providers",
    response_model=list[ProviderInfo],
    dependencies=[Depends(authenticate)],
)
async def providers():
    return [
        ProviderInfo(
            name=p.name,
            healthy=service.breakers[p.name].is_available(),
            models=sorted(p.models),
        )
        for p in service.registry.all()
    ]


@app.post("/v1/chat", dependencies=[Depends(authenticate)])
async def chat(request: ChatRequest):
    return await service.chat(request)


@app.post("/v1/chat/stream", dependencies=[Depends(authenticate)])
async def chat_stream(request: ChatRequest):
    response = await service.chat(request)

    async def events():
        for token in response.content.split():
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
    )
