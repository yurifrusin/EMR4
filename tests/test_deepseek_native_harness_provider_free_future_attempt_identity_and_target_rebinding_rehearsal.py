from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import pytest

from orchestration_harness import native_post_hmr_future_attempt_materialisation as base
from orchestration_harness import native_post_hmr_future_attempt_rebinding as rebinding
from orchestration_harness import native_post_hmr_pre_request_controller as controller
from orchestration_harness import native_post_hmr_pre_request_diagnostic as diagnostic
from scripts import (
    deepseek_native_harness_provider_free_future_attempt_identity_and_target_rebinding_rehearsal as rehearsal,
)


CONTRACT = json.loads(rehearsal.CONTRACT_PATH.read_bytes())
IDENTITY = CONTRACT["fresh_identity"]
PREDECESSOR = CONTRACT["accepted_materialisation"]["fixture_identity"]
TARGET = CONTRACT["target_binding"]["relative_path"]
BINDINGS = CONTRACT["rebound_source_bindings"]


def _payloads() -> tuple[bytes, bytes]:
    runner, helper, observed, _ = rehearsal.source_payloads(CONTRACT)
    assert observed == BINDINGS
    return runner, helper


def _materialize(parent: Path) -> tuple[Path, dict]:
    runner, helper = _payloads()
    reading = rebinding.materialize_rebound_future_attempt(
        disposable_parent=parent,
        operation_id=IDENTITY["operation_id"],
        attempt_id=IDENTITY["attempt_id"],
        candidate_source=IDENTITY["candidate_source"],
        target_path=TARGET,
        runner_payload=runner,
        helper_payload=helper,
        controller_payload=rehearsal.CONTROLLER_PATH.read_bytes(),
        expected_bindings=BINDINGS,
    )
    return reading["root"], reading


def _sidecar() -> dict:
    return rehearsal._sidecar(CONTRACT)


def _assemble(
    parent: Path,
    *,
    sidecar: dict | bytes | None,
    counters: dict[str, int] | None = None,
) -> tuple[Path, dict]:
    root, _ = _materialize(parent)
    broker = controller.build_broker_reading(
        operation_id=IDENTITY["operation_id"],
        attempt_id=IDENTITY["attempt_id"],
        candidate_source=IDENTITY["candidate_source"],
        counters=counters,
    )
    rebinding.write_broker_fixture(root, broker)
    if isinstance(sidecar, dict):
        rebinding.write_sidecar_fixture(root, sidecar)
    elif isinstance(sidecar, bytes):
        base._write_exclusive(base._path(root, base.SIDECAR_RELATIVE_PATH), sidecar)
    terminal = rebinding.assemble_controller_terminal(
        root,
        operation_id=IDENTITY["operation_id"],
        attempt_id=IDENTITY["attempt_id"],
        candidate_source=IDENTITY["candidate_source"],
        target_path=TARGET,
        expected_bindings=BINDINGS,
    )
    return root, terminal


def test_contract_uses_machine_resolved_full_fresh_identity() -> None:
    contract = rehearsal.load_contract()
    assert len(contract["planning_source"]) == 40
    assert contract["fresh_identity"]["candidate_source"] == contract["planning_source"]
    assert all(
        contract["fresh_identity"][key]
        != contract["accepted_materialisation"]["fixture_identity"][key]
        for key in ("operation_id", "attempt_id", "candidate_source")
    )


def test_runner_rebinding_is_exact_single_and_reversible() -> None:
    accepted_contract = rehearsal.accepted_materialisation.load_contract()
    accepted_runner, _, _ = rehearsal.accepted_materialisation._source_payloads(
        accepted_contract
    )
    payload, reading = rebinding.rebind_future_runner_source(
        accepted_runner,
        expected_accepted_sha256=CONTRACT["accepted_materialisation"][
            "source_bindings"
        ]["future_runner_sha256"],
        consumed_target_path=CONTRACT["accepted_materialisation"][
            "consumed_target_path"
        ],
        target_path=TARGET,
    )
    assert hashlib.sha256(payload).hexdigest() == BINDINGS["future_runner_sha256"]
    assert reading["reverse_binding_exact"] is True
    assert reading["target_literal_count"] == 1
    assert reading["consumed_target_absent"] is True


