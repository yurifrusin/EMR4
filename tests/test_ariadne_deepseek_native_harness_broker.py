from __future__ import annotations

import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from orchestration_harness.transactional_closeout import (
    sha256 as canonical_sha256,
    validate_broker_events,
)
from orchestration_harness.provider_free_no_database_admission import (
    canonical_sha256 as boundary_sha256,
)
from scripts.ariadne_evidence_gate import COMMAND_MANIFEST_SCHEMA_VERSION
from scripts.ariadne_validation_runner import validate_execution_manifest_with_admission


ROOT = Path(__file__).resolve().parents[1]
BROKER = ROOT / "scripts" / "ariadne_deepseek_native_harness_broker.mjs"
BROKER_TOKEN = "synthetic-broker-capability-token-0123456789"
PROVIDER_KEY = "synthetic-provider-key-not-a-real-secret-987654321"
SESSION_ID = "synthetic-session-0001"
WORK_ORDER = {
    "schema_version": "ariadne.deepseek_work_order.v1",
    "work_order_id": "wo-synthetic-clockwork",
    "transaction_id": "txn-synthetic-clockwork",
    "operation_id": "synthetic-clockwork-rehearsal",
    "lease_id": "lease-synthetic-clockwork",
    "journal_id": "journal-synthetic-clockwork",
    "source_commit": "1" * 40,
    "authority_sha256": "sha256:" + "2" * 64,
    "forbidden_surfaces_sha256": "sha256:" + "3" * 64,
    "branch": "codex/synthetic-clockwork",
    "worktree": "C:/synthetic/emr4",
    "allowed_tool_names": ["edit", "glob", "read"],
    "posture": "provider_free_shadow",
    "next_sequence": 7,
    "previous_event_sha256": "sha256:" + "4" * 64,
}
COMMAND_MANIFEST = {
    "schema_version": COMMAND_MANIFEST_SCHEMA_VERSION,
    "commands": [
        {
            "id": "PF",
            "argv": [
                os.fspath(ROOT / ".venv" / "Scripts" / "python.exe"),
                "-m",
                "scripts.ariadne_provider_free_pytest",
                "--repo-root",
                str(ROOT),
                "tests/test_ariadne_provider_free_pytest.py",
            ],
        }
    ],
}
_ADMITTED_COMMAND_MANIFEST, NO_DATABASE_ADMISSION = (
    validate_execution_manifest_with_admission(
        COMMAND_MANIFEST, repo_root=ROOT, require_provider_free=True
    )
)
assert NO_DATABASE_ADMISSION is not None
WORK_ORDER_V2 = {
    **WORK_ORDER,
    "schema_version": "ariadne.deepseek_work_order.v2",
    "command_manifest_sha256": boundary_sha256(_ADMITTED_COMMAND_MANIFEST),
    "provider_free_no_database_admission_sha256": boundary_sha256(
        NO_DATABASE_ADMISSION
    ),
}


class _UpstreamHandler(BaseHTTPRequestHandler):
    records: queue.Queue[dict] = queue.Queue()
    release_response = threading.Event()

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers["content-length"])
        body = self.rfile.read(length)
        self.records.put(
            {
                "path": self.path,
                "authorization": self.headers.get("authorization"),
                "harness_session_id": self.headers.get(
                    "x-deepseek-harness-session-id"
                ),
                "body": json.loads(body),
            }
        )
        assert self.release_response.wait(timeout=10)
        payload = (
            'data: {"choices":[{"delta":{"content":"ok"}}]}\n\n'
            "data: [DONE]\n\n"
        ).encode()
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, _format: str, *_args: object) -> None:
        return


