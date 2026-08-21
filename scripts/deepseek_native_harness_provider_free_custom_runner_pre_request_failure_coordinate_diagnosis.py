"""Generate provider-free evidence for the custom-runner diagnostic design."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import tarfile
from typing import Any

from orchestration_harness import native_post_hmr_pre_request_diagnostic as diagnostic
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as accepted_runner,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-custom-runner-pre-request-failure-coordinate-diagnosis"
)
CONTRACT_PATH = EVIDENCE_ROOT / "contract.json"
EVIDENCE_PATH = EVIDENCE_ROOT / "diagnosis-evidence.json"
REPORT_PATH = EVIDENCE_ROOT / "diagnosis-report.md"
EFFICACY_PATH = EVIDENCE_ROOT / "efficacy-reading.json"
ATTEMPT_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "raisa-authored-synthetic-check-in-native-harness-bounded-worker-monitored-development-rehearsal"
    / "attempt-005"
)
TARGET_PATH = (
    "C:/Users/sarashera/EMR4-worktrees/deepseek-native-synthetic-window-worker-005/"
    "workspace/synthetic_window_coalescer.py"
)
ACCEPTED_RUNNER_SHA256 = "1233d4fc14726800dcf063c1cab5e814f3df0091040126784c4a7d42c3ec0746"

PACKAGE_SOURCES = {
    "dsh_agent": {
        "integrity": "AqBQavJYgbCUUYBHP7OGCaw8WN5082NXYQOoOfNRO72bub3E+/nWkl8b4B7BAJdFfyLo9ce+Kgb1BCHSJU/JLg==",
        "member": "package/lib/index.js",
        "sha256": "e7e40c5ca66d9827a5084c5c0c68983f9685842bb9b6d604803d4cb4642bb263",
        "fragments": (
            b"async create(options) {",
            b"Reflect.apply(target.createAgent",
        ),
    },
    "dsh_agent_loop": {
        "integrity": "98jV+6XnkZ93g4C1BJ/hCcC8k4GVhH+oNrkhLFvc6aOQz6o+9kdV8IrgEVr0qRcAfHKlCMfiV4BIDz4eBBoziw==",
        "member": "package/lib/index.js",
        "sha256": "bf8ca1e9b05e9b78320a5e2f0b4e25395eba91dd72db6d3cb5626e3dfb529204",
        "fragments": (
            b"async createAgent(ownerCtx, options) {",
            b"await raceAbort(setup?.(prepared.agent.ctx)",
            b"return prepared.publish(source);",
            b"followup(input) {",
            b"async whenIdle() {",
        ),
    },
    "dsh_agent_presets": {
        "integrity": "T/VcMV7lrXCFmRKrtoMTAz5DAdUmku6hz95wbikRvRc0WizIwQ3R04ke9KIeDiQcxK8xkE8cx+IYqEWa9C5gPg==",
        "member": "package/lib/index.js",
        "sha256": "a0b417514e3d285ad5fef74867e8049af333ebdec6e4d7639e388aa0903e0039",
        "fragments": (
            b"async resolveMountable(id) {",
            b"async mount(agentCtx, id) {",
            b"async ensureStanding(preset) {",
            b"bindings = /* @__PURE__ */ new WeakMap();",
        ),
    },
    "dsh_session": {
        "integrity": "02WVTkqIH+TyDL7dhMN3Hm+qcTEdhD0fVDC0aIAyND2fBdXj3CagEXXvpmt3mzwWfKwOTGL1RdxtC6pMA4Bl1A==",
        "member": "package/lib/index.js",
        "sha256": "9270186b579bc8a4c6c53c256e4471d3f134e94308462c6a413a722e9c7556fb",
        "fragments": (
            b"async flush(session) {",
            b"Promise.allSettled(callbacks.map",
        ),
    },
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def npm_cache_content_path(integrity: str) -> Path:
    digest = base64.b64decode(integrity, validate=True).hex()
    return (
        REPO_ROOT.parent
        / "AppData"
        / "Local"
        / "npm-cache"
        / "_cacache"
        / "content-v2"
        / "sha512"
        / digest[:2]
        / digest[2:4]
        / digest[4:]
    )


def read_cached_tar_member(integrity: str, member: str) -> bytes:
    tarball = npm_cache_content_path(integrity)
    if not tarball.is_file():
        raise diagnostic.PostHmrDiagnosticError("cached_tarball_missing")
    with tarfile.open(tarball, mode="r:gz") as archive:
        extracted = archive.extractfile(member)
        if extracted is None:
            raise diagnostic.PostHmrDiagnosticError("cached_tar_member_missing")
        return extracted.read()


def source_bindings() -> dict[str, Any]:
    bindings: dict[str, Any] = {}
    for source_id, source in PACKAGE_SOURCES.items():
        payload = read_cached_tar_member(source["integrity"], source["member"])
        bindings[source_id] = {
            "package_version": "0.1.0-rc.7",
            "tar_member": source["member"],
            **diagnostic.validate_source_binding(
                payload,
                expected_sha256=source["sha256"],
                required_fragments=source["fragments"],
            ),
        }
    return bindings


def fixture_matrix(candidate_source: str) -> dict[str, Any]:
    operation_id = (
        "deepseek-native-harness-provider-free-custom-runner-pre-request-failure-"
        "coordinate-diagnosis"
    )
    attempt_id = "future-post-hmr-diagnostic-fixture-001"
    kinds = {
        "aggregate_error": {"name": "AggregateError"},
        "error": {"name": "Error"},
        "invalid_preset_id_error": {"name": "InvalidPresetIdError"},
        "preset_mount_error": {"name": "PresetMountError"},
        "type_error": {"name": "TypeError"},
        "unknown": {"name": "DynamicSecretPathCDriveUsers"},
        "unknown_preset_error": {"name": "UnknownPresetError"},
    }
    scenario_count = 0
    for stage in diagnostic.PRE_REQUEST_STAGES:
        for expected_kind, fixture in kinds.items():
            value = diagnostic.build_diagnostic_from_fixture(
                fixture,
                operation_id=operation_id,
                attempt_id=attempt_id,
                candidate_source=candidate_source,
                stage=stage,
            )
            if value["error_kind"] != expected_kind:
                raise diagnostic.PostHmrDiagnosticError("fixture_kind_projection_mismatch")
            diagnostic.diagnostic_bytes(value)
            scenario_count += 1
    for stage, cause in (
        ("required_service_lookup", "required_service_missing"),
        ("preset_root_roster_admission", "preset_root_roster_mismatch"),
    ):
        diagnostic.build_diagnostic_from_fixture(
            {"name": "Error"},
            operation_id=operation_id,
            attempt_id=attempt_id,
            candidate_source=candidate_source,
            stage=stage,
            cause_coordinate=cause,
        )
        scenario_count += 1
    return {
        "scenario_count": scenario_count,
        "stage_count": len(diagnostic.PRE_REQUEST_STAGES),
        "error_kind_count": len(diagnostic.ERROR_KINDS),
        "special_cause_relationship_count": 2,
        "dynamic_secret_or_path_text_released": False,
    }


def build_evidence() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_bytes())
    candidate_source = contract["planning_source"]
    runner_payload = accepted_runner.runner_source(TARGET_PATH)
    runner_binding = diagnostic.validate_accepted_runner_source(
        runner_payload, expected_sha256=ACCEPTED_RUNNER_SHA256
    )
    helper = diagnostic.build_helper_source(
        operation_id=contract["operation_id"],
        attempt_id="future-post-hmr-diagnostic-fixture-001",
        candidate_source=candidate_source,
    )
    helper_binding = diagnostic.validate_helper_source(helper)
    envelope = diagnostic.future_runner_instrumentation_envelope_source()
    envelope_binding = diagnostic.validate_future_runner_instrumentation_envelope(
        envelope
    )
    bindings = source_bindings()
    attempt_bindings = {
        "occupied_terminal_sha256": file_sha256(ATTEMPT_ROOT / "occupied-terminal.json"),
        "diagnosis_sha256": file_sha256(ATTEMPT_ROOT / "diagnosis.md"),
        "efficacy_reading_sha256": file_sha256(ATTEMPT_ROOT / "efficacy-reading.json"),
        "immutable": True,
        "reclassification_permitted": False,
    }
    return {
        "schema_version": "ariadne.native_harness_post_hmr_pre_request_diagnosis_evidence.v1",
        "operation_id": contract["operation_id"],
        "result": "pass",
        "attempt_005": attempt_bindings,
        "accepted_runner": runner_binding,
        "pinned_rc7_sources": bindings,
        "closed_vocabulary": {
            "stages": list(diagnostic.PRE_REQUEST_STAGES),
            "cause_coordinates": list(diagnostic.CAUSE_COORDINATES),
            "error_kinds": list(diagnostic.ERROR_KINDS),
            "single_constant_owner": True,
        },
        "diagnostic_helper": helper_binding,
        "future_runner_envelope": envelope_binding,
        "fixture_matrix": fixture_matrix(candidate_source),
        "claim_boundary": {
            "sidecar_stage_is_source_coordinate_only": True,
            "pre_request_conclusion_requires_broker_zero_reading": True,
            "internal_rc7_suboperation_claimed": False,
            "deepseek_performance_claimed": False,
            "harness_readiness_claimed": False,
        },
        "proof_boundary": {
            "python_process_count": 1,
            "node_process_count": 0,
            "native_harness_process_count": 0,
            "broker_process_count": 0,
            "worker_process_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "network_request_count": 0,
            "database_invocation_count": 0,
            "docker_invocation_count": 0,
            "raw_attempt_stream_read_count": 0,
        },
    }


def build_report(evidence: dict[str, Any]) -> str:
    stages = evidence["closed_vocabulary"]["stages"]
    source_rows = evidence["pinned_rc7_sources"]
    return f"""# Native Harness custom-runner pre-request source-coordinate diagnosis

