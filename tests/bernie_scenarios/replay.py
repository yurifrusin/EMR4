"""
Bernie scenario replay engine.

Executes ordered scenario turns against backend endpoints, installs
the forbidden-AI-provider guard, and returns structured pass/fail evidence.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
import json
from pathlib import Path
import re
from typing import Any, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.config import settings
from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentStatus,
    BookingChannel,
)
import app.routers.appointments as appointments_router
import app.services.ai.service as ai_service

from .loader import Scenario, ScenarioTurn

INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"
NORMALIZE_URL = "/api/v1/appointments/proposals/slot-search/normalize"
SEARCH_URL = "/api/v1/appointments/proposals/slot-search/normalized"
SELECTION_URL = "/api/v1/appointments/proposals/slot-search/selection"
SUPERVISED_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"
CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm-bernie"


@dataclass
class TurnRecord:
    action: str
    request_body: Any
    status_code: int
    response: dict
    appointment_delta: int = 0
    audit_delta: int = 0


@dataclass
class ReplayResult:
    scenario_id: str
    passed: bool
    evidence: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    evidence_record: dict[str, Any] = field(default_factory=dict)


def write_evidence_record(result: ReplayResult, path: Path) -> Path:
    """Write only the redacted portable record, never raw turn payloads."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result.evidence_record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def _resolve(value: Any, ctx: "ReplayContext") -> Any:
    """Replace {practitioner_id}, {patient_id}, {practice_id} template vars."""
    if isinstance(value, str):
        value = value.replace("{practitioner_id}", str(ctx.practitioner_id))
        if ctx.other_practitioner_id is not None:
            value = value.replace(
                "{other_practitioner_id}",
                str(ctx.other_practitioner_id),
            )
        value = value.replace("{patient_id}", str(ctx.patient_id))
        value = value.replace("{practice_id}", str(ctx.practice_id))
        value = re.sub(
            r"\{appointment_id:([a-zA-Z0-9][a-zA-Z0-9_-]*)\}",
            lambda match: str(ctx.seeded_appointment_ids.get(match.group(1), match.group(0))),
            value,
        )
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
        other_practitioner_id,
        patient_id,
        practice_id,
        practice_timezone: str,
    ):
        self.client = client
        self.db = db
        self.token = token
        self.reference_date = reference_date
        self.practitioner_id = practitioner_id
        self.other_practitioner_id = other_practitioner_id
        self.patient_id = patient_id
        self.practice_id = practice_id
        self.practice_timezone = practice_timezone
        self.seeded_appointment_ids: dict[str, Any] = {}
        self.fixture_event_count: int = 0
        self._fixture_appointment_delta: int = 0
        self._fixture_audit_delta: int = 0
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
    def last_supervised_response(self) -> Optional[dict]:
        for t in reversed(self._turns):
            if t.action == "supervise":
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

    def _execute_supervise(self, turn: ScenarioTurn) -> TurnRecord:
        inp = _resolve(turn.input, self)
        command = inp.get("command") or self.last_interpret_command or self.last_normalize_input or {}
        if "context_frames" in inp:
            context_frames = inp.get("context_frames") or []
        else:
            context_frames = _requested_appointment_frames(self.last_interpret_response)
        body: dict[str, Any] = {
            "command": command,
            "reference_date": inp.get("reference_date", self.reference_date),
            "context_frames": context_frames,
            "patient_id": inp.get(
                "patient_id",
                command.get("patient_id") if isinstance(command, dict) else str(self.patient_id),
            ) or str(self.patient_id),
        }
        for key in (
            "selected_candidate_index",
            "selected_candidate",
            "practitioner_id",
            "appointment_type_id",
            "location_id",
            "patient_name_provisional",
            "reason",
            "notes",
            "booked_via",
            "turn_ref",
            "server_session_id",
            "server_session_surface_id",
            "server_session_expected_revision",
            "server_session_idempotency_key",
        ):
            if key in inp:
                body[key] = inp[key]
        resp = self.client.post(SUPERVISED_URL, json=body, headers=self._auth())
        return TurnRecord("supervise", body, resp.status_code, self._safe_json(resp))

    def _execute_confirm(self, turn: ScenarioTurn) -> TurnRecord:
        inp = _resolve(turn.input, self)
        supervised = self.last_supervised_response or {}
        supervised_payload = (supervised.get("staff_review") or {}).get("confirm_payload")
        if isinstance(supervised_payload, dict):
            body = copy.deepcopy(supervised_payload)
            body["confirmed"] = inp.get("confirmed", True)
            if "confirmed_warnings" in inp:
                body["confirmed_warnings"] = inp["confirmed_warnings"]
        else:
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

    def _execute_external_appointment(self, turn: ScenarioTurn) -> TurnRecord:
        inp = _resolve(turn.input, self)
        operation = str(inp.get("operation", ""))

        try:
            practice_tz = ZoneInfo(self.practice_timezone)
        except ZoneInfoNotFoundError:
            practice_tz = timezone.utc

        if operation == "create":
            patient_ref = str(inp.get("patient") or "{patient_id}")
            if patient_ref not in {
                "{patient_id}",
                "fixture_patient",
                "Margaret Thompson",
            }:
                raise ValueError(
                    "External appointment patient escaped the fixture allowlist"
                )
            patient_id = self.patient_id
            practitioner_ref = str(inp.get("practitioner") or "{practitioner_id}")
            if practitioner_ref not in {
                "{practitioner_id}",
                "fixture_practitioner",
                "Dr Shera",
            }:
                raise ValueError(
                    "External appointment practitioner escaped the fixture allowlist"
                )
            practitioner_id = self.practitioner_id
            appointment_date = date.fromisoformat(str(inp["date"]))
            start_time_local = time.fromisoformat(str(inp["time"]))
            local_start = datetime.combine(
                appointment_date, start_time_local
            ).replace(tzinfo=practice_tz)
            status = AppointmentStatus(
                str(inp.get("status") or AppointmentStatus.Booked.value)
            )
            appointment = Appointment(
                practice_id=self.practice_id,
                patient_id=patient_id,
                practitioner_id=practitioner_id,
                start_time=local_start.astimezone(timezone.utc),
                appointment_date=appointment_date,
                start_time_local=start_time_local,
                duration_minutes=int(inp.get("duration_minutes", 15)),
                status=status,
                reason=inp.get("reason"),
                booked_via=BookingChannel.Receptionist,
            )
            self.db.add(appointment)
            self.db.flush()
            alias = str(inp.get("id") or f"ext-{self.fixture_event_count}")
            if alias in self.seeded_appointment_ids:
                raise ValueError(f"Duplicate external appointment alias {alias!r}")
            self.seeded_appointment_ids[alias] = appointment.id
            # Track that this fixture event created a new Appointment row
            self._fixture_appointment_delta += 1

        elif operation == "set_status":
            alias = str(inp["appointment_id"])
            if alias not in self.seeded_appointment_ids:
                raise ValueError(
                    f"Unknown external appointment alias {alias!r} "
                    f"in scenario turn (fixture_event_count={self.fixture_event_count})"
                )
            appt = self.db.get(Appointment, self.seeded_appointment_ids[alias])
            if appt is not None:
                appt.status = AppointmentStatus(str(inp["status"]))
                self.db.flush()

        # The event represents a change made by another actor/transaction. It
        # must survive a later route rollback during stale-confirm revalidation.
        self.db.commit()
        self.fixture_event_count += 1
        return TurnRecord(
            "external_appointment",
            {"operation": operation},
            200,
            {"result": "fixture_applied", "operation": operation},
        )

    def execute_turn(self, turn: ScenarioTurn) -> TurnRecord:
        dispatch = {
            "interpret": self._execute_interpret,
            "normalize": self._execute_normalize,
            "search": self._execute_search,
            "select": self._execute_select,
            "supervise": self._execute_supervise,
            "confirm": self._execute_confirm,
            "external_appointment": self._execute_external_appointment,
        }
        record = dispatch[turn.action](turn)
        self._turns.append(record)
        return record


