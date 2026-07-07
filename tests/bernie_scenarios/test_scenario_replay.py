"""
Parametrized Bernie scenario replay harness.

Loads YAML fixtures from tests/fixtures/bernie_scenarios/, runs ordered backend
turns with no LLM/provider calls, and asserts structured outcomes.

Run with:
    pytest tests/bernie_scenarios/ -v

Authorship boundary:
  - tests/fixtures/bernie_scenarios/harness_demo_*.yaml: Claude/harness (mechanics)
  - tests/fixtures/bernie_scenarios/*.yaml (corpus): Antigravity (Sprint R1-B)
  - Fixture integrity: DeepSeek (Sprint R1-C)
"""

from __future__ import annotations

import pytest

from app.models.tenancy import Practitioner
from tests.conftest import make_token
from tests.bernie_scenarios.loader import Scenario, discover_scenarios
from tests.bernie_scenarios.replay import run_scenario


def _build_params() -> list:
    scenarios = discover_scenarios()
    params = []
    for s in scenarios:
        marks = []
        if s.xfail:
            marks.append(pytest.mark.xfail(reason=s.xfail.reason, strict=False))
        params.append(pytest.param(s, id=s.id, marks=marks))
    return params


_SCENARIO_PARAMS = _build_params()


@pytest.fixture()
def other_practitioner(db, practice):
    pr = Practitioner(
        practice_id=practice.id,
        first_name="Priya",
        last_name="Patel",
        ahpra_number="MED0007654321",
    )
    db.add(pr)
    db.flush()
    return pr


@pytest.mark.parametrize("scenario", _SCENARIO_PARAMS)
def test_bernie_scenario_replay(
    scenario: Scenario,
    client,
    db,
    gp_user,
    practitioner,
    other_practitioner,
    patient,
    practice,
    schedule,
    monkeypatch,
):
    token = make_token(gp_user)
    result = run_scenario(
        scenario=scenario,
        client=client,
        db=db,
        token=token,
        practitioner=practitioner,
        other_practitioner=other_practitioner,
        patient=patient,
        practice=practice,
        monkeypatch=monkeypatch,
    )

    evidence_lines = "\n".join(f"  + {e}" for e in result.evidence)
    failure_lines = "\n".join(f"  ! {f}" for f in result.failures)

    if not result.passed:
        pytest.fail(
            f"Scenario {scenario.id!r} failed:\n{failure_lines}"
            + (f"\nEvidence so far:\n{evidence_lines}" if evidence_lines else "")
        )

    print(f"\n[PASS] {scenario.id}\n{evidence_lines}")
