"""Sprint 105: Bernie typed turn contract and confirmation evidence tests.

Verifies:
- Typed turn primitives (BernieTurnRef, BernieTurnEventKind) are accepted
- Deterministic freshness id computation (stable, PHI-safe, no wall-clock)
- Staleness gate: stale freshness id blocks confirmation with no DB mutation
- Mismatched reference_date blocks confirmation with no DB mutation
- No-slot suggestion selection carries originating turn_id
- Backward compat: Sprint 104 calls omitting new fields still succeed
- No live-provider dependency throughout

All tests that hit the DB require the gp_pms_test Postgres database.
Pure-logic tests (freshness id, staleness verdict) run without any DB.
"""

from copy import deepcopy
from datetime import date, datetime, time, timezone
from typing import Any

import pytest

from app.schemas.appointments import (
    BernieTurnRef,
    BernieTurnEventKind,
    BernieNoSlotSuggestionSelectionIn,
    BernieSupervisedBookingIn,
    BernieCreateProposalConfirmationIn,
    SlotSelectionProposalOut,
    SlotCandidate,
    AppointmentCreateProposalOut,
    AppointmentCreateCommand,
    AppointmentProposalIssue,
    BernieSlotSuggestion,
    SlotSearchCommandIn,
)
from app.services.bernie_turn_evidence import (
    StalenessVerdict,
    check_staleness,
    compute_candidate_freshness_id,
    compute_proposal_freshness_id,
    mint_session_id,
    mint_turn_id,
)
import app.services.ai.service as ai_service
from tests.conftest import make_token


# ── Fixtures ───────────────────────────────────────────────────────────────────

CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm-bernie"
SUPERVISED_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"
NO_SLOT_URL = "/api/v1/appointments/proposals/bernie/no-slot-suggestion-selection"
REFERENCE_DATE = date(2026, 7, 15)
REFERENCE_DATE_STR = "2026-07-15"


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _row_counts(db):
    from app.models.appointments import Appointment, AppointmentAuditLog
    return (db.query(Appointment).count(), db.query(AppointmentAuditLog).count())


def _minimal_turn_ref(session_id: str = "s1", turn_index: int = 0) -> BernieTurnRef:
    return BernieTurnRef(
        session_id=session_id,
        turn_id=f"{session_id}-t{turn_index}",
        turn_index=turn_index,
        event_kind="confirmation",
        reference_date=REFERENCE_DATE,
    )


def _minimal_slot_candidate(
    appointment_date=REFERENCE_DATE,
    start_time: datetime = None,
    start_time_local: time = time(15, 15),
    duration_minutes: int = 15,
    freshness_id: str = None,
) -> SlotCandidate:
    if start_time is None:
        start_time = datetime(2026, 7, 15, 5, 15, tzinfo=timezone.utc)
    end_time = datetime(2026, 7, 15, 5, 30, tzinfo=timezone.utc)
    return SlotCandidate(
        appointment_date=appointment_date,
        start_time=start_time,
        end_time=end_time,
        start_time_local=start_time_local,
        duration_minutes=duration_minutes,
        warnings=[],
        candidate_freshness_id=freshness_id,
    )


def _minimal_create_command(practitioner_id, patient_id=None) -> AppointmentCreateCommand:
    import uuid
    return AppointmentCreateCommand(
        patient_id=patient_id,
        patient_name_provisional="Margaret Thompson" if patient_id is None else None,
        practitioner_id=practitioner_id,
        appointment_date=REFERENCE_DATE,
        start_time_local=time(15, 15),
        start_time=datetime(2026, 7, 15, 5, 15, tzinfo=timezone.utc),
        duration_minutes=15,
        reason="Follow-up",
    )


