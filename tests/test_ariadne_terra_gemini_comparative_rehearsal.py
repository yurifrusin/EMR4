from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema
import pytest

from scripts import ariadne_terra_gemini_comparative_rehearsal as rehearsal
from scripts import ariadne_terra_gemini_repository_only_verify as local_verify

CONTINUITY_GRAPH_PATH = (
    rehearsal.ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
)
COMPASS_PATH = (
    rehearsal.ROOT / "orchestration" / "continuity" / "emr4-compass.json"
)


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _node_contract_eval(source: str, payload: dict) -> dict:
    node = shutil.which("node")
    assert node is not None, "Node.js is required for broker contract tests."
    completed = subprocess.run(
        [node, "--input-type=module", "--eval", source],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=rehearsal.ROOT,
        timeout=30,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


def _canonical_drafts():
    document = _json(rehearsal.WORK_CELL_DOCUMENT_PATH)
    by_id = {
        item["id"]: copy.deepcopy(item)
        for item in document["draft_frames"]
        if item["id"] in rehearsal.PRIMARY_DRAFT_IDS
    }
    order = [
        "draft-ux-primary",
        "draft-human-primary",
        "draft-audit-primary",
        "draft-orchestrator-primary",
        "draft-advisory-primary",
    ]
    drafts = [by_id[item] for item in order]
    for draft in drafts:
        draft["batch_id"] = "generated-batch-001"
        draft["attempt_id"] = "generated-attempt-001"
        draft["provenance"] = {
            "kind": "model-generated-draft",
            "source": "generated-attempt-001",
        }
    next(
        item for item in drafts if item["id"] == "draft-audit-primary"
    )["payload"]["attempt_id"] = "generated-attempt-001"
    return drafts


def test_static_contract_passes_without_container_or_provider():
    result = rehearsal.validate_static()
    assert result["status"] == "passed"
    assert result["context_frame_count"] == 6
    assert result["prompt_bytes"] <= 32768
    assert result["provider_call_performed"] is False
    assert result["prompt_transmitted"] is False
    assert {
        lane: report["status"]
        for lane, report in result["provider_contracts"].items()
    } == {"terra": "passed", "gemini": "passed"}
    assert all(
        report["provider_call_performed"] is False
        for report in result["provider_contracts"].values()
    )


def test_shared_task_projection_removes_transport_and_neutralises_label():
    source = _json(rehearsal.SOURCE_ATTEMPT_PATH)
    projected = rehearsal.shared_task()
    assert "model_contract" in source
    assert "model_contract" not in projected
    source.pop("model_contract")
    source["schema_version"] = "ariadne.provider_neutral_comparison_task.v1"
    assert projected == source


def test_frozen_lane_order_models_endpoints_and_no_substitution():
    manifest = _json(rehearsal.MANIFEST_PATH)
    assert [
        (
            item["lane_id"],
            item["model_id"],
            item["host"],
            item["path"],
        )
        for item in manifest["lanes"]
    ] == [
        (
            "terra",
            "gpt-5.6-terra",
            "api.openai.com",
            "/v1/responses",
        ),
        (
            "gemini",
            "gemini-3.5-flash",
            "generativelanguage.googleapis.com",
            "/v1beta/models/gemini-3.5-flash:generateContent",
        ),
    ]
    assert "aiplatform.googleapis.com" not in json.dumps(manifest)


def test_provider_schema_and_full_schema_accept_canonical_drafts():
    envelope = {"drafts": _canonical_drafts()}
    for path in (rehearsal.PROVIDER_SCHEMA_PATH, rehearsal.FULL_SCHEMA_PATH):
        jsonschema.Draft202012Validator(_json(path)).validate(envelope)


def test_common_provider_schema_has_explicit_enum_types_and_no_boolean_enum():
    schema = _json(rehearsal.PROVIDER_SCHEMA_PATH)
    enum_nodes = []

    def walk(node):
        if isinstance(node, dict):
            if "enum" in node:
                enum_nodes.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(schema)
    assert enum_nodes
    assert all(
        node.get("type") in {"string", "integer", "number"}
        for node in enum_nodes
    )
    confirmation = schema["properties"]["drafts"]["items"]["properties"][
        "payload"
    ]["anyOf"][1]["properties"]["confirmation_required"]
    assert confirmation == {"type": "boolean"}


def test_provider_profiles_reject_untyped_and_gemini_boolean_enums():
    schema = _json(rehearsal.PROVIDER_SCHEMA_PATH)
    untyped = copy.deepcopy(schema)
    untyped["properties"]["drafts"]["items"]["properties"]["id"].pop("type")
    assert any(
        violation.endswith("enum-type-missing")
        for violation in rehearsal.provider_contract_violations(
            untyped, "terra"
        )
    )

    boolean_enum = copy.deepcopy(schema)
    confirmation = boolean_enum["properties"]["drafts"]["items"][
        "properties"
    ]["payload"]["anyOf"][1]["properties"]["confirmation_required"]
    confirmation["enum"] = [True]
    violations = rehearsal.provider_contract_violations(
        boolean_enum, "gemini"
    )
    assert any(
        violation.endswith("boolean-enum-unsupported")
        for violation in violations
    )


def test_node_provider_profiles_compile_without_network_or_credentials():
    module_url = rehearsal.PROVIDER_CONTRACT_MODULE_PATH.as_uri()
    source = f"""
import {{ compileProviderSchema }} from {json.dumps(module_url)};
import {{ readFileSync }} from "node:fs";
const input = JSON.parse(readFileSync(0, "utf8"));
const result = Object.fromEntries(
  ["terra", "gemini"].map((lane) => {{
    const compiled = compileProviderSchema(input.schema, lane);
    return [lane, {{
      confirmation: compiled.properties.drafts.items.properties.payload
        .anyOf[1].properties.confirmation_required,
      hasProviderCall: false,
    }}];
  }}),
);
process.stdout.write(JSON.stringify(result));
"""
    result = _node_contract_eval(
        source, {"schema": _json(rehearsal.PROVIDER_SCHEMA_PATH)}
    )
    assert result == {
        "terra": {
            "confirmation": {"type": "boolean"},
            "hasProviderCall": False,
        },
        "gemini": {
            "confirmation": {"type": "boolean"},
            "hasProviderCall": False,
        },
    }


def test_gemini_request_contract_excludes_unsupported_candidate_count():
    module_url = rehearsal.PROVIDER_CONTRACT_MODULE_PATH.as_uri()
    source = f"""
import {{
  buildGeminiGenerateContentRequest,
}} from {json.dumps(module_url)};
import {{ readFileSync }} from "node:fs";
const input = JSON.parse(readFileSync(0, "utf8"));
const request = buildGeminiGenerateContentRequest(
  {{
    system_prompt: "authored-synthetic-system-sentinel",
    prompt: "authored-synthetic-user-sentinel",
  }},
  input.schema,
  2048,
);
process.stdout.write(JSON.stringify({{
  topLevelFields: Object.keys(request).sort(),
  generationConfigFields: Object.keys(request.generationConfig).sort(),
  candidateCountPresent: Object.hasOwn(
    request.generationConfig,
    "candidateCount",
  ),
  maximumOutputTokens: request.generationConfig.maxOutputTokens,
  responseMimeType: request.generationConfig.responseMimeType,
  thinkingConfig: request.generationConfig.thinkingConfig,
  store: request.store,
  schemaUnchanged:
    JSON.stringify(request.generationConfig.responseJsonSchema) ===
    JSON.stringify(input.schema),
}}));
"""
    result = _node_contract_eval(
        source, {"schema": _json(rehearsal.PROVIDER_SCHEMA_PATH)}
    )
    assert result == {
        "topLevelFields": [
            "contents",
            "generationConfig",
            "store",
            "systemInstruction",
        ],
        "generationConfigFields": [
            "maxOutputTokens",
            "responseJsonSchema",
            "responseMimeType",
            "thinkingConfig",
        ],
        "candidateCountPresent": False,
        "maximumOutputTokens": 2048,
        "responseMimeType": "application/json",
        "thinkingConfig": {
            "thinkingLevel": "MEDIUM",
            "includeThoughts": False,
        },
        "store": False,
        "schemaUnchanged": True,
    }
    profile = _json(rehearsal.PROVIDER_PROFILES_PATH)["profiles"]["gemini"]
    assert profile["unsupported_generation_config_fields"] == [
        "candidateCount"
    ]


def test_provider_blocked_gemini_diagnostic_has_no_network_or_env_access():
    diagnostic_path = (
        rehearsal.ROOT
        / "scripts"
        / "ariadne_gemini_request_contract_diagnostic.mjs"
    )
    source = diagnostic_path.read_text(encoding="utf-8")
    for forbidden in (
        'from "node:http"',
        'from "node:https"',
        "fetch(",
        "process.env",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
    ):
        assert forbidden not in source

    node = shutil.which("node")
    assert node is not None
    completed = subprocess.run(
        [node, str(diagnostic_path)],
        text=True,
        capture_output=True,
        cwd=rehearsal.ROOT,
        env=local_verify.verification_environment(os.environ),
        timeout=30,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["status"] == "passed"
    assert result["diagnosis"] == {
        "finding_code": "gemini_3x_candidate_count_unsupported",
        "unsupported_field": "candidateCount",
        "field_observed_in_attempt_003_constructor": True,
        "field_present_after_repair": False,
        "capable_of_observed_invalid_argument": True,
        "exact_historical_cause_proven": False,
        "uncertainty_reason": (
            "raw_provider_error_message_was_intentionally_not_retained"
        ),
        "schema_complexity_excluded_as_possible_cause": False,
    }
    assert all(
        value is False
        for key, value in result["boundaries"].items()
        if key != "authored_synthetic_sentinels_only"
    )


def test_synthetic_provider_errors_retain_only_allowlisted_metadata():
    module_url = rehearsal.PROVIDER_CONTRACT_MODULE_PATH.as_uri()
    source = f"""
import {{ sanitiseProviderErrorMetadata }} from {json.dumps(module_url)};
import {{ readFileSync }} from "node:fs";
const input = JSON.parse(readFileSync(0, "utf8"));
const result = {{
  terra: sanitiseProviderErrorMetadata(
    "terra",
    Buffer.from(JSON.stringify(input.terra.body)),
    input.terra.headers,
  ),
  gemini: sanitiseProviderErrorMetadata(
    "gemini",
    Buffer.from(JSON.stringify(input.gemini.body)),
    input.gemini.headers,
  ),
}};
process.stdout.write(JSON.stringify(result));
"""
    result = _node_contract_eval(
        source,
        {
            "terra": {
                "body": {
                    "error": {
                        "message": "synthetic sensitive provider prose",
                        "type": "server_error",
                        "code": "internal_error",
                        "param": "text.format.schema",
                        "unknown": "must-not-survive",
                    }
                },
                "headers": {
                    "x-request-id": "req_synthetic_terra_001",
                    "authorization": "must-not-survive",
                },
            },
            "gemini": {
                "body": {
                    "error": {
                        "code": 400,
                        "message": "synthetic credential or schema prose",
                        "status": "INVALID_ARGUMENT",
                        "details": [{"reason": "must-not-survive"}],
                    }
                },
                "headers": {
                    "x-goog-request-id": "goog_synthetic_gemini_001",
                    "set-cookie": "must-not-survive",
                },
            },
        },
    )
    assert result == {
        "terra": {
            "provider_error_type": "server_error",
            "provider_error_code": "internal_error",
            "provider_error_parameter": "text.format.schema",
            "provider_request_id": "req_synthetic_terra_001",
        },
        "gemini": {
            "provider_error_status": "INVALID_ARGUMENT",
            "provider_error_code": 400,
            "provider_request_id": "goog_synthetic_gemini_001",
        },
    }
    assert "message" not in json.dumps(result).lower()
    assert "must-not-survive" not in json.dumps(result)


def test_synthetic_provider_error_metadata_rejects_unsafe_scalars():
    module_url = rehearsal.PROVIDER_CONTRACT_MODULE_PATH.as_uri()
    source = f"""
import {{ sanitiseProviderErrorMetadata }} from {json.dumps(module_url)};
import {{ readFileSync }} from "node:fs";
const input = JSON.parse(readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(sanitiseProviderErrorMetadata(
  "terra",
  Buffer.from(JSON.stringify(input.body)),
  input.headers,
)));
"""
    result = _node_contract_eval(
        source,
        {
            "body": {
                "error": {
                    "type": "unsafe value with spaces",
                    "code": "unsafe\nnewline",
                    "param": {"nested": "unsafe"},
                }
            },
            "headers": {"x-request-id": "unsafe request id"},
        },
    )
    assert result == {}


def test_public_audit_event_export_is_lossless_and_fail_closed():
    event_without_hash = {
        "audit_sequence": 1,
        "previous_event_sha256": f"sha256:{'0' * 64}",
        "event": "broker-ready",
        "lane_id": "terra",
        "model_id": "gpt-5.6-terra",
        "allowed_path": "/infer",
        "upstream_host": "api.openai.com",
        "upstream_path": "/v1/responses",
        "maximum_provider_calls": 1,
    }
    event = {
        **event_without_hash,
        "event_sha256": rehearsal.sha256_bytes(
            rehearsal.canonical_json(event_without_hash).encode()
        ),
    }
    exported = rehearsal.export_public_audit_event(event)
    assert exported == event
    assert exported is not event
    assert rehearsal._validate_broker_audit_chain([exported])

    with pytest.raises(
        rehearsal.RehearsalError,
        match="audit-event-export-field-not-allowlisted",
    ):
        rehearsal.export_public_audit_event(
            {**event, "future_unreviewed_field": "synthetic"}
        )


def test_external_audit_track_is_outside_sandbox_and_excludes_raw_reasoning():
    policy = _json(rehearsal.AUDIT_TRACK_POLICY_PATH)
    assert policy["owner"] == "trusted_broker_and_orchestrator_control_plane"
    assert policy["sandbox_append_authority"] is False
    assert policy["sandbox_rewrite_or_delete_authority"] is False
    assert "hidden_reasoning" in policy["never_record"]
    assert (
        policy["rationale_contract"]["allowed"]
        == "typed_bounded_decision_rationale_with_evidence_and_rule_references"
    )
    assert policy["current_implementation"] == {
        "broker_hash_chained_events": True,
        "host_chain_verification": True,
        "allowlisted_provider_error_metadata": True,
        "typed_output_field_manifest": True,
        "proofreader_disposition_in_host_evidence": True,
        "durable_sanitised_event_allowlist_complete": True,
        "durable_sanitised_event_export_lossless_for_allowlisted_fields": True,
        "unallowlisted_event_field_disposition": (
            "fail_closed_without_export"
        ),
        "attempt_003_original_durable_export_revalidation": (
            "failed_omitted_broker_ready_fields"
        ),
        "durable_product_audit_store": False,
        "provider_call_performed_by_this_policy": False,
    }


def test_external_audit_hash_chain_detects_tampering():
    module_url = rehearsal.PROVIDER_CONTRACT_MODULE_PATH.as_uri()
    source = f"""
import {{ sealAuditEvent }} from {json.dumps(module_url)};
import {{ createHash }} from "node:crypto";
const hash = (value) =>
  `sha256:${{createHash("sha256").update(value).digest("hex")}}`;
let previous = `sha256:${{"0".repeat(64)}}`;
const events = ["broker-ready", "provider-call-started"].map(
  (name, index) => {{
    const event = sealAuditEvent(
      {{ event: name, lane_id: "terra" }},
      index + 1,
      previous,
      hash,
    );
    previous = event.event_sha256;
    return event;
  }},
);
process.stdout.write(JSON.stringify({{ events }}));
"""
    events = _node_contract_eval(source, {})["events"]
    assert rehearsal._validate_broker_audit_chain(events) is True
    tampered = copy.deepcopy(events)
    tampered[0]["lane_id"] = "gemini"
    assert rehearsal._validate_broker_audit_chain(tampered) is False


def test_typed_output_audit_manifest_records_keys_not_sensitive_values():
    module_url = rehearsal.PROVIDER_CONTRACT_MODULE_PATH.as_uri()
    source = f"""
import {{ typedOutputAuditManifest }} from {json.dumps(module_url)};
import {{ createHash }} from "node:crypto";
import {{ readFileSync }} from "node:fs";
const input = JSON.parse(readFileSync(0, "utf8"));
const hash = (value) =>
  `sha256:${{createHash("sha256").update(value).digest("hex")}}`;
process.stdout.write(JSON.stringify(typedOutputAuditManifest(input.drafts, hash)));
"""
    result = _node_contract_eval(
        source,
        {
            "drafts": [
                {
                    "id": "draft-ux-primary",
                    "output_port_id": "port-ux",
                    "frame_type": "booking-ux-projection-candidate.v1",
                    "payload": {
                        "selected_slot_id": "sensitive-synthetic-value",
                        "context_revision": 7,
                    },
                    "provenance": {"kind": "model-generated-draft"},
                }
            ]
        },
    )
    assert result[0]["id"] == "draft-ux-primary"
    assert result[0]["output_port_id"] == "port-ux"
    assert result[0]["payload_field_names"] == [
        "context_revision",
        "selected_slot_id",
    ]
    assert result[0]["draft_sha256"].startswith("sha256:")
    assert "sensitive-synthetic-value" not in json.dumps(result)


def test_repository_only_verifier_has_fixed_conftest_free_population():
    command = local_verify.verification_command()
    assert command[:4] == [
        sys.executable,
        "-m",
        "pytest",
        "--noconftest",
    ]
    assert command.count("--noconftest") == 1
    assert tuple(command[-len(local_verify.FIXED_TEST_PATHS) :]) == (
        local_verify.FIXED_TEST_PATHS
    )
    assert "tests/test_ariadne_terra_gemini_comparative_rehearsal.py" in command
    assert all("conftest.py" not in item for item in command)


def test_repository_only_verifier_drops_database_and_provider_environment():
    environment = local_verify.verification_environment(
        {
            "PATH": "synthetic-path",
            "SYSTEMROOT": "synthetic-system-root",
            "DATABASE_URL": "synthetic-database-secret",
            "OPENAI_API_KEY": "synthetic-openai-secret",
            "GEMINI_API_KEY": "synthetic-gemini-secret",
            "UNRELATED_SECRET": "synthetic-other-secret",
        }
    )
    assert environment["PATH"] == "synthetic-path"
    assert environment["SYSTEMROOT"] == "synthetic-system-root"
    assert environment["ARIADNE_REPOSITORY_ONLY_VERIFICATION"] == "1"
    assert environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"
    assert environment["PYTEST_ADDOPTS"] == ""
    assert "DATABASE_URL" not in environment
    assert "OPENAI_API_KEY" not in environment
    assert "GEMINI_API_KEY" not in environment
    assert "UNRELATED_SECRET" not in environment


def test_continuity_accepts_only_the_provider_free_diagnostic_descendant():
    graph = _json(CONTINUITY_GRAPH_PATH)
    assert graph["graph_revision"] >= 28
    node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "ariadne-terra-gemini-diagnostic-hardening"
    )
    assert node["status"] == "accepted"
    assert node["kind"] == "tooling"
    assert {
        item["id"]: item["status"] for item in node["decisions"]
    } == {
        "ariadne-provider-contract-diagnostic-authorised": "accepted",
        "ariadne-provider-contract-diagnostic-initial-closeout-rejected": (
            "rejected"
        ),
        "ariadne-provider-contract-diagnostic-fresh-closeout-accepted": (
            "accepted"
        ),
    }
    joined = json.dumps(node)
    assert "No retry, provider call, credential read, container, database" in joined
    assert "durable practice-scoped product audit service" in joined
    comparison = next(
        item
        for item in graph["nodes"]
        if item["id"] == "ariadne-terra-gemini-comparative-rehearsal"
    )
    assert comparison["status"] == "rejected"
    decisions = {
        item["id"]: item["status"] for item in comparison["decisions"]
    }
    assert (
        decisions["ariadne-terra-gemini-attempt-003-audit-authorised"]
        == "accepted"
    )
    assert (
        decisions["ariadne-terra-gemini-attempt-003-revision-required"]
        == "rejected"
    )
    assert (
        decisions[
            "ariadne-gemini-provider-blocked-request-contract-diagnostic-accepted"
        ]
        == "accepted"
    )
    comparison_text = json.dumps(comparison)
    assert "five typed drafts passed" in comparison_text
    assert "original durable sanitized chains" in comparison_text
    assert "candidateCount" in comparison_text
    assert "fails closed on any unallowlisted event field" in comparison_text


def test_compass_records_consumed_attempt4_and_keeps_next_route_at_yuri_gate():
    graph = _json(CONTINUITY_GRAPH_PATH)
    compass = _json(COMPASS_PATH)
    assert compass["map_revision"] >= 17
    assert compass["source_graph_revision"] == graph["graph_revision"]
    horizon_ids = {
        item["id"] for item in compass["programme_support_horizon"]
    }
    decision_ids = {
        item["id"] for item in compass["user_owned_decisions"]
    }
    assert "ariadne-terra-gemini-provider-contract-diagnostic" not in horizon_ids
    assert (
        "authorize-terra-gemini-provider-contract-diagnostic-design"
        not in decision_ids
    )
    assert "ariadne-gemini-request-contract-diagnostic" not in horizon_ids
    assert (
        "authorize-gemini-request-contract-diagnostic-or-retry"
        not in decision_ids
    )
    assert "authorize-gemini-occupied-retry" not in decision_ids
    assert "authorize-next-residency-safe-model-tranche" in decision_ids
    assert any(
        "accepted provider-contract diagnostic hardening" in limit
        and "made no provider call" in limit
        for limit in compass["map_limits"]
    )
    assert any(
        "Consumed attempt 003 proves one bounded Terra generated-draft path"
        in limit
        for limit in compass["map_limits"]
    )
    assert any(
        "accepted provider-blocked Gemini diagnostic" in limit
        and "candidateCount" in limit
        and "authorises no occupied retry" in limit
        for limit in compass["map_limits"]
    )
    assert any(
        "Consumed attempt 004 made exactly one repaired direct Gemini"
        in limit
        and "no retry is authorised" in limit
        for limit in compass["map_limits"]
    )
    assert any(
        "direct Gemini Developer API attempt is not Australian-processing"
        in limit
        and "Gemini 3.5 Flash Sydney documentary descendant then failed closed"
        in limit
        for limit in compass["map_limits"]
    )


def test_full_schema_rejects_safe_looking_but_wrong_port_pairing():
    drafts = _canonical_drafts()
    drafts[0]["output_port_id"] = "port-advisory"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(
            _json(rehearsal.FULL_SCHEMA_PATH)
        ).validate({"drafts": drafts})


def test_existing_deterministic_proofreader_passes_canonical_generated_form():
    proof = rehearsal._proofread(_canonical_drafts())
    assert proof["status"] == "passed"
    assert proof["disposition"] == "release-verified-outputs"
    assert proof["released_edge_count"] == 5
    assert proof["repair_receipt_count"] == 0
    assert [item["verdict"] for item in proof["frame_verdicts"]] == [
        "pass_to_downstream",
        "pass_to_human_gate",
        "pass_to_downstream",
        "pass_to_downstream",
        "pass_to_human_gate",
    ]


def test_prompt_material_is_provider_neutral_and_deterministic():
    first = rehearsal.prompt_material()
    second = rehearsal.prompt_material()
    assert first["hashes"] == second["hashes"]
    prompt = first["prompt"].lower()
    system = first["system_prompt"].lower()
    for marker in (
        "gpt-5.6-terra",
        "gemini-3.5-flash",
        "openai",
        "google",
        "deepseek",
    ):
        assert marker not in prompt
        assert marker not in system
    assert "model_contract" not in prompt


def test_full_schema_prompt_projection_changes_metadata_not_constraints():
    source = _json(rehearsal.FULL_SCHEMA_PATH)
    projected = rehearsal.provider_neutral_full_schema()
    assert projected["$id"].endswith(
        "ariadne-provider-neutral-work-cell-output.schema.json"
    )
    assert projected["title"] == (
        "Ariadne Provider-Neutral Work-Cell Draft Envelope"
    )
    source["$id"] = projected["$id"]
    source["title"] = projected["title"]
    assert projected == source


def test_build_context_preserves_every_expected_sealed_hash_byte_for_byte():
    material = rehearsal.prompt_material()
    with tempfile.TemporaryDirectory(
        prefix="ariadne-comparison-hash-test-"
    ) as raw:
        target = Path(raw)
        rehearsal._copy_build_context(target)
        actual = {
            "shared_task_sha256": rehearsal.sha256_bytes(
                (target / "shared-task.json").read_bytes()
            ),
            "full_output_schema_sha256": rehearsal.sha256_bytes(
                (target / "full-output.schema.json").read_bytes()
            ),
            "provider_output_schema_sha256": rehearsal.sha256_bytes(
                rehearsal.js_json(
                    _json(target / "provider-output.schema.json")
                ).encode()
            ),
            "system_prompt_sha256": rehearsal.sha256_bytes(
                material["system_prompt"].encode()
            ),
            "prompt_sha256": rehearsal.sha256_bytes(
                material["prompt"].encode()
            ),
        }
        assert actual == material["hashes"]
        assert b"\r\n" not in (target / "full-output.schema.json").read_bytes()


def test_broker_fixes_one_path_call_budget_and_exact_upstreams():
    source = rehearsal.BROKER_PATH.read_text(encoding="utf-8")
    contracts = rehearsal.PROVIDER_CONTRACT_MODULE_PATH.read_text(
        encoding="utf-8"
    )
    assert 'const ALLOWED_PATH = "/infer"' in source
    assert 'model: "gpt-5.6-terra"' in source
    assert 'model: "gemini-3.5-flash"' in source
    assert 'host: "api.openai.com"' in source
    assert 'host: "generativelanguage.googleapis.com"' in source
    assert "providerCallCount >= 1" in source
    assert "providerCallCount += 1" in source
    assert "max_output_tokens: MAX_OUTPUT_TOKENS" in source
    assert "MAX_OUTPUT_TOKENS" in source
    assert "buildGeminiGenerateContentRequest" in source
    assert "candidateCount" not in source
    assert "tools: []" in source
    assert "store: false" in source
    assert "compileProviderSchema" in source
    assert "sanitiseProviderErrorMetadata" in source
    assert "provider_schema_profile_sha256" in source
    assert "previous_event_sha256" in contracts
    assert "typed-output-observed" in source
    assert "response_body" not in source
    assert "prompt:" not in source


def test_work_cell_has_no_provider_key_sdk_cli_or_model_identity():
    source = rehearsal.LAUNCHER_PATH.read_text(encoding="utf-8")
    for forbidden in (
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "gpt-5.6-terra",
        "gemini-3.5-flash",
        "@google/genai",
        "openai",
        "child_process",
    ):
        assert forbidden not in source
    assert 'path: "/infer"' in source
    assert 'hostname: "broker"' in source


def test_dockerfile_uses_non_root_fixed_launchers_and_no_wildcard_copy():
    source = rehearsal.DOCKERFILE_PATH.read_text(encoding="utf-8")
    assert source.count("USER node") == 2
    assert "COPY . " not in source
    assert "API_KEY" not in source
    assert 'CMD ["node", "/opt/ariadne/broker.mjs"]' in source
    assert 'CMD ["node", "/opt/ariadne/launcher.mjs"]' in source


def test_live_run_fails_before_consumption_when_both_credentials_absent(
    monkeypatch,
):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    before = {
        lane: _json(rehearsal.SOURCE_DIR / f"{lane}-single-use-ledger.json")
        for lane in ("terra", "gemini")
    }
    with pytest.raises(
        rehearsal.RehearsalError,
        match="both-provider-credentials-required-before-consumption",
    ):
        rehearsal.run_live(authorised=True)
    after = {
        lane: _json(rehearsal.SOURCE_DIR / f"{lane}-single-use-ledger.json")
        for lane in ("terra", "gemini")
    }
    assert after == before


def test_live_run_requires_explicit_flag_before_credential_check():
    with pytest.raises(
        rehearsal.RehearsalError,
        match="explicit-authorisation-flag-required",
    ):
        rehearsal.run_live(authorised=False)


def test_fresh_attempt_consumed_new_ledgers_without_resetting_attempt_one():
    authority = _json(rehearsal.FRESH_ATTEMPT_PATH)
    old_terra = _json(rehearsal.TERRA_LEDGER_PATH)
    fresh_terra = _json(rehearsal.FRESH_TERRA_LEDGER_PATH)
    fresh_gemini = _json(rehearsal.FRESH_GEMINI_LEDGER_PATH)
    assert authority["runtime_attempt_id"] == "comparative-runtime-attempt-002"
    assert old_terra["state"] == "consumed"
    assert fresh_terra["state"] == "consumed"
    assert fresh_gemini["state"] == "consumed"
    assert fresh_terra["runtime_attempt_id"] == (
        "comparative-runtime-attempt-002"
    )
    assert fresh_gemini["runtime_attempt_id"] == (
        "comparative-runtime-attempt-002"
    )


def test_fresh_attempt_requires_explicit_flag_and_both_credentials(
    monkeypatch,
):
    with pytest.raises(
        rehearsal.RehearsalError,
        match="explicit-fresh-attempt-authorisation-required",
    ):
        rehearsal.run_fresh_attempt(authorised=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    before = (
        _json(rehearsal.FRESH_TERRA_LEDGER_PATH),
        _json(rehearsal.FRESH_GEMINI_LEDGER_PATH),
    )
    with pytest.raises(
        rehearsal.RehearsalError,
        match="both-provider-credentials-required-before-fresh-consumption",
    ):
        rehearsal.run_fresh_attempt(authorised=True)
    after = (
        _json(rehearsal.FRESH_TERRA_LEDGER_PATH),
        _json(rehearsal.FRESH_GEMINI_LEDGER_PATH),
    )
    assert after == before


def test_attempt3_has_distinct_available_authority_and_ledgers():
    authority = _json(rehearsal.ATTEMPT3_AUTHORITY_PATH)
    terra = _json(rehearsal.ATTEMPT3_TERRA_LEDGER_PATH)
    gemini = _json(rehearsal.ATTEMPT3_GEMINI_LEDGER_PATH)
    assert authority["runtime_attempt_id"] == "comparative-runtime-attempt-003"
    assert authority["run_order"] == ["terra", "gemini"]
    assert authority["retry"] is False
    assert authority["fallback"] is False
    assert authority["required_hardening"] == {
        "provider_contract_profiles": True,
        "external_hash_chained_audit": True,
        "host_chain_verification": True,
        "typed_output_manifest_without_values": True,
        "raw_reasoning_recorded": False,
    }
    assert {
        terra["runtime_attempt_id"],
        gemini["runtime_attempt_id"],
    } == {"comparative-runtime-attempt-003"}
    assert {terra["state"], gemini["state"]} <= {"available", "consumed"}
    assert terra["retry_authorised"] is False
    assert gemini["retry_authorised"] is False


def test_attempt3_requires_explicit_flag_and_credentials_before_consumption(
    monkeypatch,
):
    with pytest.raises(
        rehearsal.RehearsalError,
        match="explicit-attempt3-authorisation-required",
    ):
        rehearsal.run_attempt3(authorised=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    before = (
        _json(rehearsal.ATTEMPT3_TERRA_LEDGER_PATH),
        _json(rehearsal.ATTEMPT3_GEMINI_LEDGER_PATH),
    )
    with pytest.raises(
        rehearsal.RehearsalError,
        match="both-provider-credentials-required-before-attempt3-consumption",
    ):
        rehearsal.run_attempt3(authorised=True)
    after = (
        _json(rehearsal.ATTEMPT3_TERRA_LEDGER_PATH),
        _json(rehearsal.ATTEMPT3_GEMINI_LEDGER_PATH),
    )
    assert after == before


def test_attempt4_has_distinct_gemini_only_authority_and_ledger():
    authority = _json(rehearsal.ATTEMPT4_AUTHORITY_PATH)
    ledger = _json(rehearsal.ATTEMPT4_GEMINI_LEDGER_PATH)
    assert authority["runtime_attempt_id"] == "comparative-runtime-attempt-004"
    assert authority["run_order"] == ["gemini"]
    assert authority["maximum_provider_calls"] == {"gemini": 1, "terra": 0}
    assert authority["required_repairs"] == {
        "gemini_candidate_count_omitted": True,
        "shared_request_constructor_used": True,
        "lossless_fail_closed_audit_exporter_used": True,
    }
    assert authority["provider_route"] == {
        "api": "gemini-developer-api",
        "host": "generativelanguage.googleapis.com",
        "australian_processing_claim": False,
        "data_class": "authored-synthetic-non-pii",
    }
    assert authority["retry"] is False
    assert authority["fallback"] is False
    assert ledger["runtime_attempt_id"] == "comparative-runtime-attempt-004"
    assert ledger["lane_id"] == "gemini"
    assert ledger["state"] in {"available", "consumed"}
    assert ledger["maximum_provider_calls"] == 1
    assert ledger["retry_authorised"] is False


def test_attempt4_requires_explicit_flag_and_gemini_credential_before_consumption(
    monkeypatch,
):
    with pytest.raises(
        rehearsal.RehearsalError,
        match="explicit-attempt4-authorisation-required",
    ):
        rehearsal.run_attempt4(authorised=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    before = _json(rehearsal.ATTEMPT4_GEMINI_LEDGER_PATH)
    with pytest.raises(
        rehearsal.RehearsalError,
        match="gemini-credential-required-before-attempt4-consumption",
    ):
        rehearsal.run_attempt4(authorised=True)
    after = _json(rehearsal.ATTEMPT4_GEMINI_LEDGER_PATH)
    assert after == before


def test_public_evidence_source_excludes_raw_content_fields():
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    assert '"raw_reasoning_recorded": False' in source
    assert '"raw_prompt_recorded": False' in source
    assert '"raw_provider_response_recorded": False' in source
    assert '"draft_payload_recorded": False' in source
    assert '"provider_secret_recorded": False' in source
    assert '"drafts": drafts' not in source


def test_provider_free_preflight_evidence_has_no_call_or_residue():
    evidence = _json(rehearsal.PREFLIGHT_EVIDENCE_PATH)
    assert evidence["status"] == "passed"
    assert evidence["provider_call_performed"] is False
    assert evidence["prompt_transmitted"] is False
    assert evidence["credential_gates"]["both_present"] == all(
        evidence["credential_gates"]["lane_presence"].values()
    )
    assert evidence["credential_gates"]["credential_values_recorded"] is False
    assert all(
        all(result.values()) for result in evidence["cleanup"].values()
    )
    for lane in ("terra", "gemini"):
        cell = evidence["lane_policies"][lane]["cell"]
        broker = evidence["lane_policies"][lane]["broker"]
        assert cell["user"] == "node"
        assert cell["read_only_root"] is True
        assert cell["published_port_count"] == 0
        assert {item["destination"] for item in cell["mounts"]} == {
            "/run/secrets/broker_token"
        }
        assert {item["destination"] for item in broker["mounts"]} == {
            "/run/secrets/broker_token",
            "/run/secrets/provider_key",
        }


def test_attempt2_preflight_preserves_consumed_hashes_and_new_images():
    evidence = _json(rehearsal.FRESH_PREFLIGHT_EVIDENCE_PATH)
    assert evidence["status"] == "passed"
    assert evidence["credential_gates"]["both_present"] is True
    assert evidence["provider_call_performed"] is False
    assert evidence["prompt_transmitted"] is False
    assert evidence["static"]["shared_hashes"] == {
        "shared_task_sha256": (
            "sha256:1a537292ad029fd49ae3d9706120606547c1ddeaa7404b7bdd9047573ea69cc8"
        ),
        "full_output_schema_sha256": (
            "sha256:7efd3644329807462b3efcd3b16552d923a9262b43876432c21698656cde8a6e"
        ),
        "provider_output_schema_sha256": (
            "sha256:12eadca2cca9798f386b796e1740fd3468030c97e54f5883061f6fcea979c65d"
        ),
        "system_prompt_sha256": (
            "sha256:876a1ef5bd03675d0d83dbc6cb66bc64bdcc2a088daae59aacc8e914803afd2c"
        ),
        "prompt_sha256": (
            "sha256:6102ebb2db7ff42b07f0d1ba7abbec9c2dc333398923030b39076a4aa055d9ea"
        ),
    }
    assert all(
        all(result.values()) for result in evidence["cleanup"].values()
    )
    assert evidence["build"]["image_ids"]["terra"] == (
        evidence["build"]["image_ids"]["gemini"]
    )


def test_attempt2_runtime_evidence_records_two_calls_no_drafts_and_cleanup():
    evidence = _json(rehearsal.FRESH_COMPARISON_EVIDENCE_PATH)
    assert evidence["result"] == (
        "ariadne_terra_gemini_comparative_rehearsal_"
        "attempt2_revision_required"
    )
    assert evidence["shared_hash_match"] is True
    assert evidence["retry_performed"] is False
    assert evidence["fallback_performed"] is False
    assert evidence["cross_model_input"] is False
    assert evidence["voting"] is False

    expected_statuses = {"terra": 500, "gemini": 400}
    for lane_id, provider_status in expected_statuses.items():
        lane = evidence["lanes"][lane_id]
        assert lane["ledger"]["state"] == "consumed"
        assert lane["status"] == "revision_required"
        assert lane["reason_codes"] == ["provider-non-success"]
        events = lane["broker_events"]
        starts = [item for item in events if item["event"] == "provider-call-started"]
        completions = [
            item for item in events if item["event"] == "provider-call-completed"
        ]
        assert len(starts) == 1
        assert len(completions) == 1
        assert starts[0]["provider_call_count"] == 1
        assert completions[0]["provider_call_count"] == 1
        assert completions[0]["provider_status"] == provider_status
        assert lane["generated_draft_count"] == 0
        assert lane["provider_schema_status"] == "not-presented"
        assert lane["full_schema_status"] == "not-presented"
        assert lane["proofreader"] is None
        assert all(lane["cleanup"].values())

    assert evidence["raw_prompt_recorded"] is False
    assert evidence["raw_provider_response_recorded"] is False
    assert evidence["draft_payload_recorded"] is False
    assert evidence["provider_secret_recorded"] is False
    assert evidence["product_or_database_access"] is False
    assert evidence["downstream_delivery"] is False


def test_attempt3_audit_records_terra_release_and_gemini_rejection():
    evidence = _json(rehearsal.ATTEMPT3_COMPARISON_EVIDENCE_PATH)
    assert evidence["runtime_attempt_id"] == "comparative-runtime-attempt-003"
    assert evidence["result"] == (
        "ariadne_terra_gemini_comparative_rehearsal_"
        "attempt3_revision_required"
    )
    assert evidence["retry_performed"] is False
    assert evidence["fallback_performed"] is False
    assert evidence["cross_model_input"] is False
    assert evidence["voting"] is False

    terra = evidence["lanes"]["terra"]
    assert terra["status"] == "passed"
    assert terra["reason_codes"] == []
    assert terra["ledger"]["state"] == "consumed"
    assert terra["generated_draft_count"] == 5
    assert terra["provider_schema_status"] == "passed"
    assert terra["full_schema_status"] == "passed"
    assert terra["proofreader"]["status"] == "passed"
    assert terra["proofreader"]["disposition"] == "release-verified-outputs"
    assert terra["external_audit_track"] == {
        "owner": "trusted-broker-and-orchestrator",
        "sandbox_append_authority": False,
        "hash_chain_status": "passed",
        "raw_reasoning_recorded": False,
        "typed_output_manifest_recorded": True,
        "proofreader_disposition": "release-verified-outputs",
    }
    assert not rehearsal._validate_broker_audit_chain(  # noqa: SLF001
        terra["broker_events"]
    )
    assert rehearsal._validate_broker_audit_chain(  # noqa: SLF001
        rehearsal._reconstruct_broker_ready_fields(  # noqa: SLF001
            terra["broker_events"], "terra"
        )
    )
    assert [item["event"] for item in terra["broker_events"]] == [
        "broker-ready",
        "provider-call-started",
        "provider-call-completed",
        "typed-output-observed",
    ]
    assert terra["broker_events"][1]["provider_call_count"] == 1
    assert terra["broker_events"][2]["provider_status"] == 200
    manifests = terra["broker_events"][3]["typed_output_manifest"]
    assert {item["id"] for item in manifests} == rehearsal.PRIMARY_DRAFT_IDS
    assert all("payload" not in item for item in manifests)
    assert all("draft_sha256" in item for item in manifests)
    assert all(terra["cleanup"].values())

    gemini = evidence["lanes"]["gemini"]
    assert gemini["status"] == "revision_required"
    assert gemini["reason_codes"] == ["provider-non-success"]
    assert gemini["ledger"]["state"] == "consumed"
    assert gemini["generated_draft_count"] == 0
    assert gemini["provider_schema_status"] == "not-presented"
    assert gemini["full_schema_status"] == "not-presented"
    assert gemini["proofreader"] is None
    assert gemini["external_audit_track"]["hash_chain_status"] == "passed"
    assert (
        gemini["external_audit_track"]["typed_output_manifest_recorded"]
        is False
    )
    assert not rehearsal._validate_broker_audit_chain(  # noqa: SLF001
        gemini["broker_events"]
    )
    assert rehearsal._validate_broker_audit_chain(  # noqa: SLF001
        rehearsal._reconstruct_broker_ready_fields(  # noqa: SLF001
            gemini["broker_events"], "gemini"
        )
    )
    assert [item["event"] for item in gemini["broker_events"]] == [
        "broker-ready",
        "provider-call-started",
        "provider-call-completed",
    ]
    assert gemini["broker_events"][1]["provider_call_count"] == 1
    assert gemini["broker_events"][2]["provider_status"] == 400
    assert (
        gemini["broker_events"][2]["provider_error_status"]
        == "INVALID_ARGUMENT"
    )
    assert gemini["broker_events"][2]["provider_error_code"] == 400
    assert all(gemini["cleanup"].values())

    for key in (
        "raw_reasoning_recorded",
        "raw_prompt_recorded",
        "raw_provider_response_recorded",
        "draft_payload_recorded",
        "provider_secret_recorded",
        "product_or_database_access",
        "downstream_delivery",
    ):
        assert evidence[key] is False


def test_attempt3_audit_analysis_preserves_incident_and_reconstructs_chain():
    analysis = _json(rehearsal.ATTEMPT3_AUDIT_ANALYSIS_PATH)
    assert analysis["result"] == (
        "ariadne_terra_gemini_attempt3_external_audit_revision_required"
    )
    assert analysis["original_durable_exports_verify"] is False
    assert analysis["reconstructed_exports_verify"] is True
    assert analysis["incident"] == {
        "reason_code": "sanitised-audit-export-omitted-hashed-fields",
        "scope": "broker-ready-event-only",
        "historical_evidence_rewritten": False,
        "future_export_allowlist_corrected": True,
    }
    for lane in ("terra", "gemini"):
        check = analysis["lane_checks"][lane]
        assert check["runtime_host_chain_status_reported"] == "passed"
        assert check["original_durable_sanitised_chain_verifies"] is False
        assert check["omitted_hashed_broker_ready_fields"] == [
            "allowed_path",
            "maximum_provider_calls",
            "upstream_host",
            "upstream_path",
        ]
        assert check["reconstructed_chain_verifies"] is True
        assert check["provider_call_start_count"] == 1
        assert check["provider_call_completion_count"] == 1
        assert check["cleanup_complete"] is True
    assert analysis["gemini_diagnostic_limit"] == {
        "observed": "http-400-invalid-argument-before-typed-output",
        "exact_rejected_field_known": False,
        "reason": "raw-provider-error-message-is-intentionally-excluded",
        "retry_performed": False,
    }


def test_attempt4_records_one_repaired_gemini_call_and_no_residency_claim():
    evidence = _json(rehearsal.ATTEMPT4_EVIDENCE_PATH)
    assert evidence["runtime_attempt_id"] == "comparative-runtime-attempt-004"
    assert evidence["result"] == (
        "ariadne_gemini_repaired_request_attempt4_revision_required"
    )
    assert evidence["run_order"] == ["gemini"]
    assert evidence["provider_route"] == {
        "api": "gemini-developer-api",
        "host": "generativelanguage.googleapis.com",
        "australian_processing_evidence": False,
        "data_class": "authored-synthetic-non-pii",
    }
    assert evidence["retry_performed"] is False
    assert evidence["fallback_performed"] is False
    assert evidence["terra_or_other_provider_call_performed"] is False
    lane = evidence["lane"]
    assert lane["status"] == "revision_required"
    assert lane["reason_codes"] == ["provider-non-success"]
    assert lane["ledger"]["state"] == "consumed"
    assert lane["generated_draft_count"] == 0
    assert lane["provider_schema_status"] == "not-presented"
    assert lane["full_schema_status"] == "not-presented"
    assert lane["proofreader"] is None
    assert lane["external_audit_track"]["hash_chain_status"] == "passed"
    assert lane["external_audit_track"]["typed_output_manifest_recorded"] is False
    assert rehearsal._validate_broker_audit_chain(  # noqa: SLF001
        lane["broker_events"]
    )
    assert [item["event"] for item in lane["broker_events"]] == [
        "broker-ready",
        "provider-call-started",
        "provider-call-completed",
    ]
    assert lane["broker_events"][1]["provider_call_count"] == 1
    assert lane["broker_events"][2]["provider_status"] == 400
    assert (
        lane["broker_events"][2]["provider_error_status"]
        == "INVALID_ARGUMENT"
    )
    assert lane["broker_events"][2]["provider_error_code"] == 400
    assert all(lane["cleanup"].values())
    for key in (
        "raw_reasoning_recorded",
        "raw_prompt_recorded",
        "raw_provider_response_recorded",
        "draft_payload_recorded",
        "provider_secret_recorded",
        "product_or_database_access",
        "downstream_delivery",
    ):
        assert evidence[key] is False


def test_attempt4_external_audit_is_complete_and_independently_verifiable():
    analysis = _json(rehearsal.ATTEMPT4_AUDIT_ANALYSIS_PATH)
    assert analysis["attempt_result"] == (
        "ariadne_gemini_repaired_request_attempt4_revision_required"
    )
    assert analysis["audit_result"] == (
        "ariadne_gemini_attempt4_external_audit_pass"
    )
    assert analysis["durable_hash_chain_verifies"] is True
    assert analysis["provider_call_start_count"] == 1
    assert analysis["provider_call_completion_count"] == 1
    assert analysis["provider_status"] == 400
    assert analysis["typed_output_manifest_count"] == 0
    assert analysis["typed_output_manifest_recorded"] is False
    assert analysis["provider_schema_status"] == "not-presented"
    assert analysis["full_schema_status"] == "not-presented"
    assert analysis["proofreader_disposition"] is None
    assert analysis["cleanup_complete"] is True
    assert all(value is False for value in analysis["exclusions"].values())
    assert analysis["australian_processing_evidence"] is False
    assert analysis["historical_attempt_evidence_rewritten"] is False
    assert analysis["retry_performed"] is False
