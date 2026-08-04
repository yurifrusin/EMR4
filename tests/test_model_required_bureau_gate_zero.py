from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.model_required_bureau_gate_zero_acceptance import (
    ARTIFACT_ROOT,
    CONTRACT_PATH,
    CONTRACT_SCHEMA_PATH,
    DESIGN_PATH,
    EXPECTED_RESULT,
    EXPECTED_SOURCE_HEAD,
    SCHEMA_EXAMPLES,
    THREAT_PATH,
    authority_index,
    build_evidence,
    join_labels,
    load_json,
    mediate_sink,
    parse_candidate_bytes,
    provider_outage_receipt,
    validator,
)


ROOT = Path(__file__).resolve().parents[1]


def _validate(schema_path: Path, value: dict) -> list:
    return list(validator(schema_path).iter_errors(value))


def _candidate_bytes(candidate: dict | None = None) -> bytes:
    payload = candidate or load_json(SCHEMA_EXAMPLES["typed_candidate"][1])
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()


def _candidate_label() -> dict:
    return deepcopy(
        load_json(SCHEMA_EXAMPLES["typed_candidate"][1])["payload"]["summary"][
            "label"
        ]
    )


def _admitted_label(**changes) -> dict:
    label = _candidate_label()
    label.update(
        {
            "integrity_principals": ["deterministic_proofreader"],
            "confidentiality_readers": ["authorized_surface"],
            "authority_ceiling": "proposal_candidate",
        }
    )
    label.update(changes)
    return label


def test_gate_zero_provider_free_acceptance_passes() -> None:
    evidence = build_evidence()
    assert evidence["passed"] is True
    assert evidence["result"] == EXPECTED_RESULT
    assert evidence["source_head"] == EXPECTED_SOURCE_HEAD
    assert set(evidence["authority_and_side_effects"].values()) == {0}


def test_shared_contract_and_all_examples_validate() -> None:
    assert _validate(CONTRACT_SCHEMA_PATH, load_json(CONTRACT_PATH)) == []
    for schema_path, example_path in SCHEMA_EXAMPLES.values():
        assert _validate(schema_path, load_json(example_path)) == []


def test_four_planes_are_ordered_and_have_distinct_principals() -> None:
    planes = load_json(CONTRACT_PATH)["planes"]
    assert [item["order"] for item in planes] == [1, 2, 3, 4]
    assert [item["id"] for item in planes] == [
        "cognitive",
        "proof",
        "authority",
        "execution_verification",
    ]
    assert len({item["principal"] for item in planes}) == 4
    assert [item["effect_authority"] for item in planes] == [
        False,
        False,
        False,
        True,
    ]


def test_broker_is_transport_not_product_or_command_authority() -> None:
    broker = load_json(CONTRACT_PATH)["transport_principal"]
    assert broker == {
        "id": "provider_broker",
        "role": "bounded_transport_not_authority_plane",
        "owns_provider_request": True,
        "owns_product_authority": False,
        "owns_command_authority": False,
    }


def test_domains_and_candidate_kinds_are_closed_and_non_crossing() -> None:
    domains = load_json(CONTRACT_PATH)["domains"]
    assert [item["id"] for item in domains] == [
        "bernie",
        "rayleen",
        "davida",
        "controlled_recovery_update",
    ]
    kinds = [kind for domain in domains for kind in domain["candidate_kinds"]]
    assert len(kinds) == len(set(kinds)) == 9
    assert all(domain["live_read_gate"] == "closed" for domain in domains)
    assert all(domain["command_gate"] == "closed" for domain in domains)


def test_shared_primitives_do_not_share_context_memory_policy_or_authority() -> None:
    isolation = load_json(CONTRACT_PATH)["domain_isolation"]
    assert isolation["shared_schema_primitives"] is True
    assert isolation["shared_proofreader_primitives"] is True
    for key in (
        "cross_domain_context",
        "cross_domain_memory",
        "cross_domain_policy",
        "cross_domain_credentials",
        "cross_domain_commands",
    ):
        assert isolation[key] is False


def test_gate_zero_authority_flags_are_all_closed() -> None:
    authority = load_json(CONTRACT_PATH)["authority"]
    assert authority["execution"] == "non_executing"
    assert authority["evidence_label"] == (
        "provider_free_gate_zero_architecture_contract"
    )
    assert all(
        value is False
        for key, value in authority.items()
        if key.endswith("_authorized")
    )


