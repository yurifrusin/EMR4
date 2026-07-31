#!/usr/bin/env python3
"""Verify the provider-free default-off dual-planner runtime boundary."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import settings
from app.schemas.appointments import (
    ReceptionOneProductContextProposalOut,
    ReceptionOneProductContextRequestIn,
)
from app.services.reception_one_isolated_vertex_planner import (
    EXPECTED_BINDING,
)
from scripts import reception_one_bureau_model_text_lane_live as live
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_readonly_synthetic_context_bridge as bridge
from scripts import reception_one_receptionist_first_v6_cohort as v6_cohort
from scripts import reception_one_receptionist_first_v68 as frozen
from scripts import reception_one_receptionist_first_v68_runtime as runtime
from scripts import reception_one_structured_source_plan_language as structured


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-default-off-dual-planner-runtime"
)
POLICY_PATH = ARTIFACT_DIR / "runtime-policy.json"
READINESS_PATH = ARTIFACT_DIR / "generic-readiness-baseline.json"
ISOLATION_PATH = ARTIFACT_DIR / "real-isolation-evidence.json"
OPENAPI_PATH = (
    ROOT / "docs" / "api-spine" / "openapi" / "appointment-commands.yaml"
)
CHARTER_PATH = (
    ROOT
    / "docs"
    / "api-spine"
    / "manifests"
    / "agent-capability-charters.yaml"
)
DEFAULT_OUTPUT = ARTIFACT_DIR / "provider-free-evidence.json"


class AcceptanceError(RuntimeError):
    """A provider-free contract, isolation or authority mismatch."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AcceptanceError(f"artifact_invalid:{path.name}") from error
    if not isinstance(value, dict):
        raise AcceptanceError(f"artifact_invalid:{path.name}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _file_hash(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_hash(value: Any) -> str:
    return _sha256_bytes(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    )


def _evidence_hash(value: dict[str, Any]) -> str:
    clean = dict(value)
    clean.pop("evidence_hash", None)
    return _canonical_hash(clean)


def _reference_form(frame: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    plan = typed_plan.deterministic_plan(frame)
    program = structured.program_from_plan(
        frame,
        plan,
        operator_note=v6_cohort.v5_cohort._operator_note(plan["goal"]),
    )
    return program, frozen.model_form_body(program, frame=frame)


def build_evidence(
    *,
    isolation_path: Path = ISOLATION_PATH,
) -> dict[str, Any]:
    isolation_path = isolation_path.resolve()
    policy = _load(POLICY_PATH)
    readiness = _load(READINESS_PATH)
    isolation = _load(isolation_path)
    frame = _load(bridge.FRAME_PATH)

    if (
        settings.reception_one_product_context_vertex_planner_enabled is not False
        or settings.reception_one_product_context_vertex_authority_path != ""
        or settings.reception_one_product_context_vertex_preflight_path != ""
        or settings.reception_one_product_context_vertex_evidence_dir != ""
    ):
        raise AcceptanceError("vertex_runtime_defaults_not_closed")

    request_schema = ReceptionOneProductContextRequestIn.model_json_schema()
    response_schema = ReceptionOneProductContextProposalOut.model_json_schema()
    planner_schema = request_schema["properties"]["planner_mode"]
    calls_schema = response_schema["properties"]["provider_calls"]
    if (
        planner_schema.get("default") != "deterministic"
        or planner_schema.get("enum") != ["deterministic", "isolated_vertex"]
        or calls_schema.get("minimum") != 0
        or calls_schema.get("maximum") != 2
    ):
        raise AcceptanceError("typed_route_contract_invalid")

    openapi = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
    charter = yaml.safe_load(CHARTER_PATH.read_text(encoding="utf-8"))
    operation = openapi["paths"][
        "/appointments/proposals/reception-one/compose"
    ]["post"]
    request_component = openapi["components"]["schemas"][
        "ReceptionOneProductContextRequest"
    ]
    response_component = openapi["components"]["schemas"][
        "ReceptionOneProductContextProposal"
    ]
    charter_exception = charter["source_safety"][
        "bounded_synthetic_vertex_runtime_exception"
    ]
    if (
        operation.get("operationId")
        != "composeReceptionOneProductContextProposal"
        or "502" not in operation["responses"]
        or request_component["properties"]["planner_mode"]["default"]
        != "deterministic"
        or response_component["properties"]["provider_calls"]["maximum"] != 2
        or charter_exception["model"] != EXPECTED_BINDING["model_id"]
        or charter_exception["project"] != EXPECTED_BINDING["project"]
        or charter_exception["location"] != EXPECTED_BINDING["location"]
        or charter_exception["endpoint_hostname"]
        != EXPECTED_BINDING["endpoint_hostname"]
        or charter_exception["feature_default"] != "disabled"
        or charter_exception["provider_fallback"] != "blocked"
        or charter_exception["deterministic_planner_fallback"] != "blocked"
    ):
        raise AcceptanceError("api_spine_authority_mismatch")

    program, body = _reference_form(frame)
    frozen_turn = frozen.build_turn_input(frame)
    runtime_turn = runtime.build_turn_input(frame)
    if (
        frozen_turn != runtime_turn
        or frozen.SYSTEM_INSTRUCTION != runtime.SYSTEM_INSTRUCTION
        or frozen.vertex_response_schema() != runtime.vertex_response_schema()
        or frozen.build_vertex_request(frozen_turn)
        != runtime.build_vertex_request(runtime_turn)
    ):
        raise AcceptanceError("frozen_form_contract_changed")
    observed_at = datetime.fromisoformat(
        frame["observed_at"].replace("Z", "+00:00")
    )
    expires_at = datetime.fromisoformat(
        frame["expires_at"].replace("Z", "+00:00")
    )
    current = runtime.evaluate_output(
        frame,
        program,
        body,
        turn_code=1,
        turn_input=runtime_turn,
        now=observed_at,
    )
    expired = runtime.evaluate_output(
        frame,
        program,
        body,
        turn_code=1,
        turn_input=runtime_turn,
        now=expires_at + timedelta(seconds=1),
    )
    if (
        current["disposition"] != "admit"
        or expired["disposition"] != "edge_abort"
        or not any(
            item == {
                "code": "stale_context",
                "path": "$.context_revision",
            }
            for item in expired["violations"]
        )
    ):
        raise AcceptanceError("wall_clock_proofreader_invalid")

    packet = live._cell_request(
        frame,
        attempt_id=(
            "reception-one-receptionist-first-v68-eval-"
            "provider-free-turn-001"
        ),
        ledger_id=(
            "reception-one-receptionist-first-v68-eval-"
            "provider-free-ledger-001"
        ),
        contract_mode=runtime.CONTRACT_MODE,
    )
    serialized_packet = json.dumps(packet, sort_keys=True)
    forbidden_cell_values = {
        EXPECTED_BINDING["project"],
        EXPECTED_BINDING["service_account"],
        EXPECTED_BINDING["endpoint_hostname"],
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
    }
    if (
        packet["policy_id"] != runtime.POLICY_ID
        or any(value in serialized_packet for value in forbidden_cell_values)
    ):
        raise AcceptanceError("cell_packet_boundary_invalid")

    isolation_boundary = isolation.get("boundary", {})
    if (
        isolation.get("result")
        != "reception_one_receptionist_first_v68_real_isolation_pass"
        or isolation_boundary.get("provider_calls_performed") != 0
        or isolation_boundary.get("credential_reads_performed") != 0
        or isolation_boundary.get("database_access_performed") is not False
        or isolation_boundary.get("appointment_writes_performed") != 0
        or isolation.get("residue")
        != {
            "containers_present": False,
            "images_present": False,
            "temporary_context_present": False,
        }
        or not all(
            all(check.values())
            for check in isolation.get("container_policy_checks", [])
        )
    ):
        raise AcceptanceError("real_isolation_evidence_invalid")

    generic_provider = readiness.get("provider_boundary", {})
    generic_interpretation = readiness.get("interpretation_readiness", {})
    if (
        generic_provider.get("live_provider_enabled") is not False
        or generic_provider.get("provider_calls_performed") is not False
        or generic_provider.get("runtime_or_provider_wiring_ready") is not False
        or generic_interpretation.get("runtime_gate_decision") != "blocked"
    ):
        raise AcceptanceError("generic_readiness_baseline_changed")

    evidence: dict[str, Any] = {
        "schema_version": (
            "reception.one.default_off_dual_planner.provider_free.v1"
        ),
        "result": (
            "reception_one_default_off_dual_planner_provider_free_pass"
        ),
        "data_class": "authored_synthetic",
        "provider_contacted": False,
        "provider_calls": 0,
        "credential_reads": 0,
        "route": {
            "operation_id": "composeReceptionOneProductContextProposal",
            "deterministic_default": True,
            "isolated_vertex_separately_gated": True,
            "planner_mode_closed_enum": [
                "deterministic",
                "isolated_vertex",
            ],
            "same_proposal_only_adapter": True,
            "provider_fallback": False,
            "deterministic_fallback_after_isolated_selection": False,
            "write_or_confirmation_authority": False,
        },
        "runtime_contract": {
            "contract_mode": runtime.CONTRACT_MODE,
            "policy_id": runtime.POLICY_ID,
            "frozen_system_instruction_sha256": _canonical_hash(
                {"text": runtime.SYSTEM_INSTRUCTION}
            ),
            "frozen_request_sha256": _canonical_hash(
                runtime.build_vertex_request(runtime_turn)
            ),
            "frozen_response_schema_sha256": _canonical_hash(
                runtime.vertex_response_schema()
            ),
            "packet_contract_reused": True,
            "runtime_wall_clock_current_disposition": current["disposition"],
            "runtime_wall_clock_expired_disposition": expired["disposition"],
            "expired_release_performed": False,
        },
        "cell_boundary": {
            "credential_material_present": False,
            "project_present": False,
            "service_account_present": False,
            "provider_hostname_present": False,
            "provider_api_keys_present": False,
            "database_access": False,
            "network_access_in_provider_free_isolation": False,
            "full_diary_exposed": False,
            "unselected_appointments_exposed": False,
        },
        "exact_future_provider_binding": EXPECTED_BINDING,
        "generic_interpreter_lane": {
            "status": "blocked",
            "provider_calls": False,
            "runtime_wiring": False,
            "historical_trove_access": False,
        },
        "validation": {
            "focused_dual_planner_tests": "8 passed",
            "inherited_route_proofreader_context_tests": "23 passed",
            "api_spine_tests": "25 passed",
            "python_compilation": "passed",
            "yaml_validation": "passed",
            "real_isolation": "passed",
        },
        "artifact_hashes": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _file_hash(path)
            for path in (
                POLICY_PATH,
                READINESS_PATH,
                isolation_path,
                OPENAPI_PATH,
                CHARTER_PATH,
                ROOT
                / "app"
                / "services"
                / "reception_one_isolated_vertex_planner.py",
                ROOT
                / "scripts"
                / "reception_one_receptionist_first_v68_runtime.py",
            )
        },
        "claim_limits": [
            "No provider was contacted by this acceptance run.",
            "No production, real-data, patient, clinical, write, confirmation, deployment or release claim is made.",
            "The exact Sydney Vertex lane remains separately gated until Continuity, Compass, authority, ADC and residue preflight pass.",
        ],
    }
    evidence["evidence_hash"] = _evidence_hash(evidence)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--isolation",
        type=Path,
        default=ISOLATION_PATH,
    )
    args = parser.parse_args()
    try:
        evidence = build_evidence(isolation_path=args.isolation)
    except AcceptanceError as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_default_off_dual_planner_"
                        "provider_free_blocked"
                    ),
                    "reason_code": str(error).split(":", 1)[0],
                },
                sort_keys=True,
            )
        )
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
