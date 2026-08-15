from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / (
    "raisa-provider-free-read-only-unmounted-delete-confirm-physical-"
    "representability-review-plan.md"
)
THREAT = ROOT / "docs" / "security" / (
    "raisa-provider-free-read-only-unmounted-delete-confirm-physical-"
    "representability-review-threat-model-delta.md"
)

SOURCES = {
    "docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission.md": "8d8e3a388aeda71800f014535dccc63af8da6aaa945834add044dc2a49097a91",
    "docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission-rehearsal-closeout.md": "202da8412733af4fa3c86df69acbac590e42e80b74ca69b19d63d0d02e7787fb",
    "orchestration/agent_inbox/codex/raisa-delete-confirm-conditional-command-kernel-architecture-admission-sol-acceptance.md": "066587bd4b48630a3f59345a873dbe755c839e1f33acc2ea8368ccd9ad057efe",
    "docs/api-spine/openapi/appointment-commands.yaml": "c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a",
    "app/models/appointments.py": "d1f7960e13efb5f87d0f53334cb365bf49c24f3b6d8574ae3fe4c18a9ae22915",
    "app/services/appointment_idempotency.py": "c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410",
    "app/routers/appointments.py": "f81fc3acc96f21efa64e1d694331792feebadf08f6384c8ac79542bb196d6624",
    "app/models/application_auth.py": "b4671fc5fd82ed06ce4af18b026ab70964a18a48e56157f719be19ce0989107b",
    "app/services/application_auth_persistence.py": "1dbfa4474178490b19c2332ebac29875641c3ea17742afe77f40aa56189f064b",
    "app/services/application_auth_role_runtime.py": "cac8a5623a838238cc68ded0c93570581391bf08226d2a312149bfe1cca87cfa",
    "alembic/versions/h8i9j0k1l2m3_add_appointment_audit_log.py": "a77be7e159614a579eb2dec2d3d8e5b401f1c1d1722f5f740367ae74e6a8a59a",
    "alembic/versions/i9j0k1l2m3n4_add_confirmed_warnings_to_audit.py": "da6493f60b8a8d39186c273db0b9615758b3927cc913d1117d12df0003f245fd",
    "alembic/versions/l1m2n3o4p5q6_add_appointment_command_idempotency.py": "78d730ddf07051f5595c268fc031dea7d454c166a930250255de6aa26e2938ae",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_plan_freezes_exact_sources_and_claim_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "Date: 2026-08-15" in text
    assert "Timestamp: 2026-08-15T13:34:23+10:00 (Australia/Brisbane)" in text
    assert (
        "raisa_provider_free_read_only_unmounted_delete_confirm_physical_"
        "representability_review_pass"
    ) in text
    assert "implementation_not_admitted" in text
    assert "AER-0325" in text
    assert "at least forty hostile changes" in text
    assert "provider-free unmounted delete-confirm physical-design architecture" in text

    for relative, expected_hash in SOURCES.items():
        assert f"`{relative}`" in text
        assert f"`{expected_hash}`" in text
        assert _sha256(ROOT / relative) == expected_hash


def test_plan_freezes_six_domains_and_api_spine_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8")

    for heading in (
        "Practice authority fence",
        "Appointment truth and lock",
        "Operation-scoped idempotency and private receipt",
        "Attributable audit and exact reasons",
        "Ordered atomic boundary",
        "Fresh readback separation",
    ):
        assert f"**{heading}.**" in text

    assert "destructive REST/OpenAPI appointment command mutation" in text
    assert "GraphQL: read-only" in text
    assert "raw compatibility delete" in text
    assert "No application/model/migration/service/route/OpenAPI/GraphQL edit" in text


def test_threat_delta_preserves_fail_closed_review() -> None:
    text = THREAT.read_text(encoding="utf-8")

    assert "Timestamp: 2026-08-15T13:34:23+10:00 (Australia/Brisbane)" in text
    assert "AER-0325" in text
    assert "practice authority fence" in text
    assert "public minimized response" in text
    assert "implementation_not_admitted" in text
    assert "No protected evidence" in text