def _scenario_clock(scenario: Scenario, practice_timezone: str) -> datetime:
    state = scenario.initial_state
    clock_date = date.fromisoformat(str(state.get("diary_date") or scenario.reference_date))
    clock_time = time.fromisoformat(str(state.get("simulated_clinic_time") or "08:00"))
    try:
        tz = ZoneInfo(practice_timezone)
    except ZoneInfoNotFoundError:
        tz = timezone.utc
    return datetime.combine(clock_date, clock_time).replace(tzinfo=tz)


def _seed_initial_state(scenario: Scenario, ctx: ReplayContext) -> int:
    seeds = scenario.initial_state.get("seeded_appointments") or []
    if not seeds:
        return 0
    try:
        practice_tz = ZoneInfo(ctx.practice_timezone)
    except ZoneInfoNotFoundError:
        practice_tz = timezone.utc

    for index, seed in enumerate(seeds):
        alias = str(seed.get("id") or f"seed-{index}")
        patient_ref = str(seed.get("patient") or "{patient_id}")
        practitioner_ref = str(seed.get("practitioner") or "{practitioner_id}")
        if patient_ref not in {
            "{patient_id}",
            "fixture_patient",
            "Margaret Thompson",
        }:
            raise ValueError("Seeded appointment patient escaped the fixture allowlist")
        if practitioner_ref not in {
            "{practitioner_id}",
            "fixture_practitioner",
            "Dr Shera",
        }:
            raise ValueError(
                "Seeded appointment practitioner escaped the fixture allowlist"
            )
        patient_id = ctx.patient_id
        practitioner_id = ctx.practitioner_id
        appointment_date = date.fromisoformat(str(seed["date"]))
        start_time_local = time.fromisoformat(str(seed["time"]))
        local_start = datetime.combine(appointment_date, start_time_local).replace(
            tzinfo=practice_tz
        )
        status = AppointmentStatus(str(seed.get("status") or AppointmentStatus.Booked.value))
        appointment = Appointment(
            practice_id=ctx.practice_id,
            patient_id=patient_id,
            practitioner_id=practitioner_id,
            start_time=local_start.astimezone(timezone.utc),
            appointment_date=appointment_date,
            start_time_local=start_time_local,
            duration_minutes=int(seed.get("duration_minutes", 15)),
            status=status,
            reason=seed.get("reason"),
            booked_via=BookingChannel.Receptionist,
        )
        ctx.db.add(appointment)
        ctx.db.flush()
        ctx.seeded_appointment_ids[alias] = appointment.id
    return len(seeds)


