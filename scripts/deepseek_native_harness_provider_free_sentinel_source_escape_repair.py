"""Prove the provider-free sentinel source escape repair without executable Harness activity."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import (  # noqa: E402
    deepseek_native_harness_provider_free_repaired_sentinel_preactivation_source_coordinate_diagnosis
    as diagnosis,
)


OPERATION_ID = "deepseek-native-harness-provider-free-sentinel-source-escape-repair"
CONTINUITY_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = CONTINUITY_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = CONTINUITY_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_ROOT / "evidence.schema.json"
EVIDENCE_PATH = CONTINUITY_ROOT / "repair-evidence.json"
REPORT_PATH = CONTINUITY_ROOT / "repair-report.md"
EVIDENCE_SCHEMA = "ariadne.deepseek_native_harness_sentinel_source_escape_repair_evidence.v1"
FULL_OID = re.compile(r"^[0-9a-f]{40}$")


class RepairError(RuntimeError):
    """The bounded source-only repair proof failed closed."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def _load_json_bytes(payload: bytes, coordinate: str) -> dict[str, Any]:
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RepairError(f"static_json_invalid:{coordinate}") from error
    if not isinstance(value, dict):
        raise RepairError(f"static_json_not_object:{coordinate}")
    return value


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = _load_json_bytes(path.read_bytes(), "contract")
    schema = _load_json_bytes(CONTRACT_SCHEMA_PATH.read_bytes(), "contract_schema")
    jsonschema.validate(contract, schema)
    if contract.get("operation_id") != OPERATION_ID:
        raise RepairError("contract_operation_mismatch")
    method = contract.get("method", {})
    zero_fields = (
        "node_process_limit",
        "harness_process_limit",
        "broker_process_limit",
        "worker_process_limit",
        "model_request_limit",
        "provider_request_limit",
        "network_request_limit",
        "raw_stream_reconstruction_limit",
    )
    if (
        method.get("execute_or_import_repair_target") is not False
        or any(method.get(field) != 0 for field in zero_fields)
        or method.get("maximum_modified_preexisting_files") != 1
    ):
        raise RepairError("contract_source_only_boundary_mismatch")
    return contract


def _git(*args: str) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RepairError(f"git_command_failed:{args[0] if args else 'none'}")
    return completed.stdout


def _git_show(commit: str, path: str) -> bytes:
    if FULL_OID.fullmatch(commit) is None:
        raise RepairError("git_source_not_full_object_id")
    return _git("show", f"{commit}:{path}")


def _git_source_is_ancestor(commit: str) -> bool:
    if FULL_OID.fullmatch(commit) is None:
        return False
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.returncode == 0


def _binding(role: str, expected: str, observed: str) -> dict[str, Any]:
    return {
        "role": role,
        "expected_sha256": expected,
        "observed_sha256": observed,
        "matched": expected == observed,
    }


def _changed_byte_count(before: bytes, after: bytes) -> int:
    prefix = 0
    while prefix < min(len(before), len(after)) and before[prefix] == after[prefix]:
        prefix += 1
    before_tail = len(before)
    after_tail = len(after)
    while (
        before_tail > prefix
        and after_tail > prefix
        and before[before_tail - 1] == after[after_tail - 1]
    ):
        before_tail -= 1
        after_tail -= 1
    return max(before_tail - prefix, after_tail - prefix)


def _tracked_paths(commit: str, roots: list[str]) -> list[str]:
    output = _git("ls-tree", "-r", "--name-only", commit, "--", *roots)
    paths = sorted({row for row in output.decode("utf-8").splitlines() if row})
    if not paths:
        raise RepairError("consumed_evidence_roots_empty")
    return paths


