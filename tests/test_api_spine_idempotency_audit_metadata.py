from pathlib import Path

import pytest

OPENAPI_PATH = Path("docs/api-spine/openapi/appointment-commands.yaml")

APPOINTMENT_COMMAND_PATHS = {
    "/appointments/proposals/create",
    "/appointments/proposals/create/confirm",
    "/appointments/proposals/update",
    "/appointments/proposals/update/confirm",
    "/appointments/proposals/status",
    "/appointments/proposals/status/confirm",
    "/appointments/proposals/delete",
    "/appointments/proposals/delete/confirm",
}

SLOT_SEARCH_READ_PATHS = {
    "/appointments/proposals/slot-search/normalize",
    "/appointments/proposals/slot-search",
    "/appointments/proposals/slot-search/select",
}

REQUIRED_BLOCKED_GATES = {
    "graphql_mutations",
    "model_to_database_writes",
    "memory_rag_graphrag_runtime_wiring",
    "h15_h_series_runtime_imports",
    "broad_historical_diary_trove_mining",
}


def _load_openapi() -> dict:
    pytest.importorskip("yaml", reason="PyYAML not installed.")
    import yaml

    return yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))


def _post_operation(spec: dict, path: str) -> dict:
    return spec["paths"][path]["post"]


def _parameter_refs(operation: dict) -> set[str]:
    return {
        parameter["$ref"]
        for parameter in operation.get("parameters", ())
        if "$ref" in parameter
    }


def test_appointment_command_paths_have_idempotency_and_correlation_headers():
    spec = _load_openapi()

    assert APPOINTMENT_COMMAND_PATHS <= set(spec["paths"])

    for path in sorted(APPOINTMENT_COMMAND_PATHS):
        refs = _parameter_refs(_post_operation(spec, path))
        assert "#/components/parameters/IdempotencyKey" in refs, path
        assert "#/components/parameters/CorrelationId" in refs, path


def test_slot_search_command_style_reads_have_correlation_without_idempotency():
    spec = _load_openapi()

    assert SLOT_SEARCH_READ_PATHS <= set(spec["paths"])

    for path in sorted(SLOT_SEARCH_READ_PATHS):
        refs = _parameter_refs(_post_operation(spec, path))
        assert "#/components/parameters/CorrelationId" in refs, path
        assert "#/components/parameters/IdempotencyKey" not in refs, path


def test_idempotency_and_correlation_parameter_shapes_are_pinned():
    parameters = _load_openapi()["components"]["parameters"]

    idempotency = parameters["IdempotencyKey"]
    assert idempotency["name"] == "Idempotency-Key"
    assert idempotency["in"] == "header"
    assert idempotency["required"] is True
    assert idempotency["schema"]["type"] == "string"
    assert idempotency["schema"]["minLength"] == 8
    assert idempotency["schema"]["maxLength"] == 128

    correlation = parameters["CorrelationId"]
    assert correlation["name"] == "X-Correlation-Id"
    assert correlation["in"] == "header"
    assert correlation["required"] is False


def test_proposal_audit_freshness_and_signed_evidence_metadata_is_structural():
    schemas = _load_openapi()["components"]["schemas"]

    proposal_base = schemas["ProposalEnvelopeBase"]
    assert "audit" in set(proposal_base["required"])
    assert (
        proposal_base["properties"]["audit"]["$ref"]
        == "#/components/schemas/AuditIntent"
    )
    assert (
        proposal_base["properties"]["freshness"]["$ref"]
        == "#/components/schemas/FreshnessRef"
    )
    assert (
        proposal_base["properties"]["signed_confirmation_evidence"]["$ref"]
        == "#/components/schemas/SignedConfirmationEvidence"
    )

    audit_intent = schemas["AuditIntent"]
    assert set(audit_intent["required"]) == {
        "audit_action",
        "target_kind",
        "expected_audit_event",
    }
    assert {
        "appointment_proposal_prepared",
        "appointment_created",
        "appointment_updated",
        "appointment_status_changed",
        "appointment_deleted",
        "slot_search_normalized",
        "slot_search_proposed",
        "slot_selected_for_proposal",
    } <= set(audit_intent["properties"]["audit_action"]["enum"])
    assert {"appointment", "slot_search", "proposal"} <= set(
        audit_intent["properties"]["target_kind"]["enum"]
    )

    assert set(schemas["FreshnessRef"]["required"]) == {
        "freshness_id",
        "basis",
        "generated_at",
        "expires_at",
    }
    assert set(schemas["SignedConfirmationEvidence"]["required"]) == {
        "scheme",
        "key_id",
        "signed_at",
        "payload_hash",
        "signature",
        "covered_fields",
    }


def test_confirmation_commands_bind_confirmer_freshness_and_explicit_confirmation():
    schemas = _load_openapi()["components"]["schemas"]
    command_names = {
        "AppointmentCreateConfirmationCommand",
        "AppointmentUpdateConfirmationCommand",
        "AppointmentStatusConfirmationCommand",
        "AppointmentDeleteConfirmationCommand",
    }

    for name in sorted(command_names):
        command = schemas[name]
        required = set(command["required"])
        assert {"meta", "confirmer", "confirmed", "confirmed_warnings", "freshness"} <= required
        assert (
            command["properties"]["confirmer"]["$ref"]
            == "#/components/schemas/ConfirmerRef"
        )
        assert command["properties"]["confirmed"]["const"] is True
        assert (
            command["properties"]["freshness"]["$ref"]
            == "#/components/schemas/FreshnessRef"
        )


def test_confirmation_audit_event_preserves_idempotency_and_correlation_linkage():
    schemas = _load_openapi()["components"]["schemas"]

    confirm_result = schemas["AppointmentConfirmResultEnvelope"]
    assert "audit_evidence" in set(confirm_result["required"])
    assert (
        confirm_result["properties"]["audit_event"]["$ref"]
        == "#/components/schemas/ConfirmationAuditEvent"
    )

    audit_event = schemas["ConfirmationAuditEvent"]
    assert {
        "event_id",
        "practice_id",
        "action",
        "actor",
        "confirmer",
        "occurred_at",
        "correlation_id",
    } <= set(audit_event["required"])
    assert "idempotency_key" in audit_event["properties"]
    assert "correlation_id" in audit_event["properties"]
    assert set(audit_event["properties"]["action"]["enum"]) == {
        "create",
        "update",
        "status_change",
        "delete",
    }


def test_openapi_command_metadata_preflight_stays_documentation_only():
    spec = _load_openapi()

    assert spec["servers"][0]["url"].endswith(".invalid/api/v1")
    alignment = spec["x-emr4-current-backend-alignment"]
    assert alignment["status"] == "canonical_status_confirm_runtime_alias_mounted"
    assert REQUIRED_BLOCKED_GATES <= set(alignment["blocked_gates"])
