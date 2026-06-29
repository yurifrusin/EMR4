"""
Bounded Access AI usage and cost estimates.

The first implementation is deliberately approximate. It records numeric
request/response size and estimated cost metadata without storing prompts,
transcripts, generated notes, patient identifiers, or raw provider payloads.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Any

from app.services.ai.registry import AiCapabilityMetadata


@dataclass(frozen=True)
class AiCostEnvelope:
    default_provider: str
    default_project: str
    default_location: str
    model_name: str | None
    request_units: int
    response_units: int
    estimated_cost_usd: float
    max_estimated_cost_usd: float | None

    def audit_metadata(self, *, latency_ms: int | None = None) -> dict[str, str | int | float | bool | None]:
        metadata: dict[str, str | int | float | bool | None] = {
            "default_provider": self.default_provider,
            "default_project": self.default_project,
            "default_location": self.default_location,
            "model_name": self.model_name,
            "request_units": self.request_units,
            "response_units": self.response_units,
            "estimated_cost_usd": self.estimated_cost_usd,
            "max_estimated_cost_usd": self.max_estimated_cost_usd,
        }
        if latency_ms is not None:
            metadata["latency_ms"] = latency_ms
        return metadata


def estimate_ai_cost(
    metadata: AiCapabilityMetadata,
    *,
    request_contents: Any,
    response_payload: Any = None,
) -> AiCostEnvelope:
    request_units = _estimate_units(request_contents)
    response_units = _estimate_units(response_payload)
    estimated_cost_usd = _estimate_cost_usd(
        provider=metadata.default_provider,
        request_units=request_units,
        response_units=response_units,
    )
    return AiCostEnvelope(
        default_provider=metadata.default_provider,
        default_project=metadata.default_project,
        default_location=metadata.default_location,
        model_name=metadata.model_name,
        request_units=request_units,
        response_units=response_units,
        estimated_cost_usd=estimated_cost_usd,
        max_estimated_cost_usd=metadata.max_estimated_cost_usd,
    )


def _estimate_units(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, bytes):
        return max(1, ceil(len(value) / 1024))
    if isinstance(value, str):
        return max(1, ceil(len(value) / 4))
    if isinstance(value, (int, float, bool)):
        return 1
    if isinstance(value, dict):
        return sum(_estimate_units(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return sum(_estimate_units(item) for item in value)
    return max(1, ceil(len(str(value)) / 4))


def _estimate_cost_usd(*, provider: str, request_units: int, response_units: int) -> float:
    if provider == "local_deterministic":
        return 0.0
    estimated = (request_units * 0.0000002) + (response_units * 0.0000006)
    return round(estimated, 6)
