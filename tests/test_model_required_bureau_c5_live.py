from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts import model_required_bureau_c5_contract as contract
from scripts import model_required_bureau_c5_live as live
from scripts.model_required_bureau_c5_rehearsal import HttpReadbackProbe


NOW = datetime(2026, 8, 5, 10, 0, 0, tzinfo=timezone.utc)
PORT = 44123


def _frame():
    baseline = contract.InternalObservation(
        observation_id="baseline-a1",
        observation_source_id="obs-source-baseline-a1",
        kind="baseline",
        observed_at="2026-08-05T10:00:00Z",
        process_disposition="alive",
        loopback_health_disposition="reachable",
        generation=1,
        content_sha256="1" * 64,
    )
    post_fault = contract.InternalObservation(
        observation_id="post-fault-b2",
        observation_source_id="obs-source-post-fault-b2",
        kind="post_fault",
        observed_at="2026-08-05T10:00:01Z",
        process_disposition="absent",
        loopback_health_disposition="connection_refused",
        generation=None,
        content_sha256="2" * 64,
    )
    return contract.build_system_anatomy_frame_set(
        target_reference=contract.TARGET_REFERENCE,
        service_artifact_sha256=contract.EXPECTED_ARTIFACT_SHA256,
        policy_digest=contract.POLICY_DIGEST,
        catalog_digest=contract.CATALOG_DIGEST,
        baseline=baseline,
        post_fault=post_fault,
    )


def _candidate(frame, *, use_post_fault: bool = True) -> dict[str, Any]:
    evidence_id = (
        frame.observations[1].observation_id
        if use_post_fault
        else frame.observations[0].observation_id
    )
    return {
        "schema_version": contract.CANDIDATE_SCHEMA,
        "frame_digest": frame.frame_digest,
        "diagnosis": {
            "hypothesis": "The owned process is absent and the closed health read is refused.",
            "evidence_observation_ids": [evidence_id],
            "missing_evidence": [],
            "impact": "The authored-synthetic loopback target is absent.",
            "cause": "stopped_process",
        },
        "selected_runbook": contract.FORWARD_RUNBOOK,
        "expected_effect": "A fresh pinned generation 2 process becomes healthy.",
        "rollback_runbook_id": contract.ROLLBACK_RUNBOOK,
        "risk_tier": contract.RISK_TIER,
        "target": contract.TargetRef.frozen().to_dict(),
        "parameters": {},
        "uncertainty": "Low because both closed observations agree.",
        "operator_explanation": "The exact owned process is absent and the eligible pinned recovery is proposed without claiming success.",
        "success_claim": False,
        "executable_content": False,
    }


class _FakePreflight:
    def verify(self):
        return {
            "result": "c5_exact_sydney_provider_preflight_pass",
            "provider_prompt_transmitted": False,
            "model_inference_called": False,
            "external_state_changed": False,
        }


class _FakeProvider:
    is_live_capability = False

    def __init__(self, *, correction: bool = False):
        self.calls = 0
        self.correction = correction

    def invoke(self, frame: dict[str, Any], *, correction_ticket=None):
        self.calls += 1
        class _Frame:
            frame_digest = frame["frame_digest"]
            observations = tuple(
                type("Observation", (), item) for item in frame["observations"]
            )

        raw = _candidate(
            _Frame,
            use_post_fault=(not self.correction or self.calls == 2),
        )
        return live.ProviderCallResult(
            candidate=raw,
            metadata={
                "provider_contacted": False,
                "fixture_used": True,
                "raw_prompt_retained": False,
                "raw_response_retained": False,
                "provider_text_retained": False,
            },
        )


class _FakeHandle:
    def __init__(self, argv, digest):
        self.argv = list(argv)
        self.port = int(argv[6])
        self.nonce = argv[8]
        self.generation = int(argv[10])
        self.artifact_sha256 = contract.EXPECTED_ARTIFACT_SHA256
        self.python_executable_sha256 = digest
        self.pid = 1000 + self.generation
        self.terminated = False
        self.closed = False