def analyze_repair(
    contract: dict[str, Any],
    *,
    target_payload: bytes | None = None,
    binding_overrides: dict[str, bytes] | None = None,
    consumed_overrides: dict[str, bytes] | None = None,
) -> dict[str, Any]:
    target = contract["repair_target"]
    planning_source = contract["planning_source"]
    diagnosis_source = contract["accepted_diagnosis_source"]
    overrides = binding_overrides or {}
    consumed_mutations = consumed_overrides or {}

    preimage = _git_show(planning_source, target["path"])
    candidate = (
        target_payload
        if target_payload is not None
        else (REPO_ROOT / target["path"]).read_bytes()
    )
    old_token = target["old_token"].encode("utf-8")
    new_token = target["new_token"].encode("utf-8")
    replacement_count = preimage.count(old_token)
    expected_candidate = preimage.replace(old_token, new_token, 1)
    exact_delta = bool(
        replacement_count == target["required_replacement_count"]
        and candidate == expected_candidate
        and len(candidate) - len(preimage) == target["expected_changed_byte_count"]
    )

    bindings: list[dict[str, Any]] = []
    preimage_sha = _sha256(preimage)
    postimage_sha = _sha256(candidate)
    bindings.append(
        _binding("repair_target_preimage", target["preimage_sha256"], preimage_sha)
    )
    bindings.append(
        _binding("repair_target_postimage", target["postimage_sha256"], postimage_sha)
    )
    for row in contract["diagnosis_bindings"]:
        payload = overrides.get(row["path"], (REPO_ROOT / row["path"]).read_bytes())
        bindings.append(_binding(row["role"], row["sha256"], _sha256(payload)))
    zero_sha = "0" * 64
    bindings.append(
        _binding(
            "planning_source_full_and_ancestral",
            zero_sha,
            zero_sha if _git_source_is_ancestor(planning_source) else "f" * 64,
        )
    )
    bindings.append(
        _binding(
            "diagnosis_source_full_and_ancestral",
            zero_sha,
            zero_sha if _git_source_is_ancestor(diagnosis_source) else "f" * 64,
        )
    )

    try:
        module = diagnosis.extract_static_module(candidate, target["function_name"])
        violations = diagnosis.lexical_line_terminator_violations(module["bytes"])
    except diagnosis.DiagnosisError:
        module = {
            "bytes": b"",
            "sha256": _sha256(b""),
            "function_line": 1,
            "return_line": 1,
            "source_segment": "",
        }
        violations = [
            {
                "offset": 0,
                "line": 1,
                "column": 1,
                "context": "python_static_shape",
                "control": "invalid",
            }
        ]
    required_spellings = [value.encode("utf-8") for value in target["required_generated_spellings"]]
    generated_spellings_present = all(
        module["bytes"].count(spelling) == 1 for spelling in required_spellings
    )
    literal_prefix = (
        "br"
        if target["new_token"] in module["source_segment"]
        else "other"
    )

    consumed_paths = _tracked_paths(planning_source, contract["consumed_evidence_roots"])
    consumed_preserved = True
    for path in consumed_paths:
        expected = _git_show(planning_source, path)
        candidate_bytes = consumed_mutations.get(path)
        if candidate_bytes is None:
            current = REPO_ROOT / path
            if not current.is_file():
                consumed_preserved = False
                continue
            candidate_bytes = current.read_bytes()
        if candidate_bytes != expected:
            consumed_preserved = False

    repair_ok = bool(
        exact_delta
        and preimage_sha == target["preimage_sha256"]
        and postimage_sha == target["postimage_sha256"]
        and _changed_byte_count(preimage, candidate)
        == target["expected_changed_byte_count"]
        and literal_prefix == "br"
        and module["sha256"] == target["expected_generated_module_sha256"]
        and len(module["bytes"]) == target["expected_generated_module_bytes"]
        and generated_spellings_present
        and not violations
    )
    result = (
        "pass"
        if repair_ok
        and all(row["matched"] for row in bindings)
        and consumed_preserved
        else "failed_closed"
    )
    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "result": result,
        "bindings": bindings,
        "repair": {
            "exact_delta": exact_delta,
            "changed_byte_count": _changed_byte_count(preimage, candidate),
            "preimage_sha256": preimage_sha,
            "postimage_sha256": postimage_sha,
            "literal_prefix": literal_prefix,
            "generated_module_sha256": module["sha256"],
            "generated_module_bytes": len(module["bytes"]),
            "generated_spellings_present": generated_spellings_present,
            "lexical_violation_count": len(violations),
            "function_line": module["function_line"],
            "return_line": module["return_line"],
        },
        "consumed_evidence": {
            "roots": contract["consumed_evidence_roots"],
            "tracked_file_count": len(consumed_paths),
            "all_preserved": consumed_preserved,
        },
        "zero_activity": {
            "node_process_count": 0,
            "harness_process_count": 0,
            "broker_process_count": 0,
            "worker_process_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "network_request_count": 0,
            "raw_stream_reconstruction_count": 0,
        },
        "claim_boundary": contract["claim_boundary"],
    }
    schema = _load_json_bytes(EVIDENCE_SCHEMA_PATH.read_bytes(), "evidence_schema")
    jsonschema.validate(evidence, schema)
    return evidence


def report_markdown(evidence: dict[str, Any]) -> str:
    timestamp = datetime.now().astimezone().isoformat()
    repair = evidence["repair"]
    consumed = evidence["consumed_evidence"]
    return f"""# DeepSeek native Harness provider-free sentinel source escape repair

Date: {timestamp[:10]}
Timestamp: {timestamp} (Australia/Brisbane)

## Result

- Verdict: `{evidence['result']}`
- Exact one-byte source delta: `{repair['exact_delta']}`
- Literal prefix: `{repair['literal_prefix']}`
- Generated module: `{repair['generated_module_bytes']}` bytes, SHA-256 `{repair['generated_module_sha256']}`
- Required JavaScript escape spellings present: `{repair['generated_spellings_present']}`
- Raw line terminators inside JavaScript regex/quoted literals: `{repair['lexical_violation_count']}`
- Consumed tracked evidence preserved: `{consumed['all_preserved']}` across `{consumed['tracked_file_count']}` files
- Node / Harness / broker / worker / model / provider / network activity: `0 / 0 / 0 / 0 / 0 / 0 / 0`

## Reading

The sentinel author now uses a raw Python bytes literal. Python therefore preserves the intended JavaScript `\\r`, `\\n` and `"\\n"` escape spellings instead of translating them into raw control bytes. Every other pre-existing byte in the worker controller remains identical to the frozen planning-source preimage.

## Claim boundary

{evidence['claim_boundary']}
"""


def run(output_root: Path = CONTINUITY_ROOT) -> dict[str, Any]:
    contract = load_contract()
    evidence = analyze_repair(contract)
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / EVIDENCE_PATH.name).write_bytes(_canonical_json(evidence))
    (output_root / REPORT_PATH.name).write_text(
        report_markdown(evidence), encoding="utf-8", newline="\n"
    )
    return evidence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=CONTINUITY_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        evidence = run(args.output_root)
    except (RepairError, OSError, jsonschema.ValidationError) as error:
        raise SystemExit(str(error)) from error
    print(evidence["result"])
    return 0 if evidence["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
