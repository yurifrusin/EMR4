from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal-plan.md"
)
DESIGN = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal-design.md"
)
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal-threat-model-delta.md"
)
BASE = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal"
)
CONTRACT = BASE / "behavior-transaction-rehearsal-contract.json"
SCHEMA = BASE / "behavior-transaction-rehearsal-contract.schema.json"
BODY_CONTRACT = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-unmounted-durability-function-trigger-body-architecture/function-trigger-body-architecture-contract.json"
)
ROW_PROJECTION_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-row-composite-projection-order-rebind.md"
)
REGISTRATION_RLS_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-registration-rls-parent-rebind.md"
)
SYSTEM_XMIN_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-system-xmin-parent-rebind.md"
)
SYSTEM_XMIN_ALIAS_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-system-xmin-explicit-alias-parent-rebind.md"
)
RLS_LOCK_VISIBILITY_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-rls-lock-visibility-parent-rebind.md"
)
INTERVAL_CONSTRUCTION_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-interval-construction-parent-rebind.md"
)
UUID_MINIMUM_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-uuid-minimum-parent-rebind.md"
)
JSON_KEY_SET_ORDER_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-json-key-set-order-parent-rebind.md"
)
DML_NAME_AMBIGUITY_REBIND = (
    ROOT / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-"
    "dml-name-ambiguity-parent-rebind.md"
)
SUBTRANSACTION_XMIN_REBIND = (
    ROOT / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-"
    "subtransaction-xmin-parent-rebind.md"
)
SUPPORT_EXECUTE_GRANT_REBIND = (
    ROOT / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-"
    "support-execute-grant-parent-rebind.md"
)
ADMISSION_RECEIVER_BINDING_RLS_REBIND = (
    ROOT / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-"
    "admission-receiver-binding-rls-parent-rebind.md"
)
INPUT_NAMESPACE_REBIND = (
    ROOT / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-"
    "input-namespace-parent-rebind.md"
)
SOURCE_MEMBERSHIP_FIXTURE_RECOVERY = (
    ROOT / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-"
    "source-membership-fixture-recovery.md"
)
SOURCE_MEMBERSHIP_FIXTURE_THREAT = (
    ROOT / "docs/security/raisa-provider-free-disposable-postgresql-durability-"
    "behavior-source-membership-fixture-recovery-threat-model-delta.md"
)
RECEIPT_LOCK_PARENT_REBIND = (
    ROOT / "docs/raisa-provider-free-disposable-postgresql-durability-behavior-"
    "receipt-lock-parent-rebind.md"
)

EXPECTED_ORDER = [
    "BTR-E01",
    "BTR-E02",
    "BTR-E03",
    "BTR-I01",
    "BTR-E04",
    "BTR-I03",
    "BTR-E05",
    "BTR-E06",
    "BTR-I02",
    "BTR-I04",
    "BTR-T01",
    "BTR-T02",
    "BTR-T03",
    "BTR-T04",
    "BTR-R01",
    "BTR-R02",
    "BTR-R03",
    "BTR-B01",
    "BTR-B02",
    "BTR-B03",
]
EXPECTED_COVERAGE = {
    "ENTRY_POINT": 6,
    "TRIGGER": 4,
    "RLS": 3,
    "IDEMPOTENCY": 4,
    "ROLLBACK": 3,
    "total": 20,
}
EXPECTED_PARENT_BINDINGS = {
    "accepted_runtime_source": (
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal/provider-free-disposable-postgresql-evidence-admission-replay-winner-exact-reproduction.json",
        "36f076775e676620f99650043b05bd852e3a84be",
        "9ad82882150f8795789c332db8bed6e4b50d150986a6066ce832f12e48246d24",
    ),
    "inert_sql": (
        "orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/durability-schema.sql.inert",
        "5a9a7ae907308aa0a8a4256e9043b833f8c416ae",
        "dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7",
    ),
    "render_manifest": (
        "orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/render-manifest.json",
        "5a9a7ae907308aa0a8a4256e9043b833f8c416ae",
        "2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271",
    ),
    "structural_contract": (
        "orchestration/continuity/raisa-provider-free-unmounted-durability-migration-transaction-architecture/migration-transaction-architecture-contract.json",
        "a1af31e89c13a0eea72fd90a2934a0c8e0154175",
        "6c82c5a288c43ad2d8784f6eeb0c1f1efe1afea9a2b63721aebfc4371b63fe5e",
    ),
    "body_contract": (
        "orchestration/continuity/raisa-provider-free-unmounted-durability-function-trigger-body-architecture/function-trigger-body-architecture-contract.json",
        "206803a26767d7be02b45514dd02c56cce773a46",
        "21087e25e087c1865865d5f1cd24f192451f62658243420134deb903687e46bb",
    ),
    "parse_prerequisite_contract": (
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal/synthetic-prerequisite-contract.json",
        "1fd3445aea5839b7aa889fc962faa8ad2be0c95e",
        "313d283b4a53c08a34b65f7c932457010cc9317c87a3bfe6a1b9dc218ba220b7",
    ),
}


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _contract() -> dict[str, Any]:
    return _json(CONTRACT)


