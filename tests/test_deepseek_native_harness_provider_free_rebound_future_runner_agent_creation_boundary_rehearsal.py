from __future__ import annotations

import inspect
import json
from pathlib import Path

import jsonschema
import pytest
import yaml

from scripts import (
    deepseek_native_harness_provider_free_rebound_future_runner_agent_creation_boundary_rehearsal as subject,
)


CONTRACT = json.loads(subject.CONTRACT_PATH.read_bytes())


def _paths() -> dict[str, Path]:
    root = Path("C:/deterministic/rebound-agent-creation-boundary-test").resolve()
    user = root / "home" / ".agent-presets"
    return {
        "root": root,
        "profile": root / "home" / "profiles" / "headless",
        "readiness": root / "readiness.jsonl",
        "sidecar": root / "bundle" / "control" / "post-hmr-diagnostic.json",
        "shipped": (
            root
            / "installation"
            / "node_modules"
            / "@deepseek-ai"
            / "dsh"
            / "config"
            / "agent-presets"
        ),
        "user": user,
        "preset": user / subject.PRESET_ID / "agent.cordis.yml",
    }


def _patches() -> tuple[bytes, bytes]:
    paths = _paths()
    return subject.build_patch_pair(
        profile_dir=paths["profile"],
        readiness_path=paths["readiness"],
        sidecar_path=paths["sidecar"],
        shipped_root=paths["shipped"],
        user_root=paths["user"],
        preset_path=paths["preset"],
        candidate_source=CONTRACT["planning_source"],
        source_bindings=CONTRACT["source_bindings"],
    )


def _success_arguments() -> dict[str, object]:
    sidecar = subject.expected_sidecar(CONTRACT, CONTRACT["planning_source"])
    return {
        "process_started": True,
        "exit_code": 0,
        "exit_mode": "self_exited_after_typed_sidecar",
        "readiness_valid": True,
        "readiness_events": ["sentinel_activated", "stock_headless_hmr_ready"],
        "mutated": True,
        "sidecar": sidecar,
        "terminal": subject.build_controller_terminal(sidecar),
        "broker_zero": True,
        "network_attempt_count": 0,
        "network_ledger_valid": True,
        "bundle_unchanged": True,
        "target_absent": True,
        "process_absent": True,
        "root_absent": True,
    }


def test_contract_and_all_schemas_are_closed_and_valid() -> None:
    contract_schema = json.loads(subject.CONTRACT_SCHEMA_PATH.read_bytes())
    sidecar_schema = json.loads(subject.SIDECAR_SCHEMA_PATH.read_bytes())
    evidence_schema = json.loads(subject.EVIDENCE_SCHEMA_PATH.read_bytes())
    for schema in (contract_schema, sidecar_schema, evidence_schema):
        jsonschema.Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False
    jsonschema.Draft202012Validator(contract_schema).validate(CONTRACT)


def test_preset_payload_is_built_from_its_own_typed_contract_family() -> None:
    payload = subject._build_bound_preset_payload(CONTRACT)
    composition_contract = subject.native_composition.load_contract()
    assert yaml.safe_load(payload) == composition_contract["preset"]["rows"]
    assert len(payload) == CONTRACT["preset"]["bytes"]
    assert subject.sha256_bytes(payload) == CONTRACT["preset"]["sha256"]


def test_deterministic_check_owns_the_only_preset_contract_selection() -> None:
    check_source = inspect.getsource(subject.deterministic_check)
    execute_source = inspect.getsource(subject.execute_rehearsal)
    assert "preset_payload = _build_bound_preset_payload(contract)" in check_source
    assert 'preset_payload = check["preset_payload"]' in execute_source
    assert "predecessor.load_contract()" not in execute_source


def test_planning_and_accepted_sources_are_full_git_object_ids() -> None:
    values = [CONTRACT["planning_source"], *CONTRACT["accepted_sources"].values()]
    assert all(subject.FULL_OID.fullmatch(value) is not None for value in values)
    assert CONTRACT["planning_source"] == "24db4eda0580ab01c8dec33174e6c7c4c0f6f8ae"


