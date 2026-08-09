"""Focused acceptance tests for the provider-free inert DDL rehearsal renderer.

These tests exercise the sixteen acceptance clauses of the accepted inert-DDL
plan using only authored-synthetic static mutations.  No SQL is executed and no
database, network, provider or external parser is contacted.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
import subprocess
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_unmounted_durability_inert_ddl_rehearsal import (
    BODY_DIGEST,
    BODY_PATH,
    LOWERING_CONTRACT_PATH,
    LOWERING_SCHEMA_PATH,
    MANIFEST_PATH,
    PARENT_DIGEST,
    RECOVERY_SPEC,
    SQL_INERT_PATH,
    STRUCTURAL_PATH,
    _derive_conflict_constraint,
    _emit_lock_exact,
    _ordered_composites,
    _render_relations,
    _select_columns,
    _symbol_ident,
    _type_sql,
    _verify_positional_row_projections,
    _verify_trigger_terminals,
    _walk_program_nodes,
    build_lowering_contract,
    build_lowering_schema,
    canonical_digest,
    check_artifacts,
    derive_effective_catalogue,
    derive_effective_body,
    digest_preimage,
    load_and_bind_parents,
    recognize_inert_sql,
    render_expr,
    render_inert,
)

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parents() -> dict[str, Any]:
    return load_and_bind_parents()


def _base_render() -> dict[str, Any]:
    return render_inert()


# ---------------------------------------------------------------------------
# Clause 1 -- exact parent immutability/hashes, recovery population and the
# effective catalogue.
# ---------------------------------------------------------------------------


def test_parent_hashes_are_exact_and_immutable() -> None:
    structural = _load(STRUCTURAL_PATH)
    body = _load(BODY_PATH)
    assert structural["contract_sha256"] == PARENT_DIGEST
    assert body["contract_sha256"] == BODY_DIGEST
    assert body["parent_binding"]["contract_sha256"] == PARENT_DIGEST
    assert canonical_digest(structural) == PARENT_DIGEST
    assert canonical_digest(body) == BODY_DIGEST
    parents = _parents()
    assert parents["structural"]["contract_sha256"] == PARENT_DIGEST
    assert parents["body"]["contract_sha256"] == BODY_DIGEST


def test_canonical_inert_sql_checkout_is_forced_to_lf() -> None:
    relative = SQL_INERT_PATH.relative_to(ROOT).as_posix()
    attribute = subprocess.run(
        ["git", "check-attr", "eol", "--", relative],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        shell=False,
    )

    assert attribute.stdout.strip().endswith(": eol: lf")
    assert b"\r\n" not in SQL_INERT_PATH.read_bytes()


def test_recovery_population_and_effective_catalogue_reconcile() -> None:
    parents = _parents()
    effective = derive_effective_catalogue(parents)
    recovery_ids = [op["id"] for op in effective["recovery_operations"]]
    assert recovery_ids == [f"REC{idx:02d}" for idx in range(1, 27)]
    body = parents["body"]
    assert effective["relations"] == body["qualified_identifier_catalogue"]["relations"]
    assert effective["roles"] == body["effective_parent_summary"]["effective_roles"]
    assert (
        effective["trigger_declarations"]
        == body["effective_parent_summary"]["trigger_declarations"]
    )
    fabric_relations = [
        r for r in effective["relations"] if r.startswith("emr4_context_fabric.")
    ]
    assert len(effective["relations"]) == 22
    assert len(fabric_relations) == 18
    assert len(effective["roles"]) == 8
    assert len(effective["rls_policies"]) == 45
    digest_domain = next(
        row
        for row in effective["effective_structural"]["type_catalogue"]["domains"]
        if row["name"] == "digest_sha256"
    )
    assert digest_domain["not_null_values"] is False


def test_registration_initial_projection_policies_retain_narrow_lifecycle_access() -> (
    None
):
    effective = derive_effective_catalogue(_parents())
    policies = {policy["id"]: policy for policy in effective["rls_policies"]}
    lifecycle = "'LIFECYCLE'::emr4_context_fabric.logical_capability"

    required = {
        "pol_cf_01_select": "using_sql",
        "pol_cf_01_insert": "with_check_sql",
        "pol_cf_10_select": "using_sql",
        "pol_cf_10_insert": "with_check_sql",
        "pol_cf_11_select": "using_sql",
        "pol_cf_11_insert": "with_check_sql",
    }
    for policy_id, predicate_field in required.items():
        assert lifecycle in policies[policy_id][predicate_field]

    # PostgreSQL combines SELECT and UPDATE USING policy visibility for
    # SELECT FOR UPDATE. Lifecycle can therefore lock the existing stream
    # head through its closed security-definer entry point, but it cannot
    # author a replacement row or gain direct table authority.
    assert lifecycle in policies["pol_cf_01_update"]["using_sql"]
    assert lifecycle not in policies["pol_cf_01_update"]["with_check_sql"]
    for policy_id in ("pol_cf_10_update", "pol_cf_11_update"):
        assert lifecycle not in policies[policy_id]["using_sql"]
        assert lifecycle not in policies[policy_id]["with_check_sql"]

    roles = {
        role["role"]: role for role in effective["effective_structural"]["role_matrix"]
    }
    lifecycle_role = roles["emr4_context_fabric.context_lifecycle"]
    assert lifecycle_role["direct_table_dml"] == []
    assert lifecycle_role["direct_table_select"] == []


def test_rendered_stream_head_update_policy_preserves_lock_only_lifecycle_access() -> (
    None
):
    rendered = _base_render()
    sql = rendered["sql_text"]
    match = re.search(
        r"CREATE POLICY pol_cf_01_update\b.*?;",
        sql,
        flags=re.DOTALL,
    )
    assert match is not None
    policy_sql = match.group(0)
    lifecycle = "'LIFECYCLE'::emr4_context_fabric.logical_capability"
    using_sql, with_check_sql = policy_sql.split("\n    WITH CHECK ", maxsplit=1)
    assert lifecycle in using_sql
    assert lifecycle not in with_check_sql

    missing_lock = policy_sql.replace(", " + lifecycle, "", 1)
    widened_check = policy_sql.replace(
        "ARRAY['PRODUCER'::emr4_context_fabric.logical_capability]",
        "ARRAY['PRODUCER'::emr4_context_fabric.logical_capability, " + lifecycle + "]",
        1,
    )
    assert missing_lock != policy_sql
    assert widened_check != policy_sql
    for hostile_policy in (missing_lock, widened_check):
        hostile_sql = sql.replace(policy_sql, hostile_policy, 1)
        report = recognize_inert_sql(
            hostile_sql,
            rendered["manifest"],
            rendered["effective"],
        )
        assert not report.valid


def test_recovered_effective_body_population_is_exact() -> None:
    parents = _parents()
    effective = derive_effective_catalogue(parents)
    body, recovered = derive_effective_body(parents["body"], effective)

    assert len(parents["body"]["body_programs"]) == 22
    assert len(body["body_programs"]) == 23
    assert len(recovered["signatures"]["entry_points"]) == 9
    assert len(recovered["signatures"]["trigger_functions"]) == 14
    assert len(recovered["trigger_declarations"]) == 14
    assert body["postgresql_16_representability_recovery_v1"] == RECOVERY_SPEC


def test_effective_relation_row_order_matches_typed_catalogue() -> None:
    parents = _parents()
    effective = derive_effective_catalogue(parents)
    typed_relations = parents["body"]["qualified_identifier_catalogue"]["relations"]
    for relation in effective["effective_structural"]["relation_catalogue"][
        "relations"
    ]:
        relation_id = "emr4_context_fabric." + relation["name"]
        names = [
            column["name"] for column in relation["columns"] if column["name"] != "xmin"
        ]
        expected = [name for name in typed_relations[relation_id] if name != "xmin"]
        assert names == expected


def test_positional_row_projection_order_is_mechanically_closed() -> None:
    parents = _parents()
    effective = derive_effective_catalogue(parents)
    body, recovered = derive_effective_body(parents["body"], effective)
    _verify_positional_row_projections(body, recovered)

    candidate = copy.deepcopy(body)
    registration = next(
        program
        for program in candidate["body_programs"]
        if program["id"] == "emr4_context_fabric.register_observer_generation_v1"
    )
    binding_read = next(
        node
        for node in _walk_program_nodes(registration)
        if node["node_id"].endswith("binding.select")
    )
    columns = binding_read["operands"]["columns"]
    columns[4], columns[8] = columns[8], columns[4]
    with pytest.raises(ValueError, match="positional row projection order mismatch"):
        _verify_positional_row_projections(candidate, recovered)


def test_recovery_operations_are_position_closed_and_fragment_sealed() -> None:
    operations = RECOVERY_SPEC["operations"]
    assert [row["id"] for row in operations] == RECOVERY_SPEC["operation_order"]
    assert len(operations) == 9
    for operation in operations:
        assert operation["affected_ids"]
        assert operation["old_fragment_sha256"].startswith("sha256:")
        assert operation["new_fragment_sha256"].startswith("sha256:")
    nullability = operations[0]
    assert nullability["id"] == "RELAX_DIGEST_DOMAIN_NULLABILITY"
    assert nullability["affected_ids"] == ["emr4_context_fabric.digest_sha256"]
    reselect = operations[5]
    assert len(reselect["sites"]) == 4
    for site in reselect["sites"]:
        assert site["source_node_id"]
        assert site["effective_node_id"]
        assert site["reselect_node_id"]
        assert site["old_expression_sha256"].startswith("sha256:")
        assert site["new_expression_sha256"].startswith("sha256:")
        assert site["new_reselect_sha256"].startswith("sha256:")


def test_digest_domain_defers_presence_to_nullable_and_required_columns() -> None:
    sql = _base_render()["sql_text"]

    assert (
        "CREATE DOMAIN emr4_context_fabric.digest_sha256 AS pg_catalog.text\n"
        "    CONSTRAINT digest_sha256_check"
    ) in sql
    assert ("last_observation_digest emr4_context_fabric.digest_sha256,") in sql
    assert ("audit_head_digest emr4_context_fabric.digest_sha256 NOT NULL,") in sql
    assert ("last_contiguous_position = 0 AND last_observation_digest IS NULL") in sql
    assert "NULL::emr4_context_fabric.digest_sha256" in sql


def test_recovery_fragment_seal_drift_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = copy.deepcopy(RECOVERY_SPEC["operations"])
    candidate[0]["new_fragment_sha256"] = "sha256:" + "0" * 64
    monkeypatch.setitem(RECOVERY_SPEC, "operations", candidate)
    parents = _parents()
    with pytest.raises(ValueError, match="fragment-seal drift"):
        derive_effective_body(parents["body"], derive_effective_catalogue(parents))


def test_wrong_parent_hash_fails_closed() -> None:
    parents = _parents()
    structural = copy.deepcopy(parents["structural"])
    structural["contract_sha256"] = "sha256:" + "0" * 64
    parents["structural"] = structural
    with pytest.raises((ValueError, AssertionError)):
        derive_effective_catalogue(parents)


# ---------------------------------------------------------------------------
# Clause 2 -- whole lowering-contract JSON Schema validation and hostile
# unknown fields.
# ---------------------------------------------------------------------------


def test_lowering_contract_schema_accepts_contract() -> None:
    contract = build_lowering_contract()
    schema = build_lowering_schema()
    Draft202012Validator.check_schema(schema)
    assert list(Draft202012Validator(schema).iter_errors(contract)) == []
    assert contract["postgresql_target"]["major"] == 16
    assert (
        contract["opcode_populations"]["absent_instruction_opcode"] == "DERIVE_BINDING"
    )
    assert contract["opcode_populations"]["declared_instruction_opcodes"] == 22
    assert contract["opcode_populations"]["observed_instruction_opcodes"] == 21
    assert contract["opcode_populations"]["declared_expression_opcodes"] == 34
    assert contract["opcode_populations"]["observed_expression_opcodes"] == 34


def test_lowering_contract_hostile_unknown_field_rejected() -> None:
    contract = build_lowering_contract()
    schema = build_lowering_schema()
    candidate = copy.deepcopy(contract)
    candidate["invented_authority"] = True
    assert list(Draft202012Validator(schema).iter_errors(candidate))


def test_canonical_lowering_contract_files_validate() -> None:
    contract = _load(LOWERING_CONTRACT_PATH)
    schema = _load(LOWERING_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    assert list(Draft202012Validator(schema).iter_errors(contract)) == []
    assert contract == build_lowering_contract()
    assert schema == build_lowering_schema()


# ---------------------------------------------------------------------------
# Clause 3 -- two isolated byte-identical renders and exact canonical
# regeneration.
# ---------------------------------------------------------------------------


def test_isolated_renders_are_byte_identical() -> None:
    first = render_inert()
    second = render_inert()
    assert first["sql_text"] == second["sql_text"]
    assert first["manifest"] == second["manifest"]
    assert first["sql_text"].endswith("\n")


def test_renderer_uses_physical_pg_catalog_type_names() -> None:
    sql = _base_render()["sql_text"]
    assert _type_sql("pg_catalog.boolean") == "pg_catalog.bool"
    assert _type_sql("pg_catalog.bigint") == "pg_catalog.int8"
    assert _type_sql("pg_catalog.integer") == "pg_catalog.int4"
    assert _type_sql("pg_catalog.smallint") == "pg_catalog.int2"
    assert _type_sql("pg_catalog.bigint[]") == "pg_catalog.int8[]"

    # Logical type labels remain in quoted semantic-digest preimages, while
    # executable casts and declarations use PostgreSQL's physical catalog
    # names so a schema-qualified parse cannot resolve the wrong object kind.
    assert "'pg_catalog.bigint'" in sql
    for alias in ("boolean", "bigint", "integer", "smallint"):
        assert f"::pg_catalog.{alias}" not in sql
    assert "CREATE DOMAIN emr4_context_fabric.frame_mask AS pg_catalog.int2" in sql
    assert "    eligible pg_catalog.bool," in sql
    assert "    stream_epoch pg_catalog.int8," in sql
    assert "0::pg_catalog.int4" in sql


def test_renderer_aliases_reserved_primary_local_without_contract_drift() -> None:
    result = _base_render()
    sql = result["sql_text"]
    body = result["loaded"]["body"]
    apply_program = next(
        program
        for program in body["body_programs"]
        if program["id"] == "emr4_context_fabric.apply_durability_transition_v1"
    )

    assert _symbol_ident("primary") == "cf_primary_admission"
    assert any(symbol["id"] == "primary" for symbol in apply_program["symbols"])
    assert (
        "cf_primary_admission "
        "emr4_context_fabric.context_proofread_observation_admission;"
    ) in sql
    assert "cf_primary_admission.key_id" in sql
    assert re.search(r"\bprimary\.[a-zA-Z_]", sql) is None
    assert "INTO STRICT primary" not in sql


def test_json_keys_exact_canonicalizes_expected_set_order() -> None:
    source = {
        "op": "REF",
        "kind": "LOCAL",
        "symbol": "payload",
        "type": "pg_catalog.jsonb",
    }
    unsorted = {
        "op": "JSON_KEYS_EXACT",
        "source": source,
        "keys": ["practitioner_id", "appointment_id", "end_time"],
        "type": "pg_catalog.boolean",
    }
    canonical = copy.deepcopy(unsorted)
    canonical["keys"] = ["appointment_id", "end_time", "practitioner_id"]

    rendered = render_expr(unsorted)
    assert rendered == render_expr(canonical)
    assert "pg_catalog.array_agg(k.k ORDER BY k.k)" in rendered
    assert (
        "ARRAY['appointment_id', 'end_time', 'practitioner_id']"
        "::pg_catalog.text[]" in rendered
    )
    assert "ARRAY['practitioner_id', 'appointment_id', 'end_time']" not in rendered


def test_producer_json_membership_expected_keys_match_actual_sort_order() -> None:
    sql = _base_render()["sql_text"]
    expected = (
        "ARRAY['appointment_id', 'end_time', 'location_id', "
        "'practitioner_id', 'reason_codes', 'start_time']::pg_catalog.text[]"
    )
    predecessor = (
        "ARRAY['appointment_id', 'practitioner_id', 'location_id', "
        "'start_time', 'end_time', 'reason_codes']::pg_catalog.text[]"
    )

    assert sql.count(expected) == 7
    assert predecessor not in sql


def test_renderer_rejects_physical_symbol_alias_collision() -> None:
    rendered = _base_render()
    body = copy.deepcopy(rendered["loaded"]["body"])
    effective = rendered["effective"]
    program = next(
        item
        for item in body["body_programs"]
        if item["id"] == "emr4_context_fabric.apply_durability_transition_v1"
    )
    primary = next(symbol for symbol in program["symbols"] if symbol["id"] == "primary")
    collision = copy.deepcopy(primary)
    collision["id"] = "cf_primary_admission"
    program["symbols"].append(collision)

    signature = next(
        item
        for item in effective["signatures"]["entry_points"]
        if item["id"] == program["id"]
    )
    with pytest.raises(ValueError, match="physical PL/pgSQL symbol alias collision"):
        from scripts.raisa_provider_free_unmounted_durability_inert_ddl_rehearsal import (  # noqa: PLC0415
            _render_program_function,
        )

        _render_program_function(program, signature, {"effective": effective})


def test_renderer_omits_modeled_system_xmin_from_create_tables() -> None:
    result = _base_render()
    sql = result["sql_text"]
    relations = result["effective"]["effective_structural"]["relation_catalogue"][
        "relations"
    ]

    assert len(relations) == 18
    assert sql.count("CREATE TABLE emr4_context_fabric.") == 18
    assert "\n    xmin pg_catalog.xid" not in sql
    for relation in relations:
        xmin = [column for column in relation["columns"] if column["name"] == "xmin"]
        assert xmin == [
            {
                "name": "xmin",
                "data_type": "xid",
                "nullable": False,
                "default_sql": None,
            }
        ]


def test_renderer_rejects_modeled_system_xmin_shape_drift() -> None:
    effective = copy.deepcopy(_base_render()["effective"])
    relation = effective["effective_structural"]["relation_catalogue"]["relations"][0]
    xmin = next(column for column in relation["columns"] if column["name"] == "xmin")
    xmin["nullable"] = True

    with pytest.raises(ValueError, match="modeled system xmin shape drift"):
        _render_relations(effective)


def test_renderer_stages_relation_dependencies_by_statement_family() -> None:
    sql = _base_render()["sql_text"]
    tables = [
        match.start() for match in re.finditer(r"^CREATE TABLE ", sql, re.MULTILINE)
    ]
    keys = [
        match.start()
        for match in re.finditer(
            r"^(?:ALTER TABLE .* ADD CONSTRAINT (?:pk|uq)_|CREATE UNIQUE INDEX uq_)",
            sql,
            re.MULTILINE,
        )
    ]
    foreign_keys = [
        match.start()
        for match in re.finditer(
            r"^ALTER TABLE .* ADD CONSTRAINT fk_", sql, re.MULTILINE
        )
    ]
    checks = [
        match.start()
        for match in re.finditer(
            r"^ALTER TABLE .* ADD CONSTRAINT ck_", sql, re.MULTILINE
        )
    ]

    assert len(tables) == 18
    assert tables and keys and foreign_keys and checks
    assert max(tables) < min(keys)
    assert max(keys) < min(foreign_keys)
    assert max(foreign_keys) < min(checks)


def test_canonical_artifacts_regenerate_exactly() -> None:
    outcome = check_artifacts()
    assert outcome["valid"], outcome["issues"]
    result = _base_render()
    assert SQL_INERT_PATH.read_text(encoding="utf-8") == result["sql_text"]
    assert _load(MANIFEST_PATH) == result["manifest"]


# ---------------------------------------------------------------------------
# Clause 4 -- all six phases and every required population/count/order.
# ---------------------------------------------------------------------------


def test_six_phases_in_exact_order() -> None:
    sql = _base_render()["sql_text"]
    phases = re.findall(r"^-- PHASE (\d) --", sql, flags=re.MULTILINE)
    assert phases == ["1", "2", "3", "4", "5", "6"]
    ends = re.findall(r"^-- END PHASE (\d) --", sql, flags=re.MULTILINE)
    assert ends == ["1", "2", "3", "4", "5", "6"]


def test_phase_populations_and_counts() -> None:
    sql = _base_render()["sql_text"]
    assert sql.count("CREATE ROLE ") == 8
    assert sql.count("CREATE SCHEMA ") == 1
    assert sql.count("CREATE DOMAIN ") == 4
    assert sql.count("CREATE TYPE ") == 28  # 19 enums + 9 composites
    assert sql.count("CREATE TABLE emr4_context_fabric.") == 18
    assert sql.count("CREATE POLICY ") == 45
    assert sql.count("CREATE TRIGGER ") == 7
    assert sql.count("CREATE CONSTRAINT TRIGGER ") == 7
    assert sql.count("CREATE FUNCTION emr4_context_fabric.") == 24
    assert sql.count("ENABLE ROW LEVEL SECURITY") == 18
    assert sql.count("FORCE ROW LEVEL SECURITY") == 18


def test_composite_create_order_is_stable_and_dependency_safe() -> None:
    result = _base_render()
    composites = result["effective"]["effective_structural"]["type_catalogue"][
        "composites"
    ]
    expected = [
        "emr4_context_fabric." + row["name"] for row in _ordered_composites(composites)
    ]
    actual = [
        row["identifier"]
        for row in result["manifest"]["ordered_nodes"]
        if row["kind"] == "COMPOSITE"
    ]
    assert actual == expected
    assert actual.index("emr4_context_fabric.future_key_interval_v1") < actual.index(
        "emr4_context_fabric.generation_registration_v1"
    )


def test_composite_dependency_cycle_fails_closed() -> None:
    hostile = [
        {"name": "first_v1", "fields": [{"name": "second", "data_type": "second_v1"}]},
        {"name": "second_v1", "fields": [{"name": "first", "data_type": "first_v1"}]},
    ]
    with pytest.raises(ValueError, match="composite dependency cycle"):
        _ordered_composites(hostile)


def test_recognizer_rejects_composite_dependency_order_regression() -> None:
    result = _base_render()
    sql = result["sql_text"]
    future = re.search(
        r"CREATE TYPE emr4_context_fabric\.future_key_interval_v1 AS \(\n.*?\n\);",
        sql,
        flags=re.DOTALL,
    )
    registration = re.search(
        r"CREATE TYPE emr4_context_fabric\.generation_registration_v1 AS \(\n.*?\n\);",
        sql,
        flags=re.DOTALL,
    )
    assert future is not None and registration is not None
    assert future.start() < registration.start()
    sentinel = "__EMR4_FUTURE_KEY_INTERVAL_COMPOSITE__"
    mutated = sql.replace(future.group(0), sentinel, 1)
    mutated = mutated.replace(registration.group(0), future.group(0), 1)
    mutated = mutated.replace(sentinel, registration.group(0), 1)
    report = recognize_inert_sql(mutated, result["manifest"], result["effective"])
    assert not report.valid
    assert any(issue.code == "composite_dependency_order" for issue in report.issues)


def test_renderer_order_is_preserved() -> None:
    manifest = _base_render()["manifest"]
    parents = _parents()
    body, _ = derive_effective_body(
        parents["body"], derive_effective_catalogue(parents)
    )
    expected = body["renderer_order"]
    entry_ids = [
        item["identifier"]
        for item in manifest["ordered_nodes"]
        if item["kind"] == "ENTRY_POINT"
    ]
    trigger_ids = [
        item["identifier"]
        for item in manifest["ordered_nodes"]
        if item["kind"] == "TRIGGER_FUNCTION"
    ]
    assert entry_ids == expected[:9]
    assert trigger_ids == expected[9:]


def _walk_ioc_nodes(body: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []
    for program in body["body_programs"]:
        for node in _walk_program_nodes(program):
            if node["op"] == "INSERT_OR_RELOAD_COMPARE":
                out.append((program["id"], node))
    return out


# ---------------------------------------------------------------------------
# Clause 5 -- immutable-parent and recovered effective-program accounting.
# ---------------------------------------------------------------------------


def test_all_effective_programs_accounted_and_expression_ceiling() -> None:
    manifest = _base_render()["manifest"]
    accounting = manifest["body_program_accounting"]
    assert manifest["immutable_parent_program_count"] == 22
    assert manifest["effective_program_count"] == 23
    assert len(accounting) == 23
    assert sum(row["node_count"] for row in accounting) == 756
    assert sum(row["expression_count"] for row in accounting) == 14488
    for row in accounting:
        assert sum(row["instruction_counts"].values()) == row["node_count"]
    parents = _parents()
    body, _ = derive_effective_body(
        parents["body"], derive_effective_catalogue(parents)
    )
    program_ids = {program["id"] for program in body["body_programs"]}
    assert {row["id"] for row in accounting} == program_ids
    assert manifest["catalogue_assertions"]["insert_or_reload_compare"] == 21
    assert manifest["catalogue_assertions"]["derive_binding_occurrences"] == 0
    assert manifest["opcode_populations"] == {
        "declared_instruction_opcodes": 22,
        "observed_instruction_opcodes": 21,
        "declared_expression_opcodes": 34,
        "observed_expression_opcodes": 34,
        "absent_instruction_opcode": "DERIVE_BINDING",
    }


# ---------------------------------------------------------------------------
# Clause 6 -- all 21 exact conflict mappings plus wrong/untargeted conflict,
# zero/multiple-winner and write-subtransaction hostile mutations.
# ---------------------------------------------------------------------------


def test_all_21_insert_or_reload_compare_unique_mappings() -> None:
    parents = _parents()
    effective = derive_effective_catalogue(parents)
    result = _base_render()
    ioc_nodes = _walk_ioc_nodes(parents["body"])
    assert len(ioc_nodes) == 21
    assert result["sql_text"].count("ON CONFLICT ON CONSTRAINT ") == 21
    for _program_id, node in ioc_nodes:
        ops = node["operands"]
        name = _derive_conflict_constraint(
            effective, ops["relation"], ops["conflict_key_columns"]
        )
        assert "ON CONFLICT ON CONSTRAINT " + name + " DO NOTHING" in result["sql_text"]
    assert "WHEN unique_violation THEN" not in result["sql_text"]
    assert "GET STACKED DIAGNOSTICS cf_constraint_name" not in result["sql_text"]
    assert "cf_constraint_name pg_catalog.text" not in result["sql_text"]


def test_conflict_derivation_rejects_multiple_winners() -> None:
    parents = _parents()
    effective = derive_effective_catalogue(parents)
    node = _walk_ioc_nodes(parents["body"])[0][1]
    ops = node["operands"]
    effective["constraints"][ops["relation"]].append(
        {
            "kind": "PRIMARY_KEY",
            "name": "pk_duplicate",
            "columns": list(ops["conflict_key_columns"]),
        }
    )
    with pytest.raises(ValueError):
        _derive_conflict_constraint(
            effective, ops["relation"], ops["conflict_key_columns"]
        )


def test_conflict_derivation_rejects_zero_winners() -> None:
    parents = _parents()
    effective = derive_effective_catalogue(parents)
    node = _walk_ioc_nodes(parents["body"])[0][1]
    ops = node["operands"]
    relation = ops["relation"]
    effective["constraints"][relation] = [
        row
        for row in effective["constraints"][relation]
        if row["columns"] != list(ops["conflict_key_columns"])
    ]
    with pytest.raises(ValueError):
        _derive_conflict_constraint(effective, relation, ops["conflict_key_columns"])


def test_all_39_updates_are_uniquely_keyed_and_avoid_write_subtransactions() -> None:
    parents = _parents()
    effective = derive_effective_catalogue(parents)
    result = _base_render()
    update_nodes = [
        node
        for program in parents["body"]["body_programs"]
        for node in _walk_program_nodes(program)
        if node["op"] == "UPDATE"
    ]

    assert len(update_nodes) == 39
    for node in update_nodes:
        ops = node["operands"]
        assert _derive_conflict_constraint(
            effective, ops["relation"], ops["key_columns"]
        )

    function_start = result["sql_text"].index(
        "CREATE FUNCTION emr4_context_fabric.project_update_confirm_reschedule_v1"
    )
    function_end = result["sql_text"].index(
        "$durability_inert$\nLANGUAGE", function_start
    )
    function_sql = result["sql_text"][function_start:function_end]
    update_start = function_sql.index(
        "UPDATE emr4_context_fabric.context_observation_stream_head SET"
    )
    update_end = function_sql.index("END IF;", update_start) + len("END IF;")
    update_sql = function_sql[update_start:update_end]
    assert " INTO updated_head;" in update_sql
    assert "IF NOT FOUND THEN" in update_sql
    assert "INTO STRICT updated_head" not in update_sql
    assert "\n    EXCEPTION\n" not in update_sql


def test_update_renderer_rejects_a_non_unique_declared_key() -> None:
    parents = _parents()
    effective = derive_effective_catalogue(parents)
    update = next(
        node
        for program in parents["body"]["body_programs"]
        for node in _walk_program_nodes(program)
        if node["op"] == "UPDATE"
    )
    ops = update["operands"]
    with pytest.raises(ValueError, match="does not map to exactly one"):
        _derive_conflict_constraint(effective, ops["relation"], ["practice_id"])


def test_untargeted_conflict_mutation_is_rejected() -> None:
    result = _base_render()
    mutated = result["sql_text"].replace(
        "ON CONFLICT ON CONSTRAINT pk_cf_02 DO NOTHING",
        "ON CONFLICT DO NOTHING",
        1,
    )
    report = recognize_inert_sql(mutated, result["manifest"], result["effective"])
    assert not report.valid
    assert any(issue.code == "on_conflict_do_nothing" for issue in report.issues)


def test_wrong_constraint_name_mutation_is_rejected() -> None:
    result = _base_render()
    mutated = result["sql_text"].replace(
        "ON CONFLICT ON CONSTRAINT pk_cf_02 DO NOTHING",
        "ON CONFLICT ON CONSTRAINT pk_bogus DO NOTHING",
        1,
    )
    report = recognize_inert_sql(mutated, result["manifest"], result["effective"])
    assert not report.valid
    assert any(issue.code == "wrong_constraint" for issue in report.issues)


# ---------------------------------------------------------------------------
# Clause 7 -- digest delimiter/null/type/order/time-zone hostile vectors.
# ---------------------------------------------------------------------------


def test_digest_null_and_empty_text_cannot_collide() -> None:
    null_pre = digest_preimage("edge", ["pg_catalog.text"], [None])
    empty_pre = digest_preimage("edge", ["pg_catalog.text"], [""])
    assert null_pre != empty_pre
    assert null_pre.endswith(":-1")
    assert empty_pre.endswith(":0:")


def test_digest_operand_reorder_changes_preimage() -> None:
    a = digest_preimage("edge", ["pg_catalog.text", "pg_catalog.bigint"], ["x", 7])
    b = digest_preimage("edge", ["pg_catalog.bigint", "pg_catalog.text"], [7, "x"])
    assert a != b


def test_digest_type_change_changes_preimage() -> None:
    a = digest_preimage("edge", ["pg_catalog.text"], ["7"])
    b = digest_preimage("edge", ["pg_catalog.bigint"], [7])
    assert a != b


def test_digest_vectors_are_recorded_and_sql_uses_unit_separator() -> None:
    result = _base_render()
    assert len(result["manifest"]["digest_vectors"]) >= 4
    assert len(result["manifest"]["digest_profiles"]) == 12
    assert "pg_catalog.chr(31)" in result["sql_text"]
    for vector in result["manifest"]["digest_vectors"]:
        assert vector["preimage"] == digest_preimage(
            vector["profile"], vector["operand_types"], vector["values"]
        )


def test_digest_time_zone_is_utc_six_fractional_digits() -> None:
    # The timestamptz canonical text must render UTC with six fractional digits
    # and a literal terminal Z in both the SQL and the Python reference.
    result = _base_render()
    assert "AT TIME ZONE 'UTC'" in result["sql_text"]
    assert 'HH24:MI:SS.US"Z"' in result["sql_text"]
    assert re.search(r'HH24:MI:SS\.US(?!")', result["sql_text"]) is None
    import datetime as _dt

    sample = _dt.datetime(2026, 8, 8, 12, 34, 56, 123456, tzinfo=_dt.timezone.utc)
    pre = digest_preimage("edge.ts", ["pg_catalog.timestamptz"], [sample])
    assert pre.endswith(":2026-08-08T12:34:56.123456Z")
    assert "Z" in pre


# ---------------------------------------------------------------------------
# Clause 8 -- independent recognizer rejection of hostile mutations.
# ---------------------------------------------------------------------------


def test_recognizer_rejects_hostile_mutations() -> None:
    result = _base_render()
    sql = result["sql_text"]
    manifest = result["manifest"]
    effective = result["effective"]

    def rejected(mutated: str, code: str | None = None) -> None:
        report = recognize_inert_sql(mutated, manifest, effective)
        assert not report.valid
        if code is not None:
            assert any(issue.code == code for issue in report.issues)

    rejected(sql + "\nSELECT 1;", "top_level_dml")
    rejected(sql + "\nBEGIN;", "transaction_control")
    rejected(
        sql + "\nDELETE FROM emr4_context_fabric.context_retention_policy;",
        "top_level_dml",
    )
    rejected(sql + "\n\\dt", "psql_meta")
    rejected(sql + "\nCREATE EXTENSION pgcrypto;", "extension")
    rejected(
        sql + "\nCOPY emr4_context_fabric.context_retention_policy FROM PROGRAM 'x';",
        "file_network",
    )
    rejected(
        sql
        + "\nCREATE FUNCTION emr4_context_fabric.helper_v1() RETURNS void AS $$ BEGIN NULL; END; $$ LANGUAGE plpgsql;",
        "helper_overload",
    )
    rejected(
        sql.replace(
            "CREATE TABLE emr4_context_fabric.context_observation_stream_head",
            "CREATE TABLE context_observation_stream_head",
            1,
        ),
        "unqualified_identifier",
    )
    rejected(
        sql.replace(
            "SET search_path = pg_catalog, emr4_context_fabric",
            "SET search_path = public, pg_catalog",
            1,
        ),
        "search_path",
    )
    rejected(sql.replace("SECURITY DEFINER", "SECURITY INVOKER", 1), "security_invoker")
    rejected(
        sql.replace("REVOKE ALL ON SCHEMA emr4_context_fabric FROM PUBLIC;", "", 1),
        "missing_revoke",
    )
    rejected(
        sql
        + "\nGRANT EXECUTE ON FUNCTION emr4_context_fabric.cf_guard_claim_v1() TO context_producer;",
        "trigger_grant",
    )
    rejected(
        sql + "\nINSERT INTO public.appointments (id) VALUES (NULL);", "application_dml"
    )
    rejected(sql + "\n-- C:\\temp\\escape\nSELECT 1;", "path_escape")


def test_recognizer_rejects_malformed_quotes_and_dollar_bodies() -> None:
    result = _base_render()
    sql = result["sql_text"]
    manifest = result["manifest"]
    effective = result["effective"]
    malformed_quote = sql.replace(
        "'in_progress'::pg_catalog.text", "'in_progress''::pg_catalog.text", 1
    )
    report = recognize_inert_sql(malformed_quote, manifest, effective)
    assert not report.valid
    malformed_dollar = sql.replace(
        "$durability_inert$\nLANGUAGE", "$durability_inert\nLANGUAGE", 1
    )
    report = recognize_inert_sql(malformed_dollar, manifest, effective)
    assert not report.valid


def test_recognizer_rejects_missing_and_swapped_statements() -> None:
    result = _base_render()
    sql = result["sql_text"]
    manifest = result["manifest"]
    effective = result["effective"]
    missing = sql.replace(
        "CREATE POLICY pol_cf_18_insert", "CREATE POLICY pol_cf_18_insert_x", 1
    )
    missing = missing.replace(
        "CREATE POLICY pol_cf_18_insert_x ON emr4_context_fabric.context_retention_policy",
        "",
        1,
    )
    report = recognize_inert_sql(missing, manifest, effective)
    assert not report.valid
    swapped = sql.replace(
        "CREATE ROLE context_producer", "CREATE ROLE context_observer", 1
    )
    report = recognize_inert_sql(swapped, manifest, effective)
    assert not report.valid


# ---------------------------------------------------------------------------
# Clause 9 -- no dependency/process/socket/database/provider/environment/
# Alembic reachability.
# ---------------------------------------------------------------------------


def test_module_imports_are_stdlib_only() -> None:
    source = (
        ROOT / "scripts/raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py"
    ).read_text(encoding="utf-8")
    forbidden_imports = [
        "import subprocess",
        "from subprocess",
        "import socket",
        "from socket",
        "import http",
        "from http",
        "import sqlalchemy",
        "from sqlalchemy",
        "import psycopg",
        "from psycopg",
        "import alembic",
        "from alembic",
        "import requests",
        "from requests",
        "import urllib",
        "from urllib",
    ]
    for token in forbidden_imports:
        assert token not in source, token
    assert "os.environ" not in source
    assert "os.system" not in source


def test_monkeypatched_sentinel_surfaces_are_never_touched(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("forbidden surface touched")

    monkeypatch.setattr("socket.socket", boom)
    monkeypatch.setattr("subprocess.Popen", boom)
    result = render_inert()
    assert result["sql_text"]
    assert result["manifest"]["statement_count"] > 0


def test_unknown_lock_mode_fails_before_emission() -> None:
    node = {
        "node_id": "hostile.unknown-lock",
        "op": "LOCK_EXACT",
        "operands": {
            "relation": "public.appointments",
            "columns": ["id"],
            "predicate": {
                "op": "CONST",
                "type": "pg_catalog.boolean",
                "value": True,
            },
            "output_symbol": "appointment",
            "mode": "RAW_CALLER_SELECTED_LOCK",
        },
    }
    with pytest.raises(ValueError, match="unknown lock mode"):
        _emit_lock_exact(node, {}, 0)


# ---------------------------------------------------------------------------
# Clause 10 -- DERIVE_BINDING occurrence, wrong SQLSTATE, wrong OLD/NEW,
# omitted trigger/policy/constraint and arbitrary retry elimination all fail
# closed.
# ---------------------------------------------------------------------------


def _mutated_loaded_with_derive_binding() -> dict[str, Any]:
    parents = _parents()
    body = copy.deepcopy(parents["body"])
    program = body["body_programs"][0]
    program["ast"]["nodes"].insert(
        1,
        {
            "node_id": program["id"] + ".injected.derive",
            "op": "DERIVE_BINDING",
            "operands": {},
        },
    )
    parents["body"] = body
    return parents


def test_derive_binding_occurrence_fails_closed() -> None:
    loaded = _mutated_loaded_with_derive_binding()
    with pytest.raises((ValueError, AssertionError)):
        render_inert(loaded=loaded)


def test_wrong_sqlstate_mutation_is_rejected() -> None:
    result = _base_render()
    mutated = result["sql_text"].replace(
        "ERRCODE = 'CF004', MESSAGE = 'required_row_missing_or_ambiguous'",
        "ERRCODE = 'P0001', MESSAGE = 'required_row_missing_or_ambiguous'",
        1,
    )
    report = recognize_inert_sql(mutated, result["manifest"], result["effective"])
    assert not report.valid
    assert any(issue.code == "wrong_sqlstate" for issue in report.issues)


def test_wrong_old_new_terminal_fails_closed() -> None:
    parents = _parents()
    body = copy.deepcopy(parents["body"])
    guard = next(
        program
        for program in body["body_programs"]
        if program["id"].endswith("cf_guard_claim_v1")
    )
    switch = guard["ast"]["nodes"][1]["operands"]
    update_arm = next(arm for arm in switch["arms"] if arm["tg_op"] == "UPDATE")
    for node in _walk_program_nodes({"ast": {"nodes": update_arm["nodes"]}}):
        if node["op"] == "RETURN_NEW":
            node["op"] = "RETURN_OLD"
            break
    with pytest.raises((ValueError, AssertionError)):
        _verify_trigger_terminals(body)


def test_omitted_policy_fails_closed() -> None:
    parents = _parents()
    effective = derive_effective_catalogue(parents)
    removed = effective["rls_policies"].pop()
    assert removed["id"]
    mutated = render_inert(effective=effective, loaded=parents)
    # The original canonical manifest no longer matches the reduced artifact.
    original = _base_render()
    report = recognize_inert_sql(mutated["sql_text"], original["manifest"], effective)
    assert not report.valid


def test_arbitrary_retry_marker_fails_closed() -> None:
    parents = _parents()
    body = copy.deepcopy(parents["body"])

    def find_marker(nodes: list[dict[str, Any]]) -> dict[str, Any] | None:
        for node in nodes:
            if node["op"] == "IF" and node["operands"]["then"]:
                first = node["operands"]["then"][0]
                if first["op"] == "PROPAGATE_RETRYABLE":
                    return first["operands"]
            for child in _walk_program_nodes({"ast": {"nodes": nodes}}):
                if child["op"] == "IF" and child["operands"]["then"]:
                    first = child["operands"]["then"][0]
                    if first["op"] == "PROPAGATE_RETRYABLE":
                        return first["operands"]
        return None

    marker = None
    for program in body["body_programs"]:
        marker = find_marker(program["ast"]["nodes"])
        if marker is not None:
            break
    assert marker is not None
    marker["internal_retry"] = True
    parents["body"] = body
    with pytest.raises((ValueError, AssertionError)):
        render_inert(loaded=parents)


def test_manifest_records_parent_hashes_and_effective_digest() -> None:
    manifest = _base_render()["manifest"]
    assert manifest["structural_parent"]["contract_sha256"] == PARENT_DIGEST
    assert manifest["body_parent"]["contract_sha256"] == BODY_DIGEST
    assert manifest["postgresql_major"] == 16
    assert manifest["effective_catalogue_digest"].startswith("sha256:")
    assert manifest["sql_sha256"].startswith("sha256:")
    assert manifest["artifact"] == (
        "orchestration/continuity/raisa-provider-free-unmounted-durability-"
        "inert-ddl-rehearsal/durability-schema.sql.inert"
    )


# ---------------------------------------------------------------------------
# Same-lane correction 1 -- exact cardinality, isolation assertions, bounded
# source delete, PostgreSQL syntax/types and canonical values.
# ---------------------------------------------------------------------------


def test_renderer_exact_cardinality_maps_zero_and_multiple_to_cf004() -> None:
    sql = _base_render()["sql_text"]
    assert sql.count("WHEN NO_DATA_FOUND THEN") >= 1
    assert sql.count("WHEN TOO_MANY_ROWS THEN") >= 1
    assert sql.count("INTO STRICT ") >= 100
    # Exact reads map zero and non-unique results to CF004. Uniquely keyed
    # UPDATEs map zero through FOUND; their renderer-time unique-key proof makes
    # a multiple-row result structurally impossible without catalogue damage.
    cf004 = "RAISE EXCEPTION USING ERRCODE = 'CF004', MESSAGE = 'required_row_missing_or_ambiguous'"
    assert sql.count(cf004) >= 100
    assert " INTO updated_head;\n    IF NOT FOUND THEN" in sql
    # No P0001/P0002/P0003 or class-42 substitution is permitted.
    for leaked in ("'P0001'", "'P0002'", "'P0003'", "ERRCODE = '42"):
        assert leaked not in sql, leaked


def test_renderer_key_bounded_delete_uses_exact_key_cte() -> None:
    sql = _base_render()["sql_text"]
    assert "WITH selected_keys AS (" in sql
    assert (
        "DELETE FROM emr4_context_fabric.diary_context_observation_outbox_v1 AS d USING selected_keys AS s"
        in sql
    )
    assert "LIMIT 1000" in sql
    assert "SELECT pg_catalog.count(*) INTO purged_row_count FROM deleted;" in sql
    # No DELETE ... ORDER BY ... LIMIT form remains anywhere.
    assert re.search(r"DELETE\s+FROM\b[^;]*\bORDER\s+BY\b", sql) is None
    assert re.search(r"DELETE\s+FROM\b[^;]*\bLIMIT\b", sql) is None


def test_renderer_typed_complete_sets_construct_full_rows() -> None:
    sql = _base_render()["sql_text"]
    # Partial projection (audit log id only) is built into a full typed row.
    assert (
        "array_agg((ROW(public.appointment_audit_log.id, NULL::pg_catalog.uuid" in sql
    )
    # The two system-xmin set projections stay honest: only the accepted user
    # projected value plus explicitly typed nulls, never a composite xmin member.
    assert (
        "array_agg((ROW(public.diary_committed_events.id, NULL::pg_catalog.uuid" in sql
    )
    assert (
        "array_agg((ROW(NULL::pg_catalog.uuid, NULL::emr4_context_fabric.source_contract_code, NULL::pg_catalog.uuid, emr4_context_fabric.diary_context_aggregate_aliases_v1.opaque_aggregate_alias"
        in sql
    )
    # No anonymous-record aggregation and no pg_catalog grammar misuse.
    assert "array_agg(sub" not in sql
    assert "pg_catalog.ARRAY" not in sql
    assert "pg_catalog.ROW" not in sql


def test_renderer_system_xmin_uses_record_local() -> None:
    sql = _base_render()["sql_text"]
    # xmin-carrying exact reads use a record local and explicitly name the
    # system-column output field. Direct var.xmin lookup preserves the runtime
    # shape of an anonymous PL/pgSQL record; (var).xmin requires a fixed
    # composite descriptor and is therefore forbidden.
    assert "claim record;" in sql
    assert "event record;" in sql
    assert "claim.xmin" in sql
    assert "event.xmin" in sql
    assert "old_appointment record;" in sql
    assert "old_appointment.xmin" in sql
    for symbol in (
        "head",
        "outbox",
        "final_alias",
        "alias_outbox",
        "final_head",
        "head_outbox",
    ):
        assert f"{symbol} record;" in sql
        assert f"{symbol}.xmin" in sql
        assert f"({symbol}).xmin" not in sql
    assert "OLD.xmin" not in sql
    assert "NEW.xmin" not in sql
    assert ").xmin" not in sql
    assert ".xmin INTO STRICT" not in sql
    assert sql.count(".xmin AS xmin INTO STRICT") == 62
    assert sql.count(".xmin") == 118
    assert (
        _select_columns(
            "emr4_context_fabric.context_observation_stream_head",
            ["practice_id", "xmin"],
        )
        == "emr4_context_fabric.context_observation_stream_head.practice_id, "
        "emr4_context_fabric.context_observation_stream_head.xmin AS xmin"
    )
    # SELECT_SET arrays that only count rows remain typed composite arrays.
    assert "current_events public.diary_committed_events[];" in sql


def test_recovery_manifest_closes_owners_dependencies_and_applicability() -> None:
    manifest = _base_render()["manifest"]

    assert manifest["catalogue_assertions"]["schema_owner"] == "context_schema_owner"
    assert manifest["catalogue_assertions"]["fabric_type_owner_count"] == 32
    assert manifest["catalogue_assertions"]["fabric_relation_owner_count"] == 18
    assert manifest["catalogue_assertions"]["application_owner_changes"] == 0
    assert manifest["catalogue_assertions"]["runtime_schema_create_grants"] == 0
    assert manifest["dependency_assertions"] == {
        "support_helper_precedes_all_rls_policies": True,
        "paired_guard_dependencies": RECOVERY_SPEC["paired_guard_dependencies"],
    }
    applicability = manifest["postgresql_16_representability_recovery_v1"][
        "appointment_applicability"
    ]
    assert applicability == {
        "source": "single_complete_set_read",
        "zero": "inert",
        "one": "proof_required",
        "multiple": {"failure_id": "F_CARDINALITY", "sqlstate": "CF004"},
        "arbitrary_stream_selection": False,
    }


def test_renderer_isolation_assertions_are_read_only() -> None:
    sql = _base_render()["sql_text"]
    assert sql.count("pg_catalog.current_setting('transaction_isolation')") == 9
    assert sql.count("'read committed'") == 2
    assert sql.count("'serializable'") == 7
    # A comment is not an assertion.
    assert "-- assert_isolation" not in sql


def test_renderer_unique_race_reload_proves_exact_cardinality() -> None:
    sql = _base_render()["sql_text"]
    # Insert-success stays in the top-level transaction and an exact conflict
    # target suppresses only the typed winner race.
    assert (
        sql.count(
            "RETURNING cf_target.practice_id, cf_target.source_contract_id, "
            "cf_target.product_appointment_uuid, cf_target.opaque_aggregate_alias, "
            "cf_target.created_at, cf_target.stream_id INTO alias;\n"
            "    IF NOT FOUND THEN"
        )
        >= 1
    )
    assert "ON CONFLICT ON CONSTRAINT pk_cf_02 DO NOTHING" in sql
    # Winner reload is a strict exact read mapping zero/multiple to CF004.
    assert "INTO STRICT alias\n" in sql
    assert "WHEN NO_DATA_FOUND THEN" in sql
    assert "WHEN TOO_MANY_ROWS THEN" in sql
    # No write-bearing exception block or mutable constraint-name diagnostic
    # remains anywhere in the renderer output.
    assert "WHEN unique_violation THEN" not in sql
    assert "GET STACKED DIAGNOSTICS cf_constraint_name" not in sql
    assert "cf_constraint_name pg_catalog.text" not in sql


def test_renderer_disambiguates_local_values_and_dml_returning_columns() -> None:
    sql = _base_render()["sql_text"]
    program_count = _base_render()["manifest"]["effective_program_count"]

    assert sql.count("<<cf_body>>\nDECLARE") == program_count
    assert sql.count("END cf_body;\n$durability_inert$") == program_count
    assert (
        ", cf_body.aggregate_revision, cf_body.source_contract_digest, "
        "pg_catalog.transaction_timestamp())"
    ) in sql
    assert (
        "RETURNING cf_target.practice_id, cf_target.source_contract_id, "
        "cf_target.stream_id, cf_target.stream_epoch, "
        "cf_target.transaction_position, cf_target.predecessor_position, "
        "cf_target.raw_event_uuid, cf_target.opaque_aggregate_alias, "
        "cf_target.aggregate_revision, cf_target.source_contract_digest, "
        "cf_target.transaction_authored_at INTO inserted_outbox;"
    ) in sql
    assert (
        "RETURNING emr4_context_fabric.context_observation_stream_head.practice_id, "
        "emr4_context_fabric.context_observation_stream_head.source_contract_id"
    ) in sql
    assert "#variable_conflict" not in sql


def test_renderer_digest_profile_frame_is_component_zero() -> None:
    result = _base_render()
    sql = result["sql_text"]
    # Profile is component zero using the same type-byte-length rule: the type
    # name is the literal "profile" (7 bytes), the value is the profile string.
    assert re.search(
        r"\(7 \|\| ':' \|\| 'profile' \|\| ':' \|\| 39 \|\| ':' \|\| 'emr4_context_fabric\.admission_digest_v1'\)",
        sql,
    )
    first_vector = result["manifest"]["digest_vectors"][0]
    assert first_vector["preimage"].startswith("7:profile:")
    # Python reference and SQL agree on the profile frame bytes.
    assert digest_preimage(
        first_vector["profile"], first_vector["operand_types"], first_vector["values"]
    ).startswith("7:profile:")


# ---------------------------------------------------------------------------
# Same-lane correction 2 -- recognizer hostile tests for the first bytes.
# ---------------------------------------------------------------------------


def test_recognizer_rejects_invalid_first_candidate_patterns() -> None:
    result = _base_render()
    sql = result["sql_text"]
    manifest = result["manifest"]
    effective = result["effective"]

    def rejected(mutated: str, code: str) -> None:
        report = recognize_inert_sql(mutated, manifest, effective)
        assert not report.valid
        assert any(issue.code == code for issue in report.issues), (
            code,
            [issue.code for issue in report.issues],
        )

    # pg_catalog.ARRAY / pg_catalog.ROW grammar misuse.
    rejected(
        sql.replace(
            "ARRAY['appointment_time_changed'::pg_catalog.text]",
            "pg_catalog.ARRAY['appointment_time_changed'::pg_catalog.text]",
            1,
        ),
        "pg_catalog_array",
    )
    rejected(sql.replace("(ROW(", "(pg_catalog.ROW(", 1), "pg_catalog_row")
    # Comment-only isolation is not an assertion.
    rejected(
        sql.replace(
            "IF NOT (pg_catalog.current_setting('transaction_isolation') = 'read committed') THEN",
            "-- assert_isolation READ_COMMITTED",
            1,
        ),
        "comment_only_isolation",
    )
    # Non-strict exact read.
    rejected(sql.replace("INTO STRICT ", "INTO ", 1), "non_strict_exact")
    # Direct uniquely keyed UPDATE must retain its immediate zero-row guard.
    rejected(
        sql.replace(
            " INTO updated_head;\n    IF NOT FOUND THEN",
            " INTO updated_head;\n    IF FOUND THEN",
            1,
        ),
        "non_strict_exact",
    )
    # Invalid bounded delete syntax.
    m = re.search(
        r"    WITH selected_keys AS \(\n(?:.*?\n)*?"
        r"    SELECT pg_catalog\.count\(\*\) INTO purged_row_count FROM deleted;",
        sql,
    )
    assert m is not None
    invalid_delete = (
        "    DELETE FROM emr4_context_fabric.diary_context_observation_outbox_v1\n"
        "        WHERE practice_id = practice_source_stream.practice_id\n"
        "        ORDER BY practice_id\n"
        "        LIMIT 1000\n"
        "        RETURNING pg_catalog.count(*) INTO purged_row_count;"
    )
    rejected(sql.replace(m.group(0), invalid_delete, 1), "delete_order_limit")
    # Anonymous-record set aggregation.
    agg = re.search(
        r"pg_catalog\.array_agg\(\(ROW\(.*?\)\)::[a-zA-Z0-9_\.]+ ORDER BY [^)]*\)",
        sql,
        flags=re.DOTALL,
    )
    assert agg is not None
    rejected(
        sql.replace(agg.group(0), "pg_catalog.array_agg(sub)", 1),
        "anonymous_record_set",
    )
    # Schema-qualified owner role.
    rejected(
        sql.replace(
            "OWNER TO context_schema_owner",
            "OWNER TO emr4_context_fabric.context_schema_owner",
            1,
        ),
        "schema_qualified_owner",
    )
    # Missing support function owner.
    support_owner = re.search(
        r"ALTER FUNCTION emr4_context_fabric\.session_binding_allows_v1\([^;]*OWNER TO [a-z_]+;",
        sql,
    )
    assert support_owner is not None
    rejected(sql.replace(support_owner.group(0) + "\n", "", 1), "missing_owner")
    # UTC digest text without the literal terminal Z.
    rejected(sql.replace('HH24:MI:SS.US"Z"', "HH24:MI:SS.US", 1), "digest_utc_z")


def test_renderer_fails_closed_on_null_constants() -> None:
    sql = _base_render()["sql_text"]
    # None must never be quoted as Python text or an identifier.
    assert "None::" not in sql
    assert "'None'::" not in sql
    assert "NULL::pg_catalog.int8" in sql
    assert "NULL::pg_catalog.timestamptz" in sql


def test_renderer_keeps_postgresql_special_forms_unqualified() -> None:
    result = _base_render()
    sql = result["sql_text"]

    assert "pg_catalog.coalesce(" not in sql.lower()
    assert "COALESCE(pg_catalog.array_length(" in sql

    qualified = sql.replace(
        "COALESCE(pg_catalog.array_length(cf_body.producer_bindings, 1), 0)",
        "pg_catalog.coalesce(pg_catalog.array_length(cf_body.producer_bindings, 1), 0)",
        1,
    )
    assert qualified != sql
    qualified_report = recognize_inert_sql(
        qualified, result["manifest"], result["effective"]
    )
    assert not qualified_report.valid
    assert any(issue.code == "pg_catalog_coalesce" for issue in qualified_report.issues)


def test_renderer_lowers_integer_timestamp_offsets_without_numeric_times_interval() -> (
    None
):
    result = _base_render()
    sql = result["sql_text"]

    assert " * pg_catalog.make_interval(" not in sql
    assert "pg_catalog.make_interval(mins => appointment.duration_minutes)" in sql
    assert "pg_catalog.make_interval(secs => (" in sql
    assert ")::pg_catalog.float8)" in sql

    invalid = sql.replace(
        "pg_catalog.make_interval(mins => appointment.duration_minutes)",
        "appointment.duration_minutes * pg_catalog.make_interval(mins => 1)",
        1,
    )
    assert invalid != sql
    invalid_report = recognize_inert_sql(
        invalid, result["manifest"], result["effective"]
    )
    assert not invalid_report.valid
    assert any(
        issue.code == "numeric_times_interval" for issue in invalid_report.issues
    )


def test_renderer_lowers_uuid_minimum_as_typed_ordered_selection() -> None:
    result = _base_render()
    sql = result["sql_text"]
    ordered = (
        "(SELECT s.stream_id FROM pg_catalog.unnest(cf_body.producer_bindings) AS s "
        "ORDER BY s.stream_id ASC NULLS LAST LIMIT 1)"
    )

    assert sql.count(ordered) == 2
    assert "pg_catalog.min(s.stream_id)" not in sql
    assert sql.count("pg_catalog.min(s.last_contiguous_position)") == 2

    invalid = sql.replace(
        ordered,
        "(SELECT pg_catalog.min(s.stream_id) FROM "
        "pg_catalog.unnest(cf_body.producer_bindings) AS s)",
        1,
    )
    invalid_report = recognize_inert_sql(
        invalid, result["manifest"], result["effective"]
    )
    assert not invalid_report.valid
    assert any(issue.code == "uuid_min_aggregate" for issue in invalid_report.issues)

    with pytest.raises(ValueError, match="MIN_FIELD has no admitted lowering"):
        render_expr(
            {
                "op": "MIN_FIELD",
                "source": {
                    "op": "REF",
                    "kind": "LOCAL",
                    "symbol": "unsupported_set",
                    "type": "pg_catalog.text[]",
                },
                "field": "value",
                "type": "pg_catalog.text",
            }
        )


# ---------------------------------------------------------------------------
# PostgreSQL-16 representability recovery -- hostile static byte mutations.
# ---------------------------------------------------------------------------


def test_recovery_recognizer_rejects_nullable_count_and_trigger_row_xmin() -> None:
    result = _base_render()
    sql = result["sql_text"]

    nullable = sql.replace(
        "COALESCE(pg_catalog.array_length(cf_body.producer_bindings, 1), 0)",
        "pg_catalog.array_length(cf_body.producer_bindings, 1)",
        1,
    )
    nullable_report = recognize_inert_sql(
        nullable, result["manifest"], result["effective"]
    )
    assert not nullable_report.valid
    assert any(issue.code == "nullable_count" for issue in nullable_report.issues)

    trigger_xmin = sql.replace("old_appointment.xmin", "OLD.xmin", 1)
    xmin_report = recognize_inert_sql(
        trigger_xmin, result["manifest"], result["effective"]
    )
    assert not xmin_report.valid
    assert any(issue.code == "trigger_row_xmin" for issue in xmin_report.issues)

    anonymous_record_xmin = sql.replace(
        "old_appointment.xmin", "(old_appointment).xmin", 1
    )
    anonymous_record_report = recognize_inert_sql(
        anonymous_record_xmin, result["manifest"], result["effective"]
    )
    assert not anonymous_record_report.valid
    assert any(
        issue.code == "anonymous_record_xmin"
        for issue in anonymous_record_report.issues
    )


def test_recovery_recognizer_rejects_trigger_kind_and_missing_guard() -> None:
    result = _base_render()
    sql = result["sql_text"]

    wrong_kind = sql.replace(
        "CREATE CONSTRAINT TRIGGER trg_cf_claim_fence",
        "CREATE TRIGGER trg_cf_claim_fence",
        1,
    )
    wrong_kind_report = recognize_inert_sql(
        wrong_kind, result["manifest"], result["effective"]
    )
    assert not wrong_kind_report.valid
    assert any(
        issue.code == "ordinary_trigger_deferrable"
        for issue in wrong_kind_report.issues
    )

    guard_pattern = re.compile(
        r"CREATE TRIGGER trg_cf_appointment_guard BEFORE UPDATE ON "
        r"public\.appointments\n"
        r"    FOR EACH ROW\n"
        r"    EXECUTE FUNCTION "
        r"emr4_context_fabric\.cf_guard_appointment_update_v1\(\);\n"
    )
    missing_guard, replacements = guard_pattern.subn("", sql, count=1)
    assert replacements == 1
    missing_guard_report = recognize_inert_sql(
        missing_guard, result["manifest"], result["effective"]
    )
    assert not missing_guard_report.valid
    assert any(
        issue.code == "trigger_population" for issue in missing_guard_report.issues
    )


def test_recovery_recognizer_rejects_dependency_and_owner_regressions() -> None:
    result = _base_render()
    sql = result["sql_text"]

    helper_missing = sql.replace(
        "CREATE FUNCTION emr4_context_fabric.session_binding_allows_v1",
        "CREATE FUNCTION emr4_context_fabric.session_binding_denies_v1",
        1,
    )
    helper_report = recognize_inert_sql(
        helper_missing, result["manifest"], result["effective"]
    )
    assert not helper_report.valid
    assert any(issue.code == "dependency_order" for issue in helper_report.issues)

    owner_missing = sql.replace(
        "ALTER DOMAIN emr4_context_fabric.source_contract_code "
        "OWNER TO context_schema_owner;\n",
        "",
        1,
    )
    owner_report = recognize_inert_sql(
        owner_missing, result["manifest"], result["effective"]
    )
    assert not owner_report.valid
    assert any(issue.code == "object_owner" for issue in owner_report.issues)

    schema_owner = sql.replace(
        "CREATE SCHEMA emr4_context_fabric AUTHORIZATION context_schema_owner;",
        "CREATE SCHEMA emr4_context_fabric;",
        1,
    )
    schema_report = recognize_inert_sql(
        schema_owner, result["manifest"], result["effective"]
    )
    assert not schema_report.valid
    assert any(issue.code == "schema_owner" for issue in schema_report.issues)

    application_owner = (
        sql + "\nALTER TABLE public.appointments OWNER TO context_schema_owner;\n"
    )
    application_report = recognize_inert_sql(
        application_owner, result["manifest"], result["effective"]
    )
    assert not application_report.valid
    assert any(issue.code == "application_ddl" for issue in application_report.issues)
