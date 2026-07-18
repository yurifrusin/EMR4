from __future__ import annotations

import copy

import pytest

from scripts.bernie_t3r2_approval_check import (
    assert_packet_blocked,
    build_status,
    load_packet,
)


def test_t3r2_approval_packet_is_balanced_and_blocked():
    assert_packet_blocked(load_packet())


def test_t3r2_status_is_aggregate_and_performs_no_calls():
    assert build_status() == {
        "schema_version": "emr4.bernie.t3r2_approval_status.v1",
        "decision": "blocked",
        "selected_case_count": 24,
        "candidate_lane_count": 2,
        "maximum_scheduled_samples": 96,
        "provider_calls_performed": False,
        "external_calls_ready": False,
        "awaiting": [
            "exact_model_revisions",
            "privacy_and_retention_approval",
            "kill_switch_verification",
            "explicit_yuri_run_approval",
        ],
    }


@pytest.mark.parametrize(
    "mutate",
    [
        lambda packet: packet.update(decision="approved"),
        lambda packet: packet.update(authorizes_provider_calls=True),
        lambda packet: packet["execution_limits"].update(max_scheduled_samples=97),
        lambda packet: packet["execution_limits"].update(automatic_retries=True),
        lambda packet: packet["privacy_and_retention"].update(patient_or_practice_data_allowed=True),
        lambda packet: packet["authority"].update(runtime_wiring=True),
    ],
)
def test_t3r2_checker_rejects_gate_limit_privacy_or_authority_drift(mutate):
    packet = copy.deepcopy(load_packet())
    mutate(packet)
    with pytest.raises(AssertionError):
        assert_packet_blocked(packet)