def test_execution_attempt_is_exactly_one_process_without_retry() -> None:
    assert CONTRACT["execution_attempt"] == {
        "attempt_id": subject.EXECUTION_ATTEMPT_ID,
        "native_process_count": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
    }


def test_factory_boundary_distinguishes_private_preparation_from_publication() -> None:
    assert CONTRACT["factory_boundary"] == {
        "private_session_id": subject.PRIVATE_SESSION_ID,
        "publication_stop": subject.PUBLICATION_STOP,
        "agents_create_invocations": 1,
        "private_agent_preparations": 1,
        "private_session_preparations": 1,
        "published_agents": 0,
        "published_sessions": 0,
    }


def test_package_source_members_are_exact_rc7_bytes() -> None:
    package_root = (
        subject.predecessor.PACKAGE_SEED_ROOT / "node_modules" / "@deepseek-ai" / "dsh"
    )
    assert (
        subject.verify_package_members(package_root, CONTRACT)
        == CONTRACT["package_source_members"]
    )


def test_runner_source_is_exactly_bound_and_closed() -> None:
    runner = subject.runner_source()
    projection = subject.validate_runner_source(runner)
    assert projection["sha256"] == CONTRACT["source_bindings"]["future_runner_sha256"]
    assert all(projection["checks"].values())


def test_runner_reaches_veto_only_after_preset_and_model_selection() -> None:
    source = subject.runner_source().decode()
    guard = source.index("await assertEffectiveToolComposition")
    model = source.index("installModelSelection(agentCtx")
    commit = source.index("commit() {")
    veto = source.index("throw new Error(PUBLICATION_STOP);")
    sidecar = source.index("writeSidecar(config.sidecarPath")
    assert guard < model < commit < veto < sidecar


def test_runner_does_not_drive_agent_or_reach_request_services() -> None:
    source = subject.runner_source().decode()
    for forbidden in (
        ".followup(",
        "createUserMessage",
        ".whenIdle(",
        'ctx.get("broker")',
        'ctx.get("models")',
        'ctx.get("providers")',
    ):
        assert forbidden not in source


def test_runner_has_one_factory_call_one_commit_and_one_sidecar() -> None:
    source = subject.runner_source().decode()
    assert source.count("await agents.create({") == 1
    assert source.count("commit() {") == 1
    assert source.count("throw new Error(PUBLICATION_STOP);") == 1
    assert source.count("writeSidecar(config.sidecarPath") == 1


def test_initial_patch_mounts_roots_but_not_runner() -> None:
    initial, _ = _patches()
    direct, inserted = subject._patch_rows(initial)
    assert [row["id"] for row in direct] == [
        "headless-runner",
        "code-runtime",
        "session-telemetry-otel",
    ]
    assert [row["id"] for row in inserted] == [
        "provider-free-rebound-hmr-sentinel",
        "agent-presets",
    ]


def test_changed_patch_adds_exact_runner_injection_and_two_root_derivation() -> None:
    _, changed = _patches()
    rows = yaml.safe_load(changed)
    inserted = rows[-1]["insert"]
    assert inserted[1]["config"] == {
        "default": subject.PRESET_ID,
        "roots": [{"path": str(_paths()["shipped"]), "trust": "system"}],
        "includeUserRoot": True,
    }
    assert inserted[2]["inject"] == [
        "hmr",
        "headlessStartup",
        "agents",
        "sessions",
        "agentPresets",
    ]


