"""Run one pragmatic, traceable native-Harness EMR4 worker session.

This coordinator deliberately reuses the pinned rc.7 stock headless runner and
the accepted EMR4 broker.  It creates no new agent loop, runner, broker, guard,
or retry mechanism.  Its job is limited to preparing one sparse worktree,
materialising the accepted package, applying the minimal profile overlay,
running one natural multi-turn session, and reducing the raw result to
structural evidence for Sol review.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import queue
import secrets
import shutil
import subprocess
import threading
import time
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "raisa-native-harness-first-pragmatic-real-development-run-canonical-"
    "check-in-manifest-normalizer"
)
ATTEMPT_ID = "deepseek-native-manifest-normalizer-001"
ATTEMPT_ROOT = Path(
    "C:/Users/sarashera/EMR4-worktrees/deepseek-native-manifest-normalizer-001"
)
WORKSPACE = ATTEMPT_ROOT / "workspace"
HOME = ATTEMPT_ROOT / "home"
INSTALLATION = ATTEMPT_ROOT / "installation"
PREPARATION_PATH = ATTEMPT_ROOT / "preparation.json"
AUTHORITY_PATH = ATTEMPT_ROOT / "authority.json"
FORBIDDEN_PATH = ATTEMPT_ROOT / "forbidden-surfaces.json"
WORK_ORDER_PATH = ATTEMPT_ROOT / "work-order-v2.json"
COMMAND_MANIFEST_PATH = ATTEMPT_ROOT / "command-manifest.json"
NO_DATABASE_ADMISSION_PATH = ATTEMPT_ROOT / "provider-free-no-database-admission.json"
TERMINAL_PATH = ATTEMPT_ROOT / "occupied-terminal.json"
BROKER_PATH = REPO_ROOT / "scripts" / "ariadne_deepseek_native_harness_broker.mjs"
TRANSACTION_PATH = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-governance-clockwork"
    / "transaction.json"
)
PACKAGE_VERSION = "0.1.0-rc.7"
MODEL_ID = "deepseek-v4-flash"
TOOLS = ["edit", "glob", "read"]
OWNED_PATHS = [
    "app/services/appointment_check_in_environment_manifest.py",
    "tests/test_appointment_check_in_environment_manifest.py",
]
READ_ONLY_PACKET_PATHS = [
    "AGENTS.md",
    "docs/raisa-native-harness-first-pragmatic-real-development-run-canonical-check-in-manifest-normalizer-plan.md",
    "orchestration/continuity/raisa-native-harness-first-pragmatic-real-development-run-canonical-check-in-manifest-normalizer/contract.json",
    "orchestration/continuity/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture/environment-manifest.schema.json",
]
SPARSE_PATHS = READ_ONLY_PACKET_PATHS + OWNED_PATHS
WORKER_ENVIRONMENT_ALLOWLIST = [
    "PATH",
    "PATHEXT",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "WINDIR",
    "COMSPEC",
]
PROVIDER_ENVIRONMENT_NAMES = {
    "ANTHROPIC_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "DEEPSEEK_API_KEY",
    "GOOGLE_API_KEY",
    "OPENAI_API_KEY",
}


class PragmaticWorkerError(RuntimeError):
    """The bounded worker envelope failed closed."""


def canonical_bytes(value: Any, *, pretty: bool = False) -> bytes:
    if pretty:
        text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    else:
        text = json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    return (text + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value, pretty=True))


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise PragmaticWorkerError(f"json_object_required:{path.name}")
    return value


def run_checked(
    argv: list[str], *, cwd: Path = REPO_ROOT, timeout: int = 120
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        argv,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )
    if completed.returncode != 0:
        raise PragmaticWorkerError(f"command_failed:{argv[0]}:{completed.returncode}")
    return completed


def git(*args: str, cwd: Path = REPO_ROOT) -> str:
    return run_checked(["git", *args], cwd=cwd).stdout.strip()


def full_source(source: str) -> str:
    resolved = git("rev-parse", "--verify", f"{source}^{{commit}}")
    if len(resolved) != 40 or any(character not in "0123456789abcdef" for character in resolved):
        raise PragmaticWorkerError("source_not_full_git_object")
    if git("merge-base", "--is-ancestor", resolved, "HEAD") != "":
        raise PragmaticWorkerError("source_not_ancestor_of_head")
    return resolved


def profile_patch(port: int) -> bytes:
    workspace = json.dumps(str(WORKSPACE.resolve()))
    sessions = json.dumps(str((ATTEMPT_ROOT / "raw-sessions").resolve()))
    disabled = [
        "code-runtime",
        "session-telemetry-otel",
        "session-title-llm",
        "compaction-basic",
        "command-compact",
        "llm-pi-ai",
        "llm-retry",
        "tool-bash",
        "tool-pwsh",
        "tool-jobs",
        "tool-skill",
        "tool-goal",
        "tool-ralph",
        "tool-subagent",
        "tool-subagent-fork",
        "tool-subagent-control",
        "tool-subagent-list-agents",
        "tool-subagent-report",
        "tool-workflow",
        "tool-todo",
        "tool-web",
        "web-search-deepseek",
        "tool-str-replace-editor",
    ]
    rows = "".join(f"- id: {name}\n  disabled: true\n" for name in disabled)
    rows += f"""- id: session-persistence-jsonl
  config:
    root: {sessions}
    compression: none
