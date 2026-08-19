from __future__ import annotations

import ast
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from scripts import (
    raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal as harness,
)


ROOT = Path(__file__).resolve().parents[1]
HARNESS_PATH = ROOT / (
    "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_"
    "relay_free_rollback_unknown_commit_recovery_rehearsal.py"
)
CONTAINER_ID = "c" * 64
NETWORK_ID = "a" * 64
NETWORK_NAME = "emr4-checkin-rfr-net-0123456789abcdef"
NONCE = "b" * 32
TOKEN = "0123456789abcdef"
ATTEMPT_003_TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-check-in-relay-free-recovery-attempt-003"
)


@pytest.fixture
def contract() -> dict[str, Any]:
    return json.loads(harness.CONTRACT_PATH.read_text(encoding="utf-8"))


def _owned_row(
    contract: dict[str, Any],
    *,
    container_id: str = CONTAINER_ID,
    name: str | None = None,
) -> dict[str, Any]:
    profile = contract["containment_profile"]
    exact_name = name or profile["server_name_prefix"] + TOKEN
    return {
        "Id": container_id,
        "Name": "/" + exact_name,
        "Image": profile["image_id"],
        "Config": {
            "Image": profile["image_reference"],
            "Labels": {
                profile["harness_label_key"]: profile["harness_label_value"],
                profile["nonce_label_key"]: NONCE,
            },
        },
        "State": {"Status": "created", "Running": False},
    }


def _result(*, stdout: str = "", returncode: int = 0) -> object:
    return type("Result", (), {"stdout": stdout, "returncode": returncode})()


def test_exactly_two_creation_profile_calls_bind_captured_network_name() -> None:
    tree = ast.parse(HARNESS_PATH.read_text(encoding="utf-8"))
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    calls: list[tuple[str, ast.Call]] = []
    for function_name in ("_create_server", "_create_sidecar"):
        for node in ast.walk(functions[function_name]):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "_container_profile_predicates"
            ):
                calls.append((function_name, node))
    assert [name for name, _ in calls] == ["_create_server", "_create_sidecar"]
    for _, call in calls:
        keywords = {item.arg: item.value for item in call.keywords}
        assert isinstance(keywords["network_name"], ast.Name)
        assert keywords["network_name"].id == "network_name"