Date: 2026-08-21

Timestamp: 2026-08-21T20:13:19.9793090+10:00 (Australia/Brisbane)

## Result

`pass`

The accepted attempt-005 runner and four relevant cached rc.7 source members
match their frozen SHA-256 bindings and required operation shapes. The runner's
generic catch spans seven source-visible pre-request or request-adjacent
coordinates:

{chr(10).join(f'- `{stage}`' for stage in stages)}

The future sidecar selects only from that list. It projects one closed cause
coordinate and one closed constructor/name kind, reads no raw message, stack,
code, cause or path, writes once with exclusive-create semantics and cannot
replace the primary rejection.

## Source boundary

- accepted runner: `{evidence['accepted_runner']['sha256']}`
- rc.7 dsh-agent: `{source_rows['dsh_agent']['sha256']}`
- rc.7 dsh-agent-loop: `{source_rows['dsh_agent_loop']['sha256']}`
- rc.7 dsh-agent-presets: `{source_rows['dsh_agent_presets']['sha256']}`
- rc.7 dsh-session: `{source_rows['dsh_session']['sha256']}`

`agents.create` is one honest runner coordinate even though rc.7 performs
session preparation, setup/preset mounting, publication and loop start inside
it. This tranche does not claim a narrower internal coordinate. Likewise,
`first_turn_idle_wait` becomes a pre-request conclusion only when joined to an
independent broker reading of zero requests.

