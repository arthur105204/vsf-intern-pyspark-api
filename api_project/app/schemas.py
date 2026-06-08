from __future__ import annotations

from pydantic import BaseModel


class PredictionResponse(BaseModel):
    user_id: str
    prediction_score: float
    prediction_label: int
    model_version: str
    scored_at: str
    request_id: str
    trace_id: str
    timestamp: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    request_id: str
    trace_id: str
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    record_count: int | None
    cache_size: int
    cache_hits: int
    cache_misses: int
