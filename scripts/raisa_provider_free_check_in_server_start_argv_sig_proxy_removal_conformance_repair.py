from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import jsonschema

from scripts import (
    raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal
    as harness,
)


ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "raisa-provider-free-check-in-server-start-argv-sig-proxy-removal-"
    "conformance-repair"
)
OPERATION_DIR = ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_DIR / "contract.json"
SCHEMA_PATH = OPERATION_DIR / "repair-attestation.schema.json"
ATTESTATION_PATH = OPERATION_DIR / "repair-attestation.json"
EXPECTED_ARGV = (
    "<executable>",
    "start",
    "--attach",
    "--interactive",
    "<container_id>",
)


class RepairError(RuntimeError):
    pass


class _FakeStdin:
    def __init__(self) -> None:
        self.writes: list[bytes] = []
        self.flush_count = 0
        self.close_count = 0
        self.closed = False

    def write(self, value: bytes) -> int:
        self.writes.append(value)
        return len(value)

    def flush(self) -> None:
        self.flush_count += 1

    def close(self) -> None:
        self.close_count += 1
        self.closed = True


class _FakeAttachment:
    def __init__(self) -> None:
        self.stdin = _FakeStdin()
        self.running = True
        self.terminate_count = 0
        self.kill_count = 0
        self.wait_count = 0

    def poll(self) -> int | None:
        return None if self.running else 0

    def terminate(self) -> None:
        self.terminate_count += 1
        self.running = False

    def kill(self) -> None:
        self.kill_count += 1
        self.running = False

    def wait(self, timeout: int) -> int:
        if timeout != 5:
            raise RepairError("unexpected attachment wait timeout")
        self.wait_count += 1
        self.running = False
        return 0


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RepairError(f"expected object: {path.name}")
    return value


def _git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    head = result.stdout.strip()
    if re.fullmatch(r"[0-9a-f]{40}", head) is None:
        raise RepairError("HEAD is not a full Git object identifier")
    return head


def _git_source(commit: str, path: str) -> bytes:
    if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise RepairError("historical source is not a full Git object identifier")
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return result.stdout


def _assert_ancestor(commit: str, head: str) -> None:
    if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise RepairError("plan source is not a full Git object identifier")
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, head],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RepairError("plan source is not an ancestor of HEAD")


def _function(tree: ast.Module, name: str) -> ast.FunctionDef:
    rows = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if len(rows) != 1:
        raise RepairError(f"expected exactly one {name} function")
    return rows[0]


def _symbol(node: ast.expr) -> str | bool:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return f"{node.value.id}.{node.attr}"
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value
    raise RepairError("unadmitted Popen profile expression")


def _argv_element(node: ast.expr) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name) and node.id in {"executable", "container_id"}:
        return f"<{node.id}>"
    raise RepairError("unadmitted start argv expression")


def source_profile(source: str) -> dict[str, Any]:
    tree = ast.parse(source)
    start = _function(tree, "_start_attached")
    popen = [
        node
        for node in ast.walk(start)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "Popen"
    ]
    if len(popen) != 1 or not popen[0].args or not isinstance(popen[0].args[0], ast.List):
        raise RepairError("expected one literal Popen argv")
    argv = tuple(_argv_element(node) for node in popen[0].args[0].elts)
    kwargs = {item.arg: _symbol(item.value) for item in popen[0].keywords}
    calls = [
        node.func.attr
        for node in ast.walk(start)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    ]
    stop = _function(tree, "_stop_attachment")
    stop_calls = [
        node.func.attr
        for node in ast.walk(stop)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    ]
    return {
        "argv": argv,
        "popen_profile": kwargs,
        "start_calls": {name: calls.count(name) for name in set(calls)},
        "stop_calls": {name: stop_calls.count(name) for name in set(stop_calls)},
    }


