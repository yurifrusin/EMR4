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


ROOT = Path(__file__).resolve().parents[1]
BROKER = ROOT / "scripts" / "ariadne_deepseek_native_harness_broker.mjs"
BROKER_TOKEN = "synthetic-broker-capability-token-0123456789"
PROVIDER_KEY = "synthetic-provider-key-not-a-real-secret-987654321"
SESSION_ID = "synthetic-session-0001"


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
def broker_process() -> tuple[subprocess.Popen[str], int, queue.Queue[dict]]:
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