def test_provider_outage_is_explicit_and_releases_nothing() -> None:
    policy = load_json(CONTRACT_PATH)["provider_admission"]
    receipt = provider_outage_receipt()
    assert policy["model_required_for_agentic_claim"] is True
    assert policy["gate_zero_provider_call_authorized"] is False
    assert policy["no_silent_provider_fallback"] is True
    assert policy["no_silent_model_fallback"] is True
    assert policy["no_equivalent_heuristic_fallback"] is True
    assert receipt["reason_code"] == "PROVIDER_REQUIRED_UNAVAILABLE"
    assert receipt["provider_call_count"] == 0
    assert receipt["candidate_released"] is False
    assert receipt["command_attempted"] is False


def test_label_join_is_monotone_and_conservative() -> None:
    left = _admitted_label(
        source_ids=["authorized_backend_read:one"],
        integrity_principals=["deterministic_proofreader", "backend_truth"],
        confidentiality_readers=["authorized_surface", "authorized_operator"],
        expires_at="2026-08-04T02:03:00Z",
        authority_ceiling="projection_candidate",
    )
    right = _admitted_label(
        source_ids=["provider_model_candidate:one"],
        integrity_principals=["deterministic_proofreader"],
        confidentiality_readers=["authorized_surface"],
        expires_at="2026-08-04T02:05:00Z",
        authority_ceiling="proposal_candidate",
    )
    joined = join_labels(left, right)
    assert joined["source_ids"] == [
        "authorized_backend_read:one",
        "provider_model_candidate:one",
    ]
    assert joined["integrity_principals"] == ["deterministic_proofreader"]
    assert joined["confidentiality_readers"] == ["authorized_surface"]
    assert joined["expires_at"] == "2026-08-04T02:03:00Z"
    assert joined["authority_ceiling"] == "projection_candidate"


def test_stale_input_contaminates_join() -> None:
    joined = join_labels(
        _admitted_label(freshness_state="fresh"),
        _admitted_label(freshness_state="stale"),
    )
    assert joined["freshness_state"] == "stale"


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"freshness_state": "stale"}, "CONTEXT_STALE"),
        (
            {"confidentiality_readers": ["authorized_operator"]},
            "READER_NOT_AUTHORIZED",
        ),
        ({"integrity_principals": ["untrusted_model"]}, "INTEGRITY_INSUFFICIENT"),
        ({"authority_ceiling": "effect"}, "AUTHORITY_CEILING_EXCEEDED"),
    ],
)
def test_sink_mediation_denies_unsafe_label(changes: dict, reason: str) -> None:
    assert mediate_sink(_admitted_label(**changes), "proposal_release") == reason


def test_sink_mediation_admits_exact_safe_candidate_label() -> None:
    assert mediate_sink(_admitted_label(), "proposal_release") is None


def test_unknown_sink_fails_closed() -> None:
    assert mediate_sink(_admitted_label(), "generic_tool_or_command") == (
        "SCHEMA_REJECTED"
    )


def test_authority_order_rejects_unknown_value() -> None:
    with pytest.raises(ValueError, match="unknown authority ceiling"):
        authority_index("model_says_authorized")


def test_hostile_parser_accepts_only_closed_candidate_object() -> None:
    parsed, reason = parse_candidate_bytes(_candidate_bytes())
    assert reason is None
    assert parsed == load_json(SCHEMA_EXAMPLES["typed_candidate"][1])


def test_hostile_parser_rejects_duplicate_keys_before_schema() -> None:
    parsed, reason = parse_candidate_bytes(
        b'{"schema_version":"first","schema_version":"second"}'
    )
    assert parsed is None
    assert reason == "DUPLICATE_KEY"


def test_hostile_parser_rejects_invalid_utf8() -> None:
    assert parse_candidate_bytes(b"\xff") == (None, "INVALID_UTF8")


def test_hostile_parser_rejects_trailing_json() -> None:
    assert parse_candidate_bytes(_candidate_bytes() + b"{}") == (
        None,
        "SCHEMA_REJECTED",
    )