def _validate_contract(contract: Mapping[str, Any], head: str) -> tuple[bytes, bytes]:
    if contract.get("schema_version") != (
        "emr4.check-in-start-argv-sig-proxy-removal-repair-contract.v1"
    ):
        raise RepairError("contract schema mismatch")
    if contract.get("operation_id") != OPERATION_ID:
        raise RepairError("operation mismatch")
    if tuple(contract.get("expected_argv", ())) != EXPECTED_ARGV:
        raise RepairError("expected argv mismatch")
    plan_source = contract.get("plan_source")
    if not isinstance(plan_source, str):
        raise RepairError("plan source missing")
    _assert_ancestor(plan_source, head)
    for binding in contract.get("source_bindings", []):
        if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
            raise RepairError("invalid source binding")
        path = (ROOT / binding["path"]).resolve()
        if ROOT not in path.parents or not path.is_file():
            raise RepairError("source binding escaped or is absent")
        if _sha256(path) != binding["sha256"]:
            raise RepairError(f"source binding drift: {binding['path']}")
    harness_path = contract.get("harness_path")
    diagnosis_source = contract.get("accepted_diagnosis_source")
    if not isinstance(harness_path, str) or not isinstance(diagnosis_source, str):
        raise RepairError("harness source binding missing")
    historical = _git_source(diagnosis_source, harness_path)
    current_path = (ROOT / harness_path).resolve()
    current = current_path.read_bytes()
    if _sha256_bytes(historical) != contract.get("pre_repair_harness_sha256"):
        raise RepairError("pre-repair harness drift")
    if _sha256_bytes(current) != contract.get("post_repair_harness_sha256"):
        raise RepairError("post-repair harness drift")
    removed = (str(contract.get("removed_line")) + "\n").encode("utf-8")
    if historical.count(removed) != 1 or historical.replace(removed, b"", 1) != current:
        raise RepairError("repair is not the exact one-line deletion")
    profile = source_profile(current.decode("utf-8"))
    if profile["argv"] != EXPECTED_ARGV:
        raise RepairError("repaired argv mismatch")
    if profile["popen_profile"] != contract.get("popen_profile"):
        raise RepairError("Popen profile drift")
    start_calls = profile["start_calls"]
    if start_calls.get("write") != 1 or start_calls.get("flush") != 1:
        raise RepairError("stdin write or flush drift")
    for forbidden in ("close", "terminate", "kill", "wait", "send_signal"):
        if start_calls.get(forbidden, 0) != 0:
            raise RepairError("normal-path signal or close drift")
    stop_calls = profile["stop_calls"]
    for required in ("close", "terminate", "kill", "wait", "poll"):
        if stop_calls.get(required, 0) < 1:
            raise RepairError("teardown profile drift")
    return historical, current


def _fake_lifecycle() -> dict[str, Any]:
    attachment = _FakeAttachment()
    captured: dict[str, Any] = {}

    def fake_popen(argv: Sequence[str], **kwargs: Any) -> _FakeAttachment:
        captured["argv"] = list(argv)
        captured["kwargs"] = kwargs
        return attachment

    original = harness.subprocess.Popen
    harness.subprocess.Popen = fake_popen  # type: ignore[assignment]
    try:
        observed = harness._start_attached(
            "docker.exe", "c" * 64, ("first", "second")
        )
    finally:
        harness.subprocess.Popen = original  # type: ignore[assignment]
    if observed is not attachment:
        raise RepairError("fake attachment identity mismatch")
    normal = {
        "writes": list(attachment.stdin.writes),
        "flush_count": attachment.stdin.flush_count,
        "closed": attachment.stdin.closed,
        "close_count": attachment.stdin.close_count,
        "terminate_count": attachment.terminate_count,
        "kill_count": attachment.kill_count,
    }
    if not harness._stop_attachment(attachment):
        raise RepairError("fake teardown did not close")
    return {"captured": captured, "normal": normal, "attachment": attachment}


