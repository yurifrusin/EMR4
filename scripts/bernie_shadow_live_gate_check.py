"""Validate the narrow T3 external-provider replay gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "bernie.shadow_live_replay_gate.v1"
DEFAULT_GATE_PATH = (
    Path(__file__).resolve().parents[1] / "docs" / "bernie-t3-live-replay-gate.json"
)
REQUIRED_SCOPE = {
    "external_provider_prompt_calls",
    "provider_executed_tools",
    "raw_response_persistence",
    "model_promotion",
    "runtime_authority",
}
REQUIRED_REVIEWS = {
    "exact_provider_model_ledger",
    "synthetic_corpus_only",
    "no_write_and_read_only_tool_proof",
    "bounded_case_and_repeat_limits",
    "redacted_or_hashed_artifact_plan",
    "cost_ceiling_or_explicit_run_approval",
    "adapter_contract_tests",
}
REQUIRED_ALLOWED = {
    "contract_and_scoring_tests",
    "source_safe_corpus_tests",
    "injected_fake_adapter_tests",
    "provider_adapter_implementation_without_calls",
    "static_adapter_review",
}
REQUIRED_FORBIDDEN = {
    "external_prompt_execution",
    "provider_tool_execution",
    "raw_model_response_commit",
    "patient_or_practice_data_input",
    "appointment_or_audit_mutation",
    "route_or_runtime_wiring",
    "promotion_or_release_claim",
}


def load_gate(path: Path = DEFAULT_GATE_PATH) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to load T3 live-replay gate: {exc}") from exc


def assert_gate_blocked(gate: dict[str, Any]) -> None:
    assert gate.get("schema_version") == SCHEMA_VERSION
    assert gate.get("decision") == "blocked"
    scope = gate.get("scope")
    assert isinstance(scope, dict)
    assert set(scope) == REQUIRED_SCOPE
    assert all(value is False for value in scope.values())
    assert set(gate.get("required_before_unblocking", [])) == REQUIRED_REVIEWS
    assert set(gate.get("allowed_while_blocked", [])) == REQUIRED_ALLOWED
    assert set(gate.get("forbidden_while_blocked", [])) == REQUIRED_FORBIDDEN


def build_gate_status(path: Path = DEFAULT_GATE_PATH) -> dict[str, Any]:
    gate = load_gate(path)
    assert_gate_blocked(gate)
    return {
        "schema_version": "bernie.shadow_live_replay_gate_status.v1",
        "decision": "blocked",
        "blocked_scope_count": len(gate["scope"]),
        "required_review_count": len(gate["required_before_unblocking"]),
        "allowed_development_use_count": len(gate["allowed_while_blocked"]),
        "forbidden_use_count": len(gate["forbidden_while_blocked"]),
        "external_calls_ready": False,
        "runtime_authority_ready": False,
        "sprint_engine_state": "continuing_adapter_contract_work",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE_PATH)
    args = parser.parse_args()
    print(json.dumps(build_gate_status(args.gate), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
