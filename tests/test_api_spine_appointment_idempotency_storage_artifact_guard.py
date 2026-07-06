import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUARD_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_storage_artifact_guard.md"
)
DESIGN_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_storage_design.md"
)
MODELS_DIR = ROOT / "app" / "models"
MIGRATIONS_DIR = ROOT / "alembic" / "versions"
APPOINTMENTS_ROUTER = ROOT / "app" / "routers" / "appointments.py"

TABLE_NAME = "appointment_command_idempotency"
MODEL_NAME = "AppointmentCommandIdempotency"
REQUIRED_COLUMNS = (
    "practice_id",
    "actor_user_id",
    "actor_role",
    "operation_id",
    "route_family",
    "idempotency_key_hash",
    "request_body_hash",
    "request_body_canonicalization_version",
    "state",
    "response_status_code",
    "response_body_hash",
    "response_body_json",
    "result_kind",
    "target_appointment_id",
    "audit_log_id",
    "created_at",
    "updated_at",
    "expires_at",
)
FORBIDDEN_STORAGE_FIELDS = (
    "raw_idempotency_key",
    "idempotency_key_raw",
    "raw_request_body",
    "request_body_json",
)
REQUIRED_STORAGE_HELPER_TEST_SIGNALS = (
    "same-key/same-body replay returns the stored response",
    "same-key/different-body conflicts",
    "concurrent same-key attempts cannot create a second appointment",
    "rollback before commit leaves no appointment",
    "stale `in_progress` recovery cannot create a second appointment",
    "replay audit/telemetry is distinct from first execution",
    "lock ordering is ledger-first and appointment-row-second",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _texts_under(root: Path) -> dict[Path, str]:
    return {
        path: _read(path)
        for path in sorted(root.glob("*.py"))
        if path.is_file()
    }


def _model_texts_with_table() -> dict[Path, str]:
    return {
        path: text
        for path, text in _texts_under(MODELS_DIR).items()
        if TABLE_NAME in text or MODEL_NAME in text
    }


def _migration_texts_with_table() -> dict[Path, str]:
    return {
        path: text
        for path, text in _texts_under(MIGRATIONS_DIR).items()
        if TABLE_NAME in text
    }


def _combined(texts: dict[Path, str]) -> str:
    return "\n".join(texts.values())


def _idempotency_test_text() -> str:
    return "\n".join(
        _read(path)
        for path in sorted((ROOT / "tests").glob("*idempotency*.py"))
        if path.is_file()
    )


def test_storage_artifact_guard_records_scope_and_closed_gates():
    text = _read(GUARD_DOC)

    assert "# API Spine Appointment Idempotency Storage Artifact Guard" in text
    assert "| Sprint | 127 |" in text
    assert "Guard only; no model, migration, route behavior" in text
    assert "GraphQL remains read-only" in text
    assert "route enforcement only after the model and migration satisfy" in text
    assert "storage helper tests prove at least" in text
    for closed_gate in (
        "providers",
        "runtime FGA clients",
        "external patient clients",
        "H15/H-series",
        "memory/RAG/GraphRAG",
        "broad trove mining",
        "model-to-database",
    ):
        assert closed_gate in text


def test_storage_artifact_guard_matches_sprint_126_design_contract():
    guard = _read(GUARD_DOC)
    design = _read(DESIGN_DOC)

    for token in (
        TABLE_NAME,
        "unique",
        "practice_id, actor_user_id, operation_id, idempotency_key_hash",
        "ledger-first and appointment-row-second",
        "stale `in_progress` recovery cannot create a second appointment",
        "replay",
        "audit",
        "telemetry",
    ):
        assert token in guard
        assert token in design


def test_no_partial_model_or_migration_artifact_can_land():
    model_texts = _model_texts_with_table()
    migration_texts = _migration_texts_with_table()

    assert bool(model_texts) == bool(migration_texts), (
        "appointment command idempotency storage must not land as a partial "
        "model-only or migration-only artifact"
    )


def test_future_model_artifact_must_match_storage_contract():
    model_text = _combined(_model_texts_with_table())
    if not model_text:
        assert "Future storage implementation is expected to introduce" in _read(GUARD_DOC)
        return

    assert MODEL_NAME in model_text
    assert f'__tablename__ = "{TABLE_NAME}"' in model_text
    for column in REQUIRED_COLUMNS:
        assert column in model_text
    assert "UniqueConstraint" in model_text
    for unique_member in (
        '"practice_id"',
        '"actor_user_id"',
        '"operation_id"',
        '"idempotency_key_hash"',
    ):
        assert unique_member in model_text
    assert "Index" in model_text
    assert "target_appointment_id" in model_text
    assert "created_at" in model_text
    for forbidden in FORBIDDEN_STORAGE_FIELDS:
        assert forbidden not in model_text
    assert "CheckConstraint" in model_text
    for state in ("in_progress", "completed", "failed_transient"):
        assert state in model_text
    assert "nullable=False" in model_text


def test_future_migration_artifact_must_match_storage_contract():
    migration_text = _combined(_migration_texts_with_table())
    if not migration_text:
        assert "migration that creates `appointment_command_idempotency`" in _read(GUARD_DOC)
        return

    assert f'create_table("{TABLE_NAME}"' in migration_text or f"create_table('{TABLE_NAME}'" in migration_text
    for column in REQUIRED_COLUMNS:
        assert column in migration_text
    assert "UniqueConstraint" in migration_text
    assert "create_index" in migration_text or "Index" in migration_text
    assert "CheckConstraint" in migration_text or "check" in migration_text.lower()
    for state in ("in_progress", "completed", "failed_transient"):
        assert state in migration_text
    assert "nullable=False" in migration_text
    for forbidden in FORBIDDEN_STORAGE_FIELDS:
        assert forbidden not in migration_text


def test_route_idempotency_enforcement_waits_for_storage_artifacts():
    route_text = _read(APPOINTMENTS_ROUTER)
    route_mentions_header = bool(
        re.search(r"Idempotency-Key|Header\([^)]*idempotency", route_text)
    )
    route_mentions_ledger = TABLE_NAME in route_text or MODEL_NAME in route_text

    if route_mentions_header or route_mentions_ledger:
        assert _model_texts_with_table(), (
            "appointment route idempotency enforcement requires the storage model first"
        )
        assert _migration_texts_with_table(), (
            "appointment route idempotency enforcement requires the storage migration first"
        )
        test_text = _idempotency_test_text()
        for signal in REQUIRED_STORAGE_HELPER_TEST_SIGNALS:
            assert signal in test_text
    else:
        assert "must not bind or enforce the HTTP" in _read(GUARD_DOC)


def test_route_enforcement_gate_names_required_storage_helper_scenarios():
    text = _read(GUARD_DOC)

    for signal in REQUIRED_STORAGE_HELPER_TEST_SIGNALS:
        assert signal in text