def build_attestation(contract: Mapping[str, Any], head: str) -> dict[str, Any]:
    historical, current = _validate_contract(contract, head)
    lifecycle = _fake_lifecycle()
    captured = lifecycle["captured"]
    normal = lifecycle["normal"]
    attachment = lifecycle["attachment"]
    expected_runtime_argv = [
        "docker.exe",
        "start",
        "--attach",
        "--interactive",
        "c" * 64,
    ]
    if captured["argv"] != expected_runtime_argv:
        raise RepairError("runtime argv mismatch")
    expected_kwargs = {
        "cwd": harness.ROOT,
        "stdin": subprocess.PIPE,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "shell": False,
    }
    if captured["kwargs"] != expected_kwargs:
        raise RepairError("runtime Popen profile mismatch")
    if normal != {
        "writes": [b"first\nsecond\n"],
        "flush_count": 1,
        "closed": False,
        "close_count": 0,
        "terminate_count": 0,
        "kill_count": 0,
    }:
        raise RepairError("normal stdin or signal lifecycle mismatch")
    diagnosis = _load_json(
        ROOT
        / "orchestration"
        / "continuity"
        / "raisa-provider-free-read-only-check-in-server-start-attach-created-state-"
        "failure-coordinate-diagnosis"
        / "diagnosis-evidence.json"
    )
    if diagnosis["cli_evidence"]["advertised_options"] != contract.get(
        "diagnosis_option_surface"
    ):
        raise RepairError("diagnosis option surface drift")
    evidence: dict[str, Any] = {
        "schema_version": (
            "emr4.check-in-start-argv-sig-proxy-removal-repair-attestation.v1"
        ),
        "operation_id": OPERATION_ID,
        "result": contract["result"],
        "source_head": head,
        "input_bindings_verified": True,
        "exact_diff": {
            "pre_repair_sha256": _sha256_bytes(historical),
            "post_repair_sha256": _sha256_bytes(current),
            "removed_tokens": ["--sig-proxy=false"],
            "added_tokens": [],
            "other_harness_changes": 0,
        },
        "start_attached": {
            "argv": list(EXPECTED_ARGV),
            "advertised_options": contract["diagnosis_option_surface"],
            "popen_profile": contract["popen_profile"],
        },
        "stdin_lifecycle": {
            "payload": "two_lines_ascii_newline_terminated",
            "write_count": 1,
            "flush_count": normal["flush_count"],
            "open_after_delivery": not normal["closed"],
            "normal_path_close_count": normal["close_count"],
        },
        "signal_and_teardown": {
            "docker_attach_default_forwards_signals": True,
            "normal_path_terminate_count": normal["terminate_count"],
            "normal_path_kill_count": normal["kill_count"],
            "teardown_stdin_close_count": attachment.stdin.close_count,
            "teardown_terminate_count": attachment.terminate_count,
            "teardown_wait_count": attachment.wait_count,
            "teardown_kill_count": attachment.kill_count,
            "teardown_result": "attachment_absent",
        },
        "historical_diagnosis": {
            "evidence_sha256": _sha256(
                ROOT
                / "orchestration"
                / "continuity"
                / "raisa-provider-free-read-only-check-in-server-start-attach-"
                "created-state-failure-coordinate-diagnosis"
                / "diagnosis-evidence.json"
            ),
            "historical_argv_contains_sig_proxy": b"--sig-proxy=false" in historical,
            "current_live_source_check": (
                "source_binding_drift_expected_after_accepted_repair"
            ),
            "reclassified": False,
        },
        "repair": {
            "surface": (
                "remove_unsupported_sig_proxy_option_from_docker_start_argv"
            ),
            "implemented": True,
            "attempt_007_authorized": False,
        },
        "closed_boundaries": {
            key: value
            for key, value in contract["closed_boundaries"].items()
            if key != "attempt_007_authorized"
        },
    }
    schema = _load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator(schema).validate(evidence)
    return evidence


def check() -> None:
    head = _git_head()
    contract = _load_json(CONTRACT_PATH)
    _validate_contract(contract, head)
    jsonschema.Draft202012Validator.check_schema(_load_json(SCHEMA_PATH))


def execute() -> None:
    if ATTESTATION_PATH.exists():
        raise RepairError("repair attestation already exists")
    head = _git_head()
    contract = _load_json(CONTRACT_PATH)
    attestation = build_attestation(contract, head)
    with ATTESTATION_PATH.open("xb") as stream:
        stream.write(_canonical_bytes(attestation))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the provider-free sig-proxy start-argv repair."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.check:
            check()
        else:
            execute()
    except (
        RepairError,
        OSError,
        subprocess.SubprocessError,
        json.JSONDecodeError,
        jsonschema.ValidationError,
    ) as error:
        parser.exit(1, f"repair failed closed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