def test_hostile_parser_rejects_over_budget_bytes() -> None:
    limit = load_json(CONTRACT_PATH)["cell_contract"]["quotas"][
        "output_bytes_max"
    ]
    assert parse_candidate_bytes(b"x" * (limit + 1)) == (
        None,
        "BYTE_BUDGET_EXCEEDED",
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "command",
        "command_envelope",
        "confirmation_evidence",
        "writes_authorized",
        "actuator",
        "shell",
        "sql",
    ],
)
def test_candidate_schema_rejects_authority_bearing_payload_names(
    field_name: str,
) -> None:
    candidate = load_json(SCHEMA_EXAMPLES["typed_candidate"][1])
    candidate["payload"][field_name] = candidate["payload"].pop("summary")
    assert parse_candidate_bytes(_candidate_bytes(candidate)) == (
        None,
        "SCHEMA_REJECTED",
    )


def test_candidate_schema_rejects_unknown_domain_and_kind() -> None:
    schema = SCHEMA_EXAMPLES["typed_candidate"][0]
    candidate = load_json(SCHEMA_EXAMPLES["typed_candidate"][1])
    candidate["domain"] = "combined_bureau"
    assert _validate(schema, candidate)
    candidate = load_json(SCHEMA_EXAMPLES["typed_candidate"][1])
    candidate["candidate_kind"] = "execute_arbitrary_command"
    assert _validate(schema, candidate)


def test_candidate_schema_rejects_cross_domain_kind() -> None:
    candidate = load_json(SCHEMA_EXAMPLES["typed_candidate"][1])
    candidate["candidate_kind"] = "appointment_proposal"
    assert _validate(SCHEMA_EXAMPLES["typed_candidate"][0], candidate)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("integrity_principals", ["backend_authority_service"]),
        ("integrity_principals", ["deterministic_proofreader"]),
        ("confidentiality_readers", ["authorized_surface"]),
        ("authority_ceiling", "command_argument"),
        ("authority_ceiling", "effect"),
    ],
)
def test_raw_candidate_cannot_claim_proof_authority_or_effect(
    field: str, value,
) -> None:
    candidate = load_json(SCHEMA_EXAMPLES["typed_candidate"][1])
    candidate["payload"]["summary"]["label"][field] = value
    assert _validate(SCHEMA_EXAMPLES["typed_candidate"][0], candidate)


def test_context_schema_requires_per_field_label() -> None:
    schema = SCHEMA_EXAMPLES["labeled_context_frame"][0]
    frame = load_json(SCHEMA_EXAMPLES["labeled_context_frame"][1])
    del frame["fields"]["active_practitioner_count"]["label"]
    assert _validate(schema, frame)


def test_context_schema_rejects_unknown_reader_and_authority_ceiling() -> None:
    schema = SCHEMA_EXAMPLES["labeled_context_frame"][0]
    frame = load_json(SCHEMA_EXAMPLES["labeled_context_frame"][1])
    label = frame["fields"]["active_practitioner_count"]["label"]
    label["confidentiality_readers"] = ["the_entire_internet"]
    assert _validate(schema, frame)
    frame = load_json(SCHEMA_EXAMPLES["labeled_context_frame"][1])
    frame["fields"]["active_practitioner_count"]["label"][
        "authority_ceiling"
    ] = "model_decides"
    assert _validate(schema, frame)


def test_context_schema_rejects_model_or_effect_authority_labels() -> None:
    schema = SCHEMA_EXAMPLES["labeled_context_frame"][0]
    frame = load_json(SCHEMA_EXAMPLES["labeled_context_frame"][1])
    label = frame["fields"]["active_practitioner_count"]["label"]
    label["integrity_principals"] = ["untrusted_model"]
    assert _validate(schema, frame)
    frame = load_json(SCHEMA_EXAMPLES["labeled_context_frame"][1])
    frame["fields"]["active_practitioner_count"]["label"][
        "authority_ceiling"
    ] = "effect"
    assert _validate(schema, frame)


