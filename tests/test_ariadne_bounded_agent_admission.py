"""Deterministic tests for the non-executing agent-admission design."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from scripts import ariadne_bounded_agent_admission as admission


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-bounded-agent-admission.schema.json"
)
EXAMPLE_PATH = admission.EXAMPLE_PATH
MANIFEST_PATH = admission.MANIFEST_PATH
EVIDENCE_PATH = admission.EVIDENCE_PATH
SCRIPT_PATH = ROOT / "scripts" / "ariadne_bounded_agent_admission.py"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def document() -> dict:
    return admission.load_document()


def test_schema_is_draft_2020_12_and_canonical_document_valid(document):
    schema = _load(SCHEMA_PATH)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    assert not list(validator.iter_errors(document))


def test_semantic_validator_accepts_only_the_inert_design(document):
    result = admission.validate_document(document)
    assert result == {
        "status": "valid",
        "case_count": 15,
        "source_binding_count": 6,
        "topology_count": 3,
        "context_frame_count": 6,
        "output_port_count": 5,
    }


def test_every_predecessor_binding_is_exact_and_repository_local(document):
    for binding in document["source_bindings"]:
        path = ROOT / binding["path"]
        assert path.is_file()
        assert not path.is_symlink()
        assert _sha256(path) == binding["sha256"]


def test_source_binding_hash_drift_fails_closed(document):
    changed = copy.deepcopy(document)
    changed["source_bindings"][0]["sha256"] = "sha256:" + "0" * 64
    with pytest.raises(admission.AdmissionDesignError, match="source-binding-hash"):
        admission.validate_document(changed)


def test_every_connection_and_runtime_flag_remains_closed(document):
    assert document["closed_connections"]
    assert not any(document["closed_connections"].values())
    envelope = document["admission_envelope"]
    for key in (
        "execution_enabled",
        "agent_attached",
        "model_selected",
        "provider_selected",
        "transport_selected",
        "container_started",
    ):
        assert envelope[key] is False


def test_topology_catalogue_is_complete_but_selects_nothing(document):
    catalogue = document["topology_catalogue"]
    assert {item["topology_id"] for item in catalogue} == {
        "in-cell-local",
        "host-brokered-local",
        "remote-provider-broker",
    }
    for item in catalogue:
        assert item["selected"] is False
        assert item["configured"] is False
        assert item["execution_enabled"] is False
        assert item["new_boundaries"]
        assert item["required_future_decisions"]


def test_any_topology_selection_fails_semantic_validation(document):
    changed = copy.deepcopy(document)
    changed["topology_catalogue"][0]["selected"] = True
    with pytest.raises(admission.AdmissionDesignError, match="topology"):
        admission.validate_document(changed)


def test_instruction_policy_is_independently_hashed(document):
    assert document["instruction_policy_digest"] == admission._sha256_json(
        document["instruction_policy"]
    )
    assert (
        document["instruction_policy"]["evidence_semantics"]
        == "data_only_never_policy_or_capability"
    )


def test_instruction_policy_mutation_fails_closed(document):
    changed = copy.deepcopy(document)
    changed["instruction_policy"]["sole_egress_route"] = "direct-downstream"
    with pytest.raises(
        admission.AdmissionDesignError, match="instruction-policy-digest"
    ):
        admission.validate_document(changed)


def test_embedded_instruction_is_data_and_policy_digest_is_unchanged(document):
    case = next(
        case
        for case in document["validation_cases"]
        if case["case_id"] == "embedded-policy-bypass-text"
    )
    before = document["instruction_policy_digest"]
    result = admission.evaluate_case(document, case)
    assert result == {
        "case_id": "embedded-policy-bypass-text",
        "decision": "design_valid",
        "reason_codes": [
            "evidence-instruction-treated-as-data",
            "policy-digest-unchanged",
        ],
    }
    assert document["instruction_policy_digest"] == before
    assert document["admission_envelope"]["execution_enabled"] is False


def test_context_is_typed_minimal_source_labelled_and_purpose_bound(document):
    allowed_types = set(
        document["instruction_policy"]["allowed_context_frame_types"]
    )
    frames = document["context_frames"]
    assert len(frames) == 6
    for frame in frames:
        assert frame["frame_type"] in allowed_types
        assert frame["source_label"] in admission.EXPECTED_SOURCE_LABELS
        assert frame["purpose"] == admission.EXPECTED_PURPOSE
        assert frame["practice_id"] == "practice-synth-a"
        assert frame["principal_id"] == "principal-reception"
        assert frame["context_revision"] == 7
        assert frame["freshness"]["status"] == "current"
        size, digest = admission._frame_payload_metrics(frame)
        assert frame["canonical_bytes"] == size
        assert frame["payload_sha256"] == digest


def test_context_payload_has_no_real_people_or_connection_material(document):
    text = json.dumps(document["context_frames"], sort_keys=True).lower()
    for forbidden in (
        "margaret",
        "shera",
        "medicare",
        "postgres",
        "http://",
        "https://",
        "api_key",
        "password",
        "bearer",
    ):
        assert forbidden not in text


@pytest.mark.parametrize(
    ("case_id", "decision"),
    [
        ("transport-selection", "reject_transport_selection"),
        ("guessed-token-budget", "reject_token_policy"),
        ("network-capability-request", "reject_capability_expansion"),
        ("cross-practice-frame", "reject_scope_mismatch"),
        ("cross-principal-frame", "reject_scope_mismatch"),
        ("unknown-context-frame", "reject_context_type"),
        ("secret-sensitivity", "reject_context_sensitivity"),
        ("stale-availability", "reject_stale_context"),
        ("oversized-input", "reject_input_budget"),
        ("too-many-output-drafts", "reject_output_budget"),
        ("late-after-cancellation", "reject_cancelled_or_late"),
        ("proofreader-bypass", "reject_egress_bypass"),
        ("command-shaped-output", "reject_output_authority"),
    ],
)
def test_adversarial_case_rejects_with_exact_decision(document, case_id, decision):
    case = next(case for case in document["validation_cases"] if case["case_id"] == case_id)
    result = admission.evaluate_case(document, case)
    assert result["decision"] == decision
    assert result["reason_codes"] == case["expected_reason_codes"]


def test_all_authored_cases_match_their_exact_expectations(document):
    results = admission.evaluate_cases(document)
    assert len(results) == 15
    assert [item["case_id"] for item in results] == [
        item["case_id"] for item in document["validation_cases"]
    ]
    for case, result in zip(document["validation_cases"], results, strict=True):
        assert result["decision"] == case["expected_decision"]
        assert result["reason_codes"] == case["expected_reason_codes"]


def test_token_budget_is_explicitly_unresolved_not_guessed(document):
    token = document["admission_envelope"]["token_budget"]
    assert token["status"] == "unresolved-until-model-and-tokenizer-selected"
    assert token["value"] is None
    assert token["unit"] is None
    assert token["model_independent_caps_remain_binding"] is True


def test_model_independent_budgets_are_finite_and_current_input_fits(document):
    envelope = document["admission_envelope"]
    budgets = envelope["budgets"]
    assert budgets == {
        "maximum_context_frames": 8,
        "maximum_input_bytes": 4096,
        "maximum_output_drafts": 5,
        "maximum_output_bytes": 8192,
        "maximum_attempts_per_context_revision": 2,
        "observed_output_drafts": 0,
        "observed_output_bytes": 0,
    }
    assert envelope["context_binding"]["observed_input_bytes"] == 660


def test_capability_vacuum_is_exact(document):
    capabilities = document["admission_envelope"]["capabilities"]
    assert capabilities["tools"] == []
    assert capabilities["secrets"] == []
    assert not any(
        value
        for key, value in capabilities.items()
        if key not in {"tools", "secrets"}
    )


def test_output_ports_are_the_exact_accepted_predecessor_ports(document):
    predecessor = _load(admission.PREDECESSOR_PATH)
    predecessor_ports = {
        (port["id"], port["frame_type"], port["authority_ceiling"])
        for port in predecessor["output_ports"]
    }
    admission_ports = {
        (port["port_id"], port["frame_type"], port["authority_ceiling"])
        for port in document["instruction_policy"]["allowed_output_ports"]
    }
    assert predecessor_ports == admission_ports == admission.EXPECTED_PORTS


def test_proofreader_is_the_only_egress_and_output_is_draft_only(document):
    output = document["admission_envelope"]["output_contract"]
    assert output["requested_authority"] == "draft-only"
    assert output["egress_route"] == "deterministic-proofreader-v1"
    assert output["direct_downstream_delivery"] is False
    assert output["direct_human_gate_delivery"] is False


def test_cancelled_attempt_is_terminal_before_proofreader(document):
    case = next(
        item
        for item in document["validation_cases"]
        if item["case_id"] == "late-after-cancellation"
    )
    result = admission.evaluate_case(document, case)
    assert result["decision"] == "reject_cancelled_or_late"
    assert result["reason_codes"] == ["attempt-terminal-before-egress"]


def test_compiled_manifests_are_exactly_committed_and_inert(document):
    compiled = admission.compile_manifests(document)
    assert compiled == _load(MANIFEST_PATH)
    assert compiled["manifest_count"] == 6
    assert compiled["source_document_sha256"] == _sha256(EXAMPLE_PATH)
    for manifest in compiled["manifests"]:
        assert manifest["dry_run"] is True
        assert manifest["execution_enabled"] is False
        assert manifest["default_decision"] == "deny"


def test_manifests_have_no_runtime_coordinates_or_secret_material():
    text = MANIFEST_PATH.read_text(encoding="utf-8").lower()
    for forbidden in (
        "endpoint",
        "dsn",
        "credential",
        "api_key",
        "password",
        "image:",
        "command_line",
        "provider_name",
        "model_name",
    ):
        assert forbidden not in text


def test_evidence_is_exactly_reproducible_and_runtime_negative(document):
    observed = admission.build_evidence(document)
    committed = _load(EVIDENCE_PATH)
    assert observed == committed
    assert committed["result"] == "ariadne_bounded_agent_admission_design_pass"
    assert committed["counts"]["case_count"] == 15
    assert not any(committed["runtime_posture"].values())


def test_public_trace_is_fixed_minimal_and_does_not_echo_context(document):
    trace = admission._trace(document)
    assert "status: valid" in trace
    assert "execution-enabled: false" in trace
    assert "transport-selected: false" in trace
    assert "adversarial-cases: 15" in trace
    assert "booking-request-001" not in trace
    assert "Ignore policy" not in trace
    assert "patient-candidate" not in trace


@pytest.mark.parametrize("command", ["validate", "compile-manifests", "trace"])
def test_cli_exposes_only_the_three_non_executing_commands(monkeypatch, capsys, command):
    monkeypatch.setattr(sys, "argv", [SCRIPT_PATH.name, command])
    assert admission.main() == 0
    output = capsys.readouterr().out
    assert output
    if command == "validate":
        assert "execution_enabled=false" in output
    elif command == "compile-manifests":
        parsed = json.loads(output)
        assert parsed == _load(MANIFEST_PATH)
    else:
        assert "mode: design-only" in output


def test_script_imports_only_standard_library_and_has_no_actuator_modules():
    tree = ast.parse(SCRIPT_PATH.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    assert imported_roots <= {
        "__future__",
        "argparse",
        "copy",
        "hashlib",
        "json",
        "pathlib",
        "typing",
    }
    assert not imported_roots & {
        "asyncio",
        "docker",
        "httpx",
        "openai",
        "psycopg",
        "requests",
        "socket",
        "sqlalchemy",
        "subprocess",
        "threading",
        "time",
        "urllib",
    }


def test_script_has_no_runtime_or_product_actuator_language():
    source = SCRIPT_PATH.read_text(encoding="utf-8").lower()
    for forbidden in (
        "docker run",
        "docker build",
        "create_subprocess",
        "popen(",
        "requests.get",
        "requests.post",
        "psycopg.connect",
        "sqlalchemy.create_engine",
        "uvicorn.run",
    ):
        assert forbidden not in source


def test_design_docs_preserve_the_non_executing_api_spine_boundary():
    text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in (
            "docs/ariadne-bounded-agent-admission-design-plan.md",
            "docs/ariadne-bounded-agent-admission-design.md",
            "docs/security/ariadne-bounded-agent-admission-threat-model-delta.md",
        )
    ).lower()
    assert "graphql remains read-only" in text
    assert "rest/openapi" in text
    assert "proofreader" in text
    assert "no model" in text
    assert "no `docs/api-spine/`" in text