def _flat(*paths: Path) -> str:
    return " ".join(
        "\n".join(path.read_text(encoding="utf-8") for path in paths).split()
    )


def _assert_semantics(candidate: dict[str, Any]) -> None:
    schema = _json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(candidate)

    scenarios = candidate["scenarios"]
    assert candidate["scenario_order"] == EXPECTED_ORDER
    assert [scenario["id"] for scenario in scenarios] == EXPECTED_ORDER
    counts = Counter(scenario["category"] for scenario in scenarios)
    assert {**counts, "total": len(scenarios)} == EXPECTED_COVERAGE
    assert candidate["category_coverage"] == EXPECTED_COVERAGE

    serializable_ids = {
        scenario["id"]
        for scenario in scenarios
        if "serializable" in scenario["transaction_shape"]
    }
    assert serializable_ids == {"BTR-E01", "BTR-E04", "BTR-I03", "BTR-B03"}

    failures = {
        item["id"]: item["sqlstate"]
        for item in _json(BODY_CONTRACT)["failure_registry"]
    }
    for scenario in scenarios:
        outcome = scenario["expected_outcome"]
        failure_id = scenario["expected_failure_id"]
        sqlstate = scenario["expected_sqlstate"]
        if outcome in {"COMMIT_PASS", "COMMIT_NO_EFFECT", "COMMIT_IDEMPOTENT_REPLAY"}:
            assert failure_id is None
            assert sqlstate is None
        elif outcome == "ROLLBACK_EXPECTED_SQLSTATE":
            assert failure_id in failures
            assert failures[failure_id] == sqlstate
        elif outcome == "ROLLBACK_INJECTED":
            assert failure_id is None
            assert sqlstate == "P0001"
        elif outcome == "DENIED_STANDARD_PRIVILEGE":
            assert failure_id is None
            assert sqlstate == "42501"
        else:  # pragma: no cover - schema closes the outcome vocabulary
            raise AssertionError(outcome)

    runtime = candidate["runtime_profile"]
    assert runtime == {
        "postgresql_major": 16,
        "image": "postgres:16-bookworm",
        "pull_policy": "never",
        "network_mode": "none",
        "published_ports": 0,
        "mounts": 0,
        "storage": "container_local_tmpfs",
        "database_count": 1,
        "container_count": 1,
        "shell": False,
        "caller_selected_inputs": False,
        "cleanup": "exact_captured_container_id_after_ownership_reverification",
    }
    privileges = candidate["fixture_privileges"]
    assert privileges["fabric_direct_grant_changes"] == []
    assert len(privileges["producer_application_table_grants"]) == 4
    assert all(
        grant.split(":", maxsplit=1)[0]
        in {
            "appointments",
            "appointment_command_idempotency",
            "appointment_audit_log",
            "diary_committed_events",
        }
        for grant in privileges["producer_application_table_grants"]
    )
    assert candidate["closed_surfaces"] == [
        "app",
        "alembic",
        "api_spine_change",
        "diary_ui",
        "outbox_feed_watcher_listener",
        "operational_database",
        "patient_product_protected_data",
        "provider_model_external_retrieval",
        "command_or_product_write_authority",
        "deployment_production_release_pages",
        "protected_refs",
        "docs_branding",
    ]


def test_contract_and_schema_are_valid_and_semantically_closed() -> None:
    _assert_semantics(_contract())


