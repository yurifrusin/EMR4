import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import orchestration_harness.programme_admission as programme_admission
from orchestration_harness.verdict import ReviewVerdict
from scripts import ariadne_antigravity
from scripts.ariadne_antigravity import WorktreeState, build_command
from scripts.raisa_ariadne_recovery_preflight import build_task_manifest


@pytest.fixture(autouse=True)
def _admit_direct_worker_unit_surface(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        ariadne_antigravity, "require_programme_admission", lambda **_kwargs: None
    )


def _state(branch: str = "antigravity/bounded") -> WorktreeState:
    return WorktreeState(
        root=Path("C:/worktrees/bounded"),
        branch=branch,
        head="abc123",
        dirty=False,
    )


def _assessment(decision: str) -> dict[str, object]:
    integration_authorized = decision == "pass"
    return {
        "artifact_kind": "decision",
        "artifact_valid": True,
        "review_verdict": decision,
        "integration_authorized": integration_authorized,
        "canonical_marker": f"DECISION: {decision.upper()}",
        "reason_code": "terminal_marker_observed",
    }


def _command_manifest() -> dict[str, object]:
    return {
        "schema_version": "ariadne.verifier-command-manifest.v1",
        "commands": [
            {"id": "LINT", "argv": ["python", "-m", "ruff", "check", "."]},
            {"id": "TEST", "argv": ["python", "-m", "pytest", "-q"]},
        ],
    }


def _command_results(*exit_codes: int) -> list[dict[str, object]]:
    manifest = _command_manifest()
    commands = manifest["commands"]
    assert isinstance(commands, list)
    return [
        {
            "id": command["id"],
            "argv": command["argv"],
            "exit_code": exit_code,
        }
        for command, exit_code in zip(commands, exit_codes, strict=True)
    ]


def _mock_completed_worker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    stdout: str,
) -> tuple[Path, Path, Path]:
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    state = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head="abc123",
        dirty=False,
    )
    states = iter([state, state])
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: next(states),
    )
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0,
            stdout=stdout,
            stderr="",
        ),
    )
    return packet, output, orchestrator_receipt


def _passed_orchestrator_receipt(tmp_path: Path) -> Path:
    path = tmp_path / "orchestrator-receipt.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "ariadne.orchestrator_receipt.v1",
                "status": "passed",
                "worker_dispatch_permitted": True,
                "rehydration_sources": sorted(ariadne_antigravity.REHYDRATION_SOURCES),
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def test_command_always_binds_a_fresh_project_and_exact_worktree():
    command = build_command(
        packet="Review the change.",
        state=_state(),
        model="gemini-3.7-flash-high",
        os_sandbox=False,
    )

    assert command[:2] == ["agy", "-p"]
    assert "--new-project" in command
    assert command[command.index("--add-dir") + 1] == "C:\\worktrees\\bounded"
    assert command[command.index("--model") + 1] == "gemini-3.7-flash-high"
    assert command[command.index("--effort") + 1] == "high"
    assert command[command.index("--mode") + 1] == "plan"
    assert command[command.index("--print-timeout") + 1] == "45m"
    assert command[command.index("--output-format") + 1] == "json"
    schema = json.loads(command[command.index("--json-schema") + 1])
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["decision", "review"]
    assert "BOUND BRANCH: antigravity/bounded" in command[2]
    assert "STRUCTURED OUTPUT OVERRIDE" in command[2]
    assert "--sandbox" not in command


def test_os_sandbox_is_explicit_and_never_the_unattended_default():
    command = build_command(
        packet="Review.",
        state=_state(),
        model="gemini-3.6-flash-medium",
        os_sandbox=True,
    )

    assert command[-1] == "--sandbox"


def test_legacy_model_alias_is_canonicalized_with_explicit_effort():
    command = build_command(
        packet="Review.",
        state=_state(),
        model="Gemini 3.5 Flash (High)",
        os_sandbox=False,
    )

    assert command[command.index("--model") + 1] == "gemini-3.5-flash-high"
    assert command[command.index("--effort") + 1] == "high"