@pytest.fixture
def broker_process(
    request: pytest.FixtureRequest, tmp_path: Path
) -> tuple[subprocess.Popen[str], int, queue.Queue[dict]]:
    while not _UpstreamHandler.records.empty():
        _UpstreamHandler.records.get_nowait()
    _UpstreamHandler.release_response.set()
    upstream = ThreadingHTTPServer(("127.0.0.1", 0), _UpstreamHandler)
    upstream_thread = threading.Thread(target=upstream.serve_forever, daemon=True)
    upstream_thread.start()

    env = {
        **os.environ,
        "EMR4_BROKER_TEST_MODE": "1",
        "EMR4_BROKER_LISTEN_HOST": "127.0.0.1",
        "EMR4_BROKER_LISTEN_PORT": "0",
        "EMR4_BROKER_TEST_UPSTREAM_URL": (
            f"http://127.0.0.1:{upstream.server_port}/chat/completions"
        ),
        "DSH_EMR4_BROKER_TOKEN": BROKER_TOKEN,
        "DEEPSEEK_API_KEY": PROVIDER_KEY,
    }
    selected = getattr(request, "param", None)
    provider_call_allowance: int | None = None
    if isinstance(selected, tuple):
        selected_work_order, provider_call_allowance = selected
    else:
        selected_work_order = selected
    if provider_call_allowance is not None:
        env["EMR4_BROKER_MAX_PROVIDER_CALLS"] = str(provider_call_allowance)
    if selected_work_order is not None:
        work_order_path = tmp_path / "work-order.json"
        work_order_path.write_text(json.dumps(selected_work_order), encoding="utf-8")
        env["EMR4_BROKER_WORK_ORDER_PATH"] = str(work_order_path)
        env["EMR4_BROKER_WORK_ORDER_SHA256"] = canonical_sha256(selected_work_order)
        if selected_work_order["schema_version"] == "ariadne.deepseek_work_order.v1":
            env["EMR4_BROKER_ALLOW_LEGACY_WORK_ORDER_V1"] = "1"
        else:
            command_manifest_path = tmp_path / "command-manifest.json"
            command_manifest_path.write_text(
                json.dumps(_ADMITTED_COMMAND_MANIFEST), encoding="utf-8"
            )
            admission_path = tmp_path / "no-database-admission.json"
            admission_path.write_text(
                json.dumps(NO_DATABASE_ADMISSION), encoding="utf-8"
            )
            env["EMR4_BROKER_COMMAND_MANIFEST_PATH"] = str(command_manifest_path)
            env["EMR4_BROKER_NO_DATABASE_ADMISSION_PATH"] = str(admission_path)
    process = subprocess.Popen(
        ["node", str(BROKER)],
        cwd=ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdout is not None
    ready = json.loads(process.stdout.readline())
    assert ready["event"] == "broker-ready"
    assert ready["provider_call_budget"] == (
        "none_beyond_process_wall_clock_and_prepaid_balance"
    )

    events: queue.Queue[dict] = queue.Queue()
    events.put(ready)

    def collect() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            events.put(json.loads(line))

    collector = threading.Thread(target=collect, daemon=True)
    collector.start()
    try:
        yield process, ready["listen_port"], events
    finally:
        _UpstreamHandler.release_response.set()
        process.terminate()
        process.wait(timeout=10)
        upstream.shutdown()
        upstream.server_close()
        upstream_thread.join(timeout=10)
        collector.join(timeout=10)


def _payload(*, tool_names: tuple[str, ...] = ("read", "glob", "edit")) -> bytes:
    return json.dumps(
        {
            "model": "deepseek-v4-flash",
            "stream": True,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": "authored synthetic test"}],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": f"synthetic {name}",
                        "parameters": {"type": "object", "properties": {}},
                    },
                }
                for name in tool_names
            ],
        },
        separators=(",", ":"),
    ).encode()


def _request(
    port: int,
    *,
    token: str = BROKER_TOKEN,
    session_id: str = SESSION_ID,
    tool_names: tuple[str, ...] = ("read", "glob", "edit"),
) -> tuple[int, bytes]:
    request = Request(
        f"http://127.0.0.1:{port}/chat/completions",
        data=_payload(tool_names=tool_names),
        method="POST",
        headers={
            "authorization": f"Bearer {token}",
            "content-type": "application/json",
            "x-deepseek-harness-session-id": session_id,
        },
    )
    try:
        with urlopen(request, timeout=10) as response:  # noqa: S310
            return response.status, response.read()
    except HTTPError as error:
        return error.code, error.read()


def _wait_for_event(events: queue.Queue[dict], event_type: str) -> dict:
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        event = events.get(timeout=max(deadline - time.monotonic(), 0.01))
        if event["event"] == event_type:
            return event
    raise AssertionError(f"event not observed: {event_type}")


def test_broker_replaces_capability_with_provider_key_and_streams_metadata(
    broker_process: tuple[subprocess.Popen[str], int, queue.Queue[dict]],
) -> None:
    process, port, events = broker_process
    status, response = _request(port)

    assert process.poll() is None
    assert status == 200
    assert b"data: [DONE]" in response
    upstream = _UpstreamHandler.records.get(timeout=5)
    assert upstream["path"] == "/chat/completions"
    assert upstream["authorization"] == f"Bearer {PROVIDER_KEY}"
    assert upstream["harness_session_id"] is None
    assert BROKER_TOKEN not in json.dumps(upstream)
    assert upstream["body"]["model"] == "deepseek-v4-flash"

    started = _wait_for_event(events, "provider-call-started")
    completed = _wait_for_event(events, "provider-call-completed")
    assert started["provider_call_ordinal"] == 1
    assert started["declared_tool_names"] == ["edit", "glob", "read"]
    assert started["maximum_output_tokens"] == 4096
    assert started["session_id_sha256"].startswith("sha256:")
    assert completed["provider_call_ordinal"] == 1
    assert completed["provider_status"] == 200
    retained = json.dumps([started, completed])
    assert BROKER_TOKEN not in retained
    assert PROVIDER_KEY not in retained