@pytest.mark.parametrize(
    "target",
    [
        "/workspace/authored_synthetic_control_probe.py",
        "C:/workspace/authored_synthetic_control_probe.py",
        "//server/share/authored_synthetic_control_probe.py",
        "workspace\\authored_synthetic_control_probe.py",
        "workspace/../authored_synthetic_control_probe.py",
        "./workspace/authored_synthetic_control_probe.py",
        "workspace/other.py",
        "other/authored_synthetic_control_probe.py",
        "workspace/authored_synthetic_control_probe.py/extra",
        "workspace/authored_synthetic_control_probé.py",
        "",
    ],
)
def test_target_is_literal_allowlisted_relative_ascii(target: str) -> None:
    with pytest.raises(
        rebinding.FutureAttemptRebindingError, match="target_path_invalid"
    ):
        rebinding.validate_target_path(target)


def test_target_binding_hash_and_authority_are_closed() -> None:
    binding = rebinding.build_target_binding(TARGET)
    assert binding == CONTRACT["target_binding"]
    assert binding["occupied_target_use_authorized"] is False
    assert binding["coordinate_sha256"] == hashlib.sha256(TARGET.encode()).hexdigest()


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        ({"classification": "descriptive"}, "target_classification_invalid"),
        ({"relative_path": "workspace/other.py"}, "target_path_invalid"),
        ({"coordinate_sha256": "0" * 64}, "target_coordinate_sha256_invalid"),
        ({"occupied_target_use_authorized": True}, "target_use_authority_invalid"),
    ],
)
def test_target_binding_mutations_reject(mutation: dict, error: str) -> None:
    binding = {**CONTRACT["target_binding"], **mutation}
    with pytest.raises(rebinding.FutureAttemptRebindingError, match=error):
        rebinding.validate_target_binding(binding)


def test_runner_hash_and_literal_count_substitutions_reject() -> None:
    accepted_contract = rehearsal.accepted_materialisation.load_contract()
    accepted_runner, _, _ = rehearsal.accepted_materialisation._source_payloads(
        accepted_contract
    )
    kwargs = {
        "expected_accepted_sha256": CONTRACT["accepted_materialisation"][
            "source_bindings"
        ]["future_runner_sha256"],
        "consumed_target_path": CONTRACT["accepted_materialisation"][
            "consumed_target_path"
        ],
        "target_path": TARGET,
    }
    with pytest.raises(
        rebinding.FutureAttemptRebindingError,
        match="accepted_future_runner_sha256_mismatch",
    ):
        rebinding.rebind_future_runner_source(accepted_runner + b"\n", **kwargs)
    with pytest.raises(
        rebinding.FutureAttemptRebindingError,
        match="consumed_target_literal_count_invalid",
    ):
        rebinding.rebind_future_runner_source(
            accepted_runner.replace(
                json.dumps(kwargs["consumed_target_path"]).encode(), b'"other"'
            ),
            **{
                **kwargs,
                "expected_accepted_sha256": hashlib.sha256(
                    accepted_runner.replace(
                        json.dumps(kwargs["consumed_target_path"]).encode(), b'"other"'
                    )
                ).hexdigest(),
            },
        )


def test_helper_contains_only_fresh_identity() -> None:
    _, helper = _payloads()
    for value in IDENTITY.values():
        assert helper.count(json.dumps(value).encode()) == 1
    for value in PREDECESSOR.values():
        assert value.encode() not in helper


