"""Diagnose bounded behavior attempt 047 without another database run."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FAILURE_PATH = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-behavior-transaction-rehearsal/"
    "provider-free-behavior-transaction-failure-evidence-047.json"
)
HARNESS_PATH = ROOT / (
    "scripts/raisa_provider_free_disposable_postgresql_durability_"
    "behavior_transaction_rehearsal.py"
)
ARTIFACT_PATH = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-"
    "inert-ddl-rehearsal/durability-schema.sql.inert"
)
FAILED_SOURCE_HEAD = "5f4067340be0958612b0dad351222f32f13900d1"
FAILURE_SHA256 = "bc577de88b7acafac72828bb2ddae898181886d08676c8802acf84ef925ebd63"


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _git_source(head: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{head}:{path}"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
        shell=False,
    )
    if result.returncode != 0:
        raise ValueError("failed_source_unavailable")
    return result.stdout.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def _section(source: str, start: str, end: str) -> str:
    before, found, tail = source.partition(start)
    del before
    if not found:
        raise ValueError(f"missing_section:{start}")
    body, found, _after = tail.partition(end)
    if not found:
        raise ValueError(f"missing_section_end:{end}")
    return start + body


def build_diagnosis() -> dict[str, Any]:
    failure_raw = FAILURE_PATH.read_bytes()
    if _sha256(failure_raw) != FAILURE_SHA256:
        raise ValueError("failure_hash")
    failure = json.loads(failure_raw)
    envelope = failure["environment"]["failure"]
    if envelope != {
        "code": "sqlstate_mismatch",
        "detail_digest": (
            "sha256:960cf807fa744689cd61d0a1dcf9609c724af2ff0cbd5b3a0d64dd79c54a46c8"
        ),
        "expected_sqlstate": "P0001",
        "observed_sqlstates": ["22012"],
        "psql_exit": 3,
        "scenario_id": "BTR-B03",
        "sqlstate": "22012",
        "stage": "scenario",
    }:
        raise ValueError("failure_envelope")
    if failure["cleanup"]["status"] != "cleanup_verified":
        raise ValueError("cleanup")

    old_source = _git_source(
        FAILED_SOURCE_HEAD, HARNESS_PATH.relative_to(ROOT).as_posix()
    )
    new_source = HARNESS_PATH.read_text(encoding="utf-8")
    old_precondition = _section(
        old_source,
        "def render_rollback_primary_precondition",
        "def render_role_matrix",
    )
    new_precondition = _section(
        new_source,
        "def render_rollback_primary_precondition",
        "def render_role_matrix",
    )
    old_scenarios = _section(
        old_source, "def render_scenario_sql", "def render_position_two_precondition"
    )
    new_scenarios = _section(
        new_source, "def render_scenario_sql", "def render_position_two_precondition"
    )
    old_probe = _section(old_source, "def _probe_sql", "def _probe")
    new_probe = _section(new_source, "def _probe_sql", "def _probe")

    required_old = (
        ('packet = _packet(f).replace("__POSITION__", "2")', old_precondition),
        ('+ ",2,"', old_precondition),
        ('observer="observer_rollback", position=2', old_scenarios),
        ("source_position=2 AND entry_kind='PRIMARY'", old_probe),
        ("'assertion',1 / CASE WHEN result_kind=", old_source),
    )
    if any(fragment not in source for fragment, source in required_old):
        raise ValueError("failed_fixture_shape")

    required_new = (
        ('packet = _packet(f).replace("__POSITION__", "1")', new_precondition),
        ('+ ",1,"', new_precondition),
        ('observer="observer_rollback", position=1', new_scenarios),
        ("source_position=1 AND entry_kind='PRIMARY'", new_probe),
    )
    if any(fragment not in source for fragment, source in required_new):
        raise ValueError("recovery_fixture_shape")

    artifact = ARTIFACT_PATH.read_text(encoding="utf-8")
    gap_guard = (
        "(cf_arg_admission_locator).source_position > "
        "(checkpoint.last_contiguous_position + 1::pg_catalog.int8)"
    )
    if gap_guard not in artifact or "rebase_result_gap" not in artifact:
        raise ValueError("gap_semantics")

    return {
        "schema_version": "emr4.context-fabric.behavior-failure-047-diagnosis.v1",
        "status": "diagnosed_repository_only",
        "attempt": {
            "id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + FAILURE_SHA256,
            "scenario_id": "BTR-B03",
            "expected_sqlstate": "P0001",
            "observed_sqlstate": "22012",
            "cleanup_verified": True,
        },
        "causal_chain": [
            "observer_rollback_checkpoint_started_at_zero",
            "failed_fixture_precommitted_only_source_position_two",
            "failed_fixture_requested_transition_at_source_position_two",
            "position_two_exceeded_last_contiguous_position_plus_one",
            "artifact_correctly_selected_coverage_gap_rebase_result",
            "harness_result_assertion_emitted_division_by_zero_before_fixed_rollback",
        ],
        "classification": "harness_fixture_noncontiguous_position_not_artifact_defect",
        "recovery": {
            "scope": "behavior_harness_only",
            "precommit_primary_position": 1,
            "transition_position": 1,
            "probe_position": 1,
            "expected_transition_result": "RECEIPT_APPLIED",
            "expected_terminal_sqlstate": "P0001",
            "artifact_changed": False,
            "behavior_contract_changed": False,
        },
        "closed_surfaces": [
            "no_database_rerun",
            "no_artifact_or_parse_change",
            "no_scenario_or_authority_expansion",
            "no_operational_or_provider_surface",
        ],
    }


def main() -> int:
    print(json.dumps(build_diagnosis(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