def _redacted_evidence_record(
    scenario: Scenario,
    ctx: ReplayContext,
    *,
    seeded_appointment_count: int,
    fixture_event_count: int,
    appointment_delta: int,
    audit_delta: int,
    failure_count: int,
) -> dict[str, Any]:
    turns = []
    for index, record in enumerate(ctx._turns):
        turns.append({
            "index": index,
            "action": record.action,
            "status_code": record.status_code,
            "result_kind": record.response.get("result")
            or record.response.get("intent")
            or record.response.get("status"),
            "safe": record.response.get("safe"),
            "requires_confirmation": record.response.get("requires_confirmation"),
            "appointment_delta": record.appointment_delta,
            "audit_delta": record.audit_delta,
        })
    return {
        "schema_version": "bernie.scenario.evidence.v1",
        "scenario_id": scenario.id,
        "evidence_level": "E1_fake_provider_db_backed_route_replay",
        "provider_calls_performed": False,
        "raw_instruction_included": False,
        "raw_response_included": False,
        "seeded_appointment_count": seeded_appointment_count,
        "fixture_event_count": fixture_event_count,
        "turn_count": len(turns),
        "turns": turns,
        "appointment_delta": appointment_delta,
        "audit_delta": audit_delta,
        "failure_count": failure_count,
        "passed": failure_count == 0,
    }


def run_scenario(
    scenario: Scenario,
    client,
    db,
    token: str,
    practitioner,
    patient,
    practice,
    monkeypatch,
    other_practitioner=None,
) -> ReplayResult:
    """Run all turns for a scenario and return structured pass/fail evidence."""
    ctx = ReplayContext(
        client=client,
        db=db,
        token=token,
        reference_date=scenario.reference_date,
        practitioner_id=practitioner.id,
        other_practitioner_id=(
            other_practitioner.id if other_practitioner is not None else None
        ),
        patient_id=patient.id,
        practice_id=practice.id,
        practice_timezone=practice.timezone or "Australia/Sydney",
    )

    _install_forbidden_ai_provider_guard(monkeypatch)
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    scenario_now = _scenario_clock(scenario, ctx.practice_timezone)
    monkeypatch.setattr(
        appointments_router,
        "_clinic_local_now",
        lambda tz: scenario_now.astimezone(tz),
    )

    seeded_appointment_count = _seed_initial_state(scenario, ctx)

    appt_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    evidence: list[str] = []
    failures: list[str] = []
    preserved_snapshots: dict[str, Any] = {}

    for idx, turn in enumerate(scenario.turns):
        turn_appt_before = db.query(Appointment).count()
        turn_audit_before = db.query(AppointmentAuditLog).count()
        record = ctx.execute_turn(turn)
        record.appointment_delta = db.query(Appointment).count() - turn_appt_before
        record.audit_delta = db.query(AppointmentAuditLog).count() - turn_audit_before

        # Zero deltas for external fixture events — they are scenario-environment
        # setup, not product writes. Tracked separately via fixture_event_count.
        if turn.action == "external_appointment":
            record.appointment_delta = 0
            record.audit_delta = 0

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

        for label, expected_delta, actual_delta in (
            ("appointment_delta", turn.expect.appointment_delta, record.appointment_delta),
            ("audit_delta", turn.expect.audit_delta, record.audit_delta),
        ):
            if expected_delta is None:
                continue
            if actual_delta != expected_delta:
                failures.append(
                    f"turn[{idx}] {turn.action}: {label} "
                    f"expected={expected_delta} actual={actual_delta}"
                )
            else:
                evidence.append(
                    f"turn[{idx}] {turn.action}: {label}={actual_delta} OK"
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
    # Exclude fixture-created rows from product-write detection
    product_appt_delta = appt_after - appt_before - ctx._fixture_appointment_delta
    product_audit_delta = audit_after - audit_before - ctx._fixture_audit_delta
    appt_written = product_appt_delta > 0
    audit_written = product_audit_delta > 0

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

    evidence_record = _redacted_evidence_record(
        scenario,
        ctx,
        seeded_appointment_count=seeded_appointment_count,
        fixture_event_count=ctx.fixture_event_count,
        appointment_delta=product_appt_delta,
        audit_delta=product_audit_delta,
        failure_count=len(failures),
    )
    return ReplayResult(
        scenario_id=scenario.id,
        passed=len(failures) == 0,
        evidence=evidence,
        failures=failures,
        evidence_record=evidence_record,
    )
