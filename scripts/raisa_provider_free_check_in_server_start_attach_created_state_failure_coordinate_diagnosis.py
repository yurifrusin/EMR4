from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "raisa-provider-free-read-only-check-in-server-start-attach-created-state-"
    "failure-coordinate-diagnosis"
)
OPERATION_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-read-only-check-in-server-start-attach-created-state-"
    "failure-coordinate-diagnosis"
)
CONTRACT_PATH = OPERATION_DIR / "contract.json"
SCHEMA_PATH = OPERATION_DIR / "diagnosis-evidence.schema.json"
EVIDENCE_PATH = OPERATION_DIR / "diagnosis-evidence.json"
HARNESS_PATH = (
    ROOT
    / "scripts"
    / "raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_"
    "rollback_unknown_commit_recovery_rehearsal.py"
)

COORDINATE_VOCABULARY = (
    "cli_option_surface_mismatch",
    "composite_start_attach_exited_while_oci_created",
    "container_exited_after_start",
    "readiness_expired_while_running",
    "insufficient_closed_evidence",
)
CLI_MANIFEST = {
    "docker_version": (
        "docker.exe",
        "version",
        "--format",
        "{{.Client.Version}}|{{.Server.Version}}",
    ),
    "docker_start_help": ("docker.exe", "start", "--help"),
}
EXPECTED_ARGV = (
    "<executable>",
    "start",
    "--attach",
    "--interactive",
    "--sig-proxy=false",
    "<container_id>",
)
VERSION_RE = re.compile(r"^(?P<client>[0-9]+\.[0-9]+\.[0-9]+)\|(?P<server>[0-9]+\.[0-9]+\.[0-9]+)$")

Runner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


class DiagnosisError(RuntimeError):
    pass


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DiagnosisError(f"expected object: {path.name}")
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
        raise DiagnosisError("HEAD is not a full Git object identifier")
    return head


def _assert_ancestor(commit: str, head: str) -> None:
    if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise DiagnosisError("plan source is not a full Git object identifier")
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, head],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise DiagnosisError("plan source is not an ancestor of HEAD")


def _normalise_argv_element(node: ast.expr) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name) and node.id in {"executable", "container_id"}:
        return f"<{node.id}>"
    raise DiagnosisError("start argv contains an unadmitted expression")


def extract_start_argv(source: str) -> tuple[str, ...]:
    tree = ast.parse(source)
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_start_attached"
    ]
    if len(functions) != 1:
        raise DiagnosisError("expected exactly one _start_attached function")
    popen_calls = [
        node
        for node in ast.walk(functions[0])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "Popen"
    ]
    if len(popen_calls) != 1 or not popen_calls[0].args:
        raise DiagnosisError("expected exactly one Popen argv")
    argv_node = popen_calls[0].args[0]
    if not isinstance(argv_node, ast.List):
        raise DiagnosisError("Popen argv must be a literal list")
    return tuple(_normalise_argv_element(element) for element in argv_node.elts)


def _validate_contract(contract: Mapping[str, Any], head: str) -> None:
    if contract.get("schema_version") != (
        "emr4.check-in-start-attach-created-state-diagnosis-contract.v1"
    ):
        raise DiagnosisError("contract schema mismatch")
    if contract.get("operation_id") != OPERATION_ID:
        raise DiagnosisError("operation mismatch")
    if tuple(contract.get("coordinate_vocabulary", ())) != COORDINATE_VOCABULARY:
        raise DiagnosisError("coordinate vocabulary mismatch")
    if tuple(contract.get("expected_source_argv", ())) != EXPECTED_ARGV:
        raise DiagnosisError("expected argv mismatch")
    manifest = {
        key: tuple(value) for key, value in contract.get("cli_manifest", {}).items()
    }
    if manifest != CLI_MANIFEST:
        raise DiagnosisError("CLI manifest mismatch")
    plan_source = contract.get("plan_source")
    if not isinstance(plan_source, str):
        raise DiagnosisError("plan source missing")
    _assert_ancestor(plan_source, head)
    bindings = contract.get("source_bindings")
    if not isinstance(bindings, list) or not bindings:
        raise DiagnosisError("source bindings missing")
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
            raise DiagnosisError("invalid source binding")
        relative_path = binding["path"]
        expected_hash = binding["sha256"]
        if not isinstance(relative_path, str) or not isinstance(expected_hash, str):
            raise DiagnosisError("invalid source binding value")
        path = (ROOT / relative_path).resolve()
        if ROOT not in path.parents or not path.is_file():
            raise DiagnosisError("source binding escaped or is absent")
        if _sha256(path) != expected_hash:
            raise DiagnosisError(f"source binding drift: {relative_path}")
    source_argv = extract_start_argv(HARNESS_PATH.read_text(encoding="utf-8"))
    if source_argv != EXPECTED_ARGV:
        raise DiagnosisError("start argv source drift")


def _run_read_only(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    admitted = {tuple(value) for value in CLI_MANIFEST.values()}
    if tuple(command) not in admitted:
        raise DiagnosisError("command is outside the read-only CLI manifest")
    return subprocess.run(
        list(command),
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
    )


def _advertises(help_text: str, option: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9_-]){re.escape(option)}(?![A-Za-z0-9_-])", help_text) is not None


