from app.services.ai.contracts import AiCapability
from app.services.ai.costing import estimate_ai_cost
from app.services.ai.registry import get_capability_metadata


def test_cost_envelope_records_numeric_size_without_payload_text():
    metadata = get_capability_metadata(AiCapability.CLINICAL_EXTRACTION)

    envelope = estimate_ai_cost(
        metadata,
        request_contents={"prompt": "patient fixture text " * 10, "audio": b"1234"},
        response_payload={"summary": "generated fixture text"},
    )
    audit_metadata = envelope.audit_metadata(latency_ms=12)

    assert envelope.request_units > 0
    assert envelope.response_units > 0
    assert envelope.estimated_cost_usd >= 0
    assert audit_metadata["latency_ms"] == 12
    assert "patient fixture text" not in str(audit_metadata)
    assert "generated fixture text" not in str(audit_metadata)


def test_local_deterministic_provider_costs_zero():
    metadata = get_capability_metadata(AiCapability.BERNIE_BOOKING_SUGGEST_SLOTS)

    envelope = estimate_ai_cost(
        metadata,
        request_contents={"slot_search": "fixture"},
        response_payload={"candidates": [1, 2, 3]},
    )

    assert envelope.default_provider == "local_deterministic"
    assert envelope.estimated_cost_usd == 0.0