def test_command_rejects_non_gemini_flash_model():
    with pytest.raises(ValueError, match="unsupported Antigravity model"):
        build_command(
            packet="Review.",
            state=_state(),
            model="Claude Opus 4.6 (Thinking)",
            os_sandbox=False,
        )


def test_run_worker_records_canonical_high_model_and_read_only_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    state = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head="abc123",
        dirty=False,
    )
    states = iter([state, state])
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: next(states),
    )
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0,
            stdout=json.dumps(
                {
                    "result": {
                        "decision": "pass",
                        "review": "No material findings; focused checks passed.",
                    },
                    "usage": {"input_tokens": 10, "output_tokens": 8},
                }
            ),
            stderr="",
        ),
    )

    receipt = ariadne_antigravity.run_worker(
        packet_path=packet,
        cwd=tmp_path,
        output_path=output,
        orchestrator_receipt_path=orchestrator_receipt,
        model="gemini-3.7-flash-high",
        os_sandbox=False,
    )

    assert receipt["model"] == "gemini-3.7-flash-high"
    assert receipt["reasoning_effort"] == "high"
    assert receipt["decision"] == "pass"
    assert receipt["decision_contract"] == "schema_constrained_json_v1"
    assert receipt["decision_envelope"] == {
        "decision": "pass",
        "review": "No material findings; focused checks passed.",
        "verdict_assessment": _assessment("pass"),
    }
    assert receipt["transport"] == ("antigravity_new_project_bound_readonly_worktree")
    assert output.is_file()
    assert len(receipt["orchestrator_receipt_sha256"]) == 64


def test_nonzero_transport_writes_digest_only_failure_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "transport-failure.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    state = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head="abc123",
        dirty=False,
    )
    states = iter([state, state])
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: next(states),
    )
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=1,
            stdout="bounded diagnostic on stdout",
            stderr="",
        ),
    )
    times = iter([10.0, 2710.0])
    monkeypatch.setattr(ariadne_antigravity.time, "monotonic", lambda: next(times))

    with pytest.raises(RuntimeError, match="digest-only diagnostics written"):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.7-flash-high",
            os_sandbox=False,
        )

    failure = json.loads(output.read_text(encoding="utf-8"))
    assert failure["schema_version"] == "ariadne.transport-failure-receipt.v1"
    assert failure["status"] == "transport_failed_without_terminal_decision"
    assert failure["exit_code"] == 1
    assert failure["elapsed_ms"] == 2_700_000
    assert failure["print_timeout_seconds"] == 2_700
    assert failure["print_timeout_boundary_reached"] is True
    assert failure["stdout"]["bytes"] == len("bounded diagnostic on stdout")
    assert failure["stderr"]["empty"] is True
    assert failure["worktree_identity_unchanged"] is True
    assert failure["terminal_decision_returned"] is False
    assert failure["candidate_review_admitted"] is False
    assert "bounded diagnostic on stdout" not in output.read_text(encoding="utf-8")


def test_run_worker_rejects_revision_required_orchestrator_receipt_before_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    rejected = json.loads(orchestrator_receipt.read_text(encoding="utf-8"))
    rejected["status"] = "revision_required"
    rejected["worker_dispatch_permitted"] = False
    orchestrator_receipt.write_text(json.dumps(rejected) + "\n", encoding="utf-8")
    invoked = False

    def _unexpected_dispatch(*_args, **_kwargs):
        nonlocal invoked
        invoked = True
        raise AssertionError("provider transport must not run")

    monkeypatch.setattr(ariadne_antigravity.subprocess, "run", _unexpected_dispatch)

    with pytest.raises(ValueError, match="did not pass"):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.6-flash-high",
            os_sandbox=False,
        )

    assert invoked is False
    assert not output.exists()