- id: sandbox-policy
  config:
    mode: workspace-write
    workspaceRoot: {workspace}
- id: approval
  config:
    policy: never
- id: permission
  config:
    defaultPreset: emr4-bounded-worker
    presets:
      emr4-bounded-worker:
        sandbox: workspace-write
        approval: never
- id: agent-loop
  config:
    agents: []
    maxParallelToolCalls: 1
- id: llm-deepseek
  config:
    apiKeyEnv: DSH_EMR4_BROKER_TOKEN
    baseURL: http://127.0.0.1:{port}
    reasoningEffort: high
    maxTokens: 4096
    streamIdleTimeoutMs: 300000
    retryPolicy:
      mode: normal
      maxRetries: 0
      retryableCodes: [TRANSPORT]
      backoff:
        initialDelayMs: 1
        maxDelayMs: 1
        jitterRatio: 0
"""
    return rows.encode("utf-8")


def task_text(source: str) -> str:
    return f"""You are the DeepSeek implementation worker for one bounded, unmounted EMR4 source task at exact source {source}.

Read AGENTS.md completely, then read the frozen plan, machine contract, accepted schema, scaffold source, and focused test at these exact paths:
- {READ_ONLY_PACKET_PATHS[1]}
- {READ_ONLY_PACKET_PATHS[2]}
- {READ_ONLY_PACKET_PATHS[3]}
- {OWNED_PATHS[0]}
- {OWNED_PATHS[1]}

Implement the complete frozen closed_manifest_normalizer contract and focused tests. You may use only read, glob, and edit. You have no shell or test tool; Sol will run tests outside your session. Natural multi-turn reread and edit correction is allowed. Edit only these two exact files:
- {OWNED_PATHS[0]}
- {OWNED_PATHS[1]}

Do not edit AGENTS.md, plans, contracts, schemas, configuration, routes, API artifacts, or any other path. Do not read environment variables, .env, application configuration, credentials, secret stores, databases, network, current time, product data, or protected evidence from the implementation. Do not weaken the frozen denial precedence or move evaluator-owned freshness/admission meaning into the normalizer.