def test_all_parent_paths_heads_and_hashes_are_exact() -> None:
    bindings = {item["id"]: item for item in _contract()["parent_bindings"]}
    assert set(bindings) == set(EXPECTED_PARENT_BINDINGS)
    for binding_id, (
        relative_path,
        source_head,
        digest,
    ) in EXPECTED_PARENT_BINDINGS.items():
        binding = bindings[binding_id]
        assert binding["path"] == relative_path
        assert binding["source_head"] == source_head
        assert binding["sha256"] == f"sha256:{digest}"
        raw = (ROOT / relative_path).read_bytes()
        assert b"\r" not in raw.replace(b"\r\n", b"")
        canonical = raw.replace(b"\r\n", b"\n")
        assert hashlib.sha256(canonical).hexdigest() == digest


def test_row_projection_rebind_preserves_scenarios_and_runtime_closure() -> None:
    combined = _flat(ROW_PROJECTION_REBIND, PLAN, DESIGN).lower()

    for required in (
        "attempt 015",
        "all twenty scenarios remain byte-for-byte unchanged",
        "attempt 016",
        "fresh exact-head",
        "docs/branding/",
        "no patient, clinical, product-derived or protected data",
    ):
        assert required in combined


def test_registration_rls_rebind_preserves_twenty_scenarios_and_closure() -> None:
    combined = _flat(REGISTRATION_RLS_REBIND, PLAN, DESIGN).lower()

    for required in (
        "attempts 001-018 remain immutable",
        "exactly twenty ordered",
        "6/4/3/4/3",
        "attempt 019",
        "gemini 3.6 flash/high",
        "docs/branding/",
        "no applied migration",
        "patient/product/protected data",
    ):
        assert required in combined


def test_system_xmin_rebind_preserves_twenty_scenarios_and_closure() -> None:
    combined = _flat(SYSTEM_XMIN_REBIND, PLAN, DESIGN).lower()

    for required in (
        "attempt 019",
        "exactly twenty ordered",
        "6/4/3/4/3",
        "byte-for-byte unchanged",
        "gemini 3.6 flash/high",
        "docs/branding/",
        "no applied migration",
        "patient, product or protected data",
    ):
        assert required in combined


def test_system_xmin_alias_rebind_preserves_twenty_scenarios_and_closure() -> None:
    combined = _flat(SYSTEM_XMIN_ALIAS_REBIND, PLAN, DESIGN).lower()

    for required in (
        "attempt 020",
        "exactly twenty ordered",
        "6/4/3/4/3",
        "byte-for-byte unchanged",
        "gemini 3.6 flash/high",
        "docs/branding/",
        "no applied migration",
        "patient/product/protected data",
    ):
        assert required in combined