def test_run_worker_fails_if_verifier_modifies_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    before = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head="abc123",
        dirty=False,
    )
    after = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head="abc123",
        dirty=True,
    )
    states = iter([before, after])
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: next(states),
    )
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0,
            stdout=json.dumps(
                {"decision": "pass", "review": "Candidate remained unchanged."}
            ),
            stderr="",
        ),
    )

    with pytest.raises(RuntimeError, match="modified its read-only candidate"):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.6-flash-high",
            os_sandbox=False,
        )

    failure = json.loads(output.read_text(encoding="utf-8"))
    assert failure["schema_version"] == "ariadne.egress-failure-receipt.v1"
    assert failure["status"] == ("egress_failed_without_admitted_terminal_decision")
    assert failure["exit_code"] == 0
    assert failure["head_before"] == failure["head_after"] == "abc123"
    assert failure["dirty_after"] is True
    assert failure["worktree_identity_unchanged"] is False
    assert failure["reason_code"] == "read_only_worktree_postcondition_failed"
    assert failure["terminal_decision_admitted"] is False
    assert failure["candidate_review_admitted"] is False
    assert failure["stdout"]["bytes"] > 0
    assert "Candidate remained unchanged" not in output.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "stdout, decision_count",
    [
        ("No decision.", 0),
        ("DECISION: pass\nDECISION: pass", 2),
    ],
)
def test_run_worker_rejects_missing_or_duplicate_terminal_decision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stdout: str,
    decision_count: int,
):
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    state = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head="abc123",
        dirty=False,
    )
    states = iter([state, state])
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: next(states),
    )
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0, stdout=stdout, stderr=""
        ),
    )

    with pytest.raises(
        RuntimeError,
        match=f"exactly one terminal decision; observed {decision_count}",
    ):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.6-flash-high",
            os_sandbox=False,
            structured_decision=False,
        )

    failure = json.loads(output.read_text(encoding="utf-8"))
    assert failure["schema_version"] == "ariadne.egress-failure-receipt.v1"
    assert failure["decision_contract"] == "legacy_terminal_line_v1"
    assert failure["reason_code"] == "legacy_terminal_decision_not_admitted"
    assert failure["terminal_decision_admitted"] is False
    assert failure["candidate_review_admitted"] is False
    assert failure["stdout"]["bytes"] == len(stdout.encode("utf-8"))
    assert stdout not in output.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "stdout, envelope_count",
    [
        (json.dumps({"result": "not structured"}), 0),
        (
            json.dumps(
                {
                    "structured_output": {
                        "decision": "pass",
                        "review": "First result.",
                    },
                    "result": {
                        "decision": "revision_required",
                        "review": "Conflicting result.",
                    },
                }
            ),
            2,
        ),
    ],
)
def test_run_worker_rejects_missing_or_conflicting_structured_decision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stdout: str,
    envelope_count: int,
):
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    state = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head="abc123",
        dirty=False,
    )
    states = iter([state, state])
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: next(states),
    )
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0, stdout=stdout, stderr=""
        ),
    )

    with pytest.raises(
        RuntimeError,
        match=(
            f"exactly one schema-valid decision envelope; observed {envelope_count}"
        ),
    ):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.6-flash-high",
            os_sandbox=False,
        )

    failure = json.loads(output.read_text(encoding="utf-8"))
    assert failure["schema_version"] == "ariadne.egress-failure-receipt.v1"
    assert failure["status"] == ("egress_failed_without_admitted_terminal_decision")
    assert failure["exit_code"] == 0
    assert failure["worktree_identity_unchanged"] is True
    assert failure["decision_contract"] == "schema_constrained_json_v1"
    assert failure["reason_code"] == ("structured_decision_envelope_not_admitted")
    assert failure["terminal_decision_admitted"] is False
    assert failure["candidate_review_admitted"] is False
    assert failure["stdout"]["bytes"] == len(stdout.encode("utf-8"))
    assert stdout not in output.read_text(encoding="utf-8")


