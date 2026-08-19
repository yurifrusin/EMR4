from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-docker-created-state-profile-conformance-repair-plan.md"
THREAT = ROOT / (
    "docs/security/"
    "raisa-provider-free-docker-created-state-profile-conformance-repair-threat-model-delta.md"
)


def test_plan_freezes_exact_full_git_and_one_no_credential_execution() -> None:
    text = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "Status: `frozen`" in text
    assert "Source HEAD: `84a66372fa15419051f4dd59754ccf93ab681ed4`" in text
    assert re.search(r"Source HEAD: `[0-9a-f]{40}`", text)
    assert "exactly one execution is authorised" in text
    assert "never started and never attached" in normalized
    assert "No failure may" in normalized and "be repeated" in normalized


def test_plan_separates_credentials_nonce_and_artifact_redaction() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "Credential canaries/values" not in text
    assert "secret scan receives only actual credential" in text
    assert "ownership nonce remains mandatory at the exact label" in text
    assert "broader artifact-redaction tuple containing both" in text


def test_plan_keeps_database_product_and_protected_surfaces_closed() -> None:
    text = " ".join(
        (PLAN.read_text(encoding="utf-8") + THREAT.read_text(encoding="utf-8")).split()
    )
    for required in (
        "may not start or attach",
        "No `app/**`",
        "No live/existing/cloud/product or disposable database",
        "product/patient/appointment/clinical/historical/protected data",
        "protected-ref movement",
        "Preserve `docs/branding/`",
        "`git add .` and `git add -A` are forbidden",
    ):
        assert required in text


def test_plan_records_all_three_parallelism_dispositions() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "**DeepSeek:** declined" in text
    assert "**Gemini:** reserved" in text
    assert "**Native subagents:** declined" in text