def test_cell_manifest_is_one_attempt_and_has_no_ambient_bridge() -> None:
    manifest = load_json(SCHEMA_EXAMPLES["one_attempt_cell_manifest"][1])
    assert manifest["started"] is False
    assert manifest["broker_policy"]["request_count_max"] == 1
    assert manifest["broker_policy"]["candidate_response_count_max"] == 1
    assert manifest["cell_visible_bridges"] == [
        "typed_input_once",
        "typed_output_once",
    ]
    forbidden = set(manifest["forbidden_bridges"])
    assert {
        "shell",
        "filesystem",
        "database",
        "credential",
        "metadata_endpoint",
        "ambient_network",
        "actuator",
    } <= forbidden
    assert not forbidden.intersection(manifest["cell_visible_bridges"])
    assert set(manifest["authority"].values()) == {False}


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("started",), True),
        (("broker_policy", "provider_endpoint_visible_to_cell"), True),
        (("broker_policy", "request_count_max"), 2),
        (("quotas", "output_bytes_max"), 131072),
        (("quotas", "processes_max"), 17),
        (("authority", "database"), True),
        (("authority", "command"), True),
        (("authority", "credential"), True),
    ],
)
def test_cell_manifest_security_mutations_fail_schema(
    path: tuple[str, ...], value,
) -> None:
    manifest = load_json(SCHEMA_EXAMPLES["one_attempt_cell_manifest"][1])
    target = manifest
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value
    assert _validate(SCHEMA_EXAMPLES["one_attempt_cell_manifest"][0], manifest)


def test_unknown_cell_bridge_fails_schema() -> None:
    manifest = load_json(SCHEMA_EXAMPLES["one_attempt_cell_manifest"][1])
    manifest["cell_visible_bridges"].append("generic_tool")
    assert _validate(SCHEMA_EXAMPLES["one_attempt_cell_manifest"][0], manifest)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("broker_token_revoked", False),
        ("input_channel_closed", False),
        ("output_channel_closed", False),
        ("live_process_count", 1),
        ("live_listener_count", 1),
        ("live_mount_count", 1),
        ("live_credential_count", 1),
        ("owned_ephemeral_artifact_count", 1),
        ("raw_provider_bytes_persisted", True),
        ("provider_response_persisted", True),
        ("product_access_occurred", True),
        ("command_attempted", True),
    ],
)
def test_incomplete_teardown_or_residue_fails_schema(field: str, value) -> None:
    receipt = load_json(SCHEMA_EXAMPLES["teardown_residue_receipt"][1])
    receipt[field] = value
    assert _validate(SCHEMA_EXAMPLES["teardown_residue_receipt"][0], receipt)


def test_denial_receipt_cannot_claim_release_or_command() -> None:
    schema = SCHEMA_EXAMPLES["typed_denial_receipt"][0]
    receipt = load_json(SCHEMA_EXAMPLES["typed_denial_receipt"][1])
    receipt["candidate_released"] = True
    assert _validate(schema, receipt)
    receipt = load_json(SCHEMA_EXAMPLES["typed_denial_receipt"][1])
    receipt["command_attempted"] = True
    assert _validate(schema, receipt)


def test_shared_contract_rejects_authority_and_quota_expansion() -> None:
    contract = load_json(CONTRACT_PATH)
    contract["authority"]["provider_calls_authorized"] = True
    assert _validate(CONTRACT_SCHEMA_PATH, contract)
    contract = load_json(CONTRACT_PATH)
    contract["cell_contract"]["quotas"]["wall_time_ms_max"] = 60000
    assert _validate(CONTRACT_SCHEMA_PATH, contract)


def test_shared_contract_rejects_unknown_nested_property() -> None:
    contract = load_json(CONTRACT_PATH)
    contract["provider_admission"]["fallback_provider"] = "anything"
    assert _validate(CONTRACT_SCHEMA_PATH, contract)


def test_api_spine_keeps_reads_commands_events_and_manifests_distinct() -> None:
    spine = load_json(CONTRACT_PATH)["api_spine"]
    assert spine == {
        "read_context": "graphql_named_scoped_read_only",
        "mutation": "rest_openapi_single_purpose_backend_owned_command",
        "event": "committed_hint_requires_fresh_authorized_read",
        "manifest": "declarative_input_runtime_enforced",
        "context_frames_non_authoritative": True,
        "provider_candidate_non_authoritative": True,
    }