@pytest.mark.parametrize("field", ["operation_id", "attempt_id", "candidate_source"])
def test_partial_helper_identity_rebinding_rejects_materialisation(
    tmp_path: Path, field: str
) -> None:
    runner, _ = _payloads()
    partial = dict(IDENTITY)
    partial[field] = PREDECESSOR[field]
    helper = diagnostic.build_helper_source(**partial)
    with pytest.raises(
        rebinding.FutureAttemptRebindingError,
        match="materialisation_source_binding_mismatch",
    ):
        rebinding.materialize_rebound_future_attempt(
            disposable_parent=tmp_path,
            operation_id=IDENTITY["operation_id"],
            attempt_id=IDENTITY["attempt_id"],
            candidate_source=IDENTITY["candidate_source"],
            target_path=TARGET,
            runner_payload=runner,
            helper_payload=helper,
            controller_payload=rehearsal.CONTROLLER_PATH.read_bytes(),
            expected_bindings=BINDINGS,
        )


def test_materialises_exact_canonical_initial_tree_without_target_file(
    tmp_path: Path,
) -> None:
    root, reading = _materialize(tmp_path)
    assert reading["files"] == sorted(base.INITIAL_PATHS)
    assert reading["manifest"]["source_bindings"] == BINDINGS
    assert reading["manifest"]["target_binding"] == CONTRACT["target_binding"]
    assert reading["manifest"]["occupied_launch_authorized"] is False
    assert all(
        value is False for value in reading["manifest"]["execution_authority"].values()
    )
    assert all(
        value is False for value in reading["manifest"]["raw_retention"].values()
    )
    assert not (root / Path(TARGET)).exists()
    bundle = base._path(root, base.BUNDLE_RELATIVE_PATH)
    assert bundle.read_bytes() == rebinding.bundle_manifest_bytes(reading["manifest"])


@pytest.mark.parametrize("altered", ["runner", "helper", "controller"])
def test_source_substitution_fails_before_materialisation(
    tmp_path: Path, altered: str
) -> None:
    runner, helper = _payloads()
    controller_payload = rehearsal.CONTROLLER_PATH.read_bytes()
    if altered == "runner":
        runner += b"\n"
    elif altered == "helper":
        helper += b"\n"
    else:
        controller_payload += b"\n"
    with pytest.raises(
        rebinding.FutureAttemptRebindingError,
        match="materialisation_source_binding_mismatch",
    ):
        rebinding.materialize_rebound_future_attempt(
            disposable_parent=tmp_path,
            operation_id=IDENTITY["operation_id"],
            attempt_id=IDENTITY["attempt_id"],
            candidate_source=IDENTITY["candidate_source"],
            target_path=TARGET,
            runner_payload=runner,
            helper_payload=helper,
            controller_payload=controller_payload,
            expected_bindings=BINDINGS,
        )
    assert not (tmp_path / IDENTITY["attempt_id"]).exists()


def test_preexisting_attempt_root_and_relative_parent_fail(tmp_path: Path) -> None:
    runner, helper = _payloads()

    def invoke(parent: Path) -> None:
        rebinding.materialize_rebound_future_attempt(
            disposable_parent=parent,
            operation_id=IDENTITY["operation_id"],
            attempt_id=IDENTITY["attempt_id"],
            candidate_source=IDENTITY["candidate_source"],
            target_path=TARGET,
            runner_payload=runner,
            helper_payload=helper,
            controller_payload=rehearsal.CONTROLLER_PATH.read_bytes(),
            expected_bindings=BINDINGS,
        )

    with pytest.raises(
        rebinding.FutureAttemptRebindingError, match="disposable_parent_invalid"
    ):
        invoke(Path("relative"))
    (tmp_path / IDENTITY["attempt_id"]).mkdir()
    with pytest.raises(
        rebinding.FutureAttemptRebindingError, match="attempt_root_must_be_absent"
    ):
        invoke(tmp_path)