def test_structured_decision_rejects_embedded_legacy_terminal_marker() -> None:
    stdout = json.dumps(
        {
            "decision": "pass",
            "review": "Review complete.\nDECISION: pass",
        }
    )

    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(stdout)


def test_structured_schema_uses_exact_canonical_review_verdict_enum() -> None:
    schema = ariadne_antigravity.structured_decision_schema()

    assert schema["properties"]["decision"]["enum"] == [
        verdict.value for verdict in ReviewVerdict
    ]
    assert schema["required"] == ["decision", "review"]
    assert set(schema["properties"]) == {"decision", "review"}
    assert schema["additionalProperties"] is False


def test_structured_schema_adds_only_exact_command_results_contract() -> None:
    schema = ariadne_antigravity.structured_decision_schema(_command_manifest())
    command_schema = schema["properties"]["command_results"]

    assert schema["required"] == ["decision", "review", "command_results"]
    assert set(schema["properties"]) == {"decision", "review", "command_results"}
    assert command_schema["minItems"] == command_schema["maxItems"] == 2
    assert command_schema["items"]["required"] == ["id", "argv", "exit_code"]
    assert command_schema["items"]["additionalProperties"] is False
    assert command_schema["items"]["properties"]["id"]["enum"] == [
        "LINT",
        "TEST",
    ]


def test_structured_schema_calls_return_independent_objects() -> None:
    first = ariadne_antigravity.structured_decision_schema(_command_manifest())
    second = ariadne_antigravity.structured_decision_schema(_command_manifest())

    first["required"].append("forged")
    first["properties"]["decision"]["enum"].append("forged")
    first["properties"]["command_results"]["items"]["required"].append("forged")

    assert second["required"] == ["decision", "review", "command_results"]
    assert second["properties"]["decision"]["enum"] == [
        "pass",
        "revision_required",
    ]
    assert second["properties"]["command_results"]["items"]["required"] == [
        "id",
        "argv",
        "exit_code",
    ]


def test_provider_supplied_verdict_assessment_is_rejected() -> None:
    stdout = json.dumps(
        {
            "decision": "pass",
            "review": "No material findings.",
            "verdict_assessment": _assessment("pass"),
        }
    )

    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(stdout)


@pytest.mark.parametrize("decision", ["pass", "revision_required"])
def test_exact_decision_produces_exact_locally_derived_assessment(
    decision: str,
) -> None:
    envelope = ariadne_antigravity.parse_structured_decision(
        json.dumps({"decision": decision, "review": "  Bounded review complete.  "})
    )

    assert envelope == {
        "decision": decision,
        "review": "Bounded review complete.",
        "verdict_assessment": _assessment(decision),
    }


@pytest.mark.parametrize(
    "wrapper",
    ["structured_output", "result", "response", "output"],
)
def test_supported_wrappers_preserve_the_canonical_envelope(wrapper: str) -> None:
    envelope = ariadne_antigravity.parse_structured_decision(
        json.dumps(
            {
                wrapper: {
                    "decision": "pass",
                    "review": "No material findings.",
                },
                "usage": {"input_tokens": 10},
            }
        )
    )

    assert envelope["verdict_assessment"] == _assessment("pass")


@pytest.mark.parametrize(
    "decision",
    ["PASS", " pass", "pass ", True, None, "approved"],
)
def test_non_exact_structured_decisions_are_rejected(decision: object) -> None:
    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(
            json.dumps({"decision": decision, "review": "Bounded review."})
        )


@pytest.mark.parametrize(
    "review",
    [
        pytest.param("", id="empty"),
        pytest.param("   ", id="whitespace"),
        pytest.param(None, id="null"),
        pytest.param(7, id="non-string"),
        pytest.param("x" * 40001, id="over-length"),
    ],
)
def test_invalid_structured_review_fields_are_rejected(review: object) -> None:
    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(
            json.dumps({"decision": "pass", "review": review})
        )


