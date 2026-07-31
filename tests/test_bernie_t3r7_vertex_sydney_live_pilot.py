from __future__ import annotations

import copy
from datetime import date, datetime, timezone
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.services.ai.evals import bernie_vertex_sydney_live_pilot as pilot_module
from app.services.ai.evals.bernie_vertex_sydney_live_pilot import (
    DEFAULT_OBSERVATION_PATH,
    DEFAULT_REPORT_PATH,
    DispatchState,
    append_observation,
    build_cases,
    build_prompt,
    build_report,
    canonical_hash,
    estimate_cost_usd,
    failure_record,
    load_approval,
    load_observations,
    success_record,
    validate_approval,
    validate_observations,
)
from scripts import bernie_t3r7_vertex_sydney_live_pilot as live_script


@pytest.fixture(autouse=True)
def _freeze_consumed_t3r7_approval_date(monkeypatch):
    """Keep immutable historical-reducer tests independent of wall time."""

    class HistoricalDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 7, 18)

    monkeypatch.setattr(pilot_module, "date", HistoricalDate)


def _payload(case):
    expected = case.expected
    return {
        "intent": expected.intent,
        "entities": [list(item) for item in expected.entities],
        "date_time": [list(item) for item in expected.date_time],
        "requires_clarification": expected.requires_clarification,
        "tool_name": expected.tool_name,
        "writes_authorized": False,
        "claims_action_completed": False,
        "action_withdrawn": expected.action_withdrawn,
    }


def _success(packet, case, sample_index=0, *, response_hash_variant=False):
    payload = _payload(case)
    if response_hash_variant:
        payload["entities"] = [*payload["entities"], ["status", "synthetic-variant"]]
    return success_record(
        packet=packet,
        case=case,
        sample_index=sample_index,
        prompt_hash=canonical_hash(build_prompt(case)),
        normalized_payload=payload,
        started_at="2026-07-18T00:00:00.000Z",
        completed_at="2026-07-18T00:00:01.000Z",
        latency_ms=1000,
        input_tokens=100,
        output_tokens=20,
        model_version_observed="gemini-2.5-flash-001",
    )


def test_approval_freezes_sydney_model_population_rate_cost_and_closed_authority():
    packet = load_approval()
    validate_approval(packet, today=date(2026, 7, 18))

    assert packet["provider"]["model_id"] == "gemini-2.5-flash"
    assert packet["provider"]["location"] == "australia-southeast1"
    assert packet["source_population"]["maximum_calls"] == 48
    assert len(build_cases(packet)) == 24
    assert packet["execution_limits"]["requests_per_minute_ceiling"] == 6
    assert packet["execution_limits"]["minimum_start_interval_seconds"] == 10
    assert packet["cost_control"]["maximum_estimated_cost"] == 1.0
    assert packet["cost_control"]["maximum_token_ceiling_estimate"] == 0.325
    assert all(value is False for value in packet["authority"].values())


def test_conservative_prompt_reservation_fits_input_ceiling():
    packet = load_approval()
    prompt_bytes = [len(build_prompt(case).encode("utf-8")) for case in build_cases(packet)]

    assert max(prompt_bytes) <= packet["execution_limits"][
        "maximum_serialized_prompt_chars_per_sample"
    ]
    assert 2 * sum(prompt_bytes) <= packet["execution_limits"][
        "maximum_input_tokens_total"
    ]


@pytest.mark.parametrize(
    "mutation,message",
    [
        (lambda packet: packet["provider"].update(location="global"), "provider, model, region"),
        (
            lambda packet: packet["execution_limits"].update(
                requests_per_minute_ceiling=9
            ),
            "throttle weakened",
        ),
        (
            lambda packet: packet["execution_limits"].update(automatic_retries=True),
            "retries must remain disabled",
        ),
        (
            lambda packet: packet["privacy_and_retention"].update(
                raw_response_persistence=True
            ),
            "privacy or tool boundary",
        ),
        (
            lambda packet: packet["authority"].update(product_runtime_wiring=True),
            "prohibited product authority",
        ),
    ],
)
def test_approval_fails_closed_on_material_drift(mutation, message):
    packet = copy.deepcopy(load_approval())
    mutation(packet)
    with pytest.raises(ValueError, match=message):
        validate_approval(packet, today=date(2026, 7, 18))


def test_cost_estimate_uses_frozen_standard_rates():
    packet = load_approval()
    assert estimate_cost_usd(packet, input_tokens=250_000, output_tokens=100_000) == 0.325
    assert estimate_cost_usd(packet, input_tokens=100, output_tokens=20) == 0.00008


def test_dispatch_enforces_at_most_once_failure_stop_tokens_and_cost():
    packet = load_approval()
    case = build_cases(packet)[0]
    prompt = build_prompt(case)
    DispatchState(packet, [], 0).assert_allowed(
        case=case, sample_index=0, prompt=prompt
    )

    record = _success(packet, case)
    with pytest.raises(ValueError, match="already consumed"):
        DispatchState(packet, [record], 0).assert_allowed(
            case=case, sample_index=0, prompt=prompt
        )
    failed = {**record, "status": "provider_error", "normalized_response": None}
    with pytest.raises(ValueError, match="stopped after"):
        DispatchState(packet, [failed], 0).assert_allowed(
            case=build_cases(packet)[1], sample_index=0, prompt=prompt
        )
    with pytest.raises(ValueError, match="wall-clock"):
        DispatchState(packet, [], 30).assert_allowed(
            case=case, sample_index=0, prompt=prompt
        )


