from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_disposable_postgresql_cf_d2_event_cue_parse_catalogue_rehearsal as harness,
)


ROOT = Path(__file__).resolve().parents[1]


def _contract() -> dict:
    return json.loads(harness.CONTRACT_PATH.read_text(encoding="utf-8"))


def _manifest() -> dict:
    return json.loads(harness.MANIFEST_PATH.read_text(encoding="utf-8"))


def _synthetic_catalogue() -> dict:
    contract = _contract()
    catalogue = contract["catalogue"]
    constraints = []
    for name, expected in sorted(harness._constraint_expectations(contract).items()):
        item = {"name": name, **expected, "definition": f"definition:{name}"}
        if expected["type"] == "c":
            item["columns"] = []
        constraints.append(item)
    return {
        "schema": {
            "name": catalogue["schema_name"],
            "owner": contract["docker_profile"]["postgres_user"],
            "acl_is_null": True,
        },
        "domains": [
            {
                "name": name,
                "base_type": catalogue["domain_base_types"][name],
                "not_null": False,
                "acl_is_null": True,
                "constraints": [
                    {
                        "name": constraint_name,
                        "validated": True,
                        "definition": f"definition:{constraint_name}",
                    }
                ],
            }
            for name, constraint_name in zip(
                sorted(catalogue["domain_names"]),
                sorted(catalogue["domain_constraint_names"]),
                strict=True,
            )
        ],
        "tables": [
            {
                "name": name,
                "kind": "r",
                "row_security": False,
                "force_row_security": False,
                "acl_is_null": True,
            }
            for name in catalogue["relation_order"]
        ],
        "columns": harness._expected_columns(_manifest()),
        "constraints": constraints,
        "absence": {
            key: 0
            for key in (
                "functions",
                "triggers",
                "views",
                "materialized_views",
                "sequences",
                "policies",
                "non_internal_rules",
                "row_security_tables",
                "explicit_object_acls",
            )
        },
    }


def test_contract_schema_digest_sources_and_exact_artifact_pass() -> None:
    contract, sources, artifact, manifest = harness.verify_contract()
    assert contract["result"] == harness.PASS_RESULT
    assert len(sources) == 6
    assert len(artifact) == 12022
    assert hashlib.sha256(artifact).hexdigest() == contract["artifact"]["sha256"]
    assert manifest["statement_count"] == 18


def test_contract_and_evidence_schemas_are_whole_document_validators() -> None:
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


def test_plan_and_security_delta_freeze_timestamp_and_closed_surfaces() -> None:
    plan = (
        ROOT
        / "docs/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-parse-catalogue-rehearsal-plan.md"
    ).read_text(encoding="utf-8")
    threat = (
        ROOT
        / "docs/security/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-parse-catalogue-rehearsal-threat-model-delta.md"
    ).read_text(encoding="utf-8")
    for text in (plan, threat):
        assert "Date: 2026-08-13" in text
        assert "Timestamp: 2026-08-13T" in text
        assert "Australia/Brisbane" in text
    assert "--pull=never" in plan
    assert "transaction-protocol behavior" in plan
    assert "docs/branding/" in plan


def test_container_argv_is_networkless_tmpfs_and_never_pull() -> None:
    contract = _contract()
    argv = harness.build_container_argv(
        "docker.exe", "emr4-cf-d2-cue-pg16-catalogue-0123456789abcdef", "a" * 32, contract
    )
    joined = " ".join(argv)
    assert "--pull never" in joined
    assert "--network none" in joined
    assert "--tmpfs /var/lib/postgresql/data:" in joined
    assert "--restart no" in joined
    assert "--publish" not in argv
    assert "--volume" not in argv
    assert "--mount" not in argv
    assert contract["docker_profile"]["image_reference"] == argv[-1]


def test_psql_argv_uses_exact_container_local_unix_socket() -> None:
    profile = _contract()["docker_profile"]
    argv = harness._psql_argv(
        "docker.exe", "b" * 64, profile, single_transaction=True, tuples_only=True
    )
    assert argv[:3] == ["docker.exe", "exec", "-i"]
    assert "/var/run/postgresql" in argv
    assert "--single-transaction" in argv
    assert argv[-1] == "--file=-"
    assert "--host" in argv
    assert "localhost" not in argv