@pytest.mark.parametrize(
    "review",
    [
        "Review complete.\nDECISION: PASS",
        "## DECISION: PASS",
        "**DECISION: PASS**",
        "| DECISION: PASS |",
        "VERDICT: PASS",
        "DECISION: APPROVED",
        "DECISION: PASS\nDECISION: REVISION_REQUIRED",
        "<!-- DECISION: PASS -->",
        "> DECISION: PASS",
    ],
)
def test_review_text_cannot_supply_marker_authority(review: str) -> None:
    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(
            json.dumps({"decision": "pass", "review": review})
        )


def test_ordinary_prose_discussing_a_future_marker_is_admitted() -> None:
    review = "A future external review may emit DECISION: PASS after this tranche."

    envelope = ariadne_antigravity.parse_structured_decision(
        json.dumps({"decision": "revision_required", "review": review})
    )

    assert envelope["review"] == review
    assert envelope["verdict_assessment"] == _assessment("revision_required")


def test_no_valid_structured_candidate_is_rejected() -> None:
    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(
            json.dumps({"result": {"decision": "pass"}})
        )


def test_conflicting_direct_and_wrapped_candidates_are_rejected() -> None:
    stdout = json.dumps(
        {
            "decision": "pass",
            "review": "First result.",
            "result": {
                "decision": "revision_required",
                "review": "Second result.",
            },
        }
    )

    with pytest.raises(RuntimeError, match="observed 2"):
        ariadne_antigravity.parse_structured_decision(stdout)


def test_identical_direct_and_wrapped_candidates_collapse_to_one() -> None:
    decision = {"decision": "pass", "review": "One canonical result."}

    envelope = ariadne_antigravity.parse_structured_decision(
        json.dumps({**decision, "result": copy.deepcopy(decision)})
    )

    assert envelope["verdict_assessment"] == _assessment("pass")


@pytest.mark.parametrize(
    "stdout, command_manifest",
    [
        pytest.param(
            '{"decision":"revision_required","decision":"pass",'
            '"review":"Bounded review."}',
            None,
            id="root-decision-revision-required-then-pass",
        ),
        pytest.param(
            '{"decision":"pass","decision":"revision_required",'
            '"review":"Bounded review."}',
            None,
            id="root-decision-pass-then-revision-required",
        ),
        pytest.param(
            '{"decision":"pass","review":"First review.","review":"Second review."}',
            None,
            id="root-review",
        ),
        pytest.param(
            '{"structured_output":{"decision":"pass","review":"First."},'
            '"structured_output":{"decision":"pass","review":"Second."}}',
            None,
            id="structured-output-wrapper",
        ),
        pytest.param(
            '{"result":{"decision":"pass","review":"First."},'
            '"result":{"decision":"pass","review":"Second."}}',
            None,
            id="result-wrapper",
        ),
        pytest.param(
            '{"response":{"decision":"pass","review":"First."},'
            '"response":{"decision":"pass","review":"Second."}}',
            None,
            id="response-wrapper",
        ),
        pytest.param(
            '{"output":{"decision":"pass","review":"First."},'
            '"output":{"decision":"pass","review":"Second."}}',
            None,
            id="output-wrapper",
        ),
        pytest.param(
            '{"structured_output":{"decision":"revision_required",'
            '"decision":"pass","review":"Bounded review."}}',
            None,
            id="decision-inside-structured-output",
        ),
        pytest.param(
            '{"result":{"decision":"revision_required","decision":"pass",'
            '"review":"Bounded review."}}',
            None,
            id="decision-inside-result",
        ),
        pytest.param(
            '{"response":{"decision":"revision_required","decision":"pass",'
            '"review":"Bounded review."}}',
            None,
            id="decision-inside-response",
        ),
        pytest.param(
            '{"output":{"decision":"revision_required","decision":"pass",'
            '"review":"Bounded review."}}',
            None,
            id="decision-inside-output",
        ),
        pytest.param(
            '{"decision":"revision_required","review":"Bounded review.",'
            '"command_results":['
            '{"id":"LINT","id":"LINT","argv":'
            '["python","-m","ruff","check","."],"exit_code":0},'
            '{"id":"TEST","argv":["python","-m","pytest","-q"],'
            '"exit_code":0}]}',
            _command_manifest(),
            id="command-result-id",
        ),
        pytest.param(
            '{"decision":"revision_required","review":"Bounded review.",'
            '"command_results":['
            '{"id":"LINT","argv":["python","-m","ruff","check","."],'
            '"argv":["python","-m","ruff","check","."],"exit_code":0},'
            '{"id":"TEST","argv":["python","-m","pytest","-q"],'
            '"exit_code":0}]}',
            _command_manifest(),
            id="command-result-argv",
        ),
        pytest.param(
            '{"decision":"revision_required","review":"Bounded review.",'
            '"command_results":['
            '{"id":"LINT","argv":["python","-m","ruff","check","."],'
            '"exit_code":0,"exit_code":1},'
            '{"id":"TEST","argv":["python","-m","pytest","-q"],'
            '"exit_code":0}]}',
            _command_manifest(),
            id="command-result-exit-code",
        ),
        pytest.param(
            '{"result":{"decision":"pass","review":"Bounded review."},'
            '"usage":{"input_tokens":10,"input_tokens":11}}',
            None,
            id="arbitrary-nested-member",
        ),
        pytest.param(
            r'"{\"decision\":\"revision_required\",'
            r'\"decision\":\"pass\",\"review\":\"Bounded review.\"}"',
            None,
            id="json-string-compatibility-candidate",
        ),
        pytest.param(
            r'{"dec\u0069sion":"pass","decision":"revision_required",'
            r'"review":"Bounded review."}',
            None,
            id="escaped-and-literal-member-name",
        ),
    ],
)
def test_duplicate_json_members_admit_zero_envelopes(
    stdout: str,
    command_manifest: dict[str, object] | None,
) -> None:
    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(stdout, command_manifest)