def test_future_command_boundary_is_backend_owned_auditable_and_idempotent() -> None:
    boundary = load_json(CONTRACT_PATH)["future_command_boundary"]
    assert boundary["current_gate"] == "closed"
    assert boundary["transport"] == "rest_openapi_single_purpose"
    assert boundary["owner"] == "trusted_backend_code"
    assert {
        "practice_scope",
        "actor_id",
        "correlation_id",
        "idempotency_key",
        "expected_revision_or_etag",
        "freshness_id",
        "confirmation_or_dual_review_evidence",
        "audit_contract",
        "readback_contract",
    } <= set(boundary["required_fields"])
    assert boundary["backend_reauthorization_before_write"] is True
    assert boundary["backend_revalidation_before_write"] is True
    assert boundary["model_cell_broker_or_proofreader_may_construct"] is False


def test_access_ai_invocation_boundary_is_closed_and_not_graphql() -> None:
    boundary = load_json(CONTRACT_PATH)["provider_invocation_boundary"]
    assert boundary["current_gate"] == "closed"
    assert boundary["transport"] == "rest_access_ai_command_only"
    assert {
        "capability",
        "method",
        "actor_id",
        "practice_scope",
        "entitlement_decision",
        "context_hash",
        "data_class",
        "provider",
        "model",
        "region",
        "cost_budget",
        "correlation_id",
        "audit_policy",
    } == set(boundary["required_bindings"])
    for field in (
        "graphql_invocation",
        "raw_prompt_graphql_field",
        "raw_response_graphql_field",
        "raw_prompt_persistence",
        "raw_response_persistence",
    ):
        assert boundary[field] is False


def test_command_and_provider_boundary_expansion_fails_schema() -> None:
    contract = load_json(CONTRACT_PATH)
    contract["future_command_boundary"][
        "model_cell_broker_or_proofreader_may_construct"
    ] = True
    assert _validate(CONTRACT_SCHEMA_PATH, contract)
    contract = load_json(CONTRACT_PATH)
    contract["provider_invocation_boundary"]["graphql_invocation"] = True
    assert _validate(CONTRACT_SCHEMA_PATH, contract)


def test_evidence_classes_do_not_inflate_provider_free_claim() -> None:
    evidence = load_json(CONTRACT_PATH)["evidence_classes"]
    assert [item["id"] for item in evidence] == [
        "provider_free_component",
        "occupied_model_authored_synthetic",
        "live_product_read",
        "live_product_write",
        "live_actuator",
        "deployment",
        "production",
        "release",
    ]
    assert evidence[0]["proves"].endswith("only")


def test_artifacts_are_repository_local_and_exclude_branding_content() -> None:
    artifacts = [CONTRACT_PATH, CONTRACT_SCHEMA_PATH, DESIGN_PATH, THREAT_PATH]
    artifacts.extend(path for pair in SCHEMA_EXAMPLES.values() for path in pair)
    for path in artifacts:
        assert path.is_file()
        assert ROOT in path.parents
        text = path.read_text(encoding="utf-8")
        assert "C:\\Users\\" not in text
        assert "C:/Users/" not in text
    assert not any(path.is_relative_to(ROOT / "docs/branding") for path in artifacts)


def test_public_docs_preserve_non_authority_and_no_runtime_claim() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in (DESIGN_PATH, THREAT_PATH)
    )
    for phrase in (
        "provider-free and non-executing",
        "no provider call",
        "no silent",
        "one-attempt",
        "deterministic readback",
        "docs/branding/",
    ):
        assert phrase in combined
    for overclaim in (
        "production ready",
        "prompt injection is eliminated",
        "patient data is authorized",
    ):
        assert overclaim not in combined


def test_gate_zero_directory_contains_only_declared_architecture_artifacts() -> None:
    names = {path.name for path in ARTIFACT_ROOT.iterdir() if path.is_file()}
    assert names == {
        "shared-contract.json",
        "shared-contract.schema.json",
        "labeled-context-frame.schema.json",
        "labeled-context-frame.example.json",
        "typed-candidate.schema.json",
        "typed-candidate.example.json",
        "typed-denial-receipt.schema.json",
        "typed-denial-receipt.example.json",
        "one-attempt-cell-manifest.schema.json",
        "one-attempt-cell-manifest.example.json",
        "teardown-residue-receipt.schema.json",
        "teardown-residue-receipt.example.json",
        "provider-free-acceptance-evidence.json",
    } - ({"provider-free-acceptance-evidence.json"} if not (ARTIFACT_ROOT / "provider-free-acceptance-evidence.json").exists() else set())