def test_success_ledger_persists_only_normalized_response_hash_and_metadata(tmp_path: Path):
    packet = load_approval()
    record = _success(packet, build_cases(packet)[0])
    path = tmp_path / "observations.jsonl"
    append_observation(record, path)

    assert load_observations(path) == [record]
    assert record["estimated_cost_usd"] == 0.00008
    assert record["raw_prompt_persisted"] is False
    assert record["raw_response_persisted"] is False
    assert "instruction" not in record
    with pytest.raises(ValueError, match="raw T3R7"):
        validate_observations([{**record, "raw_response": "forbidden"}])


def test_report_reduces_48_safe_exact_observations_without_promotion_claim():
    packet = load_approval()
    records = [
        _success(packet, case, sample_index)
        for sample_index in (0, 1)
        for case in build_cases(packet)
    ]
    report = build_report(packet, records)

    assert report["decision"] == "pilot_complete"
    assert report["execution"]["consumed_calls"] == 48
    assert report["quality"]["safe_successful_samples"] == 48
    assert report["quality"]["correctness_passes"] == 288
    assert report["quality"]["completed_repeat_case_count"] == 24
    assert report["quality"]["variance_interpretable"] is True
    assert report["quality"]["variant_case_count"] == 0
    assert report["usage_and_cost"]["estimated_cost_usd"] < 1
    assert report["usage_and_cost"]["observations_with_reported_usage"] == 48
    assert report["usage_and_cost"]["observations_without_reported_usage"] == 0
    assert report["usage_and_cost"]["authoritative_billed_total"] is False
    assert all(
        value is False
        for key, value in report["api_spine_boundary"].items()
        if key != "classification"
    )


def test_finalize_accepts_one_terminal_consumed_failure_without_retry(tmp_path: Path):
    packet = load_approval()
    cases = build_cases(packet)
    source = tmp_path / "local.jsonl"
    destination = tmp_path / "durable.jsonl"
    report_destination = tmp_path / "report.json"
    for case in cases[:10]:
        append_observation(_success(packet, case), source)
    failed_case = cases[10]
    append_observation(
        failure_record(
            packet=packet,
            case=failed_case,
            sample_index=0,
            prompt_hash=canonical_hash(build_prompt(failed_case)),
            status="parse_error",
            safe_error_code="normalized_response_parse_or_schema_failure",
            started_at="2026-07-18T00:02:00.000Z",
            completed_at="2026-07-18T00:02:01.000Z",
            latency_ms=1000,
        ),
        source,
    )

    result = live_script.finalize_evidence(
        source=source,
        destination=destination,
        report_destination=report_destination,
    )
    report = json.loads(report_destination.read_text(encoding="utf-8"))

    assert result["observation_count"] == 11
    assert result["report_decision"] == "pilot_stopped_on_consumed_failure"
    assert report["execution"]["all_authorized_work_complete"] is True
    assert report["quality"]["completed_repeat_case_count"] == 0
    assert report["quality"]["variance_interpretable"] is False
    assert report["usage_and_cost"]["observations_with_reported_usage"] == 10
    assert report["usage_and_cost"]["observations_without_reported_usage"] == 1
    assert destination.read_bytes() == source.read_bytes()


def test_committed_report_matches_terminal_normalized_ledger_and_handover():
    records = load_observations(DEFAULT_OBSERVATION_PATH)
    committed = json.loads(DEFAULT_REPORT_PATH.read_text(encoding="utf-8"))
    closeout = Path("docs/bernie-t3r7-vertex-sydney-live-closeout.md").read_text(
        encoding="utf-8"
    )
    handover = Path("AGENTS.md").read_text(encoding="utf-8")

    assert len(records) == 11
    assert build_report(records=records) == committed
    assert committed["decision"] == "pilot_stopped_on_consumed_failure"
    assert committed["execution"]["consumed_calls"] == 11
    assert committed["execution"]["unused_calls"] == 37
    assert committed["quality"]["variance_interpretable"] is False
    assert committed["usage_and_cost"]["observations_without_reported_usage"] == 1
    assert "cannot be reconstructed" in closeout
    assert "no unused call" in closeout
    assert "no further provider call is authorized" in handover


def test_throttle_preserves_ten_second_start_interval_across_resume():
    reservations = {
        "one": {"reserved_at": "2026-07-18T00:00:00.000Z"},
        "two": {"reserved_at": "2026-07-18T00:00:05.000Z"},
    }
    now = datetime(2026, 7, 18, 0, 0, 9, tzinfo=timezone.utc)

    assert live_script.throttle_delay_seconds(
        reservations, now=now, minimum_interval=10
    ) == 6
    assert live_script.throttle_delay_seconds(
        reservations,
        now=datetime(2026, 7, 18, 0, 0, 20, tzinfo=timezone.utc),
        minimum_interval=10,
    ) == 0


