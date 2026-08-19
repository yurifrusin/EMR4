import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / (
    "docs/raisa-provider-free-disposable-postgresql-default-off-check-in-"
    "runtime-role-tenant-isolation-attestation-rehearsal-plan.md"
)
THREAT = ROOT / (
    "docs/security/raisa-provider-free-disposable-postgresql-default-off-"
    "check-in-runtime-role-tenant-isolation-attestation-rehearsal-threat-model-delta.md"
)


def _normalized_markdown(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("-\n", "-")
    return re.sub(r"\s+", " ", text).lower()


def test_plan_freezes_exact_role_rls_and_cleanup_boundary() -> None:
    text = _normalized_markdown(PLAN)

    for phrase in (
        "appointment_check_in_ordinary_runtime_v1",
        "NOSUPERUSER",
        "NOCREATEDB",
        "NOCREATEROLE",
        "NOINHERIT",
        "NOREPLICATION",
        "NOBYPASSRLS",
        "zero owned databases, schemas, relations, sequences, functions or policies",
        "cross-tenant read, write, update and delete",
        "SQLSTATE `42501`",
        "absent before teardown",
        "captured container/network IDs",
        "pull policy",
        "`never`",
        "no published port",
        "no fallback transport",
        "ordinary manifests, admission records and releases remain zero",
        "rotation records are shape fixtures only",
    ):
        assert phrase.lower() in text


def test_plan_and_threat_keep_product_provider_secret_and_protected_gates_closed() -> None:
    combined = _normalized_markdown(PLAN) + " " + _normalized_markdown(THREAT)

    for phrase in (
        "no product",
        "no ordinary-practice enablement",
        "live secret",
        "provider call",
        "occupied deepseek hmr",
        "production runtime",
        "protected-ref movement",
        "preserve `docs/branding/`",
        "stage explicit paths only",
    ):
        assert phrase in combined


def test_api_spine_manifest_boundary_is_declarative_and_non_authoritative() -> None:
    combined = _normalized_markdown(PLAN) + " " + _normalized_markdown(THREAT)

    assert "manifest/capability evidence rehearsal" in combined
    assert "declarative input" in combined
    assert "never a command" in combined
    assert "never becomes a policy engine or activation authority" in combined
    assert "no rest/openapi command" in combined
    assert "graphql read/mutation" in combined


def test_plan_records_all_three_parallelism_lanes() -> None:
    text = PLAN.read_text(encoding="utf-8").lower()

    assert "**deepseek:** declined" in text
    assert "**gemini:** reserved" in text
    assert "**native subagents:** declined" in text
    assert "separate provider-free boot proof" in text
    assert "claude code is not a fallback" in text
