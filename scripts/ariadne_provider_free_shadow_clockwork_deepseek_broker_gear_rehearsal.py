"""Generate the provider-free private-shadow clockwork rehearsal evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orchestration_harness.shadow_clockwork import (
    authoritative_generation_digest,
    authoritative_manifest_digest,
    build_generation,
    digest,
    measure_clean_run_overhead,
    publish_private_shadow,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "orchestration/continuity/"
    "ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-rehearsal"
)
CONTRACT = BASE / "contract.json"
GAUGES = BASE / "frozen-failure-gauges.json"
SHADOW = BASE / "private-shadow-generation"
EVIDENCE = BASE / "provider-free-rehearsal-evidence.json"
REPORT = BASE / "rehearsal-report.md"
GROWTH_FILES = (
    "orchestration_harness/shadow_clockwork.py",
    "scripts/ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_rehearsal.py",
    "orchestration/continuity/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-rehearsal/contract.json",
    "orchestration/continuity/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-rehearsal/contract.schema.json",
    "orchestration/continuity/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-rehearsal/frozen-failure-gauges.json",
    "tests/test_ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_rehearsal.py",
    "tests/test_ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_rehearsal_plan.py",
)


def _line_growth() -> dict[str, int]:
    readings = {
        relative: len((ROOT / relative).read_text(encoding="utf-8").splitlines())
        for relative in GROWTH_FILES
    }
    readings["total"] = sum(readings.values())
    return readings


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def render_report(evidence: dict[str, Any]) -> str:
    efficacy = evidence["efficacy"]
    accepted = evidence["efficacy"]["accepted"]
    outcome = (
        "One provider-free four-event causal tick was derived, validated and atomically published to a private shadow generation."
        if accepted
        else "The provider-free four-event tick was derived and validated but was not published as an accepted private generation because its measured rerun count exceeded the frozen threshold."
    )
    return f"""# Provider-free shadow clockwork / broker gear rehearsal report

## Result

`{evidence['result']}`

{outcome} Ariadne transferred one sequence lease to the broker simulation; the broker returned one terminal result; Ariadne acknowledged its exact digest and recovered the lease. There were no provider calls and no live adoption.

## Efficacy reading

- Conventional failure-induced reruns: {efficacy['comparator_failure_induced_reruns']}
- Candidate failure-induced reruns: {efficacy['candidate_failure_induced_reruns']}
- Reduction: {efficacy['failure_induced_rerun_reduction_percent']}%
- Frozen gauges covered: {efficacy['failure_gauges_covered']}/{efficacy['failure_gauges_required']}
- Caller-supplied derived fields: {efficacy['caller_supplied_derived_fields']}
- New mutable-current fixtures: {efficacy['new_mutable_current_fixtures']}
- Partial publications: {efficacy['partial_publications']}
- Uncaught escapes: {efficacy['uncaught_escapes']}
- Coverage loss: {str(efficacy['coverage_loss']).lower()}
- Raw shared line growth: {efficacy['shared_line_growth']['total']}
- Median clean-run overhead: {efficacy['clean_run_overhead_ms_median']:.3f} ms (diagnostic only)

Every one of the fourteen comparator failures was injected as an immutable malformed prospective reading and rejected in its owning phase before publication. These rejections preserve coverage and do not count as execution reruns.

## Causal binding

- Source commit: `{evidence['source_commit']}`
- Acknowledged tip: `{evidence['acknowledged_tip_sha256']}`
- Authoritative generation digest: `{evidence['authoritative_generation_sha256']}`
- Provider calls: {evidence['provider_call_count']}
- Published files: {evidence['published_file_count']}

Timing is excluded from the authoritative generation digest and from acceptance.

## Boundary

The accepted architecture and current controls remain unchanged. No occupied DeepSeek Harness, HMR retry, provider, product/practice surface, data, runtime, deployment, release, Pages, protected evidence or protected-ref movement was exercised or authorised.
"""


def main() -> int:
    generation, contract, gauge_results = build_generation(ROOT, CONTRACT, GAUGES)
    overhead = measure_clean_run_overhead(ROOT, CONTRACT, GAUGES)
    from orchestration_harness.shadow_clockwork import calculate_efficacy

    efficacy = calculate_efficacy(
        contract,
        generation,
        gauge_results,
        line_growth=_line_growth(),
        clean_run_overhead_ms=overhead,
    )
    if efficacy["accepted"]:
        publish_private_shadow(generation, contract, gauge_results, efficacy, SHADOW)
        manifest_digest = authoritative_manifest_digest(SHADOW)
        result = "accepted_provider_free_private_shadow_rehearsal"
        published_file_count = len(contract["publication"]["authoritative_files"])
    else:
        manifest_digest = authoritative_generation_digest(
            generation,
            gauge_results,
            efficacy,
        )
        result = "revision_required_efficacy_threshold_exceeded"
        published_file_count = 0
    evidence = {
        "schema_version": "ariadne.shadow_clockwork_rehearsal_evidence.v1",
        "operation_id": contract["operation_id"],
        "result": result,
        "source_commit": generation["journal"][0]["payload"]["source_commit"],
        "acknowledged_tip_sha256": generation["acknowledgement"]["acknowledgement_event_sha256"],
        "authoritative_generation_sha256": manifest_digest,
        "contract_sha256": digest(contract),
        "failure_gauge_results": gauge_results,
        "efficacy": efficacy,
        "provider_call_count": generation["terminal_result"]["provider_call_count"],
        "published_file_count": published_file_count,
        "live_adoption": False,
        "current_controls_retired": False,
        "timing_excluded_from_authoritative_digest": True,
    }
    _write_json(EVIDENCE, evidence)
    REPORT.write_text(render_report(evidence), encoding="utf-8", newline="\n")
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