When the two files are complete, return a concise terminal summary naming them and the tests Sol should run. Do not claim tests ran inside this session."""


def _materialize_profile() -> dict[str, Any]:
    from scripts import (
        raisa_provider_free_check_in_native_harness_preset_mount_effective_tool_projection_rehearsal
        as projection,
    )

    package_root, copied = projection.materialize_accepted_node_modules(
        ATTEMPT_ROOT, projection.load_contract()
    )
    profile_dir = HOME / "profiles" / "headless"
    profile_dir.mkdir(parents=True)
    write_json(
        profile_dir / "package.json",
        {
            "name": "dsh-profile-headless",
            "private": True,
            "dependencies": {},
            "dsh": {
                "profile": {
                    "bundles": ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-headless"]
                }
            },
        },
    )
    (profile_dir / "pnpm-workspace.yaml").write_text(
        "packages:\n  - .\n\nnodeLinker: hoisted\nautoInstallPeers: false\n",
        encoding="utf-8",
        newline="\n",
    )
    (profile_dir / "cordis.patch.yml").write_bytes(profile_patch(43123))
    package = load_json(package_root / "package.json")
    if package.get("name") != "@deepseek-ai/dsh" or package.get("version") != PACKAGE_VERSION:
        raise PragmaticWorkerError("package_identity_mismatch")
    stock_runner = package_root.parent / "dsh-headless" / "lib" / "index.js"
    return {
        "package_root": package_root.as_posix(),
        "package_json_sha256": sha256_file(package_root / "package.json"),
        "stock_runner_sha256": sha256_file(stock_runner),
        "profile_template_sha256": sha256_bytes(profile_patch(43123)),
        "materialized_package_count": len(copied),
    }


def _prepare_command_boundary() -> tuple[dict[str, Any], dict[str, Any]]:
    from scripts.ariadne_evidence_gate import COMMAND_MANIFEST_SCHEMA_VERSION
    from scripts.ariadne_validation_runner import (
        validate_execution_manifest_with_admission,
    )

    python = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    manifest = {
        "schema_version": COMMAND_MANIFEST_SCHEMA_VERSION,
        "commands": [
            {
                "id": "PF_MANIFEST_NORMALIZER_SOL_VERIFICATION",
                "argv": [
                    str(python),
                    "-m",
                    "scripts.ariadne_provider_free_pytest",
                    "--repo-root",
                    str(REPO_ROOT),
                    "tests/test_appointment_check_in_environment_manifest.py",
                    "tests/test_api_spine_artifacts.py",
                ],
            }
        ],
    }
    admitted, admission = validate_execution_manifest_with_admission(
        manifest, repo_root=REPO_ROOT, require_provider_free=True
    )
    if admission is None or admission.get("status") != "passed":
        raise PragmaticWorkerError("provider_free_command_admission_failed")
    return admitted, admission


def prepare(source: str) -> dict[str, Any]:
    source = full_source(source)
    if ATTEMPT_ROOT.exists():
        raise PragmaticWorkerError("attempt_root_not_fresh")
    ATTEMPT_ROOT.parent.mkdir(parents=True, exist_ok=True)
    ATTEMPT_ROOT.mkdir()
    try:
        run_checked(
            ["git", "worktree", "add", "--detach", "--no-checkout", str(WORKSPACE), source]
        )
        run_checked(["git", "sparse-checkout", "init", "--no-cone"], cwd=WORKSPACE)
        run_checked(
            ["git", "sparse-checkout", "set", "--no-cone", "--", *SPARSE_PATHS],
            cwd=WORKSPACE,
        )
        run_checked(["git", "checkout", "--detach", source], cwd=WORKSPACE)
        if git("rev-parse", "HEAD", cwd=WORKSPACE) != source:
            raise PragmaticWorkerError("worktree_source_mismatch")
        for relative in READ_ONLY_PACKET_PATHS:
            path = WORKSPACE / relative
            if not path.is_file():
                raise PragmaticWorkerError(f"sparse_packet_missing:{relative}")
            path.chmod(0o444)
        profile = _materialize_profile()
        manifest, admission = _prepare_command_boundary()
        authority = {
            "operation_id": OPERATION_ID,
            "attempt_id": ATTEMPT_ID,
            "source_commit": source,
            "provider": "deepseek-official",
            "model": MODEL_ID,
            "reasoning_effort": "high",
            "maximum_output_tokens_per_request": 4096,
            "maximum_native_wall_clock_seconds": 900,
            "provider_spend_source": "existing_user_controlled_prepaid_balance",
            "broker_currency_cap_enforced": False,
            "maximum_parallel_tool_calls": 1,
            "automatic_retries": 0,
            "fallbacks": 0,
            "auxiliary_model_calls": 0,
            "allowed_tool_names": TOOLS,
            "owned_paths": OWNED_PATHS,
            "prompt_sha256": sha256_bytes(task_text(source).encode("utf-8")),
        }
        forbidden = {
            "forbidden_surfaces": [
                "second_worker_automatic_retry_or_silent_fallback",
                "shell_test_git_web_subagent_or_workflow_tool",
                "non_owned_path_edit",
                "environment_configuration_credential_secret_or_reference_resolution",
                "database_docker_route_api_client_product_runtime_or_product_data",
                "ordinary_practice_arrived_status_grammar_waiting_area_or_admission",
                "production_deployment_release_pages_or_protected_refs",
                "raw_prompt_response_reasoning_or_credential_retention",
            ]
        }
        transaction = load_json(TRANSACTION_PATH)
        journal = transaction.get("journal")
        if not isinstance(journal, list) or not journal:
            raise PragmaticWorkerError("clockwork_journal_missing")
        tip = journal[-1]
        if tip.get("sequence") != len(journal) or not isinstance(tip.get("event_sha256"), str):
            raise PragmaticWorkerError("clockwork_journal_invalid")
        write_json(AUTHORITY_PATH, authority)
        write_json(FORBIDDEN_PATH, forbidden)
        write_json(COMMAND_MANIFEST_PATH, manifest)
        write_json(NO_DATABASE_ADMISSION_PATH, admission)
        work_order = {
            "schema_version": "ariadne.deepseek_work_order.v2",
            "work_order_id": "wo-native-manifest-normalizer-001",
            "transaction_id": transaction["transaction_id"],
            "operation_id": OPERATION_ID,
            "lease_id": "lease-native-manifest-normalizer-001",
            "journal_id": tip["journal_id"],
            "source_commit": source,
            "authority_sha256": "sha256:" + sha256_bytes(canonical_bytes(authority).rstrip(b"\n")),
            "forbidden_surfaces_sha256": "sha256:" + sha256_bytes(canonical_bytes(forbidden).rstrip(b"\n")),
            "command_manifest_sha256": "sha256:" + sha256_bytes(canonical_bytes(manifest, pretty=True)),
            "provider_free_no_database_admission_sha256": "sha256:" + sha256_bytes(canonical_bytes(admission, pretty=True)),
            "branch": "detached-native-harness-worker",
            "worktree": WORKSPACE.resolve().as_posix(),
            "allowed_tool_names": TOOLS,
            "posture": "provider_free_shadow",
            "next_sequence": tip["sequence"] + 1,
            "previous_event_sha256": tip["event_sha256"],
        }
        write_json(WORK_ORDER_PATH, work_order)
        preparation = {
            "schema_version": "emr4.native_harness_pragmatic_worker_preparation.v1",
            "operation_id": OPERATION_ID,
            "attempt_id": ATTEMPT_ID,
            "status": "passed",
            "source_commit": source,
            "workspace": WORKSPACE.resolve().as_posix(),
            "owned_paths": OWNED_PATHS,
            "read_only_packet_paths": READ_ONLY_PACKET_PATHS,
            "profile": profile,
            "broker_sha256": sha256_file(BROKER_PATH),
            "work_order_sha256": sha256_bytes(canonical_bytes(work_order).rstrip(b"\n")),
            "prompt_sha256": authority["prompt_sha256"],
            "provider_calls_before_dispatch": 0,
            "worker_sessions_before_dispatch": 0,
        }
        write_json(PREPARATION_PATH, preparation)
        return preparation
    except Exception:
        if WORKSPACE.exists():
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(WORKSPACE)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
            )
        if ATTEMPT_ROOT.exists():
            shutil.rmtree(ATTEMPT_ROOT)
        raise


def _worker_environment(port: int, token: str) -> dict[str, str]:
    environment = {
        name: os.environ[name]
        for name in WORKER_ENVIRONMENT_ALLOWLIST
        if name in os.environ
    }
    environment.update(
        {
            "DSH_HOME": str(HOME),
            "DSH_CWD": str(WORKSPACE),
            "DSH_PERMISSION_MODE": "workspace-write",
            "DSH_TOOLS_MODE": "native",
            "DSH_TELEMETRY_DISABLED": "1",
            "DSH_EMR4_BROKER_TOKEN": token,
            "NO_PROXY": f"127.0.0.1,localhost,127.0.0.1:{port}",
            "NPM_CONFIG_OFFLINE": "true",
            "NPM_CONFIG_AUDIT": "false",
            "NPM_CONFIG_FUND": "false",
            "NPM_CONFIG_IGNORE_SCRIPTS": "true",
        }
    )
    if PROVIDER_ENVIRONMENT_NAMES.intersection(environment):
        raise PragmaticWorkerError("worker_provider_credential_present")
    return environment


def _broker_environment(token: str) -> dict[str, str]:
    provider_key = os.environ.get("DEEPSEEK_API_KEY")
    if not provider_key:
        raise PragmaticWorkerError("provider_key_missing")
    work_order = load_json(WORK_ORDER_PATH)
    environment = dict(os.environ)
    environment.update(
        {
            "EMR4_BROKER_TEST_MODE": "1",
            "EMR4_BROKER_LISTEN_HOST": "127.0.0.1",
            "EMR4_BROKER_LISTEN_PORT": "0",
            "EMR4_BROKER_TEST_UPSTREAM_URL": "https://api.deepseek.com/chat/completions",
            "DSH_EMR4_BROKER_TOKEN": token,
            "DEEPSEEK_API_KEY": provider_key,
            "EMR4_BROKER_WORK_ORDER_PATH": str(WORK_ORDER_PATH),
            "EMR4_BROKER_WORK_ORDER_SHA256": "sha256:"
            + sha256_bytes(canonical_bytes(work_order).rstrip(b"\n")),
            "EMR4_BROKER_COMMAND_MANIFEST_PATH": str(COMMAND_MANIFEST_PATH),
            "EMR4_BROKER_NO_DATABASE_ADMISSION_PATH": str(NO_DATABASE_ADMISSION_PATH),
        }
    )
    environment.pop("EMR4_BROKER_MAX_PROVIDER_CALLS", None)
    return environment


def _collect_lines(
    stream: Any, channel: queue.Queue[str], retained: list[str]
) -> None:
    for line in stream:
        retained.append(line)
        channel.put(line)


def _terminate(process: subprocess.Popen[Any] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def _safe_terminal_text(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"bytes": 0, "sha256": sha256_bytes(b""), "terminal_line": None}
    payload = path.read_bytes()
    text = payload.decode("utf-8", errors="replace")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    terminal = lines[-1][:1000] if lines else None
    return {"bytes": len(payload), "sha256": sha256_bytes(payload), "terminal_line": terminal}


def _session_reading() -> dict[str, Any]:
    files = sorted((ATTEMPT_ROOT / "raw-sessions").rglob("session.jsonl"))
    if len(files) != 1:
        return {
            "session_file_count": len(files),
            "trace_complete": False,
            "request_count": 0,
            "tool_sequence": [],
            "tool_result_count": 0,
            "usage_rows": [],
            "terminal": None,
        }
    path = files[0]
    request_count = 0
    tool_sequence: list[dict[str, Any]] = []
    tool_result_count = 0
    usage_rows: list[dict[str, int]] = []
    terminal: dict[str, Any] | None = None
    event_count = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw:
            continue
        row = json.loads(raw)
        if not isinstance(row, dict):
            continue
        event_count += 1
        event_type = row.get("type")
        data = row.get("data") if isinstance(row.get("data"), dict) else {}
        if event_type == "request/header":
            request_count += 1
        elif event_type == "tool/call":
            name = data.get("name")
            tool_sequence.append(
                {
                    "ordinal": len(tool_sequence) + 1,
                    "name": name if isinstance(name, str) else "unknown",
                }
            )
        elif event_type == "tool/result":
            tool_result_count += 1
        elif event_type == "turn/end":
            reason = data.get("reason") if isinstance(data.get("reason"), dict) else {}
            error = reason.get("error") if isinstance(reason.get("error"), dict) else {}
            terminal = {
                "kind": reason.get("kind"),
                "code": error.get("code"),
                "status": error.get("status"),
            }
        usage = data.get("usage") if isinstance(data.get("usage"), dict) else None
        if usage is not None:
            selected: dict[str, int] = {}
            for key in (
                "inputTokens",
                "cacheReadTokens",
                "outputTokens",
                "reasoningTokens",
                "input_tokens",
                "cache_read_tokens",
                "output_tokens",
                "reasoning_tokens",
            ):
                value = usage.get(key)
                if isinstance(value, int) and value >= 0:
                    selected[key] = value
            if selected:
                usage_rows.append(selected)
    return {
        "session_file_count": 1,
        "session_bytes": path.stat().st_size,
        "session_sha256": sha256_file(path),
        "event_count": event_count,
        "trace_complete": terminal is not None,
        "request_count": request_count,
        "tool_sequence": tool_sequence,
        "tool_result_count": tool_result_count,
        "usage_rows": usage_rows,
        "terminal": terminal,
    }


def execute() -> dict[str, Any]:
    preparation = load_json(PREPARATION_PATH)
    source = preparation.get("source_commit")
    if source != git("rev-parse", "HEAD", cwd=WORKSPACE):
        raise PragmaticWorkerError("prepared_source_drift")
    if git("status", "--porcelain=v1", "--untracked-files=all", cwd=WORKSPACE) != "":
        raise PragmaticWorkerError("prepared_worktree_not_clean")
    token = secrets.token_urlsafe(32)
    broker: subprocess.Popen[str] | None = None
    worker: subprocess.Popen[bytes] | None = None
    broker_lines: list[str] = []
    broker_queue: queue.Queue[str] = queue.Queue()
    broker_thread: threading.Thread | None = None
    broker_stderr_path = ATTEMPT_ROOT / "broker-stderr.raw"
    worker_stdout_path = ATTEMPT_ROOT / "worker-stdout.raw"
    worker_stderr_path = ATTEMPT_ROOT / "worker-stderr.raw"
    started_at = datetime.now(timezone.utc)
    started = time.monotonic()
    timed_out = False
    exit_code: int | None = None
    broker_ready: dict[str, Any] = {}
    try:
        with broker_stderr_path.open("wb") as broker_stderr:
            broker = subprocess.Popen(
                ["node", str(BROKER_PATH)],
                cwd=REPO_ROOT,
                env=_broker_environment(token),
                stdout=subprocess.PIPE,
                stderr=broker_stderr,
                text=True,
                encoding="utf-8",
            )
            if broker.stdout is None:
                raise PragmaticWorkerError("broker_stdout_missing")
            broker_thread = threading.Thread(
                target=_collect_lines,
                args=(broker.stdout, broker_queue, broker_lines),
                daemon=True,
            )
            broker_thread.start()
            try:
                broker_ready = json.loads(broker_queue.get(timeout=15))
            except (queue.Empty, json.JSONDecodeError) as error:
                raise PragmaticWorkerError("broker_ready_invalid") from error
            if (
                broker_ready.get("event") != "broker-ready"
                or broker_ready.get("allowed_tool_names") != TOOLS
                or broker_ready.get("maximum_provider_calls") is not None
                or broker_ready.get("model_id") != MODEL_ID
            ):
                raise PragmaticWorkerError("broker_ready_contract_mismatch")
            port = broker_ready.get("listen_port")
            if not isinstance(port, int) or port < 1 or port > 65535:
                raise PragmaticWorkerError("broker_port_invalid")
            profile_path = HOME / "profiles" / "headless" / "cordis.patch.yml"
            profile_path.write_bytes(profile_patch(port))
            dsh_bin = INSTALLATION / "node_modules" / "@deepseek-ai" / "dsh" / "lib" / "bin.js"
            with worker_stdout_path.open("wb") as stdout, worker_stderr_path.open("wb") as stderr:
                worker = subprocess.Popen(
                    [
                        "node",
                        "--expose-internals",
                        str(dsh_bin),
                        "--profile",
                        "headless",
                        task_text(str(source)),
                    ],
                    cwd=WORKSPACE,
                    env=_worker_environment(port, token),
                    stdout=stdout,
                    stderr=stderr,
                )
                try:
                    exit_code = worker.wait(timeout=900)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    _terminate(worker)
                    exit_code = worker.returncode
    finally:
        _terminate(worker)
        _terminate(broker)
        if broker_thread is not None:
            broker_thread.join(timeout=10)
    ended_at = datetime.now(timezone.utc)
    broker_events: list[dict[str, Any]] = []
    for line in broker_lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            broker_events.append(value)
    changed_paths = [
        line
        for line in git("diff", "--name-only", "--", *OWNED_PATHS, cwd=WORKSPACE).splitlines()
        if line
    ]
    all_changed = [
        line
        for line in git("status", "--porcelain=v1", "--untracked-files=all", cwd=WORKSPACE).splitlines()
        if line
    ]
    terminal = {
        "schema_version": "emr4.native_harness_pragmatic_worker_terminal.v1",
        "operation_id": OPERATION_ID,
        "attempt_id": ATTEMPT_ID,
        "source_commit": source,
        "started_at": started_at.isoformat().replace("+00:00", "Z"),
        "ended_at": ended_at.isoformat().replace("+00:00", "Z"),
        "duration_ms": round((time.monotonic() - started) * 1000),
        "process": {
            "exit_code": exit_code,
            "timed_out": timed_out,
            "native_process_count": 1,
            "automatic_retries": 0,
            "fallbacks": 0,
            "auxiliary_model_calls": 0,
        },
        "broker": {
            "ready": broker_ready.get("event") == "broker-ready",
            "provider_call_started": sum(row.get("event") == "provider-call-started" for row in broker_events),
            "provider_call_completed": sum(row.get("event") == "provider-call-completed" for row in broker_events),
            "provider_call_failed": sum(row.get("event") == "provider-call-failed" for row in broker_events),
            "request_rejected": sum(row.get("event") == "broker-request-rejected" for row in broker_events),
            "maximum_provider_calls": None,
            "clock_sequence_first": broker_events[0].get("clock_sequence") if broker_events else None,
            "clock_sequence_last": broker_events[-1].get("clock_sequence") if broker_events else None,
        },
        "session": _session_reading(),
        "candidate": {
            "changed_paths": changed_paths,
            "status_rows": all_changed,
            "scope_integrity": all(
                any(row.endswith(path) for path in OWNED_PATHS) for row in all_changed
            ) and all(any(row.endswith(path) for row in all_changed) for path in changed_paths),
        },
        "streams": {
            "stdout": _safe_terminal_text(worker_stdout_path),
            "stderr": _safe_terminal_text(worker_stderr_path),
            "broker_stderr": _safe_terminal_text(broker_stderr_path),
        },
        "cleanup": {
            "broker_absent": broker is None or broker.poll() is not None,
            "worker_absent": worker is None or worker.poll() is not None,
            "raw_material_retained_pending_sol_review": True,
            "attempt_root_absent": False,
        },
    }
    write_json(TERMINAL_PATH, terminal)
    return terminal


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", metavar="SOURCE")
    group.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        result = prepare(args.prepare) if args.prepare else execute()
    except (PragmaticWorkerError, OSError, subprocess.SubprocessError, ValueError) as error:
        print(json.dumps({"status": "failed", "reason": str(error)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