def _minimal_selection_proposal(
    practitioner_id,
    patient_id=None,
    candidate_freshness_id=None,
    proposal_freshness_id=None,
) -> SlotSelectionProposalOut:
    candidate = _minimal_slot_candidate(freshness_id=candidate_freshness_id)
    cmd = _minimal_create_command(practitioner_id, patient_id)
    create_proposal = AppointmentCreateProposalOut(
        safe=True,
        requires_confirmation=True,
        autonomy_tier="proposal",
        summary="Ready.",
        command=cmd,
        warnings=[],
        blocks=[],
        patient_identity="provisional" if patient_id is None else "linked",
    )
    return SlotSelectionProposalOut(
        safe=True,
        requires_confirmation=True,
        autonomy_tier="proposal",
        summary="Prepared.",
        selected_candidate=candidate,
        create_proposal=create_proposal,
        warnings=[],
        blocks=[],
        proposal_freshness_id=proposal_freshness_id,
    )


# ── Pure-logic tests (no DB, no live provider) ─────────────────────────────────

class TestBernieTurnRef:
    def test_valid_turn_ref_accepted(self):
        ref = BernieTurnRef(
            session_id="bernie-session-abc123",
            turn_id="bernie-session-abc123-t0",
            turn_index=0,
            event_kind="staff_instruction",
            reference_date=REFERENCE_DATE,
        )
        assert ref.session_id == "bernie-session-abc123"
        assert ref.turn_index == 0
        assert ref.event_kind == "staff_instruction"

    def test_all_event_kinds_are_valid(self):
        kinds: list[BernieTurnEventKind] = [
            "staff_instruction",
            "bernie_clarification",
            "no_slot_suggestion_selection",
            "candidate_selection",
            "proposal_preview",
            "confirmation",
        ]
        for kind in kinds:
            ref = BernieTurnRef(
                session_id="s",
                turn_id="s-t0",
                turn_index=0,
                event_kind=kind,
                reference_date=REFERENCE_DATE,
            )
            assert ref.event_kind == kind

    def test_negative_turn_index_rejected(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            BernieTurnRef(
                session_id="s",
                turn_id="s-t-1",
                turn_index=-1,
                event_kind="staff_instruction",
                reference_date=REFERENCE_DATE,
            )

    def test_unknown_event_kind_rejected(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            BernieTurnRef(
                session_id="s",
                turn_id="s-t0",
                turn_index=0,
                event_kind="unknown_kind",  # type: ignore[arg-type]
                reference_date=REFERENCE_DATE,
            )


class TestCandidateFreshnessId:
    import uuid as _uuid
    _PID = _uuid.UUID("12345678-1234-5678-1234-567812345678")

    def test_deterministic_across_calls(self):
        import uuid
        pid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        dt = datetime(2026, 7, 15, 5, 15, tzinfo=timezone.utc)
        end = datetime(2026, 7, 15, 5, 30, tzinfo=timezone.utc)
        args = (REFERENCE_DATE, dt, end, time(15, 15), 15, pid, REFERENCE_DATE)
        fid1 = compute_candidate_freshness_id(*args)
        fid2 = compute_candidate_freshness_id(*args)
        assert fid1 == fid2

    def test_changes_on_different_appointment_date(self):
        import uuid
        pid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        dt = datetime(2026, 7, 15, 5, 15, tzinfo=timezone.utc)
        end = datetime(2026, 7, 15, 5, 30, tzinfo=timezone.utc)
        fid_a = compute_candidate_freshness_id(REFERENCE_DATE, dt, end, time(15, 15), 15, pid, REFERENCE_DATE)
        fid_b = compute_candidate_freshness_id(date(2026, 7, 16), dt, end, time(15, 15), 15, pid, REFERENCE_DATE)
        assert fid_a != fid_b

    def test_changes_on_different_practitioner(self):
        import uuid
        pid_a = uuid.UUID("12345678-1234-5678-1234-567812345678")
        pid_b = uuid.UUID("87654321-4321-8765-4321-876543218765")
        dt = datetime(2026, 7, 15, 5, 15, tzinfo=timezone.utc)
        end = datetime(2026, 7, 15, 5, 30, tzinfo=timezone.utc)
        fid_a = compute_candidate_freshness_id(REFERENCE_DATE, dt, end, time(15, 15), 15, pid_a, REFERENCE_DATE)
        fid_b = compute_candidate_freshness_id(REFERENCE_DATE, dt, end, time(15, 15), 15, pid_b, REFERENCE_DATE)
        assert fid_a != fid_b

    def test_changes_on_different_reference_date(self):
        """Cross-session: same slot with a different reference_date yields different freshness id."""
        import uuid
        pid = uuid.UUID("12345678-1234-5678-1234-567812345678")
        dt = datetime(2026, 7, 15, 5, 15, tzinfo=timezone.utc)
        end = datetime(2026, 7, 15, 5, 30, tzinfo=timezone.utc)
        fid_a = compute_candidate_freshness_id(REFERENCE_DATE, dt, end, time(15, 15), 15, pid, REFERENCE_DATE)
        fid_b = compute_candidate_freshness_id(REFERENCE_DATE, dt, end, time(15, 15), 15, pid, date(2026, 7, 14))
        assert fid_a != fid_b

    def test_none_practitioner_id_is_stable(self):
        dt = datetime(2026, 7, 15, 5, 15, tzinfo=timezone.utc)
        end = datetime(2026, 7, 15, 5, 30, tzinfo=timezone.utc)
        fid1 = compute_candidate_freshness_id(REFERENCE_DATE, dt, end, time(15, 15), 15, None, REFERENCE_DATE)
        fid2 = compute_candidate_freshness_id(REFERENCE_DATE, dt, end, time(15, 15), 15, None, REFERENCE_DATE)
        assert fid1 == fid2

    def test_id_is_hex_string(self):
        dt = datetime(2026, 7, 15, 5, 15, tzinfo=timezone.utc)
        end = datetime(2026, 7, 15, 5, 30, tzinfo=timezone.utc)
        fid = compute_candidate_freshness_id(REFERENCE_DATE, dt, end, time(15, 15), 15, None, REFERENCE_DATE)
        assert isinstance(fid, str)
        int(fid, 16)  # must be valid hex


class TestStalenessGate:
    def _some_fid(self) -> str:
        dt = datetime(2026, 7, 15, 5, 15, tzinfo=timezone.utc)
        end = datetime(2026, 7, 15, 5, 30, tzinfo=timezone.utc)
        return compute_candidate_freshness_id(REFERENCE_DATE, dt, end, time(15, 15), 15, None, REFERENCE_DATE)

    def test_matching_ids_are_fresh(self):
        fid = self._some_fid()
        result = check_staleness(fid, fid, REFERENCE_DATE, REFERENCE_DATE)
        assert result.verdict == StalenessVerdict.fresh

    def test_mismatched_freshness_id_is_stale(self):
        fid = self._some_fid()
        result = check_staleness("wrong_id", fid, REFERENCE_DATE, REFERENCE_DATE)
        assert result.verdict == StalenessVerdict.stale

    def test_mismatched_reference_date_is_blocked(self):
        fid = self._some_fid()
        result = check_staleness(fid, fid, date(2026, 7, 14), REFERENCE_DATE)
        assert result.verdict == StalenessVerdict.mismatched_reference_date

    def test_none_freshness_id_is_tolerated_as_fresh(self):
        """Backward compat: Sprint 104 clients omitting freshness ids are treated as fresh."""
        fid = self._some_fid()
        result = check_staleness(None, fid, REFERENCE_DATE, REFERENCE_DATE)
        assert result.verdict == StalenessVerdict.fresh

    def test_reference_date_mismatch_takes_priority_over_id_mismatch(self):
        fid = self._some_fid()
        result = check_staleness("wrong_id", fid, date(2026, 7, 14), REFERENCE_DATE)
        assert result.verdict == StalenessVerdict.mismatched_reference_date


class TestMintHelpers:
    def test_mint_session_id_is_unique(self):
        ids = {mint_session_id() for _ in range(20)}
        assert len(ids) == 20

    def test_mint_turn_id_is_deterministic_for_same_inputs(self):
        assert mint_turn_id("s1", 0) == mint_turn_id("s1", 0)

    def test_mint_turn_id_increments(self):
        t0 = mint_turn_id("s1", 0)
        t1 = mint_turn_id("s1", 1)
        assert t0 != t1

    def test_session_id_format(self):
        sid = mint_session_id()
        assert sid.startswith("bernie-session-")


# ── Schema backward-compat: new optional fields don't break Sprint 104 payloads ─

class TestBackwardCompatSchema:
    def test_slot_candidate_without_freshness_id(self):
        c = SlotCandidate(
            appointment_date=REFERENCE_DATE,
            start_time=datetime(2026, 7, 15, 5, 15, tzinfo=timezone.utc),
            end_time=datetime(2026, 7, 15, 5, 30, tzinfo=timezone.utc),
            start_time_local=time(15, 15),
            duration_minutes=15,
        )
        assert c.candidate_freshness_id is None

    def test_selection_proposal_without_turn_ref(self):
        import uuid
        cmd = AppointmentCreateCommand(
            patient_name_provisional="Test",
            practitioner_id=uuid.uuid4(),
            appointment_date=REFERENCE_DATE,
            start_time_local=time(9, 0),
            start_time=datetime(2026, 7, 15, 0, 0, tzinfo=timezone.utc),
            duration_minutes=15,
        )
        sel = SlotSelectionProposalOut(
            safe=True,
            requires_confirmation=True,
            autonomy_tier="proposal",
            summary="ok",
            create_proposal=AppointmentCreateProposalOut(
                safe=True,
                requires_confirmation=True,
                autonomy_tier="proposal",
                summary="ok",
                command=cmd,
                patient_identity="provisional",
            ),
        )
        assert sel.turn_ref is None
        assert sel.proposal_freshness_id is None

    def test_confirmation_in_without_freshness_fields(self):
        import uuid
        cmd = AppointmentCreateCommand(
            patient_name_provisional="Test",
            practitioner_id=uuid.uuid4(),
            appointment_date=REFERENCE_DATE,
            start_time_local=time(9, 0),
            start_time=datetime(2026, 7, 15, 0, 0, tzinfo=timezone.utc),
            duration_minutes=15,
        )
        sel = SlotSelectionProposalOut(
            safe=True,
            requires_confirmation=True,
            autonomy_tier="proposal",
            summary="ok",
            create_proposal=AppointmentCreateProposalOut(
                safe=True,
                requires_confirmation=True,
                autonomy_tier="proposal",
                summary="ok",
                command=cmd,
                patient_identity="provisional",
            ),
        )
        conf = BernieCreateProposalConfirmationIn(
            confirmed=True,
            selection_proposal=sel,
        )
        assert conf.turn_ref is None
        assert conf.candidate_freshness_id is None
        assert conf.proposal_freshness_id is None

    def test_supervised_booking_in_without_turn_ref(self):
        body = BernieSupervisedBookingIn(
            command=SlotSearchCommandIn(
                practitioner_id="12345678-1234-5678-1234-567812345678",
                date_from="2026-07-15",
                duration_minutes="15",
            ),
            reference_date=REFERENCE_DATE,
        )
        assert body.turn_ref is None


# ── No-slot suggestion selection event ────────────────────────────────────────

class TestNoSlotSuggestionSelection:
    def test_typed_event_carries_originating_turn_id(self):
        """BernieNoSlotSuggestionSelectionIn must carry turn_ref from the prior turn."""
        import uuid
        orig_turn = _minimal_turn_ref("bernie-session-abc", turn_index=1)
        orig_turn = orig_turn.model_copy(update={"event_kind": "candidate_selection"})
        suggestion = BernieSlotSuggestion(
            kind="next_available_day",
            summary="Search the next day.",
            params={"date_from": "2026-07-16"},
            requires_confirmation=True,
        )
        orig_request = BernieSupervisedBookingIn(
            command=SlotSearchCommandIn(
                practitioner_id=str(uuid.uuid4()),
                date_from="2026-07-15",
            ),
            reference_date=REFERENCE_DATE,
            turn_ref=orig_turn,
        )
        event = BernieNoSlotSuggestionSelectionIn(
            turn_ref=orig_turn,
            suggestion=suggestion,
            original_request=orig_request,
        )
        assert event.turn_ref.turn_id == orig_turn.turn_id
        assert event.turn_ref.session_id == orig_turn.session_id
        assert event.suggestion.kind == "next_available_day"

    def test_no_slot_suggestion_selection_endpoint(self, client, receptionist_user):
        """POST /proposals/bernie/no-slot-suggestion-selection returns next_request."""
        import uuid
        from tests.conftest import make_token
        token = make_token(receptionist_user)
        session_id = "bernie-session-test"
        orig_turn = BernieTurnRef(
            session_id=session_id,
            turn_id=f"{session_id}-t1",
            turn_index=1,
            event_kind="candidate_selection",
            reference_date=REFERENCE_DATE,
        )
        prac_id = str(uuid.uuid4())
        payload = {
            "turn_ref": orig_turn.model_dump(mode="json"),
            "suggestion": {
                "kind": "next_available_day",
                "summary": "Try next day.",
                "params": {"date_from": "2026-07-16"},
                "requires_confirmation": True,
            },
            "original_request": {
                "command": {
                    "practitioner_id": prac_id,
                    "date_from": "2026-07-15",
                },
                "reference_date": "2026-07-15",
            },
        }
        resp = client.post(NO_SLOT_URL, json=payload, headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "no_slot_suggestion_selection"
        assert data["accepted"] is True
        assert data["turn_ref"]["session_id"] == session_id
        # turn_index incremented
        assert data["turn_ref"]["turn_index"] == 2
        assert data["turn_ref"]["event_kind"] == "no_slot_suggestion_selection"
        assert data["next_request"] is not None


# ── Confirm staleness gate (integration, no DB mutation on block) ─────────────

class TestConfirmStalenessGate:
    """Staleness gate blocks confirmation without touching the DB."""

    def _assert_no_db_mutation(self, db, before_counts):
        from app.models.appointments import Appointment, AppointmentAuditLog
        after = (db.query(Appointment).count(), db.query(AppointmentAuditLog).count())
        assert after == before_counts, (
            f"DB mutated despite staleness block: before={before_counts} after={after}"
        )

    def _install_no_ai_guard(self, monkeypatch):
        def forbidden(*a, **kw):
            raise AssertionError("AI provider must not be called in confirmation path")
        monkeypatch.setattr(ai_service, "_get_default_provider", forbidden)

    def test_stale_candidate_freshness_id_blocks_no_mutation(
        self, client, db, receptionist_user, practitioner, monkeypatch
    ):
        self._install_no_ai_guard(monkeypatch)
        from tests.conftest import make_token
        token = make_token(receptionist_user)
        before = _row_counts(db)

        selection = _minimal_selection_proposal(
            practitioner_id=practitioner.id,
            candidate_freshness_id="correct_candidate_fid",
            proposal_freshness_id=None,
        )
        payload = {
            "confirmed": True,
            "selection_proposal": selection.model_dump(mode="json"),
            "candidate_freshness_id": "wrong_stale_candidate_fid",  # mismatch → stale
            "turn_ref": _minimal_turn_ref().model_dump(mode="json"),
        }
        resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["autonomy_tier"] == "blocked"
        assert any("freshness" in b["message"].lower() or "stale" in b["code"] for b in data["blocks"])
        self._assert_no_db_mutation(db, before)

    def test_stale_proposal_freshness_id_blocks_no_mutation(
        self, client, db, receptionist_user, practitioner, monkeypatch
    ):
        self._install_no_ai_guard(monkeypatch)
        from tests.conftest import make_token
        token = make_token(receptionist_user)
        before = _row_counts(db)

        selection = _minimal_selection_proposal(
            practitioner_id=practitioner.id,
            proposal_freshness_id="correct_proposal_fid",
        )
        payload = {
            "confirmed": True,
            "selection_proposal": selection.model_dump(mode="json"),
            "proposal_freshness_id": "wrong_stale_proposal_fid",  # mismatch → stale
            "turn_ref": _minimal_turn_ref().model_dump(mode="json"),
        }
        resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["autonomy_tier"] == "blocked"
        assert any("freshness" in b["message"].lower() or "stale" in b["code"] for b in data["blocks"])
        self._assert_no_db_mutation(db, before)

    def test_cross_session_freshness_id_blocks_no_mutation(
        self, client, db, receptionist_user, practitioner, monkeypatch
    ):
        """A freshness id issued in a prior session (different reference_date) must block.

        Scenario: server issued candidate_freshness_id for session with reference_date=2026-07-14.
        Client now confirms with turn_ref.reference_date=2026-07-15 (today's session).
        Server recomputes expected freshness id with reference_date=2026-07-15 → mismatch → stale.
        No DB mutation must occur.
        """
        self._install_no_ai_guard(monkeypatch)
        from tests.conftest import make_token
        token = make_token(receptionist_user)
        before = _row_counts(db)

        selection = _minimal_selection_proposal(practitioner_id=practitioner.id)
        # Freshness id from a prior session with reference_date=2026-07-14.
        dt = datetime(2026, 7, 15, 5, 15, tzinfo=timezone.utc)
        end = datetime(2026, 7, 15, 5, 30, tzinfo=timezone.utc)
        prior_session_fid = compute_candidate_freshness_id(
            REFERENCE_DATE, dt, end, time(15, 15), 15, practitioner.id, date(2026, 7, 14)
        )
        # Current session has reference_date=2026-07-15 (different from prior session).
        current_turn_ref = BernieTurnRef(
            session_id="s-new",
            turn_id="s-new-t1",
            turn_index=1,
            event_kind="confirmation",
            reference_date=REFERENCE_DATE,  # 2026-07-15 — today's session
        )

        payload = {
            "confirmed": True,
            "selection_proposal": selection.model_dump(mode="json"),
            "candidate_freshness_id": prior_session_fid,  # from prior session (2026-07-14)
            "turn_ref": current_turn_ref.model_dump(mode="json"),
        }
        resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["autonomy_tier"] == "blocked"
        # Should block as stale (freshness id mismatch due to different reference_date encoding).
        stale_codes = [b["code"] for b in data["blocks"] if "stale" in b["code"] or "freshness" in b["message"].lower()]
        assert stale_codes, f"Expected stale block, got: {[b['code'] for b in data['blocks']]}"
        self._assert_no_db_mutation(db, before)

    def test_sprint104_client_without_freshness_ids_still_succeeds(
        self, client, db, receptionist_user, practitioner, patient, monkeypatch
    ):
        """Backward compat: omitting freshness ids (Sprint 104 call) must not be blocked."""
        self._install_no_ai_guard(monkeypatch)
        from tests.conftest import make_token
        from app.models.appointments import AppointmentStatus, BookingChannel
        import app.services.bernie_slot_normalizer as norm_mod
        import app.routers.appointments as appts

        token = make_token(receptionist_user)

        # Build a proposal where the command references a practitioner that exists in DB.
        cmd = _minimal_create_command(practitioner.id, patient.id)
        create_proposal = AppointmentCreateProposalOut(
            safe=True,
            requires_confirmation=True,
            autonomy_tier="proposal",
            summary="Ready.",
            command=cmd,
            warnings=[],
            blocks=[],
            patient_identity="linked",
        )
        candidate = _minimal_slot_candidate()
        selection = SlotSelectionProposalOut(
            safe=True,
            requires_confirmation=True,
            autonomy_tier="proposal",
            summary="ok",
            selected_candidate=candidate,
            create_proposal=create_proposal,
            # No freshness ids (Sprint 104 style)
        )
        payload = {
            "confirmed": True,
            "selection_proposal": selection.model_dump(mode="json"),
            # No candidate_freshness_id, no proposal_freshness_id, no turn_ref
        }
        resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))
        # Should reach the entity-check / revalidation stage (not blocked by staleness gate).
        # May be blocked by entity checks (practitioner schedule, conflicts, etc.) but NOT
        # by the staleness gate — there should be no stale_* block code.
        data = resp.json()
        stale_codes = [b["code"] for b in data.get("blocks", []) if "stale" in b["code"]]
        assert not stale_codes, f"Staleness gate fired on Sprint 104 payload: {stale_codes}"

    def test_unconfirmed_request_still_blocked(
        self, client, db, receptionist_user, practitioner, monkeypatch
    ):
        """The explicit-confirmation gate must still fire when confirmed=False."""
        self._install_no_ai_guard(monkeypatch)
        from tests.conftest import make_token
        token = make_token(receptionist_user)
        before = _row_counts(db)

        selection = _minimal_selection_proposal(practitioner_id=practitioner.id)
        payload = {
            "confirmed": False,  # not confirmed
            "selection_proposal": selection.model_dump(mode="json"),
        }
        resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["autonomy_tier"] == "blocked"
        assert any(b["code"] == "explicit_confirmation_required" for b in data["blocks"])
        self._assert_no_db_mutation(db, before)


# ── Turn minting in supervised-booking response ────────────────────────────────

class TestSupervisedBookingTurnMinting:
    """Supervised-booking endpoint mints turn_ref on responses."""

    def test_supervised_booking_response_has_turn_ref_when_candidates_available(
        self, client, db, receptionist_user, practitioner, patient, schedule
    ):
        from tests.conftest import make_token
        token = make_token(receptionist_user)
        payload = {
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": REFERENCE_DATE_STR,
                "duration_minutes": "15",
                "patient_id": str(patient.id),
            },
            "reference_date": REFERENCE_DATE_STR,
        }
        resp = client.post(SUPERVISED_URL, json=payload, headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()
        # turn_ref must be present regardless of result
        assert data.get("turn_ref") is not None
        tr = data["turn_ref"]
        assert tr["session_id"].startswith("bernie-session-")
        assert tr["turn_index"] == 0  # first turn (no incoming turn_ref)
        # reference_date must be echoed immutably
        assert data.get("request_reference_date") == REFERENCE_DATE_STR

    def test_supervised_booking_continues_session_from_incoming_turn_ref(
        self, client, db, receptionist_user, practitioner, patient, schedule
    ):
        from tests.conftest import make_token
        token = make_token(receptionist_user)
        existing_session_id = "bernie-session-existing"
        payload = {
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": REFERENCE_DATE_STR,
                "duration_minutes": "15",
                "patient_id": str(patient.id),
            },
            "reference_date": REFERENCE_DATE_STR,
            "turn_ref": {
                "session_id": existing_session_id,
                "turn_id": f"{existing_session_id}-t0",
                "turn_index": 0,
                "event_kind": "staff_instruction",
                "reference_date": REFERENCE_DATE_STR,
            },
        }
        resp = client.post(SUPERVISED_URL, json=payload, headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("turn_ref") is not None
        tr = data["turn_ref"]
        # session_id preserved
        assert tr["session_id"] == existing_session_id
        # turn_index incremented
        assert tr["turn_index"] == 1

    def test_candidates_have_freshness_ids_stamped(
        self, client, db, receptionist_user, practitioner, patient, schedule
    ):
        from tests.conftest import make_token
        token = make_token(receptionist_user)
        payload = {
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": REFERENCE_DATE_STR,
                "duration_minutes": "15",
                "patient_id": str(patient.id),
            },
            "reference_date": REFERENCE_DATE_STR,
        }
        resp = client.post(SUPERVISED_URL, json=payload, headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()
        search_prop = data.get("search_proposal")
        if search_prop and search_prop.get("candidates"):
            for candidate in search_prop["candidates"]:
                assert candidate.get("candidate_freshness_id") is not None, (
                    "Each candidate must have candidate_freshness_id stamped"
                )

    def test_reference_date_immutable_in_response(
        self, client, db, receptionist_user, practitioner, patient, schedule
    ):
        """request_reference_date must echo the intake date unchanged."""
        from tests.conftest import make_token
        token = make_token(receptionist_user)
        payload = {
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": REFERENCE_DATE_STR,
                "duration_minutes": "15",
                "patient_id": str(patient.id),
            },
            "reference_date": REFERENCE_DATE_STR,
        }
        resp = client.post(SUPERVISED_URL, json=payload, headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["request_reference_date"] == REFERENCE_DATE_STR