def test_patch_validator_rejects_runner_injection_drift() -> None:
    initial, changed = _patches()
    paths = _paths()
    mutated = changed.replace(
        b"hmr, headlessStartup, agents, sessions, agentPresets",
        b"hmr, agents, sessions, agentPresets",
    )
    with pytest.raises(
        subject.AgentCreationBoundaryError, match="runner_patch_row_invalid"
    ):
        subject.validate_patch_pair(
            initial,
            mutated,
            sidecar_path=paths["sidecar"],
            shipped_root=paths["shipped"],
            user_root=paths["user"],
            preset_path=paths["preset"],
            candidate_source=CONTRACT["planning_source"],
            source_bindings=CONTRACT["source_bindings"],
        )


def test_expected_sidecar_is_closed_and_schema_valid() -> None:
    value = subject.expected_sidecar(CONTRACT, CONTRACT["planning_source"])
    schema = json.loads(subject.SIDECAR_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(schema).validate(value)
    assert set(value) == set(schema["required"])
    assert value["coordinate"] == subject.SIDECAR_COORDINATE


def test_sidecar_reader_rejects_semantic_drift(tmp_path: Path) -> None:
    value = subject.expected_sidecar(CONTRACT, CONTRACT["planning_source"])
    value["live_session_count"] = 1
    sidecar = tmp_path / "sidecar.json"
    sidecar.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(
        (jsonschema.ValidationError, subject.AgentCreationBoundaryError)
    ):
        subject.read_sidecar(
            sidecar,
            disposable_root=tmp_path,
            contract=CONTRACT,
            candidate_source=CONTRACT["planning_source"],
        )


def test_controller_terminal_is_one_closed_coordinate() -> None:
    sidecar = subject.expected_sidecar(CONTRACT, CONTRACT["planning_source"])
    terminal = subject.build_controller_terminal(sidecar)
    assert {key: terminal[key] for key in CONTRACT["expected_terminal"]} == CONTRACT[
        "expected_terminal"
    ]
    assert terminal["coordinate"] == subject.CONTROLLER_COORDINATE


def test_success_classifier_requires_every_containment_reading() -> None:
    assert subject._failure_coordinate(**_success_arguments()) is None


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("network_attempt_count", 1, "NETWORK_BOUNDARY_REJECTED"),
        ("exit_code", 2, "PROCESS_EXIT_REJECTED"),
        ("mutated", False, "HMR_MUTATION_REJECTED"),
        ("broker_zero", False, "BROKER_BOUNDARY_REJECTED"),
        ("bundle_unchanged", False, "CANONICAL_BUNDLE_MUTATED"),
        ("target_absent", False, "TARGET_BOUNDARY_REJECTED"),
        ("root_absent", False, "CLEANUP_REJECTED"),
    ],
)
def test_success_classifier_fails_closed(
    field: str, value: object, expected: str
) -> None:
    arguments = _success_arguments()
    arguments[field] = value
    assert subject._failure_coordinate(**arguments) == expected


def test_controller_discards_streams_and_has_one_popen_site() -> None:
    source = inspect.getsource(subject.execute_rehearsal)
    assert source.count("subprocess.Popen(") == 1
    assert "stdout=subprocess.DEVNULL" in source
    assert "stderr=subprocess.DEVNULL" in source
    assert ".stdout.read" not in source
    assert ".stderr.read" not in source


def test_controller_reads_postrollback_sidecar_before_cleanup_and_publication() -> None:
    source = inspect.getsource(subject.execute_rehearsal)
    terminate = source.index("predecessor._terminate_process(process)")
    terminal = source.index("terminal = build_controller_terminal(sidecar)")
    cleanup = source.index("root_absent = _cleanup_root(root, parent)")
    publish = source.index("_write_exclusive(EVIDENCE_PATH")
    assert terminate < terminal < cleanup < publish


def test_no_product_or_data_authority_enters_contract_or_runner() -> None:
    payload = (
        subject.CONTRACT_PATH.read_text(encoding="utf-8")
        + subject.runner_source().decode()
    ).lower()
    for forbidden in (
        "patient_id",
        "appointment_id",
        "clinical_data",
        "production_runtime",
        "ordinary_practice_enablement",
    ):
        assert forbidden not in payload