def test_expected_catalogue_census_is_exact() -> None:
    contract = _contract()
    columns = harness._expected_columns(_manifest())
    constraints = harness._constraint_expectations(contract)
    assert len(columns) == 50
    assert sum(item["type"] == "p" for item in constraints.values()) == 7
    assert sum(item["type"] == "u" for item in constraints.values()) == 3
    assert sum(item["type"] == "c" for item in constraints.values()) == 18
    assert sum(item["type"] == "f" for item in constraints.values()) == 7
    assert constraints["fk_terminal_receipt_obligation"]["deferrable"] is True
    assert constraints["fk_terminal_receipt_obligation"]["initially_deferred"] is True


def test_exact_synthetic_catalogue_is_admitted_without_definition_restatement() -> None:
    contract = _contract()
    summary = harness._assert_catalogue(_synthetic_catalogue(), contract, _manifest())
    assert summary["status"] == "exact_match"
    assert summary["fields"] == 50
    assert summary["foreign_keys"] == 7


def test_catalogue_drift_fails_closed() -> None:
    facts = _synthetic_catalogue()
    facts["columns"][0]["not_null"] = False
    with pytest.raises(harness.RehearsalFailure, match="column_shape_mismatch"):
        harness._assert_catalogue(facts, _contract(), _manifest())


def test_row_counts_are_exact_set_zero_and_returned_in_contract_order() -> None:
    contract = _contract()
    counts = {name: 0 for name in reversed(contract["catalogue"]["relation_order"])}
    admitted = harness._assert_row_counts(counts, contract)
    assert list(admitted) == contract["catalogue"]["relation_order"]
    bad = dict(counts)
    bad["terminal_receipt"] = 1
    with pytest.raises(harness.RehearsalFailure, match="nonzero_row_count"):
        harness._assert_row_counts(bad, contract)


def test_container_ownership_requires_exact_profile() -> None:
    profile = _contract()["docker_profile"]
    container_id = "c" * 64
    name = profile["container_name_prefix"] + "0123456789abcdef"
    nonce = "d" * 32
    inspect = {
        "Id": container_id,
        "Name": "/" + name,
        "Image": profile["image_id"],
        "Config": {
            "Image": profile["image_reference"],
            "Labels": {
                "com.emr4.harness": profile["harness_label"],
                "com.emr4.cleanup-nonce": nonce,
            },
            "Env": [
                f"POSTGRES_USER={profile['postgres_user']}",
                f"POSTGRES_PASSWORD={profile['postgres_password']}",
                f"POSTGRES_DB={profile['postgres_database']}",
                f"PGDATA={profile['pgdata']}",
            ],
        },
        "HostConfig": {
            "Tmpfs": {profile["data_destination"]: profile["tmpfs_options"]},
            "NetworkMode": "none",
            "Binds": None,
            "PortBindings": {},
            "Privileged": False,
            "Memory": profile["memory_bytes"],
            "NanoCpus": profile["nano_cpus"],
            "PidsLimit": profile["pids_limit"],
            "RestartPolicy": {"Name": profile["restart_policy"]},
        },
        "Mounts": [],
    }
    assert harness._container_owned(
        inspect,
        container_id=container_id,
        name=name,
        nonce=nonce,
        profile=profile,
    )
    inspect["HostConfig"]["NetworkMode"] = "bridge"
    assert not harness._container_owned(
        inspect,
        container_id=container_id,
        name=name,
        nonce=nonce,
        profile=profile,
    )


def test_source_has_no_generic_docker_discovery_or_registry_action() -> None:
    source = Path(harness.__file__).read_text(encoding="utf-8")
    forbidden = (
        '"pull"',
        '"login"',
        '"build"',
        '"prune"',
        '"container", "ls"',
        '"container", "list"',
        '"image", "rm"',
        '"volume"',
        '"network", "connect"',
    )
    for fragment in forbidden:
        assert fragment not in source
    assert "shell=False" in source
    assert "len(sys.argv) != 1" in source
    assert "if version.returncode != 0:" in source
    assert "observations = 0" in source
