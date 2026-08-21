from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import pytest

from orchestration_harness import native_post_hmr_future_attempt_materialisation as materializer
from orchestration_harness import native_post_hmr_pre_request_controller as controller
from orchestration_harness import native_post_hmr_pre_request_diagnostic as diagnostic
from scripts import (
    deepseek_native_harness_provider_free_custom_runner_pre_request_failure_coordinate_diagnosis
    as accepted_diagnosis,
)
from scripts import (
    deepseek_native_harness_provider_free_future_runner_materialisation_and_controller_terminal_fixture_rehearsal
    as rehearsal,
)
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as accepted_runner,
)


CONTRACT = json.loads(rehearsal.CONTRACT_PATH.read_bytes())
OUTER_OPERATION_ID = rehearsal.OPERATION_ID
IDENTITY = CONTRACT["fixture_identity"]
OPERATION_ID = IDENTITY["operation_id"]
ATTEMPT_ID = IDENTITY["attempt_id"]
CANDIDATE_SOURCE = IDENTITY["candidate_source"]
BINDINGS = CONTRACT["source_bindings"]
EXPECTED_BINDINGS = {
    "future_runner_sha256": BINDINGS["future_runner_sha256"],
    "generated_helper_sha256": BINDINGS["generated_helper_sha256"],
    "controller_module_sha256": BINDINGS["controller_module_sha256"],
}


def _payloads() -> tuple[bytes, bytes]:
    runner_payload, helper_payload, observed = rehearsal._source_payloads(CONTRACT)
    assert observed == BINDINGS
    return runner_payload, helper_payload


def _materialize(parent: Path) -> tuple[Path, dict]:
    runner_payload, helper_payload = _payloads()
    reading = materializer.materialize_future_attempt(
        disposable_parent=parent,
        attempt_id=ATTEMPT_ID,
        operation_id=OPERATION_ID,
        candidate_source=CANDIDATE_SOURCE,
        runner_payload=runner_payload,
        helper_payload=helper_payload,
        controller_payload=rehearsal.CONTROLLER_PATH.read_bytes(),
        expected_runner_sha256=EXPECTED_BINDINGS["future_runner_sha256"],
        expected_helper_sha256=EXPECTED_BINDINGS["generated_helper_sha256"],
        expected_controller_sha256=EXPECTED_BINDINGS["controller_module_sha256"],
    )
    return reading["root"], reading


def _sidecar(
    *,
    stage: str = "loader_readiness_wait",
    cause: str = "operation_rejected",
    error_name: str = "Error",
) -> dict:
    return diagnostic.build_diagnostic_from_fixture(
        {"name": error_name, "constructor_name": error_name},
        operation_id=OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=CANDIDATE_SOURCE,
        stage=stage,
        cause_coordinate=cause,
    )


def _broker(*, counters: dict[str, int] | None = None) -> dict:
    return controller.build_broker_reading(
        operation_id=OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=CANDIDATE_SOURCE,
        counters=counters,
    )


def _assemble(
    parent: Path,
    *,
    sidecar: dict | bytes | None = None,
    counters: dict[str, int] | None = None,
) -> tuple[Path, dict]:
    root, _ = _materialize(parent)
    materializer.write_broker_fixture(root, _broker(counters=counters))
    if isinstance(sidecar, dict):
        materializer.write_sidecar_fixture(root, sidecar)
    elif isinstance(sidecar, bytes):
        (root / Path(*materializer.SIDECAR_RELATIVE_PATH.split("/"))).write_bytes(
            sidecar
        )
    terminal = materializer.assemble_controller_terminal(
        root,
        operation_id=OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=CANDIDATE_SOURCE,
        expected_bindings=EXPECTED_BINDINGS,
    )
    return root, terminal


def _read_bundle(root: Path) -> dict:
    return materializer.read_materialized_bundle(
        root,
        operation_id=OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=CANDIDATE_SOURCE,
        expected_bindings=EXPECTED_BINDINGS,
    )


