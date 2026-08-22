from __future__ import annotations

import json

from scripts import (
    raisa_authored_synthetic_native_harness_integrated_runner_first_controlled_development_rehearsal
    as subject,
)


def test_occupied_terminal_is_one_consumed_traceable_factory_failure() -> None:
    terminal = json.loads(subject.PATH_BINDINGS["TERMINAL_PATH"].read_bytes())
    consumed = json.loads(subject.PATH_BINDINGS["CONSUMED_PATH"].read_bytes())
    assert consumed == {
        "attempt_id": subject.ATTEMPT_ID,
        "automatic_retry_count": 0,
        "candidate_source": "ae41d5487a52be7ed2f07fbb1e8612eab5359a17",
        "operation_id": subject.OPERATION_ID,
        "resume_permitted": False,
        "schema_version": "ariadne.synthetic_native_worker_consumed.v1",
        "state": "consumed",
    }
    assert terminal["result"] == "failed_closed"
    assert terminal["process"]["native_process_count"] == 1
    assert terminal["process"]["harness_exit_code"] == 1
    assert terminal["hmr_events"] == [
        "sentinel_activated",
        "stock_headless_hmr_ready",
    ]
    assert terminal["runner"]["failure_stage"] == "factory"
    assert terminal["runner"]["request_count"] == 0
    assert terminal["runner"]["tool_names"] == []
    assert terminal["runner"]["tool_result_count"] == 0
    assert terminal["runner"]["edit_argument_result"] == {
        "coordinate": None,
        "pre_dispatch_decision": "not_observed",
    }
    assert terminal["broker"] == {
        "provider_call_completed": 0,
        "provider_call_failed": 0,
        "provider_call_started": 0,
        "request_rejected": 0,
    }
    assert terminal["candidate"]["changed_paths"] == []
    assert (
        terminal["candidate"]["final_sha256"]
        == "9606d9341e6b7e53f4ee9007d7518145322968b2d0bc156622928c33ab97d4f8"
    )
    assert terminal["automatic_retry_count"] == 0
    assert terminal["fallback_count"] == 0
    assert terminal["auxiliary_model_call_count"] == 0
    assert terminal["cleanup"] == {
        "attempt_root_absent": True,
        "broker_absent": True,
        "harness_absent": True,
        "provider_key_present_in_worker_environment": False,
        "raw_logs_retained": False,
        "raw_session_retained": False,
    }


def test_efficacy_requires_provider_free_factory_diagnosis() -> None:
    value = json.loads(
        (subject.OPERATION_ROOT / "efficacy-reading.json").read_bytes()
    )
    assert value["result"] == "traceable_worker_failure"
    assert value["useful_output"] is False
    assert value["provider_reached"] is False
    assert value["failure_coordinate"] == "integrated_runner_factory_pre_request_rejected"
    assert value["observed"]["automatic_retries"] == 0
    assert value["traceability"]["cleanup_proved_complete"] is True
    assert value["parallelism"]["gemini"]["disposition"] == "declined_no_candidate"