class _FakeProcess:
    is_live_capability = False

    def __init__(self):
        self.handles: list[_FakeHandle] = []
        self.closed_generations: list[int] = []
        self.observation_count = 0

    def preflight(self, *, expected_python_sha256, expected_target_sha256):
        assert expected_target_sha256 == contract.EXPECTED_ARTIFACT_SHA256
        return {
            "python_executable_sha256": expected_python_sha256,
            "target_artifact_sha256": expected_target_sha256,
        }

    def start(self, argv, env, *, expected_python_sha256, expected_target_sha256, reservation):
        assert not any("GOOGLE" in key.upper() for key in env)
        reservation.prepare_exact_launch(port=int(argv[6]), host=contract.HOST)
        reservation.complete_handoff()
        handle = _FakeHandle(argv, expected_python_sha256)
        self.handles.append(handle)
        return handle

    def observe_process(self, handle):
        self.observation_count += 1
        return {
            "observation_id": f"obs-fake-process-{self.observation_count:04d}",
            "disposition": "absent" if handle.terminated else "alive",
            "owned": True,
            "pid": handle.pid,
            "argv_sha256": contract.canonical_sha256(handle.argv),
            "port": handle.port,
            "generation": handle.generation,
            "nonce": handle.nonce,
            "artifact_sha256": handle.artifact_sha256,
            "python_executable_sha256": handle.python_executable_sha256,
        }

    def terminate(self, handle):
        handle.terminated = True
        return True

    def close(self, handle):
        assert handle.terminated
        handle.closed = True
        self.closed_generations.append(handle.generation)

    def any_running(self):
        return any(not handle.terminated for handle in self.handles)


class _FakeHttp:
    is_live_capability = False

    def __init__(self, process):
        self.process = process
        self.count = 0

    def probe(self, host, port, path):
        self.count += 1
        active = [handle for handle in self.process.handles if not handle.terminated]
        if not active:
            return {
                "observation_id": f"obs-fake-http-{self.count:04d}",
                "status": "connection_refused",
                "host": host,
                "port": port,
                "path": path,
            }
        handle = active[-1]
        return {
            "observation_id": f"obs-fake-http-{self.count:04d}",
            "status": 200,
            "host": host,
            "port": port,
            "path": path,
            "body": {
                "schema_version": "emr4.c5_health_body.v1",
                "environment": contract.PLAN_ENVIRONMENT,
                "kind": contract.TARGET_KIND,
                "target_id": contract.TARGET_ID,
                "host": contract.HOST,
                "port": port,
                "nonce": handle.nonce,
                "generation": handle.generation,
                "artifact_sha256": handle.artifact_sha256,
                "state": "healthy",
            },
        }

    def any_listener(self, *, port):
        return any(not handle.terminated for handle in self.process.handles)


class _Reservation:
    host = contract.HOST
    port = PORT

    def __init__(self):
        self.released = False
        self.prepared = False

    def prepare_exact_launch(self, *, port, host):
        assert port == self.port and host == self.host and not self.prepared
        self.prepared = True
        return 12345

    def complete_handoff(self):
        assert self.prepared
        self.released = True

    def close(self):
        self.released = True


class _FakePortAllocator:
    is_live_capability = False

    def reserve(self):
        return _Reservation()

    def reserve_exact(self, port):
        assert port == PORT
        return _Reservation()


class _FakeDirectory:
    is_live_capability = False

    def __init__(self):
        self.path = str((live.ROOT / "synthetic-c5-task").resolve())
        self.removed = False

    def create_task_dir(self):
        return self.path

    def validate_owned_path(self, candidate):
        return str(Path(candidate).resolve()) == self.path and not self.removed

    def materialise_launch_metadata(self, candidate, metadata):
        assert self.validate_owned_path(candidate)
        assert metadata["host"] == contract.HOST
        return self.path + "/launch-metadata.json"

    def remove_task_dir(self, candidate):
        assert self.validate_owned_path(candidate)
        self.removed = True
        return True