def test_contract_schemas_and_outer_embedded_identities_are_exact() -> None:
    schemas = [
        json.loads(path.read_bytes())
        for path in (
            rehearsal.CONTRACT_SCHEMA_PATH,
            rehearsal.BUNDLE_SCHEMA_PATH,
            rehearsal.TERMINAL_SCHEMA_PATH,
            rehearsal.EVIDENCE_SCHEMA_PATH,
        )
    ]
    for schema in schemas:
        jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schemas[0]).validate(CONTRACT)
    assert OUTER_OPERATION_ID != OPERATION_ID
    assert OPERATION_ID.endswith("post-hmr-pre-request-diagnostic-sidecar-integration-rehearsal")
    assert ATTEMPT_ID == "future-post-hmr-sidecar-static-fixture-001"
    assert len(CANDIDATE_SOURCE) == 40
    assert CONTRACT["planning_source"] == "f1d3e782e7a35a19c219a4fbadd58997440bad58"


def test_every_semantic_source_binding_is_independently_exact() -> None:
    accepted_payload = accepted_runner.runner_source(accepted_diagnosis.TARGET_PATH)
    future_payload, helper_payload = _payloads()
    observed = {
        "accepted_runner_sha256": hashlib.sha256(accepted_payload).hexdigest(),
        "accepted_diagnostic_module_sha256": hashlib.sha256(
            rehearsal.DIAGNOSTIC_PATH.read_bytes()
        ).hexdigest(),
        "controller_module_sha256": hashlib.sha256(
            rehearsal.CONTROLLER_PATH.read_bytes()
        ).hexdigest(),
        "future_runner_sha256": hashlib.sha256(future_payload).hexdigest(),
        "generated_helper_sha256": hashlib.sha256(helper_payload).hexdigest(),
        "materializer_module_sha256": hashlib.sha256(
            rehearsal.MATERIALIZER_PATH.read_bytes()
        ).hexdigest(),
    }
    assert observed == BINDINGS
    assert len(set(observed.values())) == len(observed)


def test_helper_bytes_retain_accepted_embedded_identity() -> None:
    _, helper_payload = _payloads()
    text = helper_payload.decode("utf-8")
    assert OPERATION_ID in text
    assert ATTEMPT_ID in text
    assert CANDIDATE_SOURCE in text
    assert OUTER_OPERATION_ID not in text
    rejected = diagnostic.build_helper_source(
        operation_id=OUTER_OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=CONTRACT["planning_source"],
    )
    assert hashlib.sha256(rejected).hexdigest() != BINDINGS["generated_helper_sha256"]


def test_materialises_exact_initial_tree_and_canonical_bundle(tmp_path: Path) -> None:
    root, reading = _materialize(tmp_path)
    assert reading["files"] == sorted(materializer.INITIAL_PATHS)
    assert reading["runner_bytes"] == 6300
    assert reading["helper_bytes"] == 3110
    assert reading["manifest"]["path_roster"] == list(materializer.PATH_ROSTER)
    assert reading["manifest"]["source_bindings"] == EXPECTED_BINDINGS
    assert reading["manifest"]["occupied_launch_authorized"] is False
    assert all(value is False for value in reading["manifest"]["execution_authority"].values())
    assert all(value is False for value in reading["manifest"]["raw_retention"].values())
    bundle_path = root / Path(*materializer.BUNDLE_RELATIVE_PATH.split("/"))
    assert bundle_path.read_bytes() == materializer.bundle_manifest_bytes(
        reading["manifest"]
    )


@pytest.mark.parametrize(
    ("altered", "error"),
    [
        ("runner", "materialisation_source_binding_mismatch"),
        ("helper", "materialisation_source_binding_mismatch"),
        ("controller", "materialisation_source_binding_mismatch"),
    ],
)
def test_source_substitution_fails_before_materialisation(
    tmp_path: Path, altered: str, error: str
) -> None:
    runner_payload, helper_payload = _payloads()
    controller_payload = rehearsal.CONTROLLER_PATH.read_bytes()
    if altered == "runner":
        runner_payload += b"\n"
    elif altered == "helper":
        helper_payload += b"\n"
    else:
        controller_payload += b"\n"
    with pytest.raises(materializer.FutureAttemptMaterialisationError, match=error):
        materializer.materialize_future_attempt(
            disposable_parent=tmp_path,
            attempt_id=ATTEMPT_ID,
            operation_id=OPERATION_ID,
            candidate_source=CANDIDATE_SOURCE,
            runner_payload=runner_payload,
            helper_payload=helper_payload,
            controller_payload=controller_payload,
            expected_runner_sha256=EXPECTED_BINDINGS["future_runner_sha256"],
            expected_helper_sha256=EXPECTED_BINDINGS["generated_helper_sha256"],
            expected_controller_sha256=EXPECTED_BINDINGS["controller_module_sha256"],
        )
    assert not (tmp_path / ATTEMPT_ID).exists()


