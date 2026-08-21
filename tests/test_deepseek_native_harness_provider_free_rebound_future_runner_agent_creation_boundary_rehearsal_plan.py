from __future__ import annotations

import re
from pathlib import Path


PLAN_PATH = Path(
    "docs/deepseek-native-harness-provider-free-rebound-future-runner-"
    "agent-creation-boundary-rehearsal-plan.md"
)
THREAT_PATH = Path(
    "docs/security/deepseek-native-harness-provider-free-rebound-future-runner-"
    "agent-creation-boundary-rehearsal-threat-model-delta.md"
)


def test_plan_freezes_real_prepublication_factory_boundary() -> None:
    text = PLAN_PATH.read_text(encoding="utf-8")
    for required in (
        "AgentRegistry.create()",
        "AgentLoop.createAgent()",
        "SessionPreparation.create",
        "agent_create_prepublication_veto_passed",
        "post_hmr_agent_create_prepublication_stop",
        "EMR4_AGENT_PUBLICATION_STOP",
        "one private Agent/Session pair may be prepared",
        "zero live/published agents and sessions",
        "zero `session/created`, `agent/created` and `agent/session-start` events",
    ):
        assert required in text


def test_plan_binds_full_git_objects_and_exact_rc7_sources() -> None:
    text = PLAN_PATH.read_text(encoding="utf-8")
    expected = {
        "f7eff76e61f4b139741aadbe61df4c3c6a7f8d68",
        "560f471b72bef0b9790120238657dc7afd4d602b",
        "c8b0e3a587191b65da212edda36b8b833a2ecc2c",
    }
    assert expected.issubset(set(re.findall(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])", text)))
    for digest in (
        "e7e40c5ca66d9827a5084c5c0c68983f9685842bb9b6d604803d4cb4642bb263",
        "577f7ee31d8954c8a09c4af9ce9c1fbdb25220caff40b2120bec257305bd2a35",
        "bf8ca1e9b05e9b78320a5e2f0b4e25395eba91dd72db6d3cb5626e3dfb529204",
        "a0b417514e3d285ad5fef74867e8049af333ebdec6e4d7639e388aa0903e0039",
        "9270186b579bc8a4c6c53c256e4471d3f134e94308462c6a413a722e9c7556fb",
    ):
        assert digest in text
    assert text.count("0.1.0-rc.7") >= 2


def test_plan_preserves_exact_preset_tool_and_seed_bindings() -> None:
    text = PLAN_PATH.read_text(encoding="utf-8")
    assert "`emr4-bounded-worker`" in text
    assert "`edit`, `glob`, `read`" in text
    assert "`158`" in text
    assert "3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1" in text
    assert "32,744 files" in text
    assert "219,364,530 bytes" in text
    assert "d84e73067c8dbbf4836969eb948012fd364ee454bb07744cfe486995a256084d" in text


def test_plan_and_threat_have_required_brisbane_metadata() -> None:
    for path in (PLAN_PATH, THREAT_PATH):
        text = path.read_text(encoding="utf-8")
        assert "Date: 2026-08-22" in text
        assert re.search(
            r"Timestamp: 2026-08-22T\d{2}:\d{2}:\d{2}\.\d{7}\+10:00 "
            r"\(Australia/Brisbane\)",
            text,
        )


def test_threat_model_refuses_publication_equivalence_and_raw_retention() -> None:
    text = THREAT_PATH.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    for required in (
        "A prepared private Session is misreported as no session object",
        "A returned handle is quietly disposed and called equivalent",
        "one real factory invocation",
        "zero live registries and lifecycle announcements",
        "no raw retention",
    ):
        assert required in flat


def test_plan_exclusions_keep_product_and_protected_surfaces_closed() -> None:
    text = PLAN_PATH.read_text(encoding="utf-8")
    for required in (
        "no published agent/session",
        "no generic-status",
        "no product, patient, appointment, clinical, historical or",
        "no production runtime, deployment, release, Pages rebuild",
        "protected-ref movement",
    ):
        assert required in text
