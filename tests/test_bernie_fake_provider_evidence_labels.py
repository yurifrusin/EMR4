from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


def test_prompt_thread_backend_pass_labels_fake_provider_evidence_only() -> None:
    text = _compact(_read("docs/bernie-prompt-thread-fake-provider-backend-pass.md"))

    assert "fake-provider, route-level backend evidence" in text
    assert "not live-provider evidence" in text
    assert "does not prove model quality" in text
    assert "provider_calls_performed\": false" in text
    assert "live_provider_enabled\": false" in text


def test_prompt_thread_readiness_keeps_closed_gate_labels() -> None:
    text = _compact(_read("docs/bernie-prompt-thread-tranche-readiness.md"))

    assert "provider-free route-level fake-provider testing" in text
    assert "provider metadata remains `provider: fake`" in text
    assert "`live_provider: false`" in text
    assert "Do not proceed to live provider" not in text
    assert "Gates Still Closed" in text