def test_relative_symlinked_and_preexisting_roots_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner_payload, helper_payload = _payloads()

    def invoke(parent: Path) -> None:
        materializer.materialize_future_attempt(
            disposable_parent=parent,
            attempt_id=ATTEMPT_ID,
            operation_id=OPERATION_ID,
            candidate_source=CANDIDATE_SOURCE,
            runner_payload=runner_payload,
            helper_payload=helper_payload,
            controller_payload=rehearsal.CONTROLLER_PATH.read_bytes(),
            expected_runner_sha256=EXPECTED_BINDINGS["future_runner_sha256"],
            expected_helper_sha256=EXPECTED_BINDINGS["generated_helper_sha256"],
            expected_controller_sha256=EXPECTED_BINDINGS["controller_module_sha256"],
        )

    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="disposable_parent_invalid",
    ):
        invoke(Path("relative-parent"))

    original = Path.is_symlink
    monkeypatch.setattr(
        Path,
        "is_symlink",
        lambda path: path == tmp_path or original(path),
    )
    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="disposable_parent_invalid",
    ):
        invoke(tmp_path)
    monkeypatch.setattr(Path, "is_symlink", original)

    (tmp_path / ATTEMPT_ID).mkdir()
    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="attempt_root_must_be_absent",
    ):
        invoke(tmp_path)


@pytest.mark.parametrize(
    "roster",
    [
        ["../escape"],
        ["/absolute"],
        ["runner\\escape"],
        ["runner/member", "RUNNER/MEMBER"],
    ],
)
def test_traversal_absolute_backslash_and_case_colliding_rosters_reject(
    monkeypatch: pytest.MonkeyPatch, roster: list[str]
) -> None:
    monkeypatch.setattr(materializer, "PATH_ROSTER", tuple(roster))
    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="path_roster_(member_invalid|case_collision)",
    ):
        materializer._validate_roster(roster)


def test_missing_extra_and_replaced_members_fail_readback(tmp_path: Path) -> None:
    root, _ = _materialize(tmp_path)
    helper = root / Path(*materializer.HELPER_RELATIVE_PATH.split("/"))
    helper.unlink()
    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="attempt_file_roster_invalid",
    ):
        _read_bundle(root)

    other_parent = tmp_path / "other"
    other_parent.mkdir()
    other_root, _ = _materialize(other_parent)
    (other_root / "runner" / "extra.mjs").write_bytes(b"extra")
    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="attempt_member_unregistered",
    ):
        _read_bundle(other_root)

    third_parent = tmp_path / "third"
    third_parent.mkdir()
    third_root, _ = _materialize(third_parent)
    runner = third_root / Path(*materializer.RUNNER_RELATIVE_PATH.split("/"))
    runner.write_bytes(b"replacement")
    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="materialized_source_digest_mismatch",
    ):
        _read_bundle(third_root)


