import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / (
    "docs/raisa-provider-free-disposable-postgresql-default-off-check-in-"
    "rollback-unknown-commit-recovery-rehearsal-plan.md"
)
THREAT = ROOT / (
    "docs/security/raisa-provider-free-disposable-postgresql-default-off-"
    "check-in-rollback-unknown-commit-recovery-rehearsal-threat-model-delta.md"
)
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"


def _normalized_markdown(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("-\n", "-")
    return re.sub(r"\s+", " ", text).lower()


def test_plan_freezes_rollback_unknown_response_readback_and_cleanup_boundary() -> None:
    text = _normalized_markdown(PLAN)

    for phrase in (
        "source head: `26402cb8667c2dbf62e86c6eb4c0b000d274559e`",
        "explicit pre-commit transaction rollback leaves zero receipt, effect or audit rows",
        "connection_lost_without_complete_terminal_response",
        "no automatic retry",
        "timeout/pgsleep",
        "pg_terminate_backend",
        "committed_exactly_once",
        "rolled_back_zero_effect",
        "unresolved_denied",
        "one uniquely named, locally controlled, disposable postgresql 16 instance",
        "pull policy `never`",
        "no published port",
        "role is absent before teardown",
        "captured container/network ids",
        "ordinary_admission_release_count=0",
    ):
        assert phrase in text


def test_plan_and_threat_keep_product_provider_data_and_protected_gates_closed() -> None:
    combined = _normalized_markdown(PLAN) + " " + _normalized_markdown(THREAT)

    for phrase in (
        "no product",
        "no ordinary-practice enablement",
        "no live secret",
        "no provider",
        "occupied deepseek hmr",
        "production runtime",
        "protected-ref movement",
        "preserve `docs/branding/`",
        "stage explicit paths only",
    ):
        assert phrase in combined


def test_api_spine_manifest_boundary_is_declarative_and_non_authoritative() -> None:
    combined = _normalized_markdown(PLAN) + " " + _normalized_markdown(THREAT)

    assert "closed declarative fixture" in combined
    assert "not executable policy, command authority or admission authority" in combined
    assert "typed python and postgresql constraints/rls enforce" in combined
    assert "adds no rest/openapi route" in combined
    assert "graphql remains read-only" in combined


def test_plan_records_all_three_parallelism_lanes() -> None:
    text = PLAN.read_text(encoding="utf-8").lower()

    assert "**deepseek:** declined" in text
    assert "**gemini:** reserved" in text
    assert "**native subagents:** declined" in text
    assert "stock-headless-to-custom-runner boot proof" in text
    assert "claude code is not a fallback" in text


def test_active_latch_names_only_this_in_progress_tranche() -> None:
    latch = json.loads(LATCH.read_text(encoding="utf-8"))

    assert latch["operation_id"] == (
        "raisa-provider-free-disposable-postgresql-default-off-check-in-"
        "rollback-unknown-commit-recovery-rehearsal"
    )
    assert latch["status"] == "in_progress"
    assert latch["terminal_response"]["permitted"] is False
    assert latch["user_attention"]["required"] is False
    assert "explicit_path_staging_only" in latch["protected_boundaries"]


def test_recovery_addendum_preserves_failure_and_allows_one_bounded_attempt() -> None:
    text = _normalized_markdown(PLAN)
    threat = _normalized_markdown(THREAT)

    assert "worker_join_timeout" in text
    assert "e357e3a2dec7f0d0740a2ea6f518cb695dc2a5cbf88b9c321dbcd61d6e7bd1c1" in text
    assert "consume the one closed result object" in text
    assert "before joining the process" in text
    assert "exactly one recovery execution is authorised" in text
    assert "not an automatic command retry" in text
    assert "consume exactly one closed queue result" in threat
    assert "require exit within five seconds" in threat


def test_final_recovery_addendum_freezes_eof_and_immutable_attempt_controls() -> None:
    text = _normalized_markdown(PLAN)
    threat = _normalized_markdown(THREAT)

    assert "worker_outcome_missing" in text
    assert "bea605006bf36996d439876a4976ec5b733ddc4bb841d5942aae1057c5f514ed" in text
    assert "shutdown(shut_wr)" in text
    assert "provider-free socket/subprocess regression" in text
    assert "first absent numbered path" in text
    assert "exactly one final recovery execution is authorised" in text
    assert "no fourth execution may be inferred" in text
    assert "half-closes the client-facing write side" in threat
    assert "never overwrites a numbered attempt" in threat
