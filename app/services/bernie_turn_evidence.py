"""Deterministic evidence helper for Bernie typed turn contract.

Computes PHI-safe freshness ids/hashes for slot candidates and create proposals,
and provides a staleness verdict gate used by the confirm-bernie endpoint.

Design constraints:
- Deterministic across process restarts: no wall-clock, no random, no DB reads.
- PHI-safe: hashes normalized slot coordinates and UUIDs only, never raw patient text.
- All inputs normalised before hashing to prevent format-variance collisions.
- The resulting id is a hex digest; length chosen to be collision-resistant for
  practice-scale session counts (not cryptographic; not used for auth).
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import date, datetime, time
from enum import Enum
from typing import Optional


class StalenessVerdict(str, Enum):
    fresh = "fresh"
    stale = "stale"                        # freshness id mismatch (older/different turn)
    mismatched_reference_date = "mismatched_reference_date"  # date differs from session


@dataclass(frozen=True)
class StalenessResult:
    verdict: StalenessVerdict
    detail: str


def _h(*parts: str) -> str:
    """Deterministic short hex digest over ordered normalized parts."""
    payload = "\x00".join(parts)
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def _norm_date(d: date) -> str:
    return d.isoformat()


def _norm_time(t: time) -> str:
    return t.strftime("%H:%M")


def _norm_dt(dt: datetime) -> str:
    # Normalise to UTC ISO without microseconds to avoid tz-aware/naive variance.
    if dt.tzinfo is not None:
        import calendar
        epoch = calendar.timegm(dt.utctimetuple())
    else:
        import calendar
        epoch = calendar.timegm(dt.timetuple())
    return str(epoch)


def _norm_uuid(u: Optional[uuid.UUID]) -> str:
    return str(u) if u is not None else ""


def compute_candidate_freshness_id(
    appointment_date: date,
    start_time: datetime,
    end_time: datetime,
    start_time_local: time,
    duration_minutes: int,
    practitioner_id: Optional[uuid.UUID],
    reference_date: date,
) -> str:
    """Compute a deterministic freshness id for a slot candidate.

    Inputs are normalised slot coordinates only — no patient text, no wall-clock.
    The reference_date is included so a candidate from a prior session (with a
    different reference_date) yields a different id.
    """
    return _h(
        "candidate_v1",
        _norm_date(appointment_date),
        _norm_dt(start_time),
        _norm_dt(end_time),
        _norm_time(start_time_local),
        str(duration_minutes),
        _norm_uuid(practitioner_id),
        _norm_date(reference_date),
    )


def compute_proposal_freshness_id(
    appointment_date: date,
    start_time: datetime,
    start_time_local: time,
    duration_minutes: int,
    practitioner_id: Optional[uuid.UUID],
    patient_id: Optional[uuid.UUID],
    appointment_type_id: Optional[uuid.UUID],
    location_id: Optional[uuid.UUID],
    reference_date: date,
) -> str:
    """Compute a deterministic freshness id for a create proposal command.

    Captures the typed slot + identity coordinates; hashing patient_id (UUID)
    is PHI-safe.  Raw patient name text is excluded — the UUID is sufficient.
    reference_date is included so proposals from prior sessions yield different ids.
    """
    return _h(
        "proposal_v1",
        _norm_date(appointment_date),
        _norm_dt(start_time),
        _norm_time(start_time_local),
        str(duration_minutes),
        _norm_uuid(practitioner_id),
        _norm_uuid(patient_id),
        _norm_uuid(appointment_type_id),
        _norm_uuid(location_id),
        _norm_date(reference_date),
    )


def check_staleness(
    submitted_freshness_id: Optional[str],
    expected_freshness_id: str,
    submitted_reference_date: Optional[date],
    session_reference_date: date,
) -> StalenessResult:
    """Gate a confirmation by comparing echoed freshness id against expected.

    Rules (fail-closed):
    1. If reference_date differs → mismatched_reference_date (blocks, reason shown).
    2. If submitted_freshness_id mismatches expected → stale.
    3. Both match → fresh.

    submitted_freshness_id=None means the client did not echo a freshness id.
    That is treated as fresh (backward-compat with Sprint 104 clients that
    predate this contract).  The staleness gate only fires when the client
    explicitly echoes a freshness id.
    """
    if submitted_reference_date is not None and submitted_reference_date != session_reference_date:
        return StalenessResult(
            verdict=StalenessVerdict.mismatched_reference_date,
            detail=(
                f"Confirmation reference_date {submitted_reference_date} does not match "
                f"session reference_date {session_reference_date}."
            ),
        )
    if submitted_freshness_id is not None and submitted_freshness_id != expected_freshness_id:
        return StalenessResult(
            verdict=StalenessVerdict.stale,
            detail="Candidate or proposal freshness id does not match the current session evidence.",
        )
    return StalenessResult(verdict=StalenessVerdict.fresh, detail="")


def mint_session_id() -> str:
    return f"bernie-session-{uuid.uuid4().hex[:12]}"


def mint_turn_id(session_id: str, turn_index: int) -> str:
    return f"{session_id}-t{turn_index}"