def test_symlinked_attempt_root_and_member_fail_readback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _ = _materialize(tmp_path)
    runner = root / Path(*materializer.RUNNER_RELATIVE_PATH.split("/"))
    original = Path.is_symlink
    monkeypatch.setattr(
        Path,
        "is_symlink",
        lambda path: path == root or original(path),
    )
    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="attempt_root_invalid",
    ):
        _read_bundle(root)

    monkeypatch.setattr(
        Path,
        "is_symlink",
        lambda path: path == runner or original(path),
    )
    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="attempt_member_invalid",
    ):
        _read_bundle(root)


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        (b"not-json", "bundle_manifest_json_invalid"),
        (b"{}\n", "bundle_keys_invalid"),
        (b"x" * (materializer.MAX_MANIFEST_BYTES + 1), "bundle_manifest_file_invalid"),
    ],
)
def test_malformed_or_oversized_bundle_rejects(
    tmp_path: Path, payload: bytes, error: str
) -> None:
    root, _ = _materialize(tmp_path)
    bundle = root / Path(*materializer.BUNDLE_RELATIVE_PATH.split("/"))
    bundle.write_bytes(payload)
    with pytest.raises(materializer.FutureAttemptMaterialisationError, match=error):
        _read_bundle(root)


def test_noncanonical_bundle_and_runtime_identity_mismatch_reject(tmp_path: Path) -> None:
    root, reading = _materialize(tmp_path)
    bundle = root / Path(*materializer.BUNDLE_RELATIVE_PATH.split("/"))
    bundle.write_text(json.dumps(reading["manifest"]) + "\n", encoding="utf-8")
    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="bundle_manifest_canonical_bytes_required",
    ):
        _read_bundle(root)

    bundle.write_bytes(materializer.bundle_manifest_bytes(reading["manifest"]))
    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="bundle_runtime_identity_mismatch",
    ):
        materializer.read_materialized_bundle(
            root,
            operation_id=OPERATION_ID,
            attempt_id="different-attempt",
            candidate_source=CANDIDATE_SOURCE,
            expected_bindings=EXPECTED_BINDINGS,
        )


def test_shortened_candidate_and_invalid_expected_bindings_reject(tmp_path: Path) -> None:
    root, _ = _materialize(tmp_path)
    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="candidate_source_invalid",
    ):
        materializer.read_materialized_bundle(
            root,
            operation_id=OPERATION_ID,
            attempt_id=ATTEMPT_ID,
            candidate_source="cc75a9f",
            expected_bindings=EXPECTED_BINDINGS,
        )
    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="expected_bindings_invalid",
    ):
        materializer.read_materialized_bundle(
            root,
            operation_id=OPERATION_ID,
            attempt_id=ATTEMPT_ID,
            candidate_source=CANDIDATE_SOURCE,
            expected_bindings={"future_runner_sha256": "0" * 64},
        )


def test_fixture_writes_are_exclusive_and_terminal_requires_broker(tmp_path: Path) -> None:
    root, _ = _materialize(tmp_path)
    materializer.write_sidecar_fixture(root, _sidecar())
    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="exclusive_write_failed",
    ):
        materializer.write_sidecar_fixture(root, _sidecar())
    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="broker_reading_required",
    ):
        materializer.assemble_controller_terminal(
            root,
            operation_id=OPERATION_ID,
            attempt_id=ATTEMPT_ID,
            candidate_source=CANDIDATE_SOURCE,
            expected_bindings=EXPECTED_BINDINGS,
        )


def test_bundle_authority_raw_flags_and_extra_keys_fail_closed() -> None:
    manifest = materializer.build_bundle_manifest(
        operation_id=OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=CANDIDATE_SOURCE,
        runner_sha256=EXPECTED_BINDINGS["future_runner_sha256"],
        helper_sha256=EXPECTED_BINDINGS["generated_helper_sha256"],
        controller_sha256=EXPECTED_BINDINGS["controller_module_sha256"],
    )
    variants: list[tuple[dict, str]] = []
    occupied = json.loads(json.dumps(manifest))
    occupied["occupied_launch_authorized"] = True
    variants.append((occupied, "occupied_launch_authority_invalid"))
    executing = json.loads(json.dumps(manifest))
    executing["execution_authority"]["worker_process_authorized"] = True
    variants.append((executing, "execution_authority_invalid"))
    retaining = json.loads(json.dumps(manifest))
    retaining["raw_retention"]["raw_stream_retained"] = True
    variants.append((retaining, "raw_retention_invalid"))
    extra = {**manifest, "descriptive_state": "postpublication"}
    variants.append((extra, "bundle_keys_invalid"))
    for value, error in variants:
        with pytest.raises(
            materializer.FutureAttemptMaterialisationError,
            match=error,
        ):
            materializer.validate_bundle_manifest(value)


