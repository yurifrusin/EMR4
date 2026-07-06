from app.services.ai.contracts import AiCapability
from app.services.ai.costing import AiCostEnvelope, estimate_ai_cost
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
    assert audit_metadata["budget_limit_present"] is False
    assert audit_metadata["budget_threshold_ratio"] is None
    assert audit_metadata["budget_warning"] is False


def test_local_deterministic_provider_costs_zero():
    metadata = get_capability_metadata(AiCapability.BERNIE_BOOKING_SUGGEST_SLOTS)

    envelope = estimate_ai_cost(
        metadata,
        request_contents={"slot_search": "fixture"},
        response_payload={"candidates": [1, 2, 3]},
    )

    assert envelope.default_provider == "local_deterministic"
    assert envelope.estimated_cost_usd == 0.0


def test_cost_envelope_records_budget_status_when_limit_exists():
    envelope = AiCostEnvelope(
        default_provider="gemini_vertex",
        default_project="bernie-emr4-dev",
        default_location="australia-southeast1",
        model_name="gemini-2.5-flash",
        request_units=100,
        response_units=10,
        estimated_cost_usd=0.85,
        max_estimated_cost_usd=1.0,
    )

    audit_metadata = envelope.audit_metadata()

    assert audit_metadata["budget_limit_present"] is True
    assert audit_metadata["budget_threshold_ratio"] == 0.85
    assert audit_metadata["budget_warning"] is True

# ---- Adversarial test lane: Sprint Access AI cost envelope hardening ----

def test_capped_capability_has_budget_threshold_in_registry():
    from app.services.ai.registry import get_capability_metadata
    metadata = get_capability_metadata(AiCapability.PROVIDER_LIVE_SMOKE)
    assert metadata.max_estimated_cost_usd == 1.0

def test_capped_capability_budget_threshold_appears_in_cost_envelope():
    from app.services.ai.registry import get_capability_metadata
    from app.services.ai.costing import estimate_ai_cost
    metadata = get_capability_metadata(AiCapability.PROVIDER_LIVE_SMOKE)
    envelope = estimate_ai_cost(metadata, request_contents={"smoke": "test"}, response_payload={"ok": True})
    assert envelope.max_estimated_cost_usd == 1.0
    assert envelope.estimated_cost_usd <= envelope.max_estimated_cost_usd

def test_capped_capability_budget_threshold_in_audit_metadata():
    from app.services.ai.registry import get_capability_metadata
    from app.services.ai.costing import estimate_ai_cost
    metadata = get_capability_metadata(AiCapability.PROVIDER_LIVE_SMOKE)
    envelope = estimate_ai_cost(metadata, request_contents={"smoke": "test"})
    audit_meta = envelope.audit_metadata(latency_ms=5)
    assert audit_meta["max_estimated_cost_usd"] == 1.0
    assert "latency_ms" in audit_meta
    assert "estimated_cost_usd" in audit_meta

def test_uncapped_capability_has_no_budget_threshold():
    from app.services.ai.registry import get_capability_metadata
    metadata = get_capability_metadata(AiCapability.CLINICAL_EXTRACTION)
    assert metadata.max_estimated_cost_usd is None

def test_uncapped_capability_cost_envelope_has_none_threshold():
    from app.services.ai.registry import get_capability_metadata
    from app.services.ai.costing import estimate_ai_cost
    metadata = get_capability_metadata(AiCapability.CLINICAL_EXTRACTION)
    envelope = estimate_ai_cost(metadata, request_contents={"prompt": "test fixture"}, response_payload={"diagnoses": []})
    assert envelope.max_estimated_cost_usd is None
    assert envelope.estimated_cost_usd > 0

def test_cost_envelope_audit_metadata_omits_prompt_and_phi():
    audit = estimate_ai_cost(
        get_capability_metadata(AiCapability.CLINICAL_EXTRACTION),
        request_contents={"prompt": "patient history of chest pain and shortness of breath"},
        response_payload={"diagnoses": ["D001", "D002"]},
    ).audit_metadata()
    audit_str = str(audit)
    assert "patient" not in audit_str
    assert "chest pain" not in audit_str
    assert "shortness of breath" not in audit_str
    assert "D001" not in audit_str