def test_provider_request_is_exact_positive_reasoning_and_has_no_tools():
    frame = _frame()
    request = live.build_vertex_request(frame.to_dict())
    config = request["generationConfig"]
    assert config["thinkingConfig"] == {"thinkingBudget": 1024}
    assert config["maxOutputTokens"] == 2048
    assert config["candidateCount"] == 1
    assert config["temperature"] == 0
    serialized = json.dumps(request)
    assert "tools" not in request
    assert "retrieval" not in serialized.lower()
    assert str(PORT) not in serialized


def test_provider_attempt_metadata_drops_provider_text_and_unknown_fields():
    safe = live._safe_provider_attempt_metadata(
        {
            "provider_contacted": True,
            "http_status": 200,
            "request_sha256": "a" * 64,
            "usage": {"promptTokenCount": 12, "unknown": 99},
            "raw_provider_text": "must never persist",
            "credential": "must never persist",
        }
    )
    assert safe == {
        "provider_contacted": True,
        "http_status": 200,
        "request_sha256": "a" * 64,
        "usage": {"promptTokenCount": 12},
    }


def test_vertex_cell_strictly_extracts_one_candidate_without_retaining_raw(monkeypatch):
    frame = _frame()
    packet = {
        "candidates": [
            {
                "finishReason": "STOP",
                "content": {"parts": [{"text": json.dumps(_candidate(frame))}]},
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 100,
            "candidatesTokenCount": 50,
            "thoughtsTokenCount": 25,
            "totalTokenCount": 175,
        },
        "modelVersion": contract.PROVIDER_MODEL,
    }

    class _Credentials:
        token = "synthetic-test-token"

    class _Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def geturl(self):
            return live.PROVIDER_URL

        def read(self, _limit):
            return json.dumps(packet).encode("utf-8")

    class _Opener:
        def open(self, _request, timeout):
            assert timeout == 45
            return _Response()

    cell = live.C5VertexProviderCell()
    monkeypatch.setattr(cell, "_credentials", lambda: _Credentials())
    monkeypatch.setattr(cell, "_opener", lambda: _Opener())
    result = cell.invoke(frame.to_dict())
    assert result.candidate["frame_digest"] == frame.frame_digest
    assert result.metadata["model_version"] == contract.PROVIDER_MODEL
    assert result.metadata["raw_provider_response_retained"] is False
    assert result.metadata["raw_prompt_retained"] is False
    assert result.metadata["provider_text_retained"] is False


def test_correction_failure_consumes_second_store_call():
    frame = _frame()
    store = contract.C5SharedStore()
    correlation_id = "93000000-0000-4000-8000-000000000222"
    store.reserve_provider_attempt(
        correlation_id=correlation_id,
        request_metadata=contract.build_provider_request_metadata(),
        frame_digest=frame.frame_digest,
    )
    candidate, denial = contract.parse_recovery_candidate(
        _candidate(frame, use_post_fault=False), "2026-08-05T10:00:02Z"
    )
    assert denial is None and candidate is not None
    proof = contract.proofread_candidate(candidate, frame)
    assert not proof.admitted and proof.correction_ticket is not None
    store.record_provider_candidate(
        correlation_id=correlation_id,
        frame=frame,
        candidate=candidate,
        disposition=proof,
    )
    store.record_provider_failure(
        correlation_id,
        "transport",
        correction_ticket=proof.correction_ticket,
    )
    state = store.provider_attempts[correlation_id]
    assert state.call_count == 2
    assert state.state == "closed_failed"


def test_health_readiness_retries_only_connection_refused(monkeypatch):
    probe = HttpReadbackProbe()
    observations = [
        {"status": "connection_refused"},
        {"status": 200, "body": "{}"},
    ]
    monkeypatch.setattr(probe, "probe", lambda *_args: observations.pop(0))
    result = probe.probe_until_healthy("127.0.0.1", PORT, "/healthz")
    assert result["status"] == 200
    assert observations == []


def test_provider_free_full_orchestration_closes_generation_one_and_all_resources():
    process = _FakeProcess()
    provider = _FakeProvider(correction=True)
    evidence, ledger = live.run_serial_rehearsal(
        source_head="a" * 40,
        preexecution_receipt_sha256="b" * 64,
        preflight=_FakePreflight(),
        provider=provider,
        process=process,
        http=_FakeHttp(process),
        port_allocator=_FakePortAllocator(),
        directory=_FakeDirectory(),
        now=lambda: NOW,
    )
    assert provider.calls == 2
    assert process.closed_generations == [1, 2]
    assert evidence["attempt_receipt"]["result"] == "live_development_recovery_verified"
    assert evidence["cleanup_receipt"]["result"] == "cleanup_verified"
    assert evidence["result"].endswith("terminal_failure")
    assert evidence["terminal_reason_code"] == "cleanup_or_accounting_not_verified"
    assert ledger["provider_calls_consumed"] == 0
    assert evidence["operation_counters"]["provider_calls"] == 0
    assert evidence["retention"] == {
        "raw_prompt_retained": False,
        "raw_response_retained": False,
        "provider_text_retained": False,
        "thought_content_retained": False,
        "credential_or_token_retained": False,
        "patient_or_product_data_retained": False,
    }


def test_preexecution_receipt_binds_five_sources_and_exact_review(monkeypatch, tmp_path):
    source_review = tmp_path / "review.json"
    ariadne = tmp_path / "ariadne.json"
    source_review.write_text(
        json.dumps(
            {
                "status": "completed",
                "transport": "antigravity_new_project_bound_readonly_worktree",
                "decision": "pass",
                "head_before": "c" * 40,
                "head_after": "c" * 40,
                "dirty_after": False,
                "model": "gemini-3.6-flash-high",
                "reasoning_effort": "high",
            }
        ),
        encoding="utf-8",
    )
    ariadne.write_text(
        json.dumps(
            {
                "status": "passed",
                "continuation_event": "pre_sprint_planning",
                "planned_action": "execute_frozen_serial_c5_live_rehearsal",
                "rehydration_sources": live.REHYDRATION_SOURCES,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        live,
        "_current_source_state",
        lambda: (
            "c" * 40,
            live.TARGET_BRANCH,
            {
                "master": live.PROTECTED_HEAD,
                "handoff_current": live.PROTECTED_HEAD,
                "origin_master": live.PROTECTED_HEAD,
                "origin_handoff_current": live.PROTECTED_HEAD,
            },
        ),
    )
    monkeypatch.setattr(
        live,
        "_artifact_hashes",
        lambda: {f"artifact-{index}": str(index) * 64 for index in range(1, 7)},
    )
    monkeypatch.setattr(
        live,
        "_repository_relative",
        lambda _path, prefix: (
            "repository://orchestration/agent_inbox/antigravity/review.json"
            if "antigravity" in prefix
            else "repository://orchestration/agent_inbox/codex/ariadne.json"
        ),
    )
    receipt = live.build_preexecution_receipt(
        source_review_path=source_review,
        ariadne_receipt_path=ariadne,
        now=lambda: NOW,
    )
    assert receipt["status"] == "passed"
    assert receipt["source_head"] == "c" * 40
    assert receipt["ariadne_receipt"]["rehydration_sources"] == live.REHYDRATION_SOURCES
    assert receipt["provider"]["reserved_cost_per_call_usd"] == 0.25


def test_preexecution_and_occupied_schemas_are_closed():
    for schema_path in (live.PREEXECUTION_SCHEMA, live.OCCUPIED_EVIDENCE_SCHEMA):
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        assert schema["additionalProperties"] is False


def test_live_runner_is_not_product_mounted_and_api_contract_stays_empty():
    source = (live.ROOT / "scripts/model_required_bureau_c5_live.py").read_text(
        encoding="utf-8"
    )
    assert "from app" not in source
    assert "import app" not in source
    assert "shell=True" not in source
    assert "os.system(" not in source
    assert "os.popen(" not in source
    import yaml

    api = yaml.safe_load(
        (
            live.ROOT
            / "docs/api-spine/openapi/technical-control-live-development-recovery-commands.yaml"
        ).read_text(encoding="utf-8")
    )
    assert api["paths"] == {}
    assert api["servers"] == []
    assert api["x-emr4-current-backend-alignment"]["mounted"] is False
