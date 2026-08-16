from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / (
    "raisa-provider-free-disposable-postgresql-delete-confirm-scaffold-"
    "parse-catalogue-rehearsal-plan.md"
)
THREAT = ROOT / "docs" / "security" / (
    "raisa-provider-free-disposable-postgresql-delete-confirm-scaffold-"
    "parse-catalogue-rehearsal-threat-model-delta.md"
)

PLAN_HASH = "71486b39e69bdab10e23b22bafa9d48a348c816b0270ad4e11c38700dcd06b62"
THREAT_HASH = "653658d228eecdd48389d7158cfa5b211f062a35ab9af0ba85a9db4a91a68edd"

SOURCES = {
    "docs/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold-plan.md": "f6e75c7428dc5c1327166bc0e900c2804f3201ea1b32cd5577d1f8134b16c2a8",
    "docs/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold-closeout.md": "caad279b52f915bbfc1d554c2460725044c34fee945c0601e30a0cde52c4d250",
    "orchestration/agent_inbox/codex/raisa-delete-confirm-physical-schema-transaction-scaffold-sol-acceptance.md": "986de83a97449a5aeecd39b37594ab1eca740780f9c4016ae7d5b75f954428b5",
    "orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold/scaffold-contract.json": "4d4ecc83fdb9b9e90067714f4827be6bc007ddd183bc66b0cd95aa207d475f22",
    "alembic/versions/x3y4z5a6b7c8_add_delete_confirm_physical_scaffold.py": "e6542c960a9378cf7c1c3c22dd876a1c9f242b68047a180f9f383c1c62d348bb",
    "alembic.ini": "8a70641ffa66bb1c228e16a62d8b7a2111810888819c9c662c17ea72e2d70b49",
    "alembic/env.py": "5f8f7f752287ce47b507555c43065499fe797c37f724ed827c1d43ebfc5fe346",
    "docs/api-spine/openapi/appointment-commands.yaml": "c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a",
    "orchestration/harness_settings/risk_weighted_workflow.yaml": "a4bc7f92d1caecbd0b421cd40438d64916a7945197e02d2f8b9232d2162c2284",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_plan_and_threat_delta_are_frozen_and_bound() -> None:
    assert _sha256(PLAN) == PLAN_HASH
    assert _sha256(THREAT) == THREAT_HASH


def test_plan_freezes_exact_sources_and_claim_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "Date: 2026-08-16" in text
    assert "Timestamp: 2026-08-16T10:31:22+10:00 (Australia/Brisbane)" in text
    assert "frozen_for_tier_2_provider_free_disposable_postgresql_execution" in text
    assert "material database execution / Extra High" in text
    assert "Tier 2" in text
    assert "x3y4z5a6b7c8" in text
    assert "w2x3y4z5a6b7:x3y4z5a6b7c8" in text
    assert "confirmAppointmentDeleteProposal" in text
    assert "hostile leaf mutations fail closed" in text
    assert "No DML behavior, downgrade, lock, concurrency, rollback, restart or service" in text

    for relative, expected_hash in SOURCES.items():
        assert f"`{relative}`" in text
        assert f"`{expected_hash}`" in text
        assert _sha256(ROOT / relative) == expected_hash


def test_plan_freezes_api_spine_and_containment_profile() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "beneath the REST/OpenAPI command" in text
    assert "GraphQL remains read-only" in text
    assert "Events remain non-authoritative acceleration" in text
    assert "Catalogue evidence is not" in text
    assert "product truth, an authorization decision or an executable command receipt" in text
    assert "docker.exe" in text
    assert "postgres:16-bookworm" in text
    assert "--pull=never" in text
    assert "--network=none" in text
    assert "tmpfs" in text
    assert "one CPU" in text
    assert "512 MiB" in text
    assert "128 processes" in text
    assert "docker exec -i" in text
    assert "shell=False" in text
    assert "emr4-delete-confirm-pg16-catalogue-" in text
    assert "ON_ERROR_STOP=1" in text
    assert "--single-transaction" in text


def test_plan_freezes_catalogue_assertions_and_empty_relations() -> None:
    text = PLAN.read_text(encoding="utf-8")

    for heading in (
        "Alembic head exactly `x3y4z5a6b7c8`",
        "`users.authority_generation` is non-null `int8`",
        "`user_capability_grants` has exactly its three non-null columns",
        "the seven additive appointment-audit columns",
        "the exact three public PL/pgSQL trigger functions",
        "the exact three non-system row triggers",
        "no unexpected `emr4_user_*` functions",
        "each remain at zero rows",
    ):
        assert heading in text

    assert "public.users" in text
    assert "public.appointment_command_idempotency" in text
    assert "public.appointment_audit_log" in text
    assert "public.alembic_version" in text
    assert "exactly parent `w2x3y4z5a6b7`" in text
    assert "No prerequisite relation contains a row" in text
    assert "It never lists, prunes, pulls, builds, logs in" in text


def test_plan_freezes_cleanup_and_authority_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "cleanup_ownership_unverified" in text
    assert "finally" in text
    assert "exact-ID absence proof" in text
    assert "No image," in text
    assert "unrelated container is removed" in text
    assert "No patient, clinical," in text
    assert "real-person, product, historical diary or protected data" in text
    assert "Cloud cost is zero" in text
    assert "environment_unavailable" in text
    assert "behavior/transaction rehearsal the next narrow candidate" in text


def test_threat_delta_preserves_fail_closed_controls() -> None:
    text = THREAT.read_text(encoding="utf-8")

    assert "Timestamp: 2026-08-16T10:31:22+10:00 (Australia/Brisbane)" in text
    assert "x3y4z5a6b7c8" in text
    assert "No host URL or port exists" in text
    assert "Exact local image inspection precedes" in text
    assert "Reverify exact ID, name, image, labels, containment and bounds" in text
    assert "Exact range `w2x3y4z5a6b7:x3y4z5a6b7c8`" in text
    assert "All four authority/receipt/audit relations must remain at zero rows" in text
    assert "representation-only" in text
    assert "exactly one final independent veto" in text
    assert "No existing/product database" in text
