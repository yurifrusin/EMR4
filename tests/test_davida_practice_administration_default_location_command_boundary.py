"""Deterministic acceptance for the architecture-only Davida command boundary.

The tests read documentation, JSON/YAML contracts and static application source
only. They never import ``app.main``, mount a route, open a database or perform a
write.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_DIR = (
    ROOT
    / "orchestration/continuity/"
    "davida-practice-administration-default-location-command-boundary"
)
CONTRACT = BOUNDARY_DIR / "command-boundary-contract.json"
SCHEMA = BOUNDARY_DIR / "command-boundary-contract.schema.json"
OPENAPI = (
    ROOT
    / "docs/api-spine/openapi/"
    "practice-administration-default-location-commands.yaml"
)
APPOINTMENT_OPENAPI = ROOT / "docs/api-spine/openapi/appointment-commands.yaml"
PERMISSION_MATRIX = ROOT / "docs/api-spine/security/permission-matrix.yaml"
PLAN = ROOT / "docs/davida-practice-administration-default-location-command-boundary-plan.md"
DESIGN = (
    ROOT / "docs/davida-practice-administration-default-location-command-boundary-design.md"
)
THREAT = (
    ROOT
    / "docs/security/"
    "davida-practice-administration-default-location-command-boundary-threat-model-delta.md"
)

PROPOSAL_PATH = "/practice-administration/practitioners/default-location/proposals"
CONFIRM_PATH = f"{PROPOSAL_PATH}/{{proposal_id}}/confirm"
PERMITTED_ROLES = ["practice_manager", "practice_owner"]
REJECTION_CODES = [
    "unauthenticated",
    "not_authorized",
    "confirmer_not_authorized",
    "practice_scope_mismatch",
    "resource_scope_mismatch",
    "location_not_active",
    "no_change",
    "proposal_stale",
    "proposal_expired",
    "proposal_hash_mismatch",
    "aggregate_version_mismatch",
    "before_state_conflict",
    "confirmation_evidence_invalid",
    "confirmation_evidence_expired",
    "idempotency_conflict",
    "idempotency_in_progress",
    "confirmation_replay_rejected",
    "atomic_transaction_failed",
    "invalid_envelope",
]


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _yaml(path: Path) -> dict[str, Any]:
    yaml = pytest.importorskip("yaml")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _local_ref(document: dict[str, Any], reference: str) -> Any:
    assert reference.startswith("#/"), reference
    value: Any = document
    for part in reference.removeprefix("#/").split("/"):
        value = value[part.replace("~1", "/").replace("~0", "~")]
    return value


def _walk(value: Any):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _mutation_fails(mutator) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    candidate = copy.deepcopy(_json(CONTRACT))
    mutator(candidate)
    errors = list(
        jsonschema.Draft202012Validator(_json(SCHEMA)).iter_errors(candidate)
    )
    assert errors, "authority-bearing contract mutation unexpectedly validated"


def test_contract_validates_against_draft_2020_12_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.Draft202012Validator(_json(SCHEMA)).validate(_json(CONTRACT))


def test_openapi_is_separate_documentation_only_artifact() -> None:
    api = _yaml(OPENAPI)
    boundary = api["x-emr4-boundary"]

    assert api["openapi"] == "3.1.0"
    assert api["servers"] == [
        {
            "url": "https://api.example.invalid/api/v1",
            "description": "Documentation placeholder; no live endpoint exists.",
        }
    ]
    assert set(api["paths"]) == {PROPOSAL_PATH, CONFIRM_PATH}
    assert boundary["status"] == "documentation_only_no_runtime_route"
    assert boundary["actual_command_implementation_authorized"] is False
    assert boundary["actual_write_authority"] is False
    assert OPENAPI != APPOINTMENT_OPENAPI


def test_local_openapi_refs_resolve() -> None:
    api = _yaml(OPENAPI)
    refs = [item["$ref"] for item in _walk(api) if isinstance(item, dict) and "$ref" in item]

    assert refs
    for reference in refs:
        assert _local_ref(api, reference) is not None


def test_openapi_object_schemas_are_closed() -> None:
    schemas = _yaml(OPENAPI)["components"]["schemas"]

    for name, schema in schemas.items():
        if schema.get("type") == "object":
            assert schema.get("additionalProperties") is False, name


def test_proposal_is_non_mutating_and_has_no_proposal_ledger() -> None:
    api = _yaml(OPENAPI)
    operation = api["paths"][PROPOSAL_PATH]["post"]
    posture = operation["x-emr4-proposal-idempotency"]

    assert operation["x-emr4-effect"] == "none"
    assert posture["header_required"] is True
    assert posture["replay_model"] == "deterministic_re_evaluation"
    assert posture["durable_proposal_ledger"] is False
    assert posture["command_claim"] is False


def test_proposal_reference_is_signed_self_contained_without_store() -> None:
    api = _yaml(OPENAPI)
    contract = _json(CONTRACT)["proposal_phase"]
    posture = api["paths"][PROPOSAL_PATH]["post"][
        "x-emr4-proposal-idempotency"
    ]
    signed_ref = api["components"]["schemas"]["SignedProposalRef"]
    proposal = api["components"]["schemas"]["DefaultLocationProposalEnvelope"]

    assert (
        posture["proposal_reference"]
        == "backend_issued_signed_self_contained_no_proposal_store"
    )
    assert signed_ref["pattern"].startswith("^dlp1")
    assert "without a proposal store" in signed_ref["description"]
    assert proposal["properties"]["proposal_id"]["$ref"].endswith(
        "/SignedProposalRef"
    )
    assert contract["proposal_reference"] == (
        "backend_issued_signed_opaque_self_contained"
    )
    assert contract["proposal_store_required"] is False


def test_session_is_authority_and_body_is_binding_assertion_only() -> None:
    api = _yaml(OPENAPI)
    contract = _json(CONTRACT)["authority"]
    binding = api["x-emr4-session-binding"]
    schema = api["components"]["schemas"]["SessionBindingAssertion"]
    actor = api["components"]["schemas"]["SessionActorBindingAssertion"]

    assert binding == {
        "authority_source": "authenticated_application_session",
        "request_body_role": "non_authoritative_exact_match_assertion",
        "practice_actor_and_role_derived_from_session": True,
        "mismatch": "reject_before_resource_disclosure",
    }
    assert "Non-authoritative" in schema["description"]
    assert "application_session_ref" not in actor["properties"]
    assert actor["properties"]["role"]["enum"] == PERMITTED_ROLES
    assert contract["practice_actor_role_authority_source"] == (
        "authenticated_application_session"
    )
    assert contract["request_body_binding_authority"] is False
    assert contract["request_body_binding_rule"] == (
        "exact_match_session_derived_practice_actor_role_or_reject"
    )


def test_role_policy_is_future_contract_not_current_runtime_grant() -> None:
    api = _yaml(OPENAPI)
    contract = _json(CONTRACT)["confirmation_phase"]
    matrix = _yaml(PERMISSION_MATRIX)
    confirmation = api["paths"][CONFIRM_PATH]["post"]

    assert (
        confirmation["x-emr4-role-policy"]
        == "proposed_future_contract_not_current_permission_matrix_runtime_grant"
    )
    assert contract["role_policy_status"] == (
        "proposed_future_contract_not_current_permission_matrix_runtime_grant"
    )
    current_default_location_confirms = [
        item
        for item in matrix["allow_examples"]
        if item["role"] in PERMITTED_ROLES
        and item["action"] == "confirm"
        and item["resource"] == "practitioner_default_location"
    ]
    assert current_default_location_confirms == []


def test_proposal_binds_expected_version_hashes_and_expiry() -> None:
    api = _yaml(OPENAPI)
    request = api["components"]["schemas"]["DefaultLocationProposalRequest"]
    response = api["components"]["schemas"]["DefaultLocationProposalEnvelope"]

    assert {
        "practitioner_ref",
        "requested_default_location_ref",
        "expected_aggregate_version",
        "dry_run_proposal_hash",
        "dry_run_context_revision",
        "dry_run_expires_at",
    } <= set(request["required"])
    assert response["properties"]["maximum_lifetime_seconds"]["const"] == 120
    assert response["properties"]["human_confirmation_required"]["const"] is True
    assert response["properties"]["applies_change"]["const"] is False
    assert response["properties"]["davida_can_confirm"]["const"] is False


def test_confirmation_accepts_only_human_manager_or_owner() -> None:
    api = _yaml(OPENAPI)
    actor = api["components"]["schemas"]["SessionActorBindingAssertion"]
    boundary = api["x-emr4-boundary"]

    assert actor["properties"]["actor_type"]["const"] == "human_user"
    assert actor["properties"]["role"]["enum"] == PERMITTED_ROLES
    assert boundary["davida_can_confirm"] is False
    assert boundary["davida_can_apply"] is False


def test_confirmation_evidence_is_opaque_server_held_reference_only() -> None:
    api = _yaml(OPENAPI)
    contract = _json(CONTRACT)["confirmation_phase"]
    policy = api["x-emr4-confirmation-evidence"]
    command = api["components"]["schemas"]["DefaultLocationConfirmationCommand"]
    evidence = api["components"]["schemas"]["BackendConfirmationEvidenceRef"]

    assert policy["request_shape"] == (
        "opaque_backend_issued_server_held_one_use_reference_only"
    )
    assert policy["structured_client_claims_can_mint_evidence"] is False
    assert "confirmation_evidence_ref" in command["required"]
    assert "confirmation_evidence" not in command["properties"]
    assert "server-held" in evidence["description"]
    assert "cannot" in evidence["description"]
    assert contract["confirmation_evidence_shape"] == (
        "opaque_server_held_one_use_reference_only"
    )
    assert contract[
        "structured_client_claims_can_mint_confirmation_evidence"
    ] is False


def test_fresh_authorization_order_is_explicit() -> None:
    contract = _json(CONTRACT)
    order = contract["confirmation_phase"]["authorization_order"]

    assert order[0] == "authenticate_application_session"
    assert order[1] == "authorize_practice_action_before_resource_disclosure"
    assert "lock_practitioner_aggregate" in order
    assert order[-2] == (
        "reauthorize_exact_action_resource_inside_transaction_immediately_before_write"
    )
    assert contract["confirmation_phase"][
        "backend_revalidation_from_current_truth"
    ] is True


def test_confirmation_idempotency_distinguishes_safe_retry_and_conflict() -> None:
    idem = _json(CONTRACT)["durable_idempotency"]

    assert idem["applies_to"] == "confirmation_only"
    assert idem["scope"] == [
        "practice_ref",
        "operation",
        "authenticated_actor_ref",
        "idempotency_key",
    ]
    assert idem["same_key_same_fingerprint"] == (
        "return_exact_stored_domain_receipt_no_new_effect"
    )
    assert idem["same_key_different_fingerprint"] == "idempotency_conflict"
    assert idem["different_key_consumed_confirmation_evidence"] == (
        "confirmation_replay_rejected"
    )
    assert idem["failed_transaction_completes_key"] is False


def test_atomic_transaction_includes_evidence_audit_outbox_and_receipt() -> None:
    transaction = _json(CONTRACT)["atomic_transaction"]

    assert transaction["future_only_not_implemented"] is True
    assert transaction["members"] == [
        "idempotency_claim",
        "single_use_confirmation_evidence_nonce_claim",
        "one_practitioner_default_location_change",
        "aggregate_version_increment_exactly_once",
        "one_immutable_audit_event_append",
        "one_transactional_outbox_event_append",
        "idempotency_receipt_completion",
    ]
    assert transaction["rollback_on_any_failure"] is True
    assert transaction["publication_after_commit_only"] is True


def test_atomic_failure_has_no_partial_effect_or_receipt() -> None:
    transaction = _json(CONTRACT)["atomic_transaction"]

    for field in (
        "partial_aggregate_change",
        "partial_audit_event",
        "partial_outbox_event",
        "partial_idempotency_completion",
        "receipt_before_commit",
    ):
        assert transaction[field] is False


def test_rejection_vocabulary_is_closed_and_exact() -> None:
    contract = _json(CONTRACT)
    openapi_codes = _yaml(OPENAPI)["components"]["schemas"]["Rejection"][
        "properties"
    ]["reason_code"]["enum"]

    assert contract["rejection_codes"] == REJECTION_CODES
    assert openapi_codes == REJECTION_CODES


def test_bounded_receipt_excludes_free_text_and_raw_credentials() -> None:
    receipt = _json(CONTRACT)["bounded_receipt"]

    assert receipt["success_only"] is True
    assert receipt["free_text"] is False
    assert receipt["display_names"] is False
    assert receipt["raw_session_credential"] is False
    assert receipt["raw_idempotency_key"] is False
    assert receipt["patient_clinical_document_data"] is False
    assert {
        "expected_aggregate_version",
        "resulting_aggregate_version",
        "audit_event_id",
        "outbox_event_id",
        "idempotency_key_hash",
    } <= set(receipt["fields"])


def test_event_is_after_commit_signal_never_truth_or_command() -> None:
    event = _json(CONTRACT)["event_boundary"]

    assert event["transactional_outbox_required"] is True
    assert event["publish_after_commit_only"] is True
    assert event["payload_is_truth"] is False
    assert event["payload_is_command"] is False
    assert event["fresh_authorized_read_required_for_consumers"] is True
    assert event["davida_event_actuator"] is False


def test_api_spine_planes_remain_distinct() -> None:
    spine = _json(CONTRACT)["api_spine"]

    assert spine == {
        "graphql": "read_only_unchanged",
        "rest_openapi": "single_purpose_proposal_and_future_confirmation",
        "events": "committed_signal_only",
        "manifests": "declarative_only",
        "appointment_command_contract_changed": False,
        "separate_openapi_artifact": True,
    }


def test_runtime_source_has_no_mounted_boundary() -> None:
    needles = {
        "proposePractitionerDefaultLocationChange",
        "confirmPractitionerDefaultLocationChange",
        PROPOSAL_PATH,
    }
    hits: list[tuple[Path, str]] = []
    for path in sorted((ROOT / "app").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle in text:
                hits.append((path.relative_to(ROOT), needle))
    assert hits == []


def test_public_docs_keep_runtime_and_branding_gates_closed() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in (PLAN, DESIGN, THREAT)
    )
    normalized = " ".join(text.split())

    assert "architecture-only" in text
    assert "no runtime" in text or "does not implement" in text
    assert "material yuri-owned gate" in normalized
    assert "docs/branding/" in text
    assert "app.main" in text
    assert "provider-free" in text


@pytest.mark.parametrize(
    "mutator",
    [
        lambda item: item["authority"].__setitem__("davida_can_confirm", True),
        lambda item: item["authority"].__setitem__(
            "actual_command_implementation_authorized", True
        ),
        lambda item: item["proposal_phase"].__setitem__(
            "proposal_store_required", True
        ),
        lambda item: item["authority"].__setitem__(
            "request_body_binding_authority", True
        ),
        lambda item: item["confirmation_phase"].__setitem__(
            "structured_client_claims_can_mint_confirmation_evidence", True
        ),
        lambda item: item["atomic_transaction"].__setitem__(
            "rollback_on_any_failure", False
        ),
        lambda item: item["atomic_transaction"].__setitem__(
            "publication_after_commit_only", False
        ),
        lambda item: item["durable_idempotency"].__setitem__(
            "same_key_same_fingerprint", "perform_second_effect"
        ),
        lambda item: item["rejection_codes"].remove("idempotency_conflict"),
        lambda item: item["authority"].__setitem__("unknown_authority", True),
    ],
)
def test_authority_broadening_mutations_fail_schema(mutator) -> None:
    _mutation_fails(mutator)
