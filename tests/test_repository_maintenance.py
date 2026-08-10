import json
from pathlib import Path
import subprocess

from scripts.ariadne_orchestrator_preflight import write_json_lf
from scripts.verification_runtime import (
    LAUNCHER_TIMEOUT_EXIT,
    VerificationCommand,
    run_command,
)
from scripts.verify_repository import RUFF_PATHS
from scripts.python_source_state import DEFAULT_MANIFEST, load_source_state


ROOT = Path(__file__).resolve().parents[1]


def test_receipt_writer_emits_canonical_utf8_lf_bytes(tmp_path: Path):
    path = tmp_path / "receipt.json"

    write_json_lf(path, {"z": 1, "a": "receipt"})

    payload = path.read_bytes()
    assert payload.endswith(b"\n")
    assert b"\r\n" not in payload
    assert json.loads(payload) == {"a": "receipt", "z": 1}


def test_verification_runtime_labels_launcher_timeout(monkeypatch, tmp_path: Path):
    def expire(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=7)

    monkeypatch.setattr(subprocess, "run", expire)
    result = run_command(
        VerificationCommand("bounded test", ["python", "ignored.py"], 7),
        cwd=tmp_path,
    )

    assert result == LAUNCHER_TIMEOUT_EXIT


def test_verification_runtime_preserves_child_exit_code(monkeypatch, tmp_path: Path):
    def fail(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=9)

    monkeypatch.setattr(subprocess, "run", fail)
    result = run_command(
        VerificationCommand("failing child", ["python", "ignored.py"], 7),
        cwd=tmp_path,
    )

    assert result == 9
    assert result != LAUNCHER_TIMEOUT_EXIT


def test_ruff_baseline_is_pinned_and_explicitly_protected_safe():
    requirements = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")

    assert "ruff==0.15.22" in requirements
    assert "app/services/bernie" not in RUFF_PATHS
    assert "app/services/bernie/session.py" in RUFF_PATHS
    assert "app/services/bernie/session_store.py" in RUFF_PATHS
    assert all("holdout" not in path.lower() for path in RUFF_PATHS)
    state = load_source_state(DEFAULT_MANIFEST)
    assert state["target_python"] == "3.11"
    assert state["source_files"]


def test_phase0_migration_has_empty_bootstrap_and_symmetric_cleanup():
    source = (
        ROOT / "alembic/versions/d4787e8e3629_phase_0_baseline.py"
    ).read_text(encoding="utf-8")

    assert "emr4_phase0_empty_bootstrap_marker" in source
    assert "def _prepare_legacy_baseline()" in source
    assert "Phase-0 legacy baseline is incomplete" in source
    assert "def _is_empty_database_bootstrap()" in source
    assert 'op.drop_table("mbs_directory")' in source
    assert 'op.drop_table("snomed_directory")' in source
    assert "type_name.typtype = 'e'" in source