def test_missing_extra_and_replaced_members_reject(tmp_path: Path) -> None:
    root, _ = _materialize(tmp_path)
    base._path(root, base.HELPER_RELATIVE_PATH).unlink()
    with pytest.raises(
        rebinding.FutureAttemptRebindingError, match="attempt_file_roster_invalid"
    ):
        rebinding.read_rebound_bundle(
            root,
            operation_id=IDENTITY["operation_id"],
            attempt_id=IDENTITY["attempt_id"],
            candidate_source=IDENTITY["candidate_source"],
            target_path=TARGET,
            expected_bindings=BINDINGS,
        )

    other = tmp_path / "other"
    other.mkdir()
    other_root, _ = _materialize(other)
    (other_root / "runner" / "extra.mjs").write_bytes(b"extra")
    with pytest.raises(
        rebinding.FutureAttemptRebindingError, match="attempt_member_unregistered"
    ):
        rebinding.read_rebound_bundle(
            other_root,
            operation_id=IDENTITY["operation_id"],
            attempt_id=IDENTITY["attempt_id"],
            candidate_source=IDENTITY["candidate_source"],
            target_path=TARGET,
            expected_bindings=BINDINGS,
        )

    third = tmp_path / "third"
    third.mkdir()
    third_root, _ = _materialize(third)
    base._path(third_root, base.RUNNER_RELATIVE_PATH).write_bytes(b"replacement")
    with pytest.raises(
        rebinding.FutureAttemptRebindingError,
        match="materialized_source_digest_mismatch",
    ):
        rebinding.read_rebound_bundle(
            third_root,
            operation_id=IDENTITY["operation_id"],
            attempt_id=IDENTITY["attempt_id"],
            candidate_source=IDENTITY["candidate_source"],
            target_path=TARGET,
            expected_bindings=BINDINGS,
        )


def test_noncanonical_malformed_and_runtime_identity_bundle_reject(
    tmp_path: Path,
) -> None:
    root, reading = _materialize(tmp_path)
    bundle = base._path(root, base.BUNDLE_RELATIVE_PATH)
    bundle.write_text(json.dumps(reading["manifest"]) + "\n", encoding="utf-8")
    with pytest.raises(
        rebinding.FutureAttemptRebindingError,
        match="bundle_manifest_canonical_bytes_required",
    ):
        rebinding.read_rebound_bundle(
            root,
            operation_id=IDENTITY["operation_id"],
            attempt_id=IDENTITY["attempt_id"],
            candidate_source=IDENTITY["candidate_source"],
            target_path=TARGET,
            expected_bindings=BINDINGS,
        )
    bundle.write_bytes(rebinding.bundle_manifest_bytes(reading["manifest"]))
    with pytest.raises(
        rebinding.FutureAttemptRebindingError, match="bundle_runtime_identity_mismatch"
    ):
        rebinding.read_rebound_bundle(
            root,
            operation_id=IDENTITY["operation_id"],
            attempt_id="different-attempt",
            candidate_source=IDENTITY["candidate_source"],
            target_path=TARGET,
            expected_bindings=BINDINGS,
        )
    bundle.write_bytes(b"not-json")
    with pytest.raises(
        rebinding.FutureAttemptRebindingError, match="bundle_manifest_json_invalid"
    ):
        rebinding.read_rebound_bundle(
            root,
            operation_id=IDENTITY["operation_id"],
            attempt_id=IDENTITY["attempt_id"],
            candidate_source=IDENTITY["candidate_source"],
            target_path=TARGET,
            expected_bindings=BINDINGS,
        )


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        ({"occupied_launch_authorized": True}, "occupied_launch_authority_invalid"),
        ({"descriptive_state": "postpublication"}, "bundle_keys_invalid"),
    ],
)
def test_bundle_top_level_mutations_reject(mutation: dict, error: str) -> None:
    manifest = rebinding.build_bundle_manifest(
        operation_id=IDENTITY["operation_id"],
        attempt_id=IDENTITY["attempt_id"],
        candidate_source=IDENTITY["candidate_source"],
        source_bindings=BINDINGS,
        target_path=TARGET,
    )
    with pytest.raises(rebinding.FutureAttemptRebindingError, match=error):
        rebinding.validate_bundle_manifest({**manifest, **mutation})