def test_client_pins_sydney_base_url_and_one_total_attempt(monkeypatch):
    from google import genai

    captured = {}

    def fake_client(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(close=lambda: None)

    monkeypatch.setattr(genai, "Client", fake_client)
    live_script._create_client(load_approval())

    assert captured["vertexai"] is True
    assert captured["project"] == "bernie-emr4-dev"
    assert captured["location"] == "australia-southeast1"
    assert (
        captured["http_options"].base_url
        == "https://australia-southeast1-aiplatform.googleapis.com"
    )
    assert captured["http_options"].retry_options.attempts == 1


def test_vertex_call_disables_tools_cache_and_automatic_function_calls():
    packet = load_approval()
    case = build_cases(packet)[0]
    payload = _payload(case)
    captured = {}

    def generate_content(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            text=json.dumps(payload),
            usage_metadata=SimpleNamespace(
                prompt_token_count=100,
                candidates_token_count=20,
                thoughts_token_count=5,
                total_token_count=125,
            ),
            model_version="gemini-2.5-flash-001",
        )

    client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    normalized, _chars, usage = live_script._call_vertex(
        client, packet, build_prompt(case)
    )

    assert normalized == payload
    assert usage == (100, 25, "gemini-2.5-flash-001")
    config = captured["config"]
    assert config.tools == []
    assert config.cached_content is None
    assert config.automatic_function_calling.disable is True
    assert config.max_output_tokens == 2000


def test_cloud_control_preflight_requires_exact_role_audit_adc_and_logging(
    monkeypatch,
):
    packet = load_approval()
    fake_target = "synthetic-evaluator@example.invalid"

    def fake_gcloud(arguments, _safe_code):
        command = " ".join(arguments)
        if command.startswith("billing projects describe"):
            return {
                "billingEnabled": True,
                "billingAccountName": "billingAccounts/018984-CA0398-4C4B73",
            }
        if command.startswith("services list"):
            return [{"state": "ENABLED"}]
        if command.startswith("iam service-accounts list"):
            return [
                {
                    "displayName": live_script.TARGET_SERVICE_ACCOUNT_DISPLAY_NAME,
                    "email": fake_target,
                    "disabled": False,
                }
            ]
        if command.startswith("iam roles describe"):
            return {"includedPermissions": ["aiplatform.endpoints.predict"]}
        return {
            "bindings": [
                {
                    "role": live_script.CUSTOM_ROLE,
                    "members": [f"serviceAccount:{fake_target}"],
                }
            ],
            "auditConfigs": [
                {
                    "service": "aiplatform.googleapis.com",
                    "auditLogConfigs": [
                        {"logType": "DATA_READ"},
                        {"logType": "DATA_WRITE"},
                    ],
                }
            ],
        }

    class FakeCredentials:
        service_account_email = fake_target

    FakeCredentials.__module__ = "google.auth.impersonated_credentials"
    import google.auth

    monkeypatch.setattr(live_script, "_gcloud_json", fake_gcloud)
    monkeypatch.setattr(
        live_script, "_request_response_logging_disabled", lambda _packet: True
    )
    monkeypatch.setattr(
        google.auth,
        "default",
        lambda scopes: (FakeCredentials(), packet["provider"]["project"]),
    )

    assert all(live_script.verify_cloud_controls(packet).values())


def test_committed_control_evidence_binds_approval_and_keeps_product_gates_closed():
    packet = load_approval()
    evidence = json.loads(
        Path("docs/bernie-t3r7-vertex-sydney-control-evidence.json").read_text(
            encoding="utf-8"
        )
    )

    assert evidence["decision"] == "controls_passed_for_exact_approved_synthetic_pilot"
    assert evidence["approval_binding"] == canonical_hash(packet)
    assert all(evidence["checks"].values())
    assert evidence["credit_posture"]["pilot_authority_depends_on_credit"] is False
    assert evidence["credit_posture"]["vertex_gemini_sku_eligibility"].startswith(
        "unverified"
    )
    assert all(
        value is False
        for key, value in evidence["api_spine_boundary"].items()
        if key != "classification"
    )


def test_provider_sdk_and_control_subprocesses_stay_out_of_pure_reducer():
    module_source = Path(
        "app/services/ai/evals/bernie_vertex_sydney_live_pilot.py"
    ).read_text(encoding="utf-8")
    script_source = Path("scripts/bernie_t3r7_vertex_sydney_live_pilot.py").read_text(
        encoding="utf-8"
    )

    assert "google.genai" not in module_source
    assert "import subprocess" not in module_source
    assert "import fastapi" not in module_source.lower()
    assert "sqlalchemy" not in module_source
    assert "from google import genai" in script_source
    assert "HttpRetryOptions(attempts=1)" in script_source
    assert "AutomaticFunctionCallingConfig" in script_source
    assert 'tools=[]' in script_source
