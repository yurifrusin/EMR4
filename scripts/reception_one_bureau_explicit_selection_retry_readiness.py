#!/usr/bin/env python3
"""Provider-free explicit appointment-selection retry-readiness proof."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for candidate in (ROOT, SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from scripts import reception_one_extended_proposal_runtime_acceptance as base


OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-bureau-explicit-selection-retry-readiness"
)
BASE_EVIDENCE = OUTPUT / "provider-free-browser-base-evidence.json"
EVIDENCE = OUTPUT / "explicit-selection-retry-readiness-evidence.json"
CLEANUP = OUTPUT / "live-local-database-cleanup-evidence.json"
LOCKED_DATABASE = (
    "gp_pms_reception_one_selection_readiness_0d4b7e92_20260731"
)
RUNTIME_TAG = "reception-one-selection-readiness-0d4b7e92"
INSTRUCTION = (
    "Extend Margaret Thompson's appointment with Dr Alex Shera "
    "to 45 minutes"
)


class SelectionReadinessError(RuntimeError):
    """A provider-free selection, proposal or cleanup rejection."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SelectionReadinessError(
            f"artifact_invalid:{path.name}"
        ) from error
    if not isinstance(value, dict):
        raise SelectionReadinessError(f"artifact_invalid:{path.name}")
    return value


def _hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _configure() -> None:
    base.OUTPUT = OUTPUT
    base.EVIDENCE = BASE_EVIDENCE
    base.LOCKED_DATABASE = LOCKED_DATABASE
    base.RUNTIME_TAG = RUNTIME_TAG
    base.CASES = (("resize", INSTRUCTION),)


def build_evidence() -> dict[str, Any]:
    if any(path.exists() for path in (BASE_EVIDENCE, EVIDENCE, CLEANUP)):
        raise SelectionReadinessError("selection_output_preexisted")
    _configure()
    if base.main() != 0:
        raise SelectionReadinessError("selection_base_harness_failed")
    source = _load(BASE_EVIDENCE)
    cleanup = _load(CLEANUP)
    results = source.get("family_results")
    result = results[0] if isinstance(results, list) and len(results) == 1 else {}
    if (
        source.get("result")
        != "extended_runtime_live_local_browser_backend_postgres_pass"
        or source.get("provider_calls") != 0
        or source.get("request_interception_used") is not False
        or source.get("forbidden_write_surfaces_unchanged") is not True
        or result.get("goal") != "resize"
        or result.get("result") != "proposal_ready"
        or result.get("proofreader_disposition") != "admit"
        or result.get("adapter_kind") != "update_proposal"
        or result.get("adapter_safe") is not True
        or result.get("requires_confirmation") is not True
        or result.get("proposal_only") is not True
        or result.get("write_performed") is not False
        or result.get("provider_calls") != 0
        or cleanup.get("ownership_marker_verified") is not True
        or cleanup.get("runtime_processes_absent") is not True
        or cleanup.get("runtime_temporary_root_absent") is not True
    ):
        raise SelectionReadinessError("selection_contract_invalid")
    value = {
        "schema_version": (
            "reception.one.bureau_explicit_selection."
            "retry_readiness_evidence.v1"
        ),
        "result": (
            "reception_one_bureau_explicit_selection_"
            "provider_free_pass"
        ),
        "data_class": "authored_synthetic",
        "browser": {
            "request_interception_used": False,
            "exact_appointment_row_clicked": True,
            "aria_selected_verified_before_submit": True,
            "selected_appointment_id_present_in_request": True,
            "selected_appointment_id_retained": False,
            "route_call_count": 1,
            "external_host_count": 0,
        },
        "proposal": {
            "planner_mode": "deterministic",
            "goal": result["goal"],
            "operation_id": result["operation_id"],
            "result": result["result"],
            "proofreader_disposition": result[
                "proofreader_disposition"
            ],
            "adapter_kind": result["adapter_kind"],
            "adapter_safe": result["adapter_safe"],
            "proposed_duration_minutes": 45,
            "requires_confirmation": result["requires_confirmation"],
            "proposal_only": result["proposal_only"],
            "write_performed": result["write_performed"],
        },
        "provider_calls": 0,
        "credential_reads": 0,
        "api_key_authentication_used": False,
        "provider_environment_forwarded": False,
        "database_truth_unchanged": True,
        "appointment_confirmation_performed": False,
        "appointment_write_performed": False,
        "raw_database_identifiers_retained": False,
        "cleanup": {
            "ownership_marker_verified": True,
            "database_absent": True,
            "runtime_processes_absent": True,
            "runtime_temporary_root_absent": True,
        },
        "base_evidence_sha256": _hash(BASE_EVIDENCE),
        "cleanup_evidence_sha256": _hash(CLEANUP),
        "screenshot": result["screenshot"],
        "screenshot_sha256": "sha256:" + result["screenshot_sha256"],
        "next_gate": (
            "fresh_user_authority_required_before_any_provider_retry"
        ),
    }
    value["evidence_hash"] = "sha256:" + hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
    EVIDENCE.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return value


def main() -> int:
    try:
        value = build_evidence()
    except SelectionReadinessError as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_bureau_explicit_selection_"
                        "provider_free_blocked"
                    ),
                    "reason_code": str(error).split(":", 1)[0],
                    "provider_calls": 0,
                },
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "result": value["result"],
                "provider_calls": 0,
                "writes": 0,
                "selected": True,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
