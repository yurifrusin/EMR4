from __future__ import annotations

import importlib
import json
from pathlib import Path
import sys

from scripts import ariadne_vertex_sydney_gemini_25_cell as cell
from scripts import ariadne_vertex_sydney_gemini_25_launcher as launcher
from scripts import ariadne_vertex_sydney_gemini_25_rehearsal as rehearsal


ROOT = Path(__file__).resolve().parents[1]


def test_relay_has_exact_cell_visible_network_alias() -> None:
    plan = launcher.build_plan()
    command = plan["docker_commands"]["create_relay"]
    alias_index = command.index("--network-alias")
    assert command[alias_index + 1] == "broker"


def test_cell_is_created_and_inspected_before_start() -> None:
    plan = launcher.build_plan()
    assert plan["docker_commands"]["create_cell"][:2] == ["docker", "create"]
    assert plan["docker_commands"]["start_cell"] == [
        "docker",
        "start",
        "--attach",
        launcher.CELL_CONTAINER,
    ]


def test_cell_and_relay_have_hard_resource_bounds() -> None:
    plan = launcher.build_plan()
    for name, memory in (("create_cell", "128m"), ("create_relay", "64m")):
        command = plan["docker_commands"][name]
        assert command[command.index("--memory") + 1] == memory
        assert command[command.index("--memory-swap") + 1] == memory
        assert command[command.index("--ulimit") + 1] == "nofile=64:64"
        assert command[command.index("--cap-drop") + 1] == "ALL"
        assert (
            command[command.index("--security-opt") + 1]
            == "no-new-privileges=true"
        )


def test_broker_child_environment_allowlist_contains_no_auth_variable() -> None:
    assert rehearsal.BROKER_ENVIRONMENT_ALLOWLIST == tuple(
        sorted(rehearsal.BROKER_ENVIRONMENT_ALLOWLIST)
    )
    assert not (
        set(rehearsal.BROKER_ENVIRONMENT_ALLOWLIST)
        & rehearsal.CELL_CREDENTIAL_ENVIRONMENT_NAMES
    )


def test_rehearsal_schema_is_strict_at_top_level() -> None:
    schema_path = (
        ROOT
        / "orchestration"
        / "continuity"
        / "ariadne-vertex-sydney-gemini-25"
        / "rehearsal-evidence.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert schema["properties"]["fallback_performed"] == {"const": False}
    assert schema["properties"]["attempt_id"]["enum"] == [
        "gemini-25-primary-001",
        "gemini-25-repair-dry-run-001",
        "gemini-25-repair-dry-run-002",
        "gemini-25-repair-dry-run-003",
        "gemini-25-repair-001",
        "gemini-25-repair-002",
    ]
    assert schema["properties"]["ledger_id"]["enum"] == [
        "gemini-25-primary-ledger-001",
        "gemini-25-repair-dry-run-ledger-001",
        "gemini-25-repair-dry-run-ledger-002",
        "gemini-25-repair-dry-run-ledger-003",
        "gemini-25-repair-ledger-001",
        "gemini-25-repair-ledger-002",
    ]


def test_provider_blocked_launch_plan_remains_exact() -> None:
    assert launcher.check_committed() == launcher.build_plan()


def test_repair_launch_plans_bind_only_the_two_distinct_requests() -> None:
    for request_name in (
        "repair-dry-run-cell-request.json",
        "repair-occupied-cell-request.json",
        "repair-dry-run-002-cell-request.json",
        "repair-dry-run-003-cell-request.json",
        "repair-occupied-002-cell-request.json",
    ):
        source = (
            "orchestration/continuity/"
            "ariadne-vertex-sydney-gemini-25/"
            f"{request_name}"
        )
        plan = launcher.build_plan(source)
        assert launcher.validate_plan(plan) == []
        request_entry = plan["build_context"]["files"][3]
        assert request_entry == {
            "source": source,
            "target": "cell-request.json",
        }


def test_cell_retries_only_preconnect_relay_refusal(monkeypatch) -> None:
    attempts = []
    response = object()

    class FakeConnection:
        def __init__(self, *_args, **_kwargs) -> None:
            attempts.append(self)

        def request(self, *_args, **_kwargs) -> None:
            if len(attempts) == 1:
                raise ConnectionRefusedError

        def getresponse(self):
            return response

        def close(self) -> None:
            return

    monkeypatch.setattr(cell.http.client, "HTTPConnection", FakeConnection)
    monkeypatch.setattr(cell.time, "sleep", lambda _seconds: None)

    assert cell._post_to_relay(b"{}") is response
    assert len(attempts) == 2


def test_cell_relay_startup_tolerance_covers_slow_container_start() -> None:
    assert (
        cell.RELAY_CONNECT_ATTEMPTS
        * cell.RELAY_CONNECT_DELAY_SECONDS
        >= 10
    )


def test_relay_retries_only_preconnect_host_refusal(monkeypatch) -> None:
    monkeypatch.setenv("BROKER_HOST_PORT", "12345")
    module_name = "scripts.ariadne_vertex_sydney_gemini_25_relay"
    sys.modules.pop(module_name, None)
    relay = importlib.import_module(module_name)
    assert relay.MAX_BYTES == 32768
    attempts = []
    response = object()

    class FakeConnection:
        def __init__(self, *_args, **_kwargs) -> None:
            attempts.append(self)

        def request(self, *_args, **_kwargs) -> None:
            if len(attempts) == 1:
                raise ConnectionRefusedError

        def getresponse(self):
            return response

        def close(self) -> None:
            return

    monkeypatch.setattr(
        relay.http.client,
        "HTTPConnection",
        FakeConnection,
    )
    monkeypatch.setattr(relay.time, "sleep", lambda _seconds: None)

    connection, observed = relay._post_to_host(b"{}", "token")

    assert observed is response
    assert connection is attempts[-1]
    assert len(attempts) == 2


def test_failed_setup_consumes_an_open_zero_call_ledger(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    audit = tmp_path / "audit.jsonl"
    rehearsal.create_ledger(ledger, "dry-run")
    from scripts import ariadne_vertex_sydney_gemini_25_contracts as contracts

    event = contracts.audit_event(
        sequence=1,
        previous_hash="sha256:" + "0" * 64,
        event_type="broker_ready",
        fields={"provider_call": False},
    )
    audit.write_text(json.dumps(event, sort_keys=True) + "\n", encoding="utf-8")
    assert rehearsal.close_open_ledger(ledger, audit) is True
    closed = json.loads(ledger.read_text(encoding="utf-8"))
    events = [
        json.loads(line)
        for line in audit.read_text(encoding="utf-8").splitlines()
    ]
    assert closed["status"] == "consumed"
    assert closed["provider_calls_consumed"] == 0
    assert contracts.validate_audit_chain(events)
