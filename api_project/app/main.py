from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api_project.app.cache import InMemoryCache
from api_project.app.repository import PREDICTION_DATA_PATH, PredictionRepository
from api_project.app.schemas import ErrorResponse, HealthResponse, PredictionResponse


repository = PredictionRepository()
cache = InMemoryCache()


@asynccontextmanager
async def lifespan(app: FastAPI):
    repository.load()
    yield


app = FastAPI(
    title="Bank Marketing Prediction Lookup API",
    version="0.1.0",
    lifespan=lifespan,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def metadata() -> dict[str, str]:
    return {
        "request_id": f"req_{uuid4().hex[:12]}",
        "trace_id": f"trace_{uuid4().hex}",
        "timestamp": utc_now(),
    }


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    body = ErrorResponse(
        error="INTERNAL_SERVER_ERROR",
        message="Unable to retrieve prediction at this time.",
        **metadata(),
    )
    return JSONResponse(status_code=500, content=body.model_dump())


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    repository.load()
    return HealthResponse(
        status="ok",
        record_count=repository.record_count,
        cache_size=cache.size,
        cache_hits=cache.hits,
        cache_misses=cache.misses,
    )


@app.get(
    "/prediction/{user_id}",
    response_model=PredictionResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def get_prediction(user_id: str) -> PredictionResponse | JSONResponse:
    meta = metadata()

    record: dict[str, Any] | None = cache.get(user_id)
    if record is None:
        record = repository.get(user_id)
        if record is not None:
            cache.set(user_id, record)

    if record is None:
        body = ErrorResponse(
            error="USER_NOT_FOUND",
            message=f"No prediction found for user_id={user_id}",
            **meta,
        )
        return JSONResponse(status_code=404, content=body.model_dump())

    return PredictionResponse(**record, **meta)


@app.get("/metadata")
def metadata_endpoint() -> dict[str, str]:
    return {
        "data_source": str(PREDICTION_DATA_PATH),
        "serving_mode": "lookup_precomputed_predictions",
    }
