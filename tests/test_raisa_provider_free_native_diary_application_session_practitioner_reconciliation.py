"""Deterministic checks for the unmounted native-Diary reconciliation gate."""

from __future__ import annotations

import ast
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-native-diary-application-session-practitioner-reconciliation-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-native-diary-application-session-practitioner-reconciliation-threat-model-delta.md"
RECONCILER = ROOT / "orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-reconciliation/client-reconciler.mjs"
ACCEPTANCE = ROOT / "scripts/raisa_provider_free_native_diary_application_session_practitioner_reconciliation_acceptance.mjs"
PARENT_RUNTIME = ROOT / "app/graphql/native_diary_application_session_practitioner.py"

REASONS = {
    "session_inactive",
    "session_generation_stale",
    "request_superseded",
    "ticket_unknown",
    "ticket_replayed",
    "response_not_admissible",
}


def _run_acceptance(output: Path) -> dict:
    completed = subprocess.run(
        ["node", str(ACCEPTANCE), "--output", str(output)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    stdout = json.loads(completed.stdout.strip())
    persisted = json.loads(output.read_text(encoding="utf-8"))
    assert stdout == persisted
    return persisted


def test_acceptance_harness_passes_and_writes_only_explicit_temp_path(tmp_path: Path) -> None:
    evidence = _run_acceptance(tmp_path / "evidence.json")
    assert evidence["result"] == (
        "provider_free_native_diary_application_session_practitioner_reconciliation_pass"
    )
    assert evidence["evidence_label"] == (
        "provider_free_unmounted_client_state_machine"
    )
    assert evidence["data_class"] == "authored_synthetic"
    assert evidence["case_count"] == evidence["passed_case_count"]
    assert evidence["failed_case_count"] == 0
    assert evidence["rejection_reason_count"] == len(REASONS)
    assert evidence["properties"]["response_rows_retained"] is False
    assert evidence["properties"]["client_generation_is_server_bound_proof"] is False
    assert evidence["properties"]["provider_or_external_effect"] is False


def test_acceptance_harness_requires_one_explicit_output() -> None:
    missing = subprocess.run(
        ["node", str(ACCEPTANCE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert missing.returncode != 0
    assert "explicit_output_path_required" in missing.stderr


def test_reconciler_exports_exact_closed_rejection_reasons() -> None:
    source = RECONCILER.read_text(encoding="utf-8")
    match = re.search(
        r"export const REJECTION_REASONS = Object\.freeze\(\[(.*?)\]\);",
        source,
        re.DOTALL,
    )
    assert match
    assert set(re.findall(r"'([^']+)'", match.group(1))) == REASONS


def test_reconciler_is_weak_identity_bound_and_consumes_before_callback() -> None:
    source = RECONCILER.read_text(encoding="utf-8")
    assert "const tickets = new WeakMap();" in source
    assert "Object.freeze({ sessionGeneration, requestRevision })" in source
    consume = source.index("_consume(record);", source.index("const admission"))
    callback = source.index("synchronousRender(admission.rows)", consume)
    assert consume < callback
    assert "new Map()" not in source


def test_response_shape_matches_nullable_parent_projection() -> None:
    source = RECONCILER.read_text(encoding="utf-8")
    parent = PARENT_RUNTIME.read_text(encoding="utf-8")
    assert "_isNullableNonEmptyString(row.roleLabel)" in source
    assert "location === null" in source
    for field in ("id", "displayName", "roleLabel", "active", "defaultLocation"):
        assert field in source
        assert field in parent


def test_reconciler_has_no_effectful_import_or_runtime_surface() -> None:
    source = RECONCILER.read_text(encoding="utf-8")
    assert not re.search(r"^\s*import\s", source, re.MULTILINE)
    for pattern in (
        r"\bfetch\s*\(",
        r"XMLHttpRequest",
        r"\bdocument\s*\.",
        r"\bwindow\s*\.",
        r"\blocalStorage\b",
        r"\bsessionStorage\b",
        r"\bWebSocket\b",
        r"\bEventSource\b",
        r"\bindexedDB\b",
    ):
        assert not re.search(pattern, source)


def test_plan_and_threat_delta_keep_claim_and_gate_posture_exact() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    normalized_plan = " ".join(plan.split())
    assert "provider_free_unmounted_client_state_machine" in plan
    assert "client lifecycle suppression only" in normalized_plan
    assert "does not claim cryptographic or server-bound generation" in normalized_plan
    assert "does not expose that generation in the response" in normalized_plan
    assert "`docs/diary/**`" in plan
    assert "No provider/model" in threat
    for closed in (
        "real identity",
        "patient/clinical/document data",
        "commands",
        "writes",
        "deployment",
        "production",
        "release",
    ):
        assert closed in plan


def test_python_test_module_has_no_database_or_product_runtime_fixture() -> None:
    module = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(module):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert not {"sqlalchemy", "psycopg", "fastapi", "httpx", "requests"} & imports


def test_no_native_diary_product_asset_is_owned_by_this_tranche() -> None:
    owned = {PLAN, THREAT, RECONCILER, ACCEPTANCE, Path(__file__)}
    assert all("docs/diary" not in path.as_posix() for path in owned)
