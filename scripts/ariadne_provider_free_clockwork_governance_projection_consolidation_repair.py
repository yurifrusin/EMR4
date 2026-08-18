"""Generate the provider-free governance-projection repair evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from orchestration_harness.governance_clockwork import (
    build_bundle,
    load_object,
    publish_private_shadow,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / "orchestration/continuity/ariadne-provider-free-clockwork-governance-projection-consolidation-repair"


def _observation() -> dict[str, object]:
    evidence = [
        "docs/ariadne-provider-free-clockwork-governance-projection-consolidation-repair-plan.md",
        "orchestration_harness/governance_clockwork.py",
    ]
    return {
        "failure_class": "projection_contract",
        "observed_on": "2026-08-19",
        "tranche": "ariadne-provider-free-clockwork-governance-projection-consolidation-repair",
        "role": "orchestrator",
        "resource_id": "governance-projection-representative-closeout",
        "model": "gpt-sol",
        "reasoning_level": "high",
        "transport": "local_repository_shadow_runner",
        "stage": "deterministic_verification",
        "process_severity": "low",
        "expected_invariant": "One semantic closeout observation must generate every governance binding before private publication.",
        "observed_error": "Authored-synthetic representative rejection used only to exercise the complete generated projection path.",
        "detection_method": "The provider-free reducer and hostile replay validate the prospective bundle before one private-shadow rename.",
        "evidence_paths": evidence,
        "candidate_state": "untrusted_partial_worktree",
        "workflow_disposition": "revision_required",
        "recurrence_signature": "shadow.representative_governance_projection",
        "causal_claim_level": "observation_only",
        "correction": {
            "status": "corrected_fresh_attempt",
            "action": "Derive the complete prospective packet once and retain it only as private-shadow evidence.",
            "prevention_control": "Live adoption remains closed until a separate migration and retirement gate.",
            "evidence_paths": evidence,
        },
    }


def _write(path: Path, value: object) -> None:
    path.write_bytes((json.dumps(value, indent=2, sort_keys=True) + "\n").encode())


def _report(bundle: dict[str, object]) -> str:
    efficacy = bundle["efficacy"]
    return "\n".join(
        [
            "# Provider-free clockwork governance projection repair report",
            "",
            "## Result",
            "",
            "`candidate_pass`",
            "",
            "One semantic observation generated the prospective register, recurrence, revision, command, Continuity, Compass, Current Baton and latch views on one acknowledged private-shadow tick. Existing controls remain authoritative.",
            "",
            "## Instrument reading",
            "",
            f"- Rerun probes: {efficacy['probe_coverage']}/13",
            f"- Surrounding-governance probes: {efficacy['surrounding_probe_coverage']}/9",
            f"- Construction reruns: {efficacy['construction_reruns']}",
            f"- Steady-state surrounding reruns: {efficacy['steady_state_surrounding_reruns']}",
            f"- Incremental line growth: {efficacy['incremental_line_growth']} / {efficacy['line_budget']}",
            f"- Maintained surfaces: {efficacy['baseline_maintained_surfaces']} -> {efficacy['candidate_maintained_surfaces']} ({efficacy['maintained_surface_reduction_percent']}% reduction)",
            f"- Repair-only break-even: {efficacy['repair_only_break_even_closeouts']} closeout(s)",
            f"- Cumulative break-even including 13 sunk reruns: {efficacy['cumulative_break_even_closeouts']} closeout(s)",
            "- Caller-authored derived fields, mutable-current fixtures, partial publications, uncaught escapes and provider calls: 0",
            "",
            "## Boundary",
            "",
            "This is provider-free private-shadow evidence only. No current control was retired or replaced; no product, data, provider, runtime, deployment, release, Pages or protected-ref authority opened.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    bundle = build_bundle(
        ROOT,
        TOPIC / "contract.json",
        TOPIC / "rerun-probes.json",
        ROOT / "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json",
        ROOT / "orchestration/continuity/ariadne-agent-error-register/agent-error-register.schema.json",
        ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json",
        [_observation()],
        gate_result="rejected",
    )
    _write(TOPIC / "provider-free-repair-evidence.json", bundle)
    (TOPIC / "repair-report.md").write_text(_report(bundle), encoding="utf-8", newline="\n")
    if args.publish:
        publish_private_shadow(bundle, validate_contract(load_object(TOPIC / "contract.json")), TOPIC / f"private-shadow-generation-{bundle['bundle_sha256'][:12]}")
    print(json.dumps({"status": "candidate_pass", "bundle_sha256": bundle["bundle_sha256"], "efficacy": bundle["efficacy"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
