"""
Bernie scenario replay engine.

Executes ordered scenario turns against backend endpoints, installs
the forbidden-AI-provider guard, and returns structured pass/fail evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from app.config import settings
from app.models.appointments import Appointment, AppointmentAuditLog
import app.services.ai.service as ai_service

from .loader import Scenario, ScenarioTurn

INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"
NORMALIZE_URL = "/api/v1/appointments/proposals/slot-search/normalize"
SEARCH_URL = "/api/v1/appointments/proposals/slot-search/normalized"
SELECTION_URL = "/api/v1/appointments/proposals/slot-search/selection"
CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm-bernie"


@dataclass
class TurnRecord:
    action: str
    request_body: Any
    status_code: int
    response: dict


@dataclass
class ReplayResult:
    scenario_id: str
    passed: bool
    evidence: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)


def _resolve(value: Any, ctx: "ReplayContext") -> Any:
    """Replace {practitioner_id}, {patient_id}, {practice_id} template vars."""
    if isinstance(value, str):
        value = value.replace("{practitioner_id}", str(ctx.practitioner_id))
        value = value.replace("{patient_id}", str(ctx.patient_id))
        value = value.replace("{practice_id}", str(ctx.practice_id))
        return value
    if isinstance(value, dict):
        return {k: _resolve(v, ctx) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve(v, ctx) for v in value]
    return value


def _get_nested(obj: Any, dotted_path: str) -> Any:
    """Traverse a JSON dict/list using a dotted field path."""
    for part in dotted_path.split("."):
        if isinstance(obj, dict):
            obj = obj.get(part)
        elif isinstance(obj, list) and part.isdigit():
            idx = int(part)
            obj = obj[idx] if 0 <= idx < len(obj) else None
        else:
            return None
    return obj


def _install_forbidden_ai_provider_guard(monkeypatch) -> None:
    def _forbidden(*args, **kwargs):
        raise AssertionError("Scenario replay must not call AI providers")
    monkeypatch.setattr(ai_service, "_get_default_provider", _forbidden)


def _requested_appointment_frames(response: Optional[dict]) -> list[dict]:
    if not response:
        return []
    ctx = response.get("reception_context") or {}
    return [
        frame
        for frame in (ctx.get("frames") or [])
        if isinstance(frame, dict)
        and frame.get("frame_type") == "requested_appointment"
    ]


class ReplayContext:
    def __init__(
        self,
        client,
        db,
        token: str,
        reference_date: str,
        practitioner_id,
        patient_id,
        practice_id,
    ):
        self.client = client
        self.db = db
        self.token = token
        self.reference_date = reference_date
        self.practitioner_id = practitioner_id
        self.patient_id = patient_id
        self.practice_id = practice_id
        self._turns: list[TurnRecord] = []

    def _auth(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    @property
    def last_normalize_input(self) -> Optional[dict]:
        for t in reversed(self._turns):
            if t.action == "normalize":
                return t.request_body
        return None

    @property
    def last_interpret_response(self) -> Optional[dict]:
        for t in reversed(self._turns):
            if t.action == "interpret":
                return t.response
        return None

    @property
    def last_interpret_command(self) -> Optional[dict]:
        last = self.last_interpret_response
        if not last:
            return None
        command = last.get("command_candidate")
        return command if isinstance(command, dict) else None

    @property
    def last_search_response(self) -> Optional[dict]:
        for t in reversed(self._turns):
            if t.action == "search":
                return t.response
        return None

    @property
    def last_selection_response(self) -> Optional[dict]:
        for t in reversed(self._turns):
            if t.action == "select":
                return t.response
        return None

    def _safe_json(self, resp) -> dict:
        try:
            return resp.json()
        except Exception:
            return {}

    def _execute_interpret(self, turn: ScenarioTurn) -> TurnRecord:
        inp = _resolve(turn.input, self)
        if not isinstance(inp, dict):
            inp = {}
        if "context_frames" in inp:
            context_frames = inp.get("context_frames") or []
        else:
            # First interpret turn has no prior response, so this intentionally
            # starts with an empty context-frame list.
            context_frames = _requested_appointment_frames(self.last_interpret_response)
        body = {
            "instruction": inp.get("instruction", ""),
            "reference_date": inp.get("reference_date", self.reference_date),
            "context_frames": context_frames,
        }
        resp = self.client.post(
            INTERPRET_URL,
            json=body,
            headers=self._auth(),
        )
        return TurnRecord("interpret", body, resp.status_code, self._safe_json(resp))

    def _execute_normalize(self, turn: ScenarioTurn) -> TurnRecord:
        command = _resolve(turn.input, self)
        resp = self.client.post(
            NORMALIZE_URL,
            params={"reference_date": self.reference_date},
            json=command,
            headers=self._auth(),
        )
        return TurnRecord("normalize", command, resp.status_code, self._safe_json(resp))

    def _execute_search(self, turn: ScenarioTurn) -> TurnRecord:
        command = (
            _resolve(turn.input, self)
            if turn.input
            else (self.last_normalize_input or self.last_interpret_command or {})
        )
        resp = self.client.post(
            SEARCH_URL,
            params={"reference_date": self.reference_date},
            json=command,
            headers=self._auth(),
        )
        return TurnRecord("search", command, resp.status_code, self._safe_json(resp))

    def _execute_select(self, turn: ScenarioTurn) -> TurnRecord:
        inp = _resolve(turn.input, self)
        body = {
            "search_execution": self.last_search_response,
            "selected_candidate_index": inp.get("selected_candidate_index", 0),
            "patient_id": inp.get("patient_id", str(self.patient_id)),
            "reason": inp.get("reason", ""),
        }
        resp = self.client.post(SELECTION_URL, json=body, headers=self._auth())
        return TurnRecord("select", body, resp.status_code, self._safe_json(resp))

    def _execute_confirm(self, turn: ScenarioTurn) -> TurnRecord:
        inp = _resolve(turn.input, self)
        body = {
            "confirmed": inp.get("confirmed", True),
            "selection_proposal": self.last_selection_response,
        }
        headers = {
            **self._auth(),
            "Idempotency-Key": inp.get(
                "idempotency_key",
                f"scenario-replay-confirm-{len(self._turns)}",
            ),
        }
        resp = self.client.post(CONFIRM_URL, json=body, headers=headers)
        return TurnRecord("confirm", body, resp.status_code, self._safe_json(resp))

    def execute_turn(self, turn: ScenarioTurn) -> TurnRecord:
        dispatch = {
            "interpret": self._execute_interpret,
            "normalize": self._execute_normalize,
            "search": self._execute_search,
            "select": self._execute_select,
            "confirm": self._execute_confirm,
        }
        record = dispatch[turn.action](turn)
        self._turns.append(record)
        return record


def run_scenario(
    scenario: Scenario,
    client,
    db,
    token: str,
    practitioner,
    patient,
    practice,
    monkeypatch,
) -> ReplayResult:
    """Run all turns for a scenario and return structured pass/fail evidence."""
    ctx = ReplayContext(
        client=client,
        db=db,
        token=token,
        reference_date=scenario.reference_date,
        practitioner_id=practitioner.id,
        patient_id=patient.id,
        practice_id=practice.id,
    )

    _install_forbidden_ai_provider_guard(monkeypatch)
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")

    appt_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    evidence: list[str] = []
    failures: list[str] = []
    preserved_snapshots: dict[str, Any] = {}

    for idx, turn in enumerate(scenario.turns):
        record = ctx.execute_turn(turn)

        if record.status_code != turn.expect.status:
            failures.append(
                f"turn[{idx}] {turn.action}: status expected={turn.expect.status} "
                f"actual={record.status_code}"
            )
        else:
            evidence.append(
                f"turn[{idx}] {turn.action}: status={record.status_code} OK"
            )

        for path, expected_val in turn.expect.fields.items():
            resolved_expected = _resolve(expected_val, ctx)
            actual = _get_nested(record.response, path)
            if actual != resolved_expected:
                failures.append(
                    f"turn[{idx}] {turn.action}: field '{path}' "
                    f"expected={resolved_expected!r} actual={actual!r}"
                )
            else:
                evidence.append(
                    f"turn[{idx}] {turn.action}: {path}={actual!r} OK"
                )

        for pf in scenario.preserved_fields:
            actual = _get_nested(record.response, pf)
            if actual is None:
                if pf in preserved_snapshots:
                    failures.append(
                        f"turn[{idx}] preserved field '{pf}' disappeared: "
                        f"was={preserved_snapshots[pf]!r} now=None"
                    )
                continue
            if pf not in preserved_snapshots:
                preserved_snapshots[pf] = actual
                evidence.append(
                    f"turn[{idx}] preserved '{pf}'={actual!r} snapshotted"
                )
            elif preserved_snapshots[pf] != actual:
                failures.append(
                    f"turn[{idx}] preserved field '{pf}' drifted: "
                    f"was={preserved_snapshots[pf]!r} now={actual!r}"
                )

    appt_after = db.query(Appointment).count()
    audit_after = db.query(AppointmentAuditLog).count()
    appt_written = appt_after > appt_before
    audit_written = audit_after > audit_before

    if scenario.expected.appointment_written and not appt_written:
        failures.append("expected appointment_written=True but no new Appointment rows")
    elif not scenario.expected.appointment_written and appt_written:
        failures.append(
            f"expected appointment_written=False but "
            f"{appt_after - appt_before} new Appointment row(s)"
        )
    else:
        evidence.append(f"appointment_written={appt_written} as expected")

    if scenario.expected.audit_written and not audit_written:
        failures.append(
            "expected audit_written=True but no new AppointmentAuditLog rows"
        )
    elif not scenario.expected.audit_written and audit_written:
        failures.append(
            f"expected audit_written=False but "
            f"{audit_after - audit_before} new AppointmentAuditLog row(s)"
        )
    else:
        evidence.append(f"audit_written={audit_written} as expected")

    if "appointment_written" in scenario.forbidden_outcomes and appt_written:
        failures.append("FORBIDDEN: appointment_written occurred")
    if "audit_written" in scenario.forbidden_outcomes and audit_written:
        failures.append("FORBIDDEN: audit_written occurred")
    # provider_called is enforced by the monkeypatch guard: if called, turn execution
    # raises AssertionError before we reach this point.

    return ReplayResult(
        scenario_id=scenario.id,
        passed=len(failures) == 0,
        evidence=evidence,
        failures=failures,
    )
