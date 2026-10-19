"""Authored synthetic checks for local, effect-free word suggestions."""

import httpx
import pytest

from stage1_demo_intent import interpret_words
from test_stage1_demo_http import REQ_A, REQ_B, bridge_case


CLOCK = "2026-10-12 10:01"
ZONE = "Australia/Brisbane"


def interpret(kind, words, persona=None):
    return interpret_words(kind, words, persona=persona or (
        "patient" if kind == "request" else "staff"), demo_clock=CLOCK, timezone=ZONE)


def test_explicit_and_weekday_move_suggestions():
    for words in ("move to 2026-10-15 at 14:30", "move to next Thursday at 2:30 pm"):
        result = interpret("move", words)
        assert result == {"schema": "emr4.stage1_word_interpretation.v1",
            "status": "PROPOSED", "kind": "move", "method": "DETERMINISTIC_LOCAL",
            "fields": {"target_date": "2026-10-15", "target_start_local": "14:30"},
            "missing": [], "message": "READY_FOR_HUMAN_REVIEW"}


def test_bounded_request_window_and_incomplete_after():
    full = interpret("request", "book on Thursday 2026-10-15 between 2:00 pm and 5:00 pm")
    assert full["status"] == "PROPOSED"
    assert full["fields"] == {"date": "2026-10-15", "earliest_local": "14:00",
                              "latest_local": "17:00"}
    partial = interpret("request", "book on Thursday after 2 pm")
    assert partial["status"] == "CLARIFICATION"
    assert partial["fields"] == {"date": "2026-10-15", "earliest_local": "14:00"}
    assert partial["missing"] == ["latest_local"]


def test_shipped_visible_examples_produce_reviewable_fields():
    request = interpret("request", "Follow-up next Thursday between 2 pm and 4 pm.")
    assert request["status"] == "PROPOSED"
    assert request["fields"] == {"date": "2026-10-15", "earliest_local": "14:00",
                                 "latest_local": "16:00"}
    move = interpret("move", "Move this appointment next Thursday at 3 pm.")
    assert move["status"] == "PROPOSED"
    assert move["fields"] == {"target_date": "2026-10-15",
                              "target_start_local": "15:00"}


@pytest.mark.parametrize("words", [
    "move to Thursday or Friday at 2 pm",
    "move to 2026-10-15 at 2 pm and 3 pm",
    "move to 2026-10-15 at 2 pm and change the patient",
    "move to 2026-10-15 at noon",
    "move to 2026-10-15 at 2 pm maybe",
    "move to 2026-10-15 at 14:00 and 2026-10-16",
])
def test_ambiguous_or_unsupported_words_never_propose(words):
    result = interpret("move", words)
    assert result["status"] == "CLARIFICATION"
    assert result["fields"] == {}
    assert result["missing"] == ["target_date", "target_start_local"]


@pytest.mark.anyio
async def test_interpret_route_requires_persona_origin_csrf_and_exact_json(bridge_case):
    app, issuer, config, *_ = bridge_case
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53116)), base_url=config.listener_origin) as client:
        patient_cookie = dict([issuer.cookie_for("patient", REQ_B)])
        patient_session = (await client.get("/demo/stage1/session", cookies=patient_cookie)).json()
        headers = {"Origin": config.listener_origin, "X-CSRF-Token": patient_session["csrf"],
                   "Content-Type": "application/json"}
        words = {"kind": "request", "words": "book on Thursday between 2 pm and 5 pm"}
        accepted = await client.post("/demo/stage1/interpret", cookies=patient_cookie,
                                     headers=headers, json=words)
        assert accepted.status_code == 200 and accepted.json()["status"] == "PROPOSED"
        assert "no-store" in accepted.headers["cache-control"]
        assert (await client.post("/demo/stage1/interpret", cookies=patient_cookie,
            headers=headers, json={**words, "kind": "move"})).status_code == 400
        assert (await client.post("/demo/stage1/interpret", cookies=patient_cookie,
            headers={**headers, "Origin": "http://evil.test"}, json=words)).status_code == 403
        assert (await client.post("/demo/stage1/interpret", cookies=patient_cookie,
            headers={**headers, "X-CSRF-Token": "wrong"}, json=words)).status_code == 403
        duplicate = b'{"kind":"request","words":"Thursday at 2 pm","words":"Friday at 3 pm"}'
        assert (await client.post("/demo/stage1/interpret", cookies=patient_cookie,
            headers=headers, content=duplicate)).status_code == 400
        staff_cookie = dict([issuer.cookie_for("staff", REQ_A)])
        staff_session = (await client.get("/demo/stage1/session", cookies=staff_cookie)).json()
        staff_headers = {**headers, "X-CSRF-Token": staff_session["csrf"]}
        assert (await client.post("/demo/stage1/interpret", cookies=staff_cookie,
            headers=staff_headers, json={"kind": "move", "words": "move to Thursday at 14:30"})).status_code == 200
