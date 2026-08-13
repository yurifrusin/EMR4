from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_disposable_postgresql_cf_d2_event_cue_behavior_transaction_rehearsal as harness,
)


ROOT = Path(__file__).resolve().parents[1]


def _contract() -> dict:
    return json.loads(harness.CONTRACT_PATH.read_text(encoding="utf-8"))


def test_contract_schema_digest_sources_and_exact_artifact_pass() -> None:
    contract, sources, artifact = harness.verify_contract()
    assert contract["result"] == harness.PASS_RESULT
    assert len(sources) == 9
    assert len(artifact) == 12022
    assert hashlib.sha256(artifact).hexdigest() == contract["artifact"]["sha256"]
    assert [item["name"] for item in contract["protocols"]] == [
        "admit_terminal",
        "coalesce_pending",
        "advance_contiguous_checkpoint",
        "record_dispatch_attempt",
        "record_reconciliation",
    ]


def test_contract_and_evidence_schemas_are_closed() -> None:
    contract = _contract()
    schema = json.loads(harness.CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(contract)
    assert schema["additionalProperties"] is False
    evidence_schema = json.loads(harness.EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    assert evidence_schema["additionalProperties"] is False


def test_sixty_four_hostile_contract_mutations_fail_closed() -> None:
    contract = _contract()
    assert harness.hostile_mutations_rejected(contract) == 64
    changed = copy.deepcopy(contract)
    changed["docker_profile"]["network_mode"] = "bridge"
    with pytest.raises(harness.RehearsalFailure, match="contract_digest_mismatch"):
        harness._validate_contract_candidate(changed)


def test_plan_design_and_threat_delta_are_timestamped_and_narrow() -> None:
    paths = (
        ROOT / "docs/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-behavior-transaction-rehearsal-plan.md",
        ROOT / "docs/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-behavior-transaction-rehearsal-design.md",
        ROOT / "docs/security/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-behavior-transaction-rehearsal-threat-model-delta.md",
    )
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "Date: 2026-08-13" in text
        assert "Timestamp: 2026-08-13T" in text
        assert "Australia/Brisbane" in text
    plan = paths[0].read_text(encoding="utf-8")
    assert "six fixed serial" in plan.lower() or "six serial" in plan.lower()
    assert "concurrency" in plan
    assert "restart" in plan
    assert "docs/branding/" in plan


def test_container_profile_is_networkless_tmpfs_exact_cached_image() -> None:
    contract = _contract()
    argv = harness.catalogue.build_container_argv(
        "docker.exe",
        contract["docker_profile"]["container_name_prefix"] + "0123456789abcdef",
        "a" * 32,
        contract,
    )
    joined = " ".join(argv)
    assert "--pull never" in joined
    assert "--network none" in joined
    assert "--tmpfs /var/lib/postgresql/data:" in joined
    assert "--restart no" in joined
    assert "--publish" not in argv
    assert "--volume" not in argv
    assert "--mount" not in argv


def test_fixed_protocol_sql_has_fencing_atomicity_and_freshness_boundary() -> None:
    source = Path(harness.__file__).read_text(encoding="utf-8")
    for fragment in (
        "ownership_fenced",
        "identity_conflict",
        "coalesce_precondition_failed",
        "attempt_ordinal_out_of_sequence",
        "delivery_not_proved",
        "reconciliation_truth_table_invalid",
        "one_fresh_read_attempt_only",
        "FOR UPDATE",
        "ROLLBACK",
    ):
        assert fragment in source
    assert "future_freshness" not in harness.STATE_SQL


def test_source_has_no_generic_database_docker_or_network_surface() -> None:
    source = Path(harness.__file__).read_text(encoding="utf-8")
    for fragment in (
        "DATABASE_URL",
        "localhost",
        '"pull"',
        '"login"',
        '"build"',
        '"prune"',
        '"container", "ls"',
        '"image", "rm"',
        '"network", "connect"',
    ):
        assert fragment not in source
    assert "len(sys.argv) != 1" in source


def test_evidence_schema_requires_exact_six_five_and_rollback_census() -> None:
    schema = json.loads(harness.EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["properties"]["scenario_groups"]["minItems"] == 6
    assert schema["properties"]["scenario_groups"]["maxItems"] == 6
    assert schema["properties"]["protocols_proved"]["minItems"] == 5
    assert schema["properties"]["rollback_probes"]["minItems"] == 3
    assert schema["properties"]["denied_transition_probes"]["minItems"] == 8


def test_claim_boundary_refuses_concurrency_runtime_and_external_authority() -> None:
    contract = _contract()
    claim = contract["claim_boundary"]
    assert claim == harness.CLAIM_BOUNDARY
    assert contract["acceptance"]["concurrency_claim"] is False
    assert contract["acceptance"]["external_authority_or_fresh_read_claim"] is False
    assert contract["acceptance"]["runtime_or_product_wiring"] is False
    assert contract["effects"]["existing_database_or_source_connections"] == 0
    assert contract["effects"]["provider_calls"] == 0
    assert contract["effects"]["product_commands"] == 0


def test_passing_evidence_is_closed_minimized_and_complete() -> None:
    evidence = json.loads(harness.EVIDENCE_PATH.read_text(encoding="utf-8"))
    harness.validate_evidence(evidence)
    assert evidence["cleanup"]["status"] == "cleanup_verified"
    assert [item["id"] for item in evidence["scenario_groups"]] == _contract()[
        "scenario_groups"
    ]
    assert evidence["protocols_proved"] == [
        "admit_terminal",
        "coalesce_pending",
        "advance_contiguous_checkpoint",
        "record_dispatch_attempt",
        "record_reconciliation",
    ]
    assert len(evidence["rollback_probes"]) == 3
    assert len(evidence["denied_transition_probes"]) == 11
    assert len(evidence["lock_observations"]) == 5
    assert all(item["state_unchanged"] for item in evidence["rollback_probes"])
    assert all(
        item["state_unchanged"] for item in evidence["denied_transition_probes"]
    )
    assert all(
        item["required_subset_observed"] and not item["contention_claim"]
        for item in evidence["lock_observations"]
    )
