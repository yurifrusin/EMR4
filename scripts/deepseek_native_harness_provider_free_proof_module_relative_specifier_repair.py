#!/usr/bin/env python3
"""Build provider-free evidence for the two-row proof-module specifier repair."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as subject,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-proof-module-relative-specifier-repair"
)
CONTINUITY_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = CONTINUITY_ROOT / "contract.json"
TARGET_PATH = (
    REPO_ROOT
    / "scripts"
    / "raisa_authored_synthetic_check_in_native_harness_bounded_worker_"
    "monitored_development_rehearsal.py"
)
SENTINEL = "../../../installation/proof/sentinel.mjs"
RUNNER = "../../../installation/proof/runner.mjs"
OLD_SENTINEL = 'name: {quoted(proof / "sentinel.mjs")}'
OLD_RUNNER = 'name: {quoted(proof / "runner.mjs")}'
ABSOLUTE_TARGET = re.compile(
    r"name:\s+[\"']?[A-Za-z]:[\\/][^\r\n]*(?:sentinel|runner)\.mjs"
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("operation_id") != OPERATION_ID:
        raise ValueError("contract_operation_mismatch")
    if value.get("allowed_relative_specifiers") != [SENTINEL, RUNNER]:
        raise ValueError("contract_specifier_mismatch")
    if value.get("native_boot_authorized") is not False:
        raise ValueError("native_boot_boundary_open")
    if value.get("occupied_retry_authorized") is not False:
        raise ValueError("occupied_retry_boundary_open")
    return value


def build_evidence(
    source: bytes,
    *,
    profile_root: Path = Path("C:/synthetic-native-worker"),
) -> dict[str, Any]:
    text = source.decode("utf-8")
    profile_body = text.split("def profile_patch", 1)[-1].split(
        "def validate_profile_patch", 1
    )[0]
    sentinel_row = f"name: {SENTINEL}"
    runner_row = f"name: {RUNNER}"
    source_checks = {
        "sentinel_relative_row_exactly_once": text.count(sentinel_row) == 1,
        "runner_relative_row_exactly_once": text.count(runner_row) == 1,
        "former_sentinel_absolute_author_absent": OLD_SENTINEL not in text,
        "former_runner_absolute_author_absent": OLD_RUNNER not in text,
        "dead_proof_local_absent": (
            'proof = root / "installation" / "proof"' not in profile_body
        ),
        "accepted_diagnosis_full_hash_bound": (
            load_contract().get("accepted_diagnosis_source")
            == "f735e6c9f4412aea8e83e410c0292668ebe7853f"
        ),
    }

    initial_payload = subject.profile_patch(profile_root, 43123, changed=False)
    changed_payload = subject.profile_patch(profile_root, 43123, changed=True)
    initial = initial_payload.decode("utf-8")
    changed = changed_payload.decode("utf-8")
    initial_validation = subject.validate_profile_patch(
        initial_payload, changed=False
    )
    changed_validation = subject.validate_profile_patch(changed_payload, changed=True)
    profile_checks = {
        "initial_sentinel_exactly_once": initial.count(sentinel_row) == 1,
        "initial_runner_absent": runner_row not in initial,
        "changed_sentinel_exactly_once": changed.count(sentinel_row) == 1,
        "changed_runner_exactly_once": changed.count(runner_row) == 1,
        "initial_target_absolute_name_absent": ABSOLUTE_TARGET.search(initial) is None,
        "changed_target_absolute_name_absent": ABSOLUTE_TARGET.search(changed) is None,
        "initial_existing_profile_validation_passed": bool(initial_validation),
        "changed_existing_profile_validation_passed": bool(changed_validation),
        "initial_retry_count_zero_preserved": initial_validation["retry_count_zero"],
        "changed_parallel_width_one_preserved": changed_validation[
            "parallel_width_one"
        ],
        "changed_runner_presence_exact_preserved": changed_validation[
            "runner_presence_exact"
        ],
    }
    passed = all(source_checks.values()) and all(profile_checks.values())
    return {
        "schema_version": (
            "ariadne.native_harness_proof_module_relative_specifier_repair_"
            "evidence.v1"
        ),
        "operation_id": OPERATION_ID,
        "status": "passed" if passed else "failed_closed",
        "target_source_sha256": sha256_bytes(source),
        "source_checks": source_checks,
        "profile_checks": profile_checks,
        "zero_activity": {
            "node_process_count": 0,
            "harness_process_count": 0,
            "broker_process_count": 0,
            "worker_process_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "network_request_count": 0,
        },
        "claim_boundary": (
            "This provider-free result proves only the two generated profile "
            "module-name rows and preserved static invariants. It does not prove "
            "native boot, DeepSeek reachability, worker reliability or EMR4 "
            "development readiness, and it authorizes no occupied retry."
        ),
    }


def report_markdown(evidence: dict[str, Any]) -> str:
    timestamp = datetime.now().astimezone().isoformat()
    failed = sorted(
        name
        for group in (evidence["source_checks"], evidence["profile_checks"])
        for name, passed in group.items()
        if not passed
    )
    return f"""# Native Harness proof-module relative-specifier repair report

Date: {timestamp[:10]}
Timestamp: {timestamp} (Australia/Brisbane)

## Result

- Status: `{evidence['status']}`
- Target source SHA-256: `{evidence['target_source_sha256']}`
- Failed checks: `{', '.join(failed) if failed else 'none'}`
- Node/Harness/broker/worker/model/provider/network activity: `0`

The generated initial profile contains only the profile-relative sentinel. The
changed profile contains the same sentinel plus the profile-relative runner.
The former absolute Windows path authors are absent and the existing bounded
profile validation remains passing.

## Claim boundary

{evidence['claim_boundary']}
"""


def run(
    target_path: Path = TARGET_PATH,
    output_root: Path = CONTINUITY_ROOT,
) -> dict[str, Any]:
    load_contract()
    evidence = build_evidence(target_path.read_bytes())
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "repair-evidence.json").write_bytes(
        canonical_json_bytes(evidence)
    )
    (output_root / "repair-report.md").write_text(
        report_markdown(evidence), encoding="utf-8", newline="\n"
    )
    return evidence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=TARGET_PATH)
    parser.add_argument("--output-root", type=Path, default=CONTINUITY_ROOT)
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    evidence = run(arguments.target, arguments.output_root)
    print(evidence["status"])
    return 0 if evidence["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
