from __future__ import annotations

import ast
from pathlib import Path

import pytest

from scripts import ariadne_vertex_sydney_gemini_25_preflight as preflight


ROOT = Path(__file__).resolve().parents[1]


def test_preflight_binding_is_exact() -> None:
    assert preflight.PROJECT == "bernie-emr4-dev"
    assert preflight.SERVICE_ACCOUNT == (
        "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
    )
    assert preflight.CUSTOM_ROLE == (
        "projects/bernie-emr4-dev/roles/BernieVertexSyntheticEvaluator"
    )
    assert preflight.PREDICTION_PERMISSION == "aiplatform.endpoints.predict"
    assert preflight.LOCATION == "australia-southeast1"
    assert preflight.HOSTNAME == (
        "australia-southeast1-aiplatform.googleapis.com"
    )
    assert preflight.CACHE_CONTROL_HOSTNAME == (
        "us-central1-aiplatform.googleapis.com"
    )
    assert preflight.MODEL_ID == "gemini-2.5-flash"


def test_preflight_source_has_no_cloud_mutation_verbs() -> None:
    source = Path(preflight.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    string_literals = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    forbidden_exact = {
        "add-iam-policy-binding",
        "auth application-default login",
        "auth login",
        "create",
        "delete",
        "disable",
        "enable",
        "set-iam-policy",
        "update",
    }
    assert forbidden_exact.isdisjoint(string_literals)


def test_safe_child_environment_omits_provider_and_adc_overrides(
    monkeypatch,
) -> None:
    monkeypatch.setenv("PATH", "safe-path")
    monkeypatch.setenv("GEMINI_API_KEY", "do-not-read-or-forward")
    monkeypatch.setenv("GOOGLE_API_KEY", "do-not-read-or-forward")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "do-not-forward")
    environment = preflight._safe_child_environment()
    assert environment["PATH"] == "safe-path"
    assert "GEMINI_API_KEY" not in environment
    assert "GOOGLE_API_KEY" not in environment
    assert "GOOGLE_APPLICATION_CREDENTIALS" not in environment


def test_request_response_logging_check_uses_exact_regional_model(
    monkeypatch,
) -> None:
    observed: list[str] = []

    def fake_read(url: str, *, allow_not_found: bool = False):
        observed.append(url)
        assert allow_not_found is True
        return 404, None

    monkeypatch.setattr(preflight, "_read_control_json", fake_read)
    assert preflight._request_response_logging_disabled() is True
    assert observed == [
        "https://australia-southeast1-aiplatform.googleapis.com/"
        "v1beta1/projects/bernie-emr4-dev/locations/australia-southeast1/"
        "publishers/google/models/gemini-2.5-flash:"
        "fetchPublisherModelConfig"
    ]


def test_control_metadata_read_binds_exact_quota_project(monkeypatch) -> None:
    observed: dict[str, object] = {}

    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self, _maximum: int) -> bytes:
            return b'{"name":"projects/bernie-emr4-dev/cacheConfig"}'

    def fake_urlopen(request, timeout):
        observed["url"] = request.full_url
        observed["authorization"] = request.get_header("Authorization")
        observed["quota_project"] = request.get_header("X-goog-user-project")
        observed["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(
        preflight,
        "_control_access_token",
        lambda: "authored-synthetic-token-sentinel",
    )
    monkeypatch.setattr(preflight, "urlopen", fake_urlopen)

    status, value = preflight._read_control_json(
        "https://us-central1-aiplatform.googleapis.com/"
        "v1/projects/bernie-emr4-dev/cacheConfig"
    )

    assert status == 200
    assert value == {"name": "projects/bernie-emr4-dev/cacheConfig"}
    assert observed == {
        "url": (
            "https://us-central1-aiplatform.googleapis.com/"
            "v1/projects/bernie-emr4-dev/cacheConfig"
        ),
        "authorization": "Bearer authored-synthetic-token-sentinel",
        "quota_project": "bernie-emr4-dev",
        "timeout": 30,
    }


def test_cache_check_requires_explicit_disable(monkeypatch) -> None:
    observed: list[str] = []

    def enabled_default(url: str):
        observed.append(url)
        return 200, {"name": "projects/bernie-emr4-dev/cacheConfig"}

    monkeypatch.setattr(
        preflight,
        "_read_control_json",
        enabled_default,
    )
    assert preflight._in_memory_cache_disabled() is False
    assert observed == [
        "https://us-central1-aiplatform.googleapis.com/"
        "v1/projects/bernie-emr4-dev/cacheConfig"
    ]
    monkeypatch.setattr(
        preflight,
        "_read_control_json",
        lambda _url: (
            200,
            {
                "name": "projects/bernie-emr4-dev/cacheConfig",
                "disableCache": True,
            },
        ),
    )
    assert preflight._in_memory_cache_disabled() is True


def test_model_catalogue_uses_exact_target_as_quota_project(
    monkeypatch,
) -> None:
    observed: list[tuple[list[str], str]] = []

    def fake_gcloud_json(arguments, *, reason_code):
        observed.append((arguments, reason_code))
        return [{"name": "publishers/google/models/gemini-2.5-flash"}]

    monkeypatch.setattr(preflight, "_gcloud_json", fake_gcloud_json)
    assert preflight._model_catalogue() == [
        {"name": "publishers/google/models/gemini-2.5-flash"}
    ]
    assert observed == [
        (
            [
                "ai",
                "model-garden",
                "models",
                "list",
                "--project=bernie-emr4-dev",
                "--billing-project=bernie-emr4-dev",
                "--model-filter=gemini-2.5-flash",
                "--full-resource-name",
                "--limit=20",
                "--format=json(name,versionId)",
            ],
            "model_catalogue_control_read_failed",
        )
    ]


def test_preflight_reduces_adc_discovery_exception_to_safe_code(
    monkeypatch, capsys
) -> None:
    import google.auth

    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)

    def fail_default(*_args, **_kwargs):
        raise RuntimeError("credential path and raw authentication response")

    monkeypatch.setattr(google.auth, "default", fail_default)
    with pytest.raises(
        preflight.PreflightError,
        match="^impersonated_adc_discovery_failed$",
    ):
        preflight._verify_adc()
    captured = capsys.readouterr()
    assert "credential path" not in captured.out
    assert "credential path" not in captured.err