def test_valid_zero_nonzero_absent_and_invalid_sidecar_coordinates(tmp_path: Path) -> None:
    cases = [
        (_sidecar(), None, "post_hmr_pre_request_failure", True),
        (_sidecar(), {"request_count": 1}, "post_hmr_request_boundary_unresolved", False),
        (None, None, "native_harness_terminal_failure", False),
        (b"not-json", None, "native_harness_terminal_failure", False),
    ]
    for index, (sidecar, counters, coordinate, supported) in enumerate(cases):
        parent = tmp_path / str(index)
        parent.mkdir()
        _, terminal = _assemble(parent, sidecar=sidecar, counters=counters)
        assert terminal["coordinate"] == coordinate
        assert terminal["pre_request_supported"] is supported
        assert terminal["occupied_launch_authorized"] is False
        assert terminal["raw_stream_read"] is False
        assert terminal["raw_error_retained"] is False


def test_every_stage_error_kind_and_special_cause_is_terminally_closed(
    tmp_path: Path,
) -> None:
    error_names = (
        "AggregateError",
        "Error",
        "InvalidPresetIdError",
        "PresetMountError",
        "TypeError",
        "UnknownErrorName",
        "UnknownPresetError",
    )
    scenarios = [
        _sidecar(stage=stage) for stage in diagnostic.PRE_REQUEST_STAGES
    ] + [_sidecar(error_name=name) for name in error_names]
    scenarios += [
        _sidecar(stage="required_service_lookup", cause="required_service_missing"),
        _sidecar(
            stage="preset_root_roster_admission",
            cause="preset_root_roster_mismatch",
        ),
    ]
    for index, sidecar in enumerate(scenarios):
        parent = tmp_path / str(index)
        parent.mkdir()
        _, terminal = _assemble(parent, sidecar=sidecar)
        assert terminal["coordinate"] == "post_hmr_pre_request_failure"
        assert terminal["stage"] in diagnostic.PRE_REQUEST_STAGES
        assert terminal["cause_coordinate"] in diagnostic.CAUSE_COORDINATES
        assert terminal["error_kind"] in diagnostic.ERROR_KINDS


@pytest.mark.parametrize("counter", controller.BROKER_COUNTERS)
def test_each_nonzero_broker_counter_prevents_pre_request_claim(
    tmp_path: Path, counter: str
) -> None:
    _, terminal = _assemble(tmp_path, sidecar=_sidecar(), counters={counter: 1})
    assert terminal["coordinate"] == "post_hmr_request_boundary_unresolved"
    assert terminal["diagnostic_accepted"] is True
    assert terminal["broker_zero"] is False
    assert terminal["pre_request_supported"] is False


def test_invalid_or_noncanonical_broker_rejects_instead_of_falling_back(
    tmp_path: Path,
) -> None:
    root, _ = _materialize(tmp_path)
    materializer.write_sidecar_fixture(root, _sidecar())
    broker_path = root / Path(*materializer.BROKER_RELATIVE_PATH.split("/"))
    broker_path.write_bytes(b"not-json")
    with pytest.raises(controller.PostHmrControllerError, match="broker_json_invalid"):
        materializer.assemble_controller_terminal(
            root,
            operation_id=OPERATION_ID,
            attempt_id=ATTEMPT_ID,
            candidate_source=CANDIDATE_SOURCE,
            expected_bindings=EXPECTED_BINDINGS,
        )
    broker_path.write_text(json.dumps(_broker()) + "\n", encoding="utf-8")
    with pytest.raises(
        controller.PostHmrControllerError,
        match="broker_canonical_bytes_required",
    ):
        materializer.assemble_controller_terminal(
            root,
            operation_id=OPERATION_ID,
            attempt_id=ATTEMPT_ID,
            candidate_source=CANDIDATE_SOURCE,
            expected_bindings=EXPECTED_BINDINGS,
        )