## Conclusion

The exact stage vocabulary and sidecar contract are ready for a separately
authorised provider-free integration rehearsal. No occupied retry is justified
by this diagnosis alone, and no DeepSeek performance or general Harness
readiness was measured.
"""


def build_efficacy(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ariadne.native_harness_post_hmr_pre_request_diagnosis_efficacy.v1",
        "operation_id": evidence["operation_id"],
        "result": "pass",
        "measurements": {
            "closed_stage_count": len(evidence["closed_vocabulary"]["stages"]),
            "closed_cause_coordinate_count": len(
                evidence["closed_vocabulary"]["cause_coordinates"]
            ),
            "closed_error_kind_count": len(
                evidence["closed_vocabulary"]["error_kinds"]
            ),
            "fixture_scenario_count": evidence["fixture_matrix"]["scenario_count"],
            "pinned_source_member_count": len(evidence["pinned_rc7_sources"]),
            "prohibited_process_or_request_count": sum(
                value
                for key, value in evidence["proof_boundary"].items()
                if key != "python_process_count"
            ),
        },
        "efficacy": {
            "generic_runner_failure_replaced_in_design": True,
            "caller_descriptive_stage_admission": False,
            "stage_is_machine_selected_from_closed_vocabulary": True,
            "provider_position_overclaim_prevented": True,
            "raw_error_retention": False,
            "occupied_harness_readiness": "not_tested",
        },
        "next_recovery": "provider_free_future_runner_sidecar_integration_rehearsal_before_any_occupied_attempt",
    }


def write_outputs() -> dict[str, Any]:
    evidence = build_evidence()
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(build_report(evidence), encoding="utf-8", newline="\n")
    EFFICACY_PATH.write_text(
        json.dumps(build_efficacy(evidence), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    evidence = write_outputs() if args.write else build_evidence()
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