def test_broker_rejects_wrong_token_and_nonallowlisted_tool_without_upstream_call(
    broker_process: tuple[subprocess.Popen[str], int, queue.Queue[dict]],
) -> None:
    _process, port, events = broker_process

    wrong_status, wrong_body = _request(port, token="wrong-token")
    tool_status, tool_body = _request(port, tool_names=("read", "pwsh"))

    assert wrong_status == 401
    assert b"broker-authentication-failed" in wrong_body
    assert tool_status == 400
    assert b"tool-not-allowlisted" in tool_body
    assert _UpstreamHandler.records.empty()
    reasons = {
        _wait_for_event(events, "broker-request-rejected")["reason_code"],
        _wait_for_event(events, "broker-request-rejected")["reason_code"],
    }
    assert reasons == {"broker-authentication-failed", "tool-not-allowlisted"}


def test_broker_binds_one_session_without_imposing_request_count_budget(
    broker_process: tuple[subprocess.Popen[str], int, queue.Queue[dict]],
) -> None:
    _process, port, events = broker_process

    first_status, _ = _request(port)
    second_status, _ = _request(port)
    drift_status, drift_body = _request(port, session_id="synthetic-session-0002")

    assert first_status == second_status == 200
    assert drift_status == 409
    assert b"session-binding-mismatch" in drift_body
    assert _UpstreamHandler.records.qsize() == 2
    completions = [
        _wait_for_event(events, "provider-call-completed"),
        _wait_for_event(events, "provider-call-completed"),
    ]
    assert [event["provider_call_ordinal"] for event in completions] == [1, 2]
    rejected = _wait_for_event(events, "broker-request-rejected")
    assert rejected["reason_code"] == "session-binding-mismatch"


@pytest.mark.parametrize("broker_process", [(None, 1)], indirect=True)
def test_broker_optional_one_request_allowance_rejects_ordinal_two_before_upstream(
    broker_process: tuple[subprocess.Popen[str], int, queue.Queue[dict]],
) -> None:
    _process, port, events = broker_process
    ready = _wait_for_event(events, "broker-ready")
    assert ready["maximum_provider_calls"] == 1

    first_status, _ = _request(port)
    second_status, second_body = _request(port)

    assert first_status == 200
    assert second_status == 429
    assert b"provider-call-allowance-exhausted" in second_body
    assert _wait_for_event(events, "provider-call-completed")[
        "provider_call_ordinal"
    ] == 1
    rejected = _wait_for_event(events, "broker-request-rejected")
    assert rejected["reason_code"] == "provider-call-allowance-exhausted"
    assert rejected["provider_call_count"] == 1


def test_broker_rejects_overlapping_provider_call(
    broker_process: tuple[subprocess.Popen[str], int, queue.Queue[dict]],
) -> None:
    _process, port, events = broker_process
    _UpstreamHandler.release_response.clear()
    first_result: queue.Queue[tuple[int, bytes]] = queue.Queue()
    first_thread = threading.Thread(
        target=lambda: first_result.put(_request(port)),
        daemon=True,
    )
    first_thread.start()

    upstream = _UpstreamHandler.records.get(timeout=5)
    assert upstream["body"]["model"] == "deepseek-v4-flash"
    overlapping_status, overlapping_body = _request(port)

    assert overlapping_status == 409
    assert b"concurrent-provider-call-forbidden" in overlapping_body
    assert _UpstreamHandler.records.empty()
    rejected = _wait_for_event(events, "broker-request-rejected")
    assert rejected["reason_code"] == "concurrent-provider-call-forbidden"

    _UpstreamHandler.release_response.set()
    first_thread.join(timeout=10)
    assert not first_thread.is_alive()
    assert first_result.get(timeout=1)[0] == 200


