import json

from scripts import smoke_bernie_interpreter


def test_smoke_script_fake_provider_outputs_redacted_compact_payload(capsys):
    exit_code = smoke_bernie_interpreter.main([
        "--provider",
        "fake",
        "--reference-date",
        "2026-06-28",
        "--expect-result",
        "interpreted",
    ])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["provider"] == "fake"
    assert payload["mode"] == "mocked"
    assert payload["live_provider"] is False
    assert payload["result"] == "interpreted"
    assert payload["safe"] is True
    assert payload["command_candidate"]["practitioner_id"] == "[id-present]"
    assert "420fb926-750b-4914-910b-e9d3f804e0f0" not in json.dumps(payload)


def test_smoke_script_refuses_live_provider_without_explicit_allow(capsys):
    exit_code = smoke_bernie_interpreter.main(["--provider", "gemini_vertex"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Refusing live Gemini/Vertex smoke without --allow-live" in captured.err
    assert captured.out == ""


def test_smoke_script_expect_result_failure_is_nonzero(capsys):
    exit_code = smoke_bernie_interpreter.main([
        "--provider",
        "disabled",
        "--expect-result",
        "interpreted",
    ])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Expected result 'interpreted', got 'blocked'." in captured.err
    payload = json.loads(captured.out)
    assert payload["provider"] == "disabled"
    assert payload["block_codes"] == ["booking_interpreter_disabled"]


def test_smoke_script_readiness_gate_reports_fallback_ready(capsys):
    exit_code = smoke_bernie_interpreter.main([
        "--provider",
        "gemini_vertex",
        "--allow-live",
        "--check-readiness",
        "--expect-ready",
        "true",
    ])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["provider"] == "gemini_vertex"
    assert payload["ready"] is True
    assert payload["mode"] in {"live", "deterministic_fallback"}


def test_smoke_script_ordinary_time_gate_parses_receptionist_phrase(capsys):
    exit_code = smoke_bernie_interpreter.main([
        "--provider",
        "fake",
        "--instruction",
        "Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45",
        "--reference-date",
        "2026-07-01",
        "--expect-result",
        "clarification_required",
        "--expect-earliest-time",
        "14:00",
        "--expect-latest-time",
        "15:45",
        "--expect-mode",
        "mocked",
    ])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["command_candidate"]["earliest_time"] == "14:00"
    assert payload["command_candidate"]["latest_time"] == "15:45"


def test_smoke_script_id_presence_expectations_keep_compact_output_redacted(capsys):
    exit_code = smoke_bernie_interpreter.main([
        "--provider",
        "fake",
        "--instruction",
        (
            "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 "
            "patient_id:11111111-1111-1111-1111-111111111111 today 15 minutes"
        ),
        "--reference-date",
        "2026-07-01",
        "--expect-result",
        "interpreted",
        "--expect-practitioner-id-present",
        "--expect-patient-id-present",
    ])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["command_candidate"]["practitioner_id"] == "[id-present]"
    assert payload["command_candidate"]["patient_id"] == "[id-present]"


def test_smoke_script_id_presence_expectation_failure_is_nonzero(capsys):
    exit_code = smoke_bernie_interpreter.main([
        "--provider",
        "fake",
        "--instruction",
        "appointment today after 2 pm",
        "--expect-practitioner-id-present",
    ])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Expected command_candidate.practitioner_id to be present." in captured.err
    payload = json.loads(captured.out)
    assert payload["command_candidate"].get("practitioner_id") is None
    assert "420fb926-750b-4914-910b-e9d3f804e0f0" not in captured.out


def test_smoke_script_time_expectation_failure_is_nonzero(capsys):
    exit_code = smoke_bernie_interpreter.main([
        "--provider",
        "fake",
        "--instruction",
        "appointment today after 2 pm",
        "--expect-earliest-time",
        "15:00",
    ])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Expected earliest_time '15:00', got '14:00'." in captured.err