@pytest.mark.parametrize(
    "stdout",
    [
        pytest.param(
            '{"decision":"revision_required","decision":"pass",'
            '"review":"Bounded review."}',
            id="duplicate-root-decision",
        ),
        pytest.param(
            r'"{\"decision\":\"revision_required\",'
            r'\"decision\":\"pass\",\"review\":\"Bounded review.\"}"',
            id="duplicate-json-string-candidate",
        ),
    ],
)
def test_duplicate_json_worker_failure_is_digest_only_and_main_returns_two(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stdout: str,
) -> None:
    packet, output, orchestrator_receipt = _mock_completed_worker(
        tmp_path,
        monkeypatch,
        stdout=stdout,
    )
    monkeypatch.setattr(
        ariadne_antigravity.sys,
        "argv",
        [
            "ariadne_antigravity.py",
            "--packet",
            str(packet),
            "--cwd",
            str(tmp_path),
            "--output",
            str(output),
            "--orchestrator-receipt",
            str(orchestrator_receipt),
            "--model",
            "gemini-3.7-flash-high",
        ],
    )

    assert ariadne_antigravity.main() == 2

    rendered_failure = output.read_text(encoding="utf-8")
    failure = json.loads(rendered_failure)
    assert failure["schema_version"] == "ariadne.egress-failure-receipt.v1"
    assert failure["status"] == "egress_failed_without_admitted_terminal_decision"
    assert failure["decision_contract"] == "schema_constrained_json_v1"
    assert failure["reason_code"] == "structured_decision_envelope_not_admitted"
    assert failure["exit_code"] == 0
    assert failure["terminal_decision_admitted"] is False
    assert failure["candidate_review_admitted"] is False
    assert failure["stdout"]["bytes"] == len(stdout.encode("utf-8"))
    assert set(failure["stdout"]) == {"bytes", "sha256", "empty"}
    assert stdout not in rendered_failure