@pytest.mark.parametrize("broker_process", [WORK_ORDER], indirect=True)
def test_broker_continues_the_work_order_clock_without_secret_leakage(
    broker_process: tuple[subprocess.Popen[str], int, queue.Queue[dict]],
) -> None:
    _process, port, events = broker_process
    status, _response = _request(port)
    assert status == 200
    observed = [
        _wait_for_event(events, event_type)
        for event_type in (
            "broker-ready",
            "provider-call-started",
            "provider-response-started",
            "provider-call-completed",
        )
    ]
    validate_broker_events(WORK_ORDER, observed)
    assert [event["clock_sequence"] for event in observed] == [7, 8, 9, 10]
    assert all(event["work_order_id"] == WORK_ORDER["work_order_id"] for event in observed)
    retained = json.dumps(observed)
    assert BROKER_TOKEN not in retained
    assert PROVIDER_KEY not in retained


@pytest.mark.parametrize("broker_process", [WORK_ORDER_V2], indirect=True)
def test_broker_v2_validates_command_and_no_database_artifacts_before_ready(
    broker_process: tuple[subprocess.Popen[str], int, queue.Queue[dict]],
) -> None:
    _process, port, events = broker_process
    status, _response = _request(port)
    assert status == 200
    observed = [
        _wait_for_event(events, event_type)
        for event_type in (
            "broker-ready",
            "provider-call-started",
            "provider-response-started",
            "provider-call-completed",
        )
    ]
    validate_broker_events(WORK_ORDER_V2, observed)


def test_broker_rejects_unbound_v1_and_mutated_v2_artifact_before_ready(
    tmp_path: Path,
) -> None:
    cases: list[tuple[dict, dict | None, bool]] = [
        (WORK_ORDER, None, False),
        (
            WORK_ORDER_V2,
            {**NO_DATABASE_ADMISSION, "status": "revision_required"},
            True,
        ),
    ]
    for index, (order, admission, include_boundary) in enumerate(cases):
        work_order_path = tmp_path / f"work-order-boundary-{index}.json"
        work_order_path.write_text(json.dumps(order), encoding="utf-8")
        env = {
            **os.environ,
            "EMR4_BROKER_TEST_MODE": "1",
            "EMR4_BROKER_LISTEN_PORT": "0",
            "EMR4_BROKER_TEST_UPSTREAM_URL": "http://127.0.0.1:1/chat/completions",
            "DSH_EMR4_BROKER_TOKEN": BROKER_TOKEN,
            "DEEPSEEK_API_KEY": PROVIDER_KEY,
            "EMR4_BROKER_WORK_ORDER_PATH": str(work_order_path),
            "EMR4_BROKER_WORK_ORDER_SHA256": canonical_sha256(order),
        }
        if include_boundary:
            manifest_path = tmp_path / f"command-manifest-{index}.json"
            manifest_path.write_text(json.dumps(_ADMITTED_COMMAND_MANIFEST), encoding="utf-8")
            admission_path = tmp_path / f"admission-{index}.json"
            admission_path.write_text(json.dumps(admission), encoding="utf-8")
            env["EMR4_BROKER_COMMAND_MANIFEST_PATH"] = str(manifest_path)
            env["EMR4_BROKER_NO_DATABASE_ADMISSION_PATH"] = str(admission_path)
        result = subprocess.run(
            ["node", str(BROKER)],
            cwd=ROOT,
            env=env,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=10,
            check=False,
        )
        assert result.returncode == 2
        event = json.loads(result.stdout)
        assert event["event"] == "broker-start-rejected"
        assert event["reason_code"] == "work-order-invalid"


def test_broker_rejects_malformed_or_digest_drifted_work_order_before_io(
    tmp_path: Path,
) -> None:
    malformed = {**WORK_ORDER, "source_commit": "1234567"}
    for index, (payload, digest) in enumerate(
        ((malformed, canonical_sha256(malformed)), (WORK_ORDER, "sha256:" + "0" * 64))
    ):
        path = tmp_path / f"rejected-work-order-{index}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        env = {
            **os.environ,
            "EMR4_BROKER_TEST_MODE": "1",
            "EMR4_BROKER_LISTEN_PORT": "0",
            "EMR4_BROKER_TEST_UPSTREAM_URL": "http://127.0.0.1:1/chat/completions",
            "DSH_EMR4_BROKER_TOKEN": BROKER_TOKEN,
            "DEEPSEEK_API_KEY": PROVIDER_KEY,
            "EMR4_BROKER_WORK_ORDER_PATH": str(path),
            "EMR4_BROKER_WORK_ORDER_SHA256": digest,
        }
        result = subprocess.run(
            ["node", str(BROKER)], cwd=ROOT, env=env, text=True,
            encoding="utf-8", capture_output=True, timeout=10, check=False,
        )
        assert result.returncode == 2
        assert json.loads(result.stdout)["reason_code"] == "work-order-invalid"