def test_bundle_execution_and_raw_flags_reject() -> None:
    manifest = rebinding.build_bundle_manifest(
        operation_id=IDENTITY["operation_id"],
        attempt_id=IDENTITY["attempt_id"],
        candidate_source=IDENTITY["candidate_source"],
        source_bindings=BINDINGS,
        target_path=TARGET,
    )
    executing = json.loads(json.dumps(manifest))
    executing["execution_authority"]["worker_process_authorized"] = True
    retaining = json.loads(json.dumps(manifest))
    retaining["raw_retention"]["raw_stream_retained"] = True
    with pytest.raises(
        rebinding.FutureAttemptRebindingError, match="execution_authority_invalid"
    ):
        rebinding.validate_bundle_manifest(executing)
    with pytest.raises(
        rebinding.FutureAttemptRebindingError, match="raw_retention_invalid"
    ):
        rebinding.validate_bundle_manifest(retaining)


@pytest.mark.parametrize(
    ("sidecar", "counters", "coordinate", "supported"),
    [
        (_sidecar(), None, "post_hmr_pre_request_failure", True),
        (
            _sidecar(),
            {"request_count": 1},
            "post_hmr_request_boundary_unresolved",
            False,
        ),
        (None, None, "native_harness_terminal_failure", False),
        (b"not-json", None, "native_harness_terminal_failure", False),
    ],
)
def test_terminal_coordinates_remain_closed(
    tmp_path: Path,
    sidecar: dict | bytes | None,
    counters: dict[str, int] | None,
    coordinate: str,
    supported: bool,
) -> None:
    _, terminal = _assemble(tmp_path, sidecar=sidecar, counters=counters)
    assert terminal["coordinate"] == coordinate
    assert terminal["pre_request_supported"] is supported
    assert terminal["target_binding"] == CONTRACT["target_binding"]
    assert terminal["source_bindings"] == BINDINGS
    assert terminal["occupied_launch_authorized"] is False


@pytest.mark.parametrize("counter", controller.BROKER_COUNTERS)
def test_each_nonzero_broker_counter_blocks_pre_request_claim(
    tmp_path: Path, counter: str
) -> None:
    _, terminal = _assemble(tmp_path, sidecar=_sidecar(), counters={counter: 1})
    assert terminal["coordinate"] == "post_hmr_request_boundary_unresolved"
    assert terminal["broker_zero"] is False


def test_invalid_broker_rejects_instead_of_falling_back(tmp_path: Path) -> None:
    root, _ = _materialize(tmp_path)
    rebinding.write_sidecar_fixture(root, _sidecar())
    base._path(root, base.BROKER_RELATIVE_PATH).write_bytes(b"not-json")
    with pytest.raises(controller.PostHmrControllerError, match="broker_json_invalid"):
        rebinding.assemble_controller_terminal(
            root,
            operation_id=IDENTITY["operation_id"],
            attempt_id=IDENTITY["attempt_id"],
            candidate_source=IDENTITY["candidate_source"],
            target_path=TARGET,
            expected_bindings=BINDINGS,
        )


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        ({"coordinate": "descriptive-state"}, "controller_terminal_coordinate_invalid"),
        ({"broker_zero": 0}, "controller_terminal_boolean_invalid"),
        ({"pre_request_supported": False}, "controller_terminal_relationship_invalid"),
        ({"stage": "postpublication"}, "stage_invalid"),
        ({"raw_stream_read": True}, "controller_terminal_raw_or_authority_invalid"),
        (
            {"occupied_launch_authorized": True},
            "controller_terminal_raw_or_authority_invalid",
        ),
    ],
)
def test_terminal_vocabulary_types_relationships_and_authority_reject(
    tmp_path: Path, mutation: dict, error: str
) -> None:
    _, terminal = _assemble(tmp_path, sidecar=_sidecar())
    with pytest.raises(
        (rebinding.FutureAttemptRebindingError, diagnostic.PostHmrDiagnosticError),
        match=error,
    ):
        rebinding.validate_controller_terminal({**terminal, **mutation})