@pytest.mark.parametrize(
    "direct_decision, wrapped_decision",
    [
        ("revision_required", "pass"),
        ("pass", "revision_required"),
    ],
)
def test_direct_wrapper_conflict_with_metadata_rejects_the_whole_output(
    direct_decision: str,
    wrapped_decision: str,
) -> None:
    stdout = json.dumps(
        {
            "decision": direct_decision,
            "review": "Direct decision.",
            "result": {
                "decision": wrapped_decision,
                "review": "Wrapped decision.",
            },
            "usage": {"input_tokens": 10},
        }
    )

    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(stdout)


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(
            {
                "decision": "pass",
                "review": "Direct decision.",
                "usage": {"input_tokens": 10},
            },
            id="direct-metadata-without-wrapper",
        ),
        pytest.param(
            {
                "decision": "pass",
                "review": "One canonical result.",
                "result": {
                    "decision": "pass",
                    "review": "One canonical result.",
                },
                "usage": {"input_tokens": 10},
            },
            id="direct-identical-wrapper-and-metadata",
        ),
        pytest.param(
            {
                "decision": "pass",
                "review": "Direct decision.",
                "response": {
                    "decision": "pass",
                    "review": "Wrapped decision.",
                },
                "usage": {"input_tokens": 10},
            },
            id="direct-another-wrapper-and-metadata",
        ),
    ],
)
def test_complete_direct_candidate_with_unknown_metadata_is_rejected(
    payload: dict[str, object],
) -> None:
    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(json.dumps(payload))


def test_arbitrary_nested_and_unlisted_wrapper_keys_are_not_searched() -> None:
    decision = {"decision": "pass", "review": "Nested result."}

    for value in ({"payload": decision}, {"result": {"payload": decision}}):
        with pytest.raises(RuntimeError, match="observed 0"):
            ariadne_antigravity.parse_structured_decision(json.dumps(value))


def test_pass_with_exact_all_zero_command_results_is_admitted() -> None:
    envelope = ariadne_antigravity.parse_structured_decision(
        json.dumps(
            {
                "decision": "pass",
                "review": "Both checks passed.",
                "command_results": _command_results(0, 0),
            }
        ),
        _command_manifest(),
    )

    assert envelope["command_results"] == _command_results(0, 0)
    assert envelope["verdict_assessment"]["integration_authorized"] is True


def test_pass_with_nonzero_command_result_is_rejected() -> None:
    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(
            json.dumps(
                {
                    "decision": "pass",
                    "review": "One check failed.",
                    "command_results": _command_results(0, 1),
                }
            ),
            _command_manifest(),
        )


def test_revision_required_with_nonzero_command_result_is_non_authorizing() -> None:
    envelope = ariadne_antigravity.parse_structured_decision(
        json.dumps(
            {
                "decision": "revision_required",
                "review": "One check failed.",
                "command_results": _command_results(0, 1),
            }
        ),
        _command_manifest(),
    )

    assert envelope["command_results"] == _command_results(0, 1)
    assert envelope["verdict_assessment"] == _assessment("revision_required")


@pytest.mark.parametrize(
    "mutation",
    ["id", "argv", "order", "length", "container_type", "exit_type", "extra"],
)
def test_malformed_or_substituted_command_results_are_rejected(
    mutation: str,
) -> None:
    results: object = _command_results(0, 0)
    assert isinstance(results, list)
    if mutation == "id":
        results[0]["id"] = "OTHER"
    elif mutation == "argv":
        results[0]["argv"] = ["python", "-m", "ruff", "format", "."]
    elif mutation == "order":
        results.reverse()
    elif mutation == "length":
        results.pop()
    elif mutation == "container_type":
        results = {"results": results}
    elif mutation == "exit_type":
        results[0]["exit_code"] = True
    else:
        results[0]["extra"] = "forbidden"

    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(
            json.dumps(
                {
                    "decision": "revision_required",
                    "review": "Bounded check result.",
                    "command_results": results,
                }
            ),
            _command_manifest(),
        )


