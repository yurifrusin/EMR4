from __future__ import annotations

import pytest

from scripts import (
    raisa_context_fabric_durability_behavior_failure_024_undefined_symbol_diagnosis as diagnosis,
)


def test_classifies_allowlisted_sha256_function_without_raw_release() -> None:
    raw = (
        b"psql:<stdin>:6: ERROR:  42883: function pg_catalog.sha256(bytea) "
        b"does not exist at character 42\n"
    )

    assert diagnosis.classify_undefined_symbol(raw) == "pg_catalog.sha256"


def test_classifies_allowlisted_interval_operator() -> None:
    raw = b"ERROR:  42883: operator does not exist: integer * interval\n"

    assert diagnosis.classify_undefined_symbol(raw) == (
        "pg_catalog.int4_times_interval"
    )


def test_resolution_probe_is_closed_and_read_only() -> None:
    sql = diagnosis.RESOLUTION_PROBE_SQL.decode("ascii")

    assert sql.count("SELECT") == 1
    assert "INSERT" not in sql
    assert "UPDATE" not in sql
    assert "DELETE" not in sql
    assert "CREATE" not in sql
    assert diagnosis.REQUIRED_RESOLUTION_SYMBOLS == {
        "pg_catalog.sha256",
        "emr4_context_fabric.project_update_confirm_reschedule_v1",
        "pg_catalog.make_interval",
        "pg_catalog.to_char_timestamptz",
        "pg_catalog.int4_times_interval",
        "pg_catalog.timestamptz_plus_interval",
    }


@pytest.mark.parametrize(
    "raw",
    [
        b"ERROR:  42883: function unlisted(bytea) does not exist\n",
        b"ERROR:  42883: operator does not exist: text + jsonb\n",
        (
            b"ERROR:  42883: function pg_catalog.sha256(bytea) does not exist\n"
            b"ERROR:  42883: function pg_catalog.make_interval(integer) does not exist\n"
        ),
        b"ERROR:  42883: function pg_catalog.sha256(bytea) exists\n",
    ],
)
def test_rejects_unlisted_ambiguous_or_nonmatching_error(raw: bytes) -> None:
    with pytest.raises(
        RuntimeError, match="single_allowlisted_undefined_symbol_missing"
    ):
        diagnosis.classify_undefined_symbol(raw)
