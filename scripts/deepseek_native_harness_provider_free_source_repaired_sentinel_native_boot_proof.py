"""Run one fresh provider-free rc.7 boot of the source-repaired sentinel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import (  # noqa: E402
    deepseek_native_harness_provider_free_repaired_sentinel_native_boot_proof
    as engine,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-source-repaired-sentinel-native-boot-proof"
)
ATTEMPT_ID = "source-repaired-sentinel-native-boot-attempt-001"
CONTINUITY_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = CONTINUITY_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = CONTINUITY_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_ROOT / "evidence.schema.json"
CONSUMED_PATH = CONTINUITY_ROOT / "native-attempt-consumed.json"
EVIDENCE_PATH = CONTINUITY_ROOT / "provider-free-source-repaired-sentinel-native-boot-terminal.json"
REPORT_PATH = CONTINUITY_ROOT / "provider-free-source-repaired-sentinel-native-boot-report.md"
CONTRACT_SCHEMA = (
    "ariadne.deepseek_native_harness_source_repaired_sentinel_boot_contract.v1"
)
EVIDENCE_SCHEMA = (
    "ariadne.deepseek_native_harness_source_repaired_sentinel_boot_evidence.v1"
)
_PREDECESSOR_LOAD_CONTRACT = engine.load_contract


def _load_source_repaired_contract(
    path: Path = CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the fresh contract without inheriting the predecessor default path."""
    return _PREDECESSOR_LOAD_CONTRACT(path)


def _source_repair_lineage(contract: dict[str, Any]) -> dict[str, Any]:
    sources = [contract["planning_source"], *contract["accepted_sources"].values()]
    if any(not engine._git_commit_is_ancestor(source) for source in sources):
        raise engine.RepairedSentinelBootError("git_source_missing_or_not_ancestor")
    observed: list[dict[str, Any]] = []
    roles: set[str] = set()
    for row in contract["components"]:
        role = row["role"]
        path = REPO_ROOT / row["path"]
        if role in roles or not path.is_file() or path.is_symlink():
            raise engine.RepairedSentinelBootError("component_path_invalid:" + role)
        roles.add(role)
        digest = engine._file_sha256(path)
        if digest != row["sha256"]:
            raise engine.RepairedSentinelBootError("component_digest_mismatch:" + role)
        observed.append({"role": role, "sha256": digest})

    repair = engine._load_json(
        REPO_ROOT
        / "orchestration"
        / "continuity"
        / "deepseek-native-harness-provider-free-sentinel-source-escape-repair"
        / "repair-evidence.json"
    )
    if (
        repair.get("result") != "pass"
        or repair.get("repair", {}).get("postimage_sha256")
        != engine._file_sha256(Path(engine.repaired.__file__).resolve())
        or repair.get("repair", {}).get("lexical_violation_count") != 0
        or repair.get("consumed_evidence", {}).get("all_preserved") is not True
        or any(repair.get("zero_activity", {}).values())
    ):
        raise engine.RepairedSentinelBootError("source_repair_evidence_mismatch")
    return {"sources": sources, "components": observed}


def _report(evidence: dict[str, Any]) -> str:
    return f"""# Provider-free source-repaired sentinel native-boot report

Date: 2026-08-21

Result: **{evidence['result']}**

- Attempt: `{evidence['attempt_id']}`
- Candidate: `{evidence['candidate_source']}`
- Native processes / retries: `{evidence['launch']['native_process_count']}` / `0`
- HMR events: `{', '.join(evidence['hmr_events'])}`
- Failure coordinate: `{evidence['failure_coordinate']}`
- Network / model / provider requests: `{evidence['provider_boundary']['network_attempts']}` / `0` / `0`
- Process absent: `{str(evidence['cleanup']['process_absent']).lower()}`
- Disposable root absent: `{str(evidence['cleanup']['disposable_root_absent']).lower()}`
- Raw streams retained: `false`

This proves only source-repaired sentinel loading and stock-headless HMR
readiness in one provider-free rc.7 process. It is not a runner, worker,
model/provider, product-runtime or reliability result.
"""


def configure_engine() -> None:
    engine.OPERATION_ID = OPERATION_ID
    engine.ATTEMPT_ID = ATTEMPT_ID
    engine.CONTINUITY_ROOT = CONTINUITY_ROOT
    engine.CONTRACT_PATH = CONTRACT_PATH
    engine.CONTRACT_SCHEMA_PATH = CONTRACT_SCHEMA_PATH
    engine.EVIDENCE_SCHEMA_PATH = EVIDENCE_SCHEMA_PATH
    engine.CONSUMED_PATH = CONSUMED_PATH
    engine.EVIDENCE_PATH = EVIDENCE_PATH
    engine.REPORT_PATH = REPORT_PATH
    engine.CONTRACT_SCHEMA = CONTRACT_SCHEMA
    engine.EVIDENCE_SCHEMA = EVIDENCE_SCHEMA
    engine.load_contract = _load_source_repaired_contract
    engine.validate_lineage = _source_repair_lineage
    engine._render_report = _report


def deterministic_check(candidate_source: str | None = None) -> dict[str, Any]:
    configure_engine()
    return engine.deterministic_check(candidate_source)


def execute_boot(candidate_source: str) -> dict[str, Any]:
    configure_engine()
    return engine.execute_boot(candidate_source)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--execute", action="store_true")
    parser.add_argument("--candidate-source")
    args = parser.parse_args()
    try:
        if args.check:
            projection = deterministic_check(args.candidate_source)
            output = {
                "status": "passed",
                "attempt_id": ATTEMPT_ID,
                "profile_sha256": projection["profile"]["sha256"],
                "native_processes": 0,
            }
        else:
            if args.candidate_source is None:
                raise engine.RepairedSentinelBootError("candidate_source_required")
            evidence = execute_boot(args.candidate_source)
            output = {
                "status": evidence["result"],
                "attempt_id": ATTEMPT_ID,
                "hmr_events": evidence["hmr_events"],
                "cleanup": evidence["cleanup"],
            }
        print(json.dumps(output, sort_keys=True))
    except (
        engine.RepairedSentinelBootError,
        engine.materializer.PresetMountProjectionError,
        engine.ProofError,
        jsonschema.ValidationError,
    ) as error:
        print(json.dumps({"status": "revision_required", "reason": str(error)}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