def test_command_admission_receives_only_the_canonical_decision_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[str] = []

    def _admit(**kwargs):
        observed.append(kwargs["decision"])
        return kwargs["results"]

    monkeypatch.setattr(ariadne_antigravity, "admit_command_results", _admit)

    envelope = ariadne_antigravity.parse_structured_decision(
        json.dumps(
            {
                "decision": "revision_required",
                "review": "Bounded check result.",
                "command_results": _command_results(0, 1),
            }
        ),
        _command_manifest(),
    )

    assert observed == ["revision_required"]
    assert envelope["decision"] == "revision_required"


def test_run_worker_revision_required_is_completed_but_non_authorizing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet, output, orchestrator_receipt = _mock_completed_worker(
        tmp_path,
        monkeypatch,
        stdout=json.dumps(
            {
                "decision": "revision_required",
                "review": "A bounded correction is required.",
            }
        ),
    )

    receipt = ariadne_antigravity.run_worker(
        packet_path=packet,
        cwd=tmp_path,
        output_path=output,
        orchestrator_receipt_path=orchestrator_receipt,
        model="gemini-3.7-flash-high",
        os_sandbox=False,
    )

    assert receipt["status"] == "completed"
    assert receipt["decision"] == "revision_required"
    assert receipt["decision_envelope"]["verdict_assessment"] == _assessment(
        "revision_required"
    )


def test_legacy_text_mode_remains_transport_compatibility_without_assessment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet, output, orchestrator_receipt = _mock_completed_worker(
        tmp_path,
        monkeypatch,
        stdout="Legacy review text.\nDECISION: pass",
    )

    receipt = ariadne_antigravity.run_worker(
        packet_path=packet,
        cwd=tmp_path,
        output_path=output,
        orchestrator_receipt_path=orchestrator_receipt,
        model="gemini-3.7-flash-high",
        os_sandbox=False,
        structured_decision=False,
    )

    assert receipt["status"] == "completed"
    assert receipt["decision_contract"] == "legacy_terminal_line_v1"
    assert "decision_envelope" not in receipt
    assert "verdict_assessment" not in receipt


def test_current_programme_admits_only_the_exact_g1a2_task_paths() -> None:
    manifest = build_task_manifest(Path(__file__).resolve().parents[1])
    decision = programme_admission.evaluate_programme_admission(
        repo_root=Path(__file__).resolve().parents[1],
        manifest=manifest,
        entrypoint="recovery_preflight",
    )

    assert decision.admitted is True
    assert set(manifest["allowed_path_roots"]) == {
        "scripts/ariadne_antigravity.py",
        "tests/test_ariadne_antigravity.py",
    }
    for widened_paths in (
        ["scripts/ariadne_antigravity.py"],
        [*manifest["allowed_path_roots"], "scripts/agent_worktrees.py"],
    ):
        widened = dict(manifest)
        widened["allowed_path_roots"] = widened_paths
        rejected = programme_admission.evaluate_programme_admission(
            repo_root=Path(__file__).resolve().parents[1],
            manifest=widened,
            entrypoint="recovery_preflight",
        )
        assert rejected.admitted is False


def test_current_programme_denies_provider_invocation_and_later_work() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = build_task_manifest(root)
    provider = programme_admission.evaluate_programme_admission(
        repo_root=root,
        manifest=manifest,
        entrypoint="provider_invocation",
    )
    policy = programme_admission.load_programme_policy(root)
    profile = policy.overlay["profiles"]["G1A.2_ACTIVE"]

    assert provider.admitted is False
    assert provider.reason_codes == ["provider_invocation_closed_in_active_profile"]
    assert programme_admission.g1a2_provider_contract_reasons(root) == []
    assert profile["allowed_paths"] == [
        "scripts/ariadne_antigravity.py",
        "tests/test_ariadne_antigravity.py",
    ]
    assert {
        "g1b_work",
        "integration",
        "product_behavior_change",
        "deployment",
        "pages",
        "protected_ref_movement",
        "provider_invocation",
    }.issubset(profile["forbidden_effects"])
