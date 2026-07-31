from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from scripts.raisa_shared_application_auth_boundary import (
    AUTH_DECISION_SCHEMA_PATH,
    CASES_PATH,
    EXCHANGE_DECISION_SCHEMA_PATH,
    POLICY_PATH,
    POLICY_SCHEMA_PATH,
    run_acceptance,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "raisa-shared-application-auth-clinician-role-boundary-plan.md"
DESIGN = ROOT / "docs" / "raisa-shared-application-auth-clinician-role-boundary-design.md"
THREAT_MODEL = (
    ROOT
    / "docs"
    / "security"
    / "raisa-shared-application-auth-clinician-role-boundary-threat-model-delta.md"
)
CLOSEOUT = (
    ROOT
    / "docs"
    / "raisa-shared-application-auth-clinician-role-boundary-closeout.md"
)
ACCEPTANCE = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-shared-application-auth-clinician-role-boundary-sol-acceptance.md"
)
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
COMPASS_REPORT = ROOT / "docs" / "ariadne-compass-current.md"
RECEIPT = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-shared-application-auth-clinician-role-boundary-rehydration-receipt.json"
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_policy_schema_and_policy_validate() -> None:
    schema = _json(POLICY_SCHEMA_PATH)
    policy = _json(POLICY_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(policy)


def test_policy_freezes_one_backend_authority_and_three_surfaces() -> None:
    policy = _json(POLICY_PATH)
    assert policy["authority_owner"] == "emr4_backend"
    assert set(policy["surfaces"]) == {
        "word_desktop",
        "word_online",
        "native_diary",
    }
    assert policy["authorization_policy"] == {
        "decision_function": "backend_authorize_request",
        "endpoint_policy_owner": "server",
        "generic_client_selected_policy_api": False,
        "evaluate_before_data_access": True,
        "re_evaluate_commands_independently": True,
        "allow_decision_is_capability_token": False,
        "unknown_state": "deny",
        "decision_authority_source": "emr4_backend",
    }


def test_identity_is_separate_from_microsoft_and_client_claims() -> None:
    policy = _json(POLICY_PATH)
    identity = policy["identity"]
    assert identity["canonical_principal_source"] == "fresh_emr4_backend_user_record"
    assert identity["microsoft_office_identity"] == (
        "authentication_input_only_never_application_authority"
    )
    assert {
        "office_signed_in_state",
        "microsoft_account_identifier",
        "client_asserted_role",
        "client_asserted_practice",
        "office_host_capability_profile",
    } <= set(identity["forbidden_authority_inputs"])


def test_initial_clinician_policy_is_current_gp_plus_active_same_practice_link() -> None:
    clinician = _json(POLICY_PATH)["clinician_policy"]
    assert clinician["allowed_current_backend_roles"] == ["GP"]
    assert clinician["requires_active_user"] is True
    assert clinician["requires_active_practitioner_link"] is True
    assert clinician["requires_practitioner_same_practice"] is True
    assert clinician["requires_resource_same_practice"] is True
    assert set(clinician["not_implied_by_roles"]) == {
        "Receptionist",
        "Nurse",
        "Admin",
        "PracticeOwner",
    }


def test_session_and_exchange_policy_rejects_browser_secret_relay() -> None:
    session = _json(POLICY_PATH)["session_policy"]
    assert session["parent_session_storage"] == "opaque_server_side"
    assert session["surface_session_storage"] == "opaque_server_side"
    assert session["javascript_secret_storage"] == "forbidden"
    assert session["application_session_absolute_ttl_seconds_max"] <= 8 * 60 * 60
    assert session["surface_session_idle_ttl_seconds_max"] <= 30 * 60
    exchange = session["cross_surface_exchange"]
    assert exchange["maximum_ttl_seconds"] <= 60
    assert exchange["single_use"] is True
    assert exchange["atomic_consumption"] is True
    assert exchange["pkce_method"] == "S256"
    assert {"bearer_token", "cookie", "office_identity", "clinical_data"} <= set(
        exchange["forbidden_payloads"]
    )


def test_provider_free_acceptance_matches_every_frozen_case() -> None:
    evidence = run_acceptance()
    assert evidence["result"] == "pass"
    assert evidence["authorization"]["case_count"] == 23
    assert evidence["authorization"]["matched_expected_count"] == 23
    assert evidence["authorization"]["mismatches"] == []
    assert evidence["cross_surface_exchange"]["case_count"] == 13
    assert evidence["cross_surface_exchange"]["matched_expected_count"] == 13
    assert evidence["cross_surface_exchange"]["mismatches"] == []


def test_all_three_surfaces_share_the_same_backend_allow_policy() -> None:
    evidence = run_acceptance()
    decisions = {
        item["case_id"]: item for item in evidence["authorization"]["decisions"]
    }
    allowed_ids = {
        "allow-word-desktop-gp",
        "allow-word-online-gp",
        "allow-native-diary-gp",
    }
    allowed = [decisions[item] for item in sorted(allowed_ids)]
    assert {item["surface"] for item in allowed} == {
        "word_desktop",
        "word_online",
        "native_diary",
    }
    assert {item["policy_version"] for item in allowed} == {
        "clinician-workspace-read.v1"
    }
    assert {item["authority_source"] for item in allowed} == {"emr4_backend"}
    assert all(item["office_identity_used"] is False for item in allowed)
    assert all(item["client_claims_used"] is False for item in allowed)


def test_office_signin_and_client_role_cannot_create_authority() -> None:
    evidence = run_acceptance()
    decisions = {
        item["case_id"]: item for item in evidence["authorization"]["decisions"]
    }
    assert decisions["deny-office-signin-without-emr4-session"]["reason_codes"] == [
        "application_session_required"
    ]
    assert decisions["deny-client-asserted-gp-for-receptionist"]["reason_codes"] == [
        "clinician_role_required"
    ]
    assert decisions["allow-server-gp-despite-client-receptionist-hint"][
        "decision"
    ] == "allow"


def test_expiry_revocation_scope_role_and_audit_fail_closed() -> None:
    evidence = run_acceptance()
    decisions = {
        item["case_id"]: item for item in evidence["authorization"]["decisions"]
    }
    expected = {
        "deny-expired-parent-session": (401, "application_session_expired"),
        "deny-idle-expired-parent-session": (
            401,
            "application_session_idle_expired",
        ),
        "deny-revoked-parent-session": (401, "application_session_revoked"),
        "deny-surface-generation-mismatch": (
            401,
            "surface_session_generation_mismatch",
        ),
        "deny-cross-practice-resource": (403, "resource_practice_mismatch"),
        "deny-missing-practitioner-link": (
            403,
            "active_same_practice_practitioner_required",
        ),
        "error-required-audit-unavailable": (503, "required_audit_unavailable"),
    }
    for case_id, (status, reason) in expected.items():
        assert decisions[case_id]["http_status"] == status
        assert decisions[case_id]["reason_codes"] == [reason]
        assert decisions[case_id]["product_data_released"] is False


def test_cross_surface_exchange_is_single_use_bound_and_bearer_free() -> None:
    evidence = run_acceptance()
    decisions = {
        item["case_id"]: item
        for item in evidence["cross_surface_exchange"]["decisions"]
    }
    for case_id in (
        "admit-word-desktop-to-native-diary-once",
        "admit-word-online-to-native-diary-once",
    ):
        assert decisions[case_id]["decision"] == "admit"
        assert decisions[case_id]["grant_consumed"] is True
        assert decisions[case_id]["surface_session_created"] is True
        assert decisions[case_id]["bearer_material_transported"] is False

    denied_reasons = {
        "exchange_expired",
        "exchange_already_consumed",
        "exchange_pkce_mismatch",
        "exchange_state_mismatch",
        "exchange_nonce_mismatch",
        "exchange_source_origin_mismatch",
        "exchange_target_origin_mismatch",
        "exchange_audience_mismatch",
        "exchange_target_surface_mismatch",
        "exchange_parent_session_inactive",
        "exchange_parent_generation_mismatch",
    }
    assert denied_reasons <= {
        item["reason_codes"][0]
        for item in decisions.values()
        if item["decision"] == "deny"
    }


def test_decision_outputs_validate_and_contain_no_secret_or_product_fields() -> None:
    evidence = run_acceptance()
    auth_schema = _json(AUTH_DECISION_SCHEMA_PATH)
    exchange_schema = _json(EXCHANGE_DECISION_SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(auth_schema)
    jsonschema.Draft202012Validator.check_schema(exchange_schema)
    auth_validator = jsonschema.Draft202012Validator(
        auth_schema,
        format_checker=jsonschema.FormatChecker(),
    )
    exchange_validator = jsonschema.Draft202012Validator(
        exchange_schema,
        format_checker=jsonschema.FormatChecker(),
    )
    for decision in evidence["authorization"]["decisions"]:
        auth_validator.validate(decision)
    for decision in evidence["cross_surface_exchange"]["decisions"]:
        exchange_validator.validate(decision)

    forbidden_keys = {
        "password",
        "bearer_token",
        "access_token",
        "cookie",
        "exchange_code",
        "pkce_verifier",
        "microsoft_account_identifier",
        "microsoft_tenant_identifier",
        "document_identifier",
        "patient_data",
        "clinical_data",
        "document_content",
    }
    for collection in (
        evidence["authorization"]["decisions"],
        evidence["cross_surface_exchange"]["decisions"],
    ):
        for decision in collection:
            assert forbidden_keys.isdisjoint(decision)


def test_acceptance_has_zero_external_or_product_side_effects() -> None:
    side_effects = run_acceptance()["authority_and_side_effects"]
    assert side_effects
    assert set(side_effects.values()) == {0}


def test_plan_design_and_threat_model_keep_runtime_authority_closed() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    design = DESIGN.read_text(encoding="utf-8")
    threat = THREAT_MODEL.read_text(encoding="utf-8")
    for required in (
        "Microsoft/Office identity",
        "single-use",
        "revocation",
        "audit",
        "fail closed",
    ):
        assert required.lower() in (plan + design + threat).lower()
    assert "None of those runtime steps is authorized" in design
    assert threat.rstrip().endswith(
        "Repository: EMR4\n"
        "Version: 8fa732592fbee4f57c322b13d9d8ff89fcc7fa33"
    )


def test_rehydration_receipt_names_all_five_sources_and_blocks_dispatch() -> None:
    receipt = _json(RECEIPT)
    assert receipt["status"] == "passed"
    assert receipt["rehydrated_from_receipt"] is True
    assert receipt["rehydration_sources"] == [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    assert set(receipt["source_evidence"]) == set(receipt["rehydration_sources"])
    assert receipt["worker_dispatch_permitted"] is False


def test_case_manifest_is_closed_unique_and_authored_synthetic() -> None:
    manifest = _json(CASES_PATH)
    assert manifest["data_class"] == "authored_synthetic_metadata_only"
    auth_ids = [item["id"] for item in manifest["authorization_cases"]]
    exchange_ids = [item["id"] for item in manifest["exchange_cases"]]
    assert len(auth_ids) == len(set(auth_ids)) == 23
    assert len(exchange_ids) == len(set(exchange_ids)) == 13


def test_closeout_continuity_and_compass_bind_architecture_only_result() -> None:
    result = "raisa_shared_application_auth_clinician_role_boundary_architecture_pass"
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "raisa-shared-application-auth-clinician-role-boundary"
    )
    assert graph["graph_revision"] >= 181
    assert node["id"] == "raisa-shared-application-auth-clinician-role-boundary"
    assert node["status"] == "accepted"
    assert compass["map_revision"] >= 162
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert any(item["node_id"] == node["id"] for item in compass["journey"])
    assert result in CLOSEOUT.read_text(encoding="utf-8")
    assert result in ACCEPTANCE.read_text(encoding="utf-8")
    report = COMPASS_REPORT.read_text(encoding="utf-8")
    assert f"Compass map revision {compass['map_revision']}" in report
    assert f"continuity graph revision {graph['graph_revision']}" in report