def test_rls_lock_visibility_rebind_preserves_twenty_scenarios_and_closure() -> None:
    combined = _flat(RLS_LOCK_VISIBILITY_REBIND, PLAN, DESIGN).lower()

    for required in (
        "attempts 001-023 remain immutable",
        "exactly twenty ordered",
        "6/4/3/4/3",
        "attempt 024",
        "gemini 3.6 flash/high",
        "docs/branding/",
        "no applied migration",
        "patient, product or protected data",
    ):
        assert required in combined
    contract = _contract()
    canonical = json.dumps(
        {
            "scenario_order": contract["scenario_order"],
            "scenarios": contract["scenarios"],
            "category_coverage": contract["category_coverage"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == (
        "e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb"
    )


def test_interval_construction_rebind_preserves_twenty_scenarios_and_closure() -> None:
    combined = _flat(INTERVAL_CONSTRUCTION_REBIND, PLAN, DESIGN).lower()

    for required in (
        "attempts 001-024 remain immutable",
        "exactly twenty ordered",
        "6/4/3/4/3",
        "attempt 025",
        "gemini 3.6 flash/high",
        "docs/branding/",
        "no applied migration",
        "patient, product or protected data",
    ):
        assert required in combined
    contract = _contract()
    canonical = json.dumps(
        {
            "scenario_order": contract["scenario_order"],
            "scenarios": contract["scenarios"],
            "category_coverage": contract["category_coverage"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == (
        "e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb"
    )


def test_uuid_minimum_rebind_preserves_twenty_scenarios_and_closure() -> None:
    combined = _flat(UUID_MINIMUM_REBIND, PLAN, DESIGN).lower()

    for required in (
        "attempts 001-025 remain immutable",
        "exactly twenty ordered",
        "6/4/3/4/3",
        "attempt 026",
        "gemini 3.6 flash/high",
        "docs/branding/",
        "no applied migration",
        "patient, product or protected data",
    ):
        assert required in combined
    contract = _contract()
    canonical = json.dumps(
        {
            "scenario_order": contract["scenario_order"],
            "scenarios": contract["scenarios"],
            "category_coverage": contract["category_coverage"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == (
        "e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb"
    )


def test_json_key_set_order_rebind_preserves_twenty_scenarios_and_closure() -> None:
    combined = _flat(JSON_KEY_SET_ORDER_REBIND, PLAN, DESIGN).lower()

    for required in (
        "attempts 001-026 remain immutable",
        "exactly twenty ordered",
        "6/4/3/4/3",
        "attempt 027",
        "gemini 3.6 flash/high",
        "docs/branding/",
        "no applied migration",
        "patient, clinical, product or protected data",
    ):
        assert required in combined
    contract = _contract()
    canonical = json.dumps(
        {
            "scenario_order": contract["scenario_order"],
            "scenarios": contract["scenarios"],
            "category_coverage": contract["category_coverage"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == (
        "e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb"
    )


def test_dml_name_ambiguity_rebind_preserves_twenty_scenarios_and_closure() -> None:
    combined = _flat(DML_NAME_AMBIGUITY_REBIND, PLAN, DESIGN).lower()

    for required in (
        "deterministic six-parent rebind",
        "5d31d5cfd0a95a771f28cca2c6c7baf903ae97ed",
        "9513b1f8a845b29473a2ca402fcee2ac2b11eebe",
        "958f8178c872854ab0f8e1c56dbb9fe46afbea22",
        "aabab28c1087e91d2b6267e24d55fd60e28a9204621dc38699c5df9e8feb7b24",
        "6/4/3/4/3",
        "gemini 3.6 flash/high",
        "docs/branding/",
        "no applied migration",
        "product or patient data",
    ):
        assert required in combined
    contract = _contract()
    canonical = json.dumps(
        {
            "scenario_order": contract["scenario_order"],
            "scenarios": contract["scenarios"],
            "category_coverage": contract["category_coverage"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == (
        "e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb"
    )


def test_subtransaction_xmin_rebind_preserves_twenty_scenarios_and_closure() -> None:
    combined = _flat(SUBTRANSACTION_XMIN_REBIND, PLAN, DESIGN).lower()

    for required in (
        "deterministic six-parent rebind",
        "426fd229a96b7a34787dd0d0610a926808fd9961",
        "561f5c896c16f31dcf6057da37d6ece7134c0da6",
        "958f8178c872854ab0f8e1c56dbb9fe46afbea22",
        "a7278f6d87a69e9c5c9daef0a5b3640bcd22d27a3aac597ee228584dcc06d740",
        "6/4/3/4/3",
        "gemini 3.6 flash/high",
        "docs/branding/",
        "no applied migration",
        "product or patient data",
    ):
        assert required in combined
    contract = _contract()
    canonical = json.dumps(
        {
            "scenario_order": contract["scenario_order"],
            "scenarios": contract["scenarios"],
            "category_coverage": contract["category_coverage"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == (
        "e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb"
    )


def test_support_execute_grant_rebind_preserves_twenty_scenarios_and_closure() -> None:
    combined = _flat(SUPPORT_EXECUTE_GRANT_REBIND, PLAN, DESIGN).lower()

    for required in (
        "deterministic six-parent rebind",
        "edc311f0471b7b2796ecc21527015e88981448d7",
        "01da1ecf50b25a0086dcf977e0468f9f3ccbe12f",
        "958f8178c872854ab0f8e1c56dbb9fe46afbea22",
        "88650862f2dc654813d3b6c9832a7691e5b630187286f129eb1e8bd102d683bf",
        "eec93b0d67bd70a9640b3000bc63d43a08aa6817b438e0c99dbf2595a69c4c19",
        "6/4/3/4/3",
        "gemini 3.6 flash/high",
        "docs/branding/",
        "no applied migration",
        "product or patient data",
    ):
        assert required in combined
    contract = _contract()
    canonical = json.dumps(
        {
            "scenario_order": contract["scenario_order"],
            "scenarios": contract["scenarios"],
            "category_coverage": contract["category_coverage"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == (
        "e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb"
    )


def test_admission_receiver_binding_rls_rebind_preserves_scenarios_and_closure() -> (
    None
):
    combined = _flat(ADMISSION_RECEIVER_BINDING_RLS_REBIND, PLAN, DESIGN).lower()

    for required in (
        "deterministic six-parent rebind",
        "f842c023f4db16e8b0ffc381f653fb16e98280cc",
        "30ff6b01a54c339e3045977cda909628841fe57e",
        "a1a4a619222297b36fa6894a5cf5f12a179af48c",
        "c0673fc755457756719959dcfc6aea04531d6627",
        "eec93b0d67bd70a9640b3000bc63d43a08aa6817b438e0c99dbf2595a69c4c19",
        "6/4/3/4/3",
        "gemini 3.6 flash/high",
        "docs/branding/",
        "no applied migration",
        "product or patient data",
    ):
        assert required in combined
    contract = _contract()
    canonical = json.dumps(
        {
            "scenario_order": contract["scenario_order"],
            "scenarios": contract["scenarios"],
            "category_coverage": contract["category_coverage"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == (
        "e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb"
    )


def test_input_namespace_rebind_preserves_scenarios_and_closed_runtime() -> None:
    combined = _flat(INPUT_NAMESPACE_REBIND, PLAN, DESIGN).lower()

    for required in (
        "deterministic six-parent rebind",
        "e8b902cf54d50d478912c5f01e38b719e380946d",
        "f64f3cd7ad8577953c51c66309151cb288440acb",
        "a1a4a619222297b36fa6894a5cf5f12a179af48c",
        "c0673fc755457756719959dcfc6aea04531d6627",
        "eec93b0d67bd70a9640b3000bc63d43a08aa6817b438e0c99dbf2595a69c4c19",
        "6/4/3/4/3",
        "gemini 3.6 flash/high",
        "docs/branding/",
        "no applied migration",
        "product or patient data",
    ):
        assert required in combined
    contract = _contract()
    canonical = json.dumps(
        {
            "scenario_order": contract["scenario_order"],
            "scenarios": contract["scenarios"],
            "category_coverage": contract["category_coverage"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == (
        "e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb"
    )


def test_source_membership_fixture_recovery_preserves_scenarios_and_authority() -> None:
    combined = _flat(
        SOURCE_MEMBERSHIP_FIXTURE_RECOVERY,
        SOURCE_MEMBERSHIP_FIXTURE_THREAT,
        PLAN,
        DESIGN,
    ).lower()
    for required in (
        "source_membership_digest_v1",
        "all eleven fields",
        "same-locator",
        "cf201",
        "twenty scenario objects",
        "no applied migration",
        "product or patient data",
        "provider call",
        "protected-ref",
    ):
        assert required in combined
    contract = _contract()
    assert contract["fixture_namespace"]["source_membership_digest_rule"] == (
        "canonical_digest_of_complete_same_locator_outbox_row"
    )
    canonical = json.dumps(
        {
            "scenario_order": contract["scenario_order"],
            "scenarios": contract["scenarios"],
            "category_coverage": contract["category_coverage"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == (
        "e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb"
    )


def test_receipt_lock_parent_rebind_preserves_scenarios_and_authority() -> None:
    combined = _flat(RECEIPT_LOCK_PARENT_REBIND, PLAN, DESIGN).lower()
    for required in (
        "attempt 042 remains immutable",
        "receipt-lock parse reproduction",
        "1,437,022 lf bytes",
        "424 statements",
        "all twenty scenario objects",
        "6/4/3/4/3",
        "attempt 043",
        "gemini 3.6 flash/high",
        "docs/branding/",
        "no applied migration",
        "patient",
        "protected-ref",
    ):
        assert required in combined
    contract = _contract()
    canonical = json.dumps(
        {
            "scenario_order": contract["scenario_order"],
            "scenarios": contract["scenarios"],
            "category_coverage": contract["category_coverage"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == (
        "e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb"
    )


def test_scenario_population_is_exact_and_all_five_categories_are_present() -> None:
    contract = _contract()
    assert contract["scenario_order"] == EXPECTED_ORDER
    assert [scenario["id"] for scenario in contract["scenarios"]] == EXPECTED_ORDER
    assert contract["category_coverage"] == EXPECTED_COVERAGE
    assert Counter(s["category"] for s in contract["scenarios"]) == Counter(
        {key: value for key, value in EXPECTED_COVERAGE.items() if key != "total"}
    )


def test_failure_043_descendant_preserves_historical_and_current_scenario_seals() -> (
    None
):
    historical = RECEIPT_LOCK_PARENT_REBIND.read_text(encoding="utf-8")
    assert (
        "d83130af81fffe6d4fd2c404cd6a9376fc7d77332095399b023998c8c2bf92b9" in historical
    )
    contract = _contract()
    current = json.dumps(
        {
            "scenario_order": contract["scenario_order"],
            "scenarios": contract["scenarios"],
            "category_coverage": contract["category_coverage"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert hashlib.sha256(current).hexdigest() == (
        "e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb"
    )


def test_isolation_shapes_preserve_parent_entry_point_requirements() -> None:
    scenarios = {row["id"]: row for row in _contract()["scenarios"]}
    assert {
        scenario_id
        for scenario_id, scenario in scenarios.items()
        if "serializable" in scenario["transaction_shape"]
    } == {"BTR-E01", "BTR-E04", "BTR-I03", "BTR-B03"}
    combined = _flat(PLAN, DESIGN).lower()
    assert "entry-point-specific" in combined
    assert "accepted lifecycle/coordinator" in combined


def test_custom_failures_bind_the_accepted_failure_registry() -> None:
    failures = {
        item["id"]: item["sqlstate"]
        for item in _json(BODY_CONTRACT)["failure_registry"]
    }
    for scenario in _contract()["scenarios"]:
        if scenario["expected_failure_id"] is not None:
            assert (
                failures[scenario["expected_failure_id"]]
                == scenario["expected_sqlstate"]
            )
    scenarios = {row["id"]: row for row in _contract()["scenarios"]}
    assert scenarios["BTR-E06"]["expected_failure_id"] == "F_CARDINALITY"
    assert scenarios["BTR-E06"]["expected_sqlstate"] == "CF004"


def test_fixture_namespace_is_opaque_and_contains_no_patient_or_narrative_field() -> (
    None
):
    fixture = _contract()["fixture_namespace"]
    forbidden_terms = {
        "patient",
        "name",
        "address",
        "phone",
        "email",
        "reason_text",
        "note",
    }
    assert not any(term in key.lower() for key in fixture for term in forbidden_terms)
    uuid_values = [
        value
        for key, value in fixture.items()
        if isinstance(value, str)
        and (
            key.startswith(
                (
                    "practice_",
                    "stream_",
                    "appointment_",
                    "observer_",
                    "command_",
                    "audit_",
                    "event_",
                    "location_",
                )
            )
            or key in {"actor", "practitioner"}
        )
    ]
    assert len(uuid_values) == len(set(uuid_values))
    assert all(len(value) == 36 and value.count("-") == 4 for value in uuid_values)
    digest_values = [
        value for key, value in fixture.items() if key.startswith("digest_")
    ]
    assert all(
        value.startswith("sha256:") and len(value) == 71 for value in digest_values
    )


def test_runtime_profile_and_cleanup_are_fail_closed() -> None:
    combined = _flat(PLAN, DESIGN, THREAT)
    for required in (
        "exact already-local image `postgres:16-bookworm` and `--pull=never`",
        "`--network=none`",
        "no published/exposed host port",
        "no bind mount, named volume, workspace mount or Docker socket mount",
        "one container-local tmpfs",
        "argv-only process execution with `shell=False`",
        "no `POSTGRES_HOST_AUTH_METHOD=trust`",
        "captured container ID",
        "Exact-ID post-inspection",
        "must not list global containers, images, networks or volumes",
    ):
        assert required in combined


def test_api_spine_and_runtime_separation_are_explicit() -> None:
    combined = _flat(PLAN, DESIGN, THREAT)
    for required in (
        "adds no GraphQL field, subscription or mutation and no REST/OpenAPI operation",
        "does not call an application route",
        "Events remain signals that require fresh authorized reads",
        "This tranche may write only the plan, design, threat-model delta",
        "It may not start Docker or PostgreSQL",
        "runtime remains closed",
    ):
        assert required in combined


def test_preexisting_api_spine_baseline_failure_is_preserved_and_scoped_out() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "test_idempotency_continuity_index_covers_openapi_command_paths" in plan
    for path in (
        "/appointments/proposals/check-in/{appointment_id}",
        "/appointments/proposals/check-in/confirm",
        "/appointments/proposals/reception-one/compose",
    ):
        assert f"`{path}`" in plan
    assert "changes no API Spine file" in plan
    assert "later separately scoped API Spine maintenance descendant" in plan


def test_selected_claim_is_serial_and_does_not_overclaim_later_behaviors() -> None:
    contract = _contract()
    does_not_prove = set(contract["claim_boundary"]["does_not_prove"])
    assert {
        "all_nine_entry_points_or_all_fourteen_triggers",
        "concurrency_or_deadlock_behavior",
        "key_rotation_or_retention_execution",
        "unknown_commit_recovery",
        "alembic_upgrade_or_downgrade",
        "application_runtime_or_api_wiring",
        "patient_clinical_or_production_safety",
    } <= does_not_prove
    combined = _flat(PLAN, DESIGN, THREAT)
    assert "Those are later finite descendants" in combined


def test_role_and_fixture_grants_do_not_change_fabric_privileges() -> None:
    privileges = _contract()["fixture_privileges"]
    assert privileges["fabric_direct_grant_changes"] == []
    assert (
        privileges["scenario_identity_method"]
        == "set_session_authorization_once_before_begin_on_fresh_connection"
    )
    assert set(privileges["forbidden"]) >= {
        "role_passwords",
        "operational_credentials",
        "scenario_role_switch_after_begin",
        "bypassrls_grant",
        "role_inheritance",
        "fabric_table_dml_grant",
        "trigger_function_execute_grant",
    }
    assert all(
        ":practice_alpha:stream_alpha" in row for row in privileges["binding_rows"]
    )


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("runtime_profile", "network_mode"), "bridge"),
        (("runtime_profile", "pull_policy"), "always"),
        (("runtime_profile", "mounts"), 1),
        (("runtime_profile", "shell"), True),
        (
            ("fixture_privileges", "fabric_direct_grant_changes"),
            ["context_producer:INSERT"],
        ),
        (
            ("fixture_privileges", "scenario_identity_method"),
            "set_role_inside_transaction",
        ),
        (("category_coverage", "TRIGGER"), 3),
        (("closed_surfaces",), ["app"]),
    ],
)
def test_hostile_top_level_mutations_are_rejected(
    path: tuple[str, ...], value: Any
) -> None:
    candidate = copy.deepcopy(_contract())
    target: Any = candidate
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(Exception):
        _assert_semantics(candidate)


@pytest.mark.parametrize(
    ("scenario_id", "field", "value"),
    [
        ("BTR-E02", "category", "ROLLBACK"),
        ("BTR-E06", "expected_sqlstate", "CF203"),
        ("BTR-I04", "expected_failure_id", "F_PROVENANCE"),
        ("BTR-T03", "expected_sqlstate", None),
        ("BTR-R03", "expected_sqlstate", "CF001"),
        ("BTR-B01", "expected_sqlstate", "00000"),
        ("BTR-B03", "readback", ["receipt_absent"]),
    ],
)
def test_hostile_scenario_mutations_are_rejected(
    scenario_id: str, field: str, value: Any
) -> None:
    candidate = copy.deepcopy(_contract())
    scenario = next(
        item for item in candidate["scenarios"] if item["id"] == scenario_id
    )
    scenario[field] = value
    with pytest.raises(Exception):
        _assert_semantics(candidate)


def test_plan_records_standing_continuation_but_current_user_pause_after_closeout() -> (
    None
):
    plan = PLAN.read_text(encoding="utf-8")
    flat_plan = " ".join(plan.split())
    assert "standing uninterrupted- development authority" in flat_plan
    assert (
        "Pause for Yuri only if recovery exposes a genuinely non-inferable" in flat_plan
    )
    assert (
        "`docs/branding/` plus every unrelated untracked path remains unstaged"
        in flat_plan
    )


def test_planning_artifact_allowlist_excludes_runtime_and_product_files() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "No harness, SQL scenario template, runtime evidence" in plan
    assert "no application, Alembic, API Spine, Diary" in _flat(PLAN, THREAT)
    assert "No implementation worker is economical here" in plan
    assert "fresh Gemini 3.6 Flash/high Antigravity project" in plan
