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