def test_terminal_is_canonical_exclusive_and_has_no_consumed_host_path(
    tmp_path: Path,
) -> None:
    root, terminal = _assemble(tmp_path, sidecar=_sidecar())
    terminal_path = base._path(root, base.TERMINAL_RELATIVE_PATH)
    payload = terminal_path.read_bytes()
    assert payload == rebinding.controller_terminal_bytes(terminal)
    assert (
        CONTRACT["accepted_materialisation"]["consumed_target_path"].encode()
        not in payload
    )
    with pytest.raises(
        rebinding.FutureAttemptRebindingError,
        match="controller_terminal_must_be_absent",
    ):
        rebinding.assemble_controller_terminal(
            root,
            operation_id=IDENTITY["operation_id"],
            attempt_id=IDENTITY["attempt_id"],
            candidate_source=IDENTITY["candidate_source"],
            target_path=TARGET,
            expected_bindings=BINDINGS,
        )


def test_all_schemas_generated_artifacts_and_zero_boundary_are_canonical() -> None:
    expected = rehearsal._expected_outputs()
    assert all(path.read_bytes() == payload for path, payload in expected.items())
    for path in (
        rehearsal.CONTRACT_SCHEMA_PATH,
        rehearsal.BUNDLE_SCHEMA_PATH,
        rehearsal.TERMINAL_SCHEMA_PATH,
        rehearsal.EVIDENCE_SCHEMA_PATH,
    ):
        jsonschema.Draft202012Validator.check_schema(json.loads(path.read_bytes()))
    evidence = json.loads(rehearsal.EVIDENCE_PATH.read_bytes())
    jsonschema.Draft202012Validator(
        json.loads(rehearsal.EVIDENCE_SCHEMA_PATH.read_bytes())
    ).validate(evidence)
    assert evidence["terminal_matrix"]["scenario_count"] == 24
    assert evidence["transformation"]["target_literal_count"] == 1
    assert all(value == 0 for value in evidence["proof_boundary"].values())
    efficacy = json.loads(rehearsal.EFFICACY_PATH.read_bytes())
    assert efficacy["free_form_finite_control_fields"] == 0
    assert efficacy["occupied_harness_evidence"] is False
    assert efficacy["deepseek_performance_evidence"] is False


def test_plan_and_threat_freeze_non_authority_and_parallelism() -> None:
    plan = rehearsal.PLAN_PATH.read_text(encoding="utf-8")
    threat = (
        Path("docs/security") / f"{rehearsal.OPERATION_ID}-threat-model-delta.md"
    ).read_text(encoding="utf-8")
    for artifact in (plan, threat):
        assert "Date: 2026-08-21" in artifact
        assert "Timestamp: 2026-08-21T22:49:59.5125472+10:00" in artifact
    assert TARGET in plan
    assert CONTRACT["planning_source"] not in plan
    assert "No Node/Harness/broker/worker/model/provider process" in plan
    assert "DeepSeek Flash: `declined`" in plan
    assert "Gemini 3.7 Flash/high: `declined`" in plan
    assert "Native subagents: `declined`" in plan
    assert "no ordinary-practice feature-flag, allowlist" in plan
    assert "opens no JavaScript execution" in threat


def test_accepted_materialiser_and_predecessor_bindings_remain_unchanged() -> None:
    accepted = CONTRACT["accepted_materialisation"]
    accepted_contract = rehearsal.accepted_materialisation.load_contract()
    runner, helper, observed = rehearsal.accepted_materialisation._source_payloads(
        accepted_contract
    )
    assert (
        hashlib.sha256(runner).hexdigest()
        == accepted["source_bindings"]["future_runner_sha256"]
    )
    assert (
        hashlib.sha256(helper).hexdigest()
        == accepted["source_bindings"]["generated_helper_sha256"]
    )
    assert (
        observed["materializer_module_sha256"]
        == accepted_contract["source_bindings"]["materializer_module_sha256"]
    )