def classify_coordinate(
    *,
    advertised_options: Mapping[str, bool],
    source_argv: Sequence[str],
    failure: Mapping[str, Any],
) -> str:
    post = failure.get("server_post_readiness")
    if not isinstance(post, dict):
        return "insufficient_closed_evidence"
    if (
        "--sig-proxy=false" in source_argv
        and advertised_options == {
            "attach": True,
            "interactive": True,
            "sig_proxy": False,
        }
        and post.get("attachment_process") == "exited_nonzero"
        and post.get("attachment_stdin") == "open_after_delivery"
        and post.get("projection_valid") is True
        and post.get("status") == "created"
        and post.get("running") is False
    ):
        return "cli_option_surface_mismatch"
    if (
        advertised_options
        == {"attach": True, "interactive": True, "sig_proxy": True}
        and post.get("attachment_process") == "exited_nonzero"
        and post.get("status") == "created"
        and post.get("running") is False
    ):
        return "composite_start_attach_exited_while_oci_created"
    if post.get("status") == "exited" and post.get("running") is False:
        return "container_exited_after_start"
    if (
        post.get("status") == "running"
        and post.get("running") is True
        and failure.get("code") == "readiness_timeout"
    ):
        return "readiness_expired_while_running"
    return "insufficient_closed_evidence"


def build_evidence(
    *,
    contract: Mapping[str, Any],
    head: str,
    runner: Runner = _run_read_only,
) -> dict[str, Any]:
    version = runner(CLI_MANIFEST["docker_version"])
    start_help = runner(CLI_MANIFEST["docker_start_help"])
    if version.returncode != 0 or start_help.returncode != 0:
        raise DiagnosisError("read-only Docker metadata command failed")
    version_match = VERSION_RE.fullmatch(version.stdout.strip())
    if version_match is None:
        raise DiagnosisError("Docker version output is outside the closed form")
    advertised = {
        "attach": _advertises(start_help.stdout, "--attach"),
        "interactive": _advertises(start_help.stdout, "--interactive"),
        "sig_proxy": _advertises(start_help.stdout, "--sig-proxy"),
    }
    source_argv = extract_start_argv(HARNESS_PATH.read_text(encoding="utf-8"))
    failure = _load_json(
        ROOT
        / "orchestration"
        / "continuity"
        / "raisa-provider-free-check-in-relay-free-recovery-attempt-006"
        / "rehearsal-failure-evidence.json"
    )
    coordinate = classify_coordinate(
        advertised_options=advertised,
        source_argv=source_argv,
        failure=failure,
    )
    if coordinate != contract.get("expected_coordinate"):
        raise DiagnosisError("observed coordinate does not match frozen contract")
    post = failure["server_post_readiness"]
    evidence: dict[str, Any] = {
        "schema_version": (
            "emr4.check-in-start-attach-created-state-diagnosis-evidence.v1"
        ),
        "operation_id": OPERATION_ID,
        "result": contract["result"],
        "source_head": head,
        "input_bindings_verified": True,
        "cli_evidence": {
            "commands_executed": ["docker_version", "docker_start_help"],
            "docker_object_command_count": 0,
            "version_return_code": version.returncode,
            "start_help_return_code": start_help.returncode,
            "client_version": version_match.group("client"),
            "server_version": version_match.group("server"),
            "start_help_sha256": hashlib.sha256(
                start_help.stdout.encode("utf-8")
            ).hexdigest(),
            "advertised_options": advertised,
        },
        "source_coordinate": {
            "function": "_start_attached",
            "argv_profile": list(source_argv),
            "unsupported_options": [contract["expected_unsupported_option"]],
        },
        "attempt_006_projection": {
            "stage": failure["stage"],
            "code": failure["code"],
            "status": post["status"],
            "running": post["running"],
            "attachment_process": post["attachment_process"],
            "attachment_stdin": post["attachment_stdin"],
            "readiness_completed": False,
            "transaction_steps_started": False,
        },
        "coordinate": coordinate,
        "bounded_conclusion": (
            "docker_start_help_does_not_advertise_sig_proxy_but_the_exact_"
            "start_argv_supplies_it"
        ),
        "unresolved_causes": [],
        "repair": {
            "surface": contract["repair_surface"],
            "implemented": False,
            "attempt_007_authorized": False,
        },
        "closed_boundaries": {
            "docker_object_commands": 0,
            "postgresql_processes": 0,
            "sql_or_database_attempts": 0,
            "provider_requests": 0,
            "product_effects": 0,
            "ordinary_admission_releases": 0,
        },
    }
    schema = _load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator(schema).validate(evidence)
    return evidence


def check() -> None:
    head = _git_head()
    contract = _load_json(CONTRACT_PATH)
    _validate_contract(contract, head)
    schema = _load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)


def execute() -> None:
    if EVIDENCE_PATH.exists():
        raise DiagnosisError("diagnosis evidence already exists")
    head = _git_head()
    contract = _load_json(CONTRACT_PATH)
    _validate_contract(contract, head)
    evidence = build_evidence(contract=contract, head=head)
    with EVIDENCE_PATH.open("xb") as stream:
        stream.write(_canonical_bytes(evidence))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the read-only check-in start/attach failure diagnosis."
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
    except (DiagnosisError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        parser.exit(1, f"diagnosis failed closed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
