from __future__ import annotations

from pathlib import Path

import pytest

from scripts import (
    raisa_context_fabric_durability_behavior_failure_023_rls_lock_diagnosis as diagnosis,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-durability-inert-ddl-rehearsal"
    / "durability-schema.sql.inert"
)


def _artifact() -> bytes:
    raw = ARTIFACT.read_bytes()
    assert b"\r" not in raw.replace(b"\r\n", b"")
    return raw.replace(b"\r\n", b"\n")


def test_diagnostic_changes_only_the_exact_stream_head_lock_rejections() -> None:
    artifact = _artifact()
    candidate = diagnosis.diagnostic_function_sql(artifact)

    assert candidate.startswith(b"CREATE OR REPLACE FUNCTION ")
    assert candidate.count(b"stream_head_lock_diagnostic:") == 2
    assert candidate.count(diagnosis.DIAGNOSTIC_NO_DATA_RAISE) == 1
    assert candidate.count(diagnosis.DIAGNOSTIC_TOO_MANY_RAISE) == 1
    assert b"pg_catalog.coalesce" not in candidate
    assert b"SELECT emr4_context_fabric.context_observation_stream_head" in candidate
    assert b"FOR UPDATE;" in candidate


def test_diagnostic_rejects_wrong_function_or_lock_block_population() -> None:
    artifact = _artifact()

    with pytest.raises(RuntimeError, match="function_boundary_not_unique"):
        diagnosis.diagnostic_function_sql(
            artifact.replace(diagnosis.FUNCTION_START, b"CREATE FUNCTION changed(", 1)
        )

    function_start = artifact.index(diagnosis.FUNCTION_START)
    lock_start = artifact.index(diagnosis.LOCK_BLOCK_START, function_start)
    mutated = artifact[:lock_start] + artifact[lock_start:].replace(
        diagnosis.ORIGINAL_NO_DATA_RAISE,
        b"RAISE EXCEPTION USING ERRCODE = 'CF004';",
        1,
    )
    with pytest.raises(RuntimeError, match="raise_population_not_exact"):
        diagnosis.diagnostic_function_sql(mutated)
