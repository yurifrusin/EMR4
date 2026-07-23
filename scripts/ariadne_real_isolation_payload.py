#!/usr/bin/env python3
"""Run the accepted authored-synthetic tape inside the frozen container."""

from __future__ import annotations

import errno
import hashlib
import json
import os
import socket
from pathlib import Path
from typing import Any

try:
    from scripts import ariadne_scripted_cognitive_work_cell_rehearsal as runner
except ModuleNotFoundError:  # pragma: no cover - direct container invocation
    import ariadne_scripted_cognitive_work_cell_rehearsal as runner


SCHEMA_VERSION = "ariadne.real_isolation_payload.v1"
RESULT = "ariadne_real_isolation_payload_pass"
ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / (
    "orchestration/continuity/ariadne-real-isolation-rehearsal-manifest.json"
)
EXPECTED_EVIDENCE_PATH = ROOT / (
    "orchestration/continuity/"
    "ariadne-scripted-cognitive-work-cell-rehearsal-evidence.json"
)
WRITE_PROBE_PATH = ROOT / ".ariadne-real-isolation-write-probe"


class IsolationPayloadError(ValueError):
    """Raised when the in-container isolation or predecessor proof fails."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


def file_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise IsolationPayloadError("fixed_input_unreadable") from error
    if not isinstance(value, dict):
        raise IsolationPayloadError("fixed_input_not_object")
    return value


def _verify_sources(manifest: dict[str, Any]) -> dict[str, str]:
    entries = manifest.get("build_context", {}).get("allowlist")
    if not isinstance(entries, list) or not entries:
        raise IsolationPayloadError("allowlist_invalid")
    observed: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise IsolationPayloadError("allowlist_entry_invalid")
        relative = entry.get("path")
        expected = entry.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected, str):
            raise IsolationPayloadError("allowlist_entry_invalid")
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise IsolationPayloadError("allowlisted_source_invalid")
        observed[relative] = file_sha256(path)
        if observed[relative] != expected:
            raise IsolationPayloadError("allowlisted_source_hash_mismatch")

    manifest_relative = MANIFEST_PATH.relative_to(ROOT).as_posix()
    expected_files = set(observed) | {manifest_relative}
    actual_files = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
    }
    if actual_files != expected_files:
        raise IsolationPayloadError("container_file_set_mismatch")
    return observed


def _observe_isolation() -> dict[str, Any]:
    if os.getuid() != 65532 or os.getgid() != 65532:
        raise IsolationPayloadError("non_root_identity_mismatch")
    interfaces = sorted(name for _, name in socket.if_nameindex())
    if interfaces != ["lo"]:
        raise IsolationPayloadError("network_interface_mismatch")

    if WRITE_PROBE_PATH.exists():
        raise IsolationPayloadError("write_probe_preexisted")
    blocked_errno: int | None = None
    try:
        WRITE_PROBE_PATH.write_text("forbidden", encoding="utf-8")
    except OSError as error:
        blocked_errno = error.errno
    if blocked_errno != errno.EROFS or WRITE_PROBE_PATH.exists():
        raise IsolationPayloadError("read_only_write_probe_failed")
    return {
        "uid": os.getuid(),
        "gid": os.getgid(),
        "network_interfaces": interfaces,
        "loopback_only": True,
        "write_probe_blocked": True,
        "write_probe_errno": "EROFS",
        "write_probe_residue": False,
    }


def run_payload() -> dict[str, Any]:
    manifest = _load_object(MANIFEST_PATH)
    if manifest.get("schema_version") != "ariadne.real_isolation_manifest.v1":
        raise IsolationPayloadError("manifest_version_mismatch")
    source_hashes = _verify_sources(manifest)
    isolation = _observe_isolation()

    document = runner.load_json(runner.default_script_path(ROOT))
    protocol = runner.load_json(runner.default_protocol_path(ROOT))
    first = runner.build_rehearsal(document, protocol=protocol, repo_root=ROOT)
    second = runner.build_rehearsal(document, protocol=protocol, repo_root=ROOT)
    if runner.canonical_json(first) != runner.canonical_json(second):
        raise IsolationPayloadError("predecessor_runs_differ")
    projection = runner.build_evidence_projection(first)
    expected = _load_object(EXPECTED_EVIDENCE_PATH)
    if projection != expected:
        raise IsolationPayloadError("predecessor_projection_mismatch")

    totals = projection["totals"]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "result": RESULT,
        "evidence_label": (
            "authored_synthetic_disposable_local_container_payload"
        ),
        "isolation_observation": isolation,
        "allowlisted_source_count": len(source_hashes),
        "allowlisted_sources_sha256": canonical_sha256(source_hashes),
        "predecessor_projection_sha256": canonical_sha256(projection),
        "predecessor_runs_byte_identical": True,
        "predecessor_result": projection["result"],
        "scenario_count": totals["scenario_count"],
        "transition_count": totals["transition_count"],
        "released_edge_count": totals["released_edge_count"],
        "human_gate_delivery_count": totals["human_gate_delivery_count"],
        "aborted_edge_count": totals["aborted_edge_count"],
        "supersession_count": totals["supersession_count"],
        "adaptive_agent_attached": False,
        "external_effects_enabled": False,
        "command_authority": False,
    }


def main() -> int:
    try:
        print(canonical_json(run_payload()), end="")
        return 0
    except (IsolationPayloadError, runner.ScriptedRehearsalError):
        print(
            canonical_json(
                {
                    "schema_version": SCHEMA_VERSION,
                    "status": "revision_required",
                    "result": "ariadne_real_isolation_payload_failed",
                }
            ),
            end="",
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