def test_terminal_is_canonical_exclusive_and_contains_no_host_path(tmp_path: Path) -> None:
    root, terminal = _assemble(tmp_path, sidecar=_sidecar())
    terminal_path = root / Path(*materializer.TERMINAL_RELATIVE_PATH.split("/"))
    payload = terminal_path.read_bytes()
    assert payload == materializer.controller_terminal_bytes(terminal)
    assert str(tmp_path).encode() not in payload
    bundle_payload = (
        root / Path(*materializer.BUNDLE_RELATIVE_PATH.split("/"))
    ).read_bytes()
    assert str(tmp_path).encode() not in bundle_payload
    with pytest.raises(
        materializer.FutureAttemptMaterialisationError,
        match="controller_terminal_must_be_absent",
    ):
        materializer.assemble_controller_terminal(
            root,
            operation_id=OPERATION_ID,
            attempt_id=ATTEMPT_ID,
            candidate_source=CANDIDATE_SOURCE,
            expected_bindings=EXPECTED_BINDINGS,
        )


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        ({"coordinate": "descriptive-state"}, "controller_terminal_coordinate_invalid"),
        ({"broker_zero": 0}, "controller_terminal_boolean_invalid"),
        ({"pre_request_supported": False}, "controller_terminal_relationship_invalid"),
        ({"stage": "postpublication"}, "controller_terminal_diagnostic_invalid"),
        ({"raw_stream_read": True}, "controller_terminal_raw_or_authority_invalid"),
        ({"occupied_launch_authorized": True}, "controller_terminal_raw_or_authority_invalid"),
    ],
)
def test_terminal_vocabulary_relationship_types_and_raw_flags_fail_closed(
    tmp_path: Path, mutation: dict[str, object], error: str
) -> None:
    _, terminal = _assemble(tmp_path, sidecar=_sidecar())
    altered = {**terminal, **mutation}
    with pytest.raises(materializer.FutureAttemptMaterialisationError, match=error):
        materializer.validate_controller_terminal(altered)


def test_generated_evidence_report_and_efficacy_are_canonical() -> None:
    expected = rehearsal._expected_outputs()
    assert all(path.read_bytes() == payload for path, payload in expected.items())
    evidence = json.loads(rehearsal.EVIDENCE_PATH.read_bytes())
    schema = json.loads(rehearsal.EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(schema).validate(evidence)
    assert evidence["result"] == "pass"
    assert evidence["terminal_matrix"]["scenario_count"] == 24
    assert evidence["terminal_matrix"]["stage_count"] == 7
    assert evidence["terminal_matrix"]["error_kind_count"] == 7
    assert evidence["terminal_matrix"]["special_cause_count"] == 2
    assert evidence["terminal_matrix"]["nonzero_counter_count"] == 5
    assert all(value == 0 for value in evidence["proof_boundary"].values())
    assert evidence["materialisation"]["cleanup_complete"] is True
    report = rehearsal.REPORT_PATH.read_text(encoding="utf-8")
    assert "Timestamp: 2026-08-21T21:54:38.7791038+10:00" in report
    efficacy = json.loads(rehearsal.EFFICACY_PATH.read_bytes())
    assert efficacy["deepseek_performance_evidence"] is False
    assert efficacy["occupied_harness_evidence"] is False


def test_plan_threat_and_recovery_preserve_fail_closed_boundaries() -> None:
    plan = rehearsal.PLAN_PATH.read_text(encoding="utf-8")
    threat = (
        Path("docs/security") / f"{OUTER_OPERATION_ID}-threat-model-delta.md"
    ).read_text(encoding="utf-8")
    recovery = Path(
        "docs/deepseek-native-harness-provider-free-future-runner-materialisation-identity-binding-recovery.md"
    ).read_text(encoding="utf-8")
    for artifact in (plan, threat, recovery):
        assert "Date: 2026-08-21" in artifact
        assert "Timestamp: 2026-08-21T21:54:38.7791038+10:00" in artifact
    assert "No Node/Harness/broker/worker/model/provider process" in plan
    assert "occupied launch remains false" in threat.lower()
    assert "Separate the outer evidence identity" in recovery
    assert BINDINGS["generated_helper_sha256"] in recovery
    assert "Target rebinding" in plan