def test_attempt_003_terminal_evidence_and_historical_harness_remain_exact() -> None:
    bindings = {
        "rehearsal-failure-evidence.json": (
            "e8bf62e86fd3dbcfbcd7a0d68628e0d736b06617f4ef1a023a9a8928344fe96b"
        ),
        "attempt-003-execution-envelope.json": (
            "91e12b3268283fc3be48df583f7a0650a5a30bdaee40b1f74297d8185af91c75"
        ),
        "attempt-003-cleanup-recovery.json": (
            "048cd946166fabb8b2ce3400e31c85ee2fe410e6a3c07d5d26cbc79141250b71"
        ),
    }
    for name, expected in bindings.items():
        assert hashlib.sha256((ATTEMPT_003_TOPIC / name).read_bytes()).hexdigest() == (
            expected
        )
    envelope = json.loads(
        (ATTEMPT_003_TOPIC / "attempt-003-execution-envelope.json").read_text(
            encoding="utf-8"
        )
    )
    assert envelope["occupied_execution_count"] == 1
    assert envelope["automatic_retry_count"] == 0
    assert envelope["ambiguous_success_released"] is False
    historical = subprocess.run(
        [
            "git",
            "show",
            "19e4414fec067fcbb6af12818e432953432878be:"
            "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_"
            "relay_free_rollback_unknown_commit_recovery_rehearsal.py",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    assert hashlib.sha256(historical).hexdigest() == (
        "6965328b6dce6ecf939e86456bfcd99f1bdee7d32202e276f37454796e012b6b"
    )


@pytest.mark.parametrize(
    ("factory", "name_prefix", "kind"),
    (
        ("server", "server_name_prefix", "server"),
        ("sidecar", "sidecar_name_prefix", "readiness"),
    ),
)
def test_real_creation_calls_forward_all_exact_profile_bindings(
    monkeypatch: pytest.MonkeyPatch,
    contract: dict[str, Any],
    factory: str,
    name_prefix: str,
    kind: str,
) -> None:
    captured: dict[str, Any] = {}
    name = contract["containment_profile"][name_prefix] + TOKEN
    row = _owned_row(contract, name=name)

    def fake_docker(
        executable: str,
        *arguments: str,
        check: bool = True,
        timeout: int = 30,
    ) -> object:
        del executable, check, timeout
        assert arguments[0] == "create"
        return _result(stdout=CONTAINER_ID)

    def capture_predicates(candidate: dict[str, Any], **keywords: Any) -> dict[str, bool]:
        captured.update({"row": candidate, **keywords})
        return {"all_exact": True}

    monkeypatch.setattr(harness, "_docker", fake_docker)
    monkeypatch.setattr(harness, "_inspect_container", lambda *_: row)
    monkeypatch.setattr(harness, "_container_profile_predicates", capture_predicates)
    monkeypatch.setattr(harness.secrets, "token_hex", lambda _: TOKEN)
    if factory == "server":
        result = harness._create_server(
            "not-docker",
            contract,
            nonce=NONCE,
            network_id=NETWORK_ID,
            network_name=NETWORK_NAME,
            forbidden_values=("f" * 64,),
        )
    else:
        result = harness._create_sidecar(
            "not-docker",
            contract,
            nonce=NONCE,
            network_id=NETWORK_ID,
            network_name=NETWORK_NAME,
            action=kind,
            wrapper="exit 0",
            arguments=[],
            forbidden_values=("f" * 64,),
        )
    assert result == (CONTAINER_ID, name)
    assert captured == {
        "row": row,
        "container_id": CONTAINER_ID,
        "container_name": name,
        "network_name": NETWORK_NAME,
        "network_id": NETWORK_ID,
        "nonce": NONCE,
        "contract": contract,
        "kind": kind,
        "forbidden_values": ("f" * 64,),
    }


@pytest.mark.parametrize(
    ("factory", "name_prefix", "expected_stage", "expected_code"),
    (
        (
            "server",
            "server_name_prefix",
            "environment",
            "server_pre_registry_controller_failure_cleaned",
        ),
        (
            "sidecar",
            "sidecar_name_prefix",
            "sidecar",
            "sidecar_pre_registry_controller_failure_cleaned",
        ),
    ),
)
def test_unknown_post_create_failure_removes_exact_created_container(
    monkeypatch: pytest.MonkeyPatch,
    contract: dict[str, Any],
    factory: str,
    name_prefix: str,
    expected_stage: str,
    expected_code: str,
) -> None:
    name = contract["containment_profile"][name_prefix] + TOKEN
    row = _owned_row(contract, name=name)
    calls: list[tuple[str, ...]] = []
    removed = False

    def fake_docker(
        executable: str,
        *arguments: str,
        check: bool = True,
        timeout: int = 30,
    ) -> object:
        nonlocal removed
        del executable, check, timeout
        calls.append(arguments)
        if arguments[0] == "create":
            return _result(stdout=CONTAINER_ID)
        if arguments[:2] == ("container", "inspect"):
            if removed:
                return _result(returncode=1)
            return _result(stdout=json.dumps([row]))
        if arguments[:2] == ("rm", "--force"):
            assert arguments[2] == CONTAINER_ID
            removed = True
            return _result()
        raise AssertionError(arguments)

    def unexpected(*_: object, **__: object) -> dict[str, bool]:
        raise TypeError("fault injection")

    monkeypatch.setattr(harness, "_docker", fake_docker)
    monkeypatch.setattr(harness, "_inspect_container", lambda *_: row)
    monkeypatch.setattr(harness, "_container_profile_predicates", unexpected)
    monkeypatch.setattr(harness.secrets, "token_hex", lambda _: TOKEN)
    with pytest.raises(harness.RehearsalFailure) as caught:
        if factory == "server":
            harness._create_server(
                "not-docker",
                contract,
                nonce=NONCE,
                network_id=NETWORK_ID,
                network_name=NETWORK_NAME,
                forbidden_values=("f" * 64,),
            )
        else:
            harness._create_sidecar(
                "not-docker",
                contract,
                nonce=NONCE,
                network_id=NETWORK_ID,
                network_name=NETWORK_NAME,
                action="readiness",
                wrapper="exit 0",
                arguments=[],
                forbidden_values=("f" * 64,),
            )
    assert (caught.value.stage, caught.value.code) == (expected_stage, expected_code)
    assert removed is True
    assert calls[-2:] == [
        ("rm", "--force", CONTAINER_ID),
        ("container", "inspect", CONTAINER_ID),
    ]


def _cleanup_result(
    monkeypatch: pytest.MonkeyPatch,
    contract: dict[str, Any],
    *,
    rows: list[dict[str, Any]],
    candidate_id: str = CONTAINER_ID,
    remove_returncode: int = 0,
    post_remove_returncode: int = 1,
) -> tuple[bool, list[tuple[str, ...]]]:
    calls: list[tuple[str, ...]] = []
    removed = False

    def fake_docker(
        executable: str,
        *arguments: str,
        check: bool = True,
        timeout: int = 30,
    ) -> object:
        nonlocal removed
        del executable, check, timeout
        calls.append(arguments)
        if arguments[:2] == ("container", "inspect"):
            if removed:
                return _result(returncode=post_remove_returncode)
            return _result(stdout=json.dumps(rows))
        if arguments[:2] == ("rm", "--force"):
            removed = True
            return _result(returncode=remove_returncode)
        raise AssertionError(arguments)

    monkeypatch.setattr(harness, "_docker", fake_docker)
    result = harness._cleanup_pre_registry_created_container(
        "not-docker",
        contract,
        container_name=contract["containment_profile"]["server_name_prefix"] + TOKEN,
        candidate_id=candidate_id,
        nonce=NONCE,
    )
    return result, calls


def test_cleanup_accepts_invalid_candidate_only_via_exact_generated_name(
    monkeypatch: pytest.MonkeyPatch, contract: dict[str, Any]
) -> None:
    result, calls = _cleanup_result(
        monkeypatch,
        contract,
        rows=[_owned_row(contract)],
        candidate_id="abbreviated",
    )
    assert result is True
    assert calls[0] == (
        "container",
        "inspect",
        contract["containment_profile"]["server_name_prefix"] + TOKEN,
    )
    assert calls[1] == ("rm", "--force", CONTAINER_ID)


@pytest.mark.parametrize(
    "mutation",
    (
        "multiplicity",
        "resolved_id_shape",
        "candidate_relation",
        "name",
        "image_id",
        "image_reference",
        "harness_label",
        "nonce",
        "state",
        "running",
        "remove_failure",
        "removal_readback_present",
    ),
)
def test_cleanup_denies_non_exact_ownership_state_and_absence(
    monkeypatch: pytest.MonkeyPatch,
    contract: dict[str, Any],
    mutation: str,
) -> None:
    row = _owned_row(contract)
    rows = [row]
    remove_returncode = 0
    post_remove_returncode = 1
    if mutation == "multiplicity":
        rows.append(copy.deepcopy(row))
    elif mutation == "resolved_id_shape":
        row["Id"] = "short"
    elif mutation == "candidate_relation":
        row["Id"] = "d" * 64
    elif mutation == "name":
        row["Name"] = "/foreign"
    elif mutation == "image_id":
        row["Image"] = "sha256:" + "0" * 64
    elif mutation == "image_reference":
        row["Config"]["Image"] = "foreign:latest"
    elif mutation == "harness_label":
        key = contract["containment_profile"]["harness_label_key"]
        row["Config"]["Labels"][key] = "foreign"
    elif mutation == "nonce":
        key = contract["containment_profile"]["nonce_label_key"]
        row["Config"]["Labels"][key] = "0" * 32
    elif mutation == "state":
        row["State"]["Status"] = "exited"
    elif mutation == "running":
        row["State"]["Running"] = True
    elif mutation == "remove_failure":
        remove_returncode = 1
    elif mutation == "removal_readback_present":
        post_remove_returncode = 0
    result, calls = _cleanup_result(
        monkeypatch,
        contract,
        rows=rows,
        remove_returncode=remove_returncode,
        post_remove_returncode=post_remove_returncode,
    )
    assert result is False
    if mutation not in ("remove_failure", "removal_readback_present"):
        assert not any(call[:2] == ("rm", "--force") for call in calls)


@pytest.mark.parametrize(
    ("factory", "expected_code"),
    (
        ("server", "server_pre_registry_cleanup_unverified"),
        ("sidecar", "sidecar_pre_registry_cleanup_unverified"),
    ),
)
def test_cleanup_uncertainty_dominates_known_or_unknown_primary(
    monkeypatch: pytest.MonkeyPatch,
    contract: dict[str, Any],
    factory: str,
    expected_code: str,
) -> None:
    row = _owned_row(
        contract,
        name=contract["containment_profile"][
            "server_name_prefix" if factory == "server" else "sidecar_name_prefix"
        ]
        + TOKEN,
    )
    monkeypatch.setattr(harness, "_docker", lambda *_args, **_kwargs: _result(stdout=CONTAINER_ID))
    monkeypatch.setattr(harness, "_inspect_container", lambda *_: row)
    monkeypatch.setattr(
        harness,
        "_container_profile_predicates",
        lambda *_, **__: {"fault": False},
    )
    monkeypatch.setattr(
        harness, "_cleanup_pre_registry_created_container", lambda *_, **__: False
    )
    monkeypatch.setattr(harness.secrets, "token_hex", lambda _: TOKEN)
    with pytest.raises(harness.RehearsalFailure) as caught:
        if factory == "server":
            harness._create_server(
                "not-docker",
                contract,
                nonce=NONCE,
                network_id=NETWORK_ID,
                network_name=NETWORK_NAME,
                forbidden_values=(),
            )
        else:
            harness._create_sidecar(
                "not-docker",
                contract,
                nonce=NONCE,
                network_id=NETWORK_ID,
                network_name=NETWORK_NAME,
                action="readiness",
                wrapper="exit 0",
                arguments=[],
                forbidden_values=(),
            )
    assert (caught.value.stage, caught.value.code) == ("cleanup", expected_code)
