"""Drift guard: every backend BernieBookingOutcomeKind must have frontend
BERNIE_STATUS_COPY and BERNIE_HEADLINE_COPY coverage or a deliberate exception.

This test parses the relevant frontend constants from docs/diary/diary.js so
it can catch silent key drift without launching a browser or evaluating JS.

The mapping logic replicates bernieReviewTransition() from diary.js to convert
each outcome kind to a frontend transition.state, then checks whether that state
has copy coverage via:

  - BERNIE_STATUS_COPY / BERNIE_HEADLINE_COPY dict lookups
  - Hardcoded strings in bernieStatusCopyForPayload / bernieHeadlineCopyForPayload

Design exception:
  interpreted_ready — transient "proceed" outcome that immediately advances to
  context enrichment. End users rarely see it. Falls through to auto-generated
  copy (formatBernieCode -> "Interpreted Ready" / "Review this appointment").
  Revisit this exception if a sprint adds a permanent UI path that exposes
  interpreted_ready to reception staff.
"""

from __future__ import annotations

import re
from pathlib import Path


DIARY_JS = Path("docs/diary/diary.js")


def _parse_frontend_copy_object(name: str) -> dict[str, str]:
    text = DIARY_JS.read_text(encoding="utf-8")
    match = re.search(rf"const {name}\s*=\s*\{{(?P<body>.*?)\}};", text, re.DOTALL)
    assert match, f"Could not find {name} in {DIARY_JS}"

    result: dict[str, str] = {}
    for entry in re.finditer(
        r'(?P<key>[A-Za-z0-9_]+)\s*:\s*"(?P<value>(?:[^"\\]|\\.)*)"',
        match.group("body"),
    ):
        result[entry.group("key")] = entry.group("value")
    assert result, f"Could not parse any entries from {name}"
    return result


# -- Frontend transition mapping (mirror of bernieReviewTransition diary.js:885-926) -


def _bernie_review_transition_state(outcome_kind: str, payload_status: str = "") -> str:
    """Replicate the outcome-kind branch of bernieReviewTransition().

    Returns the frontend transition.state string for a given outcome kind.
    payload_status is the fallback when outcome kind has no explicit mapping.
    """
    if outcome_kind == "roster_unavailable":
        return "roster_unavailable"
    if outcome_kind == "no_matching_times":
        return "no_slots"
    if outcome_kind == "clarification_required":
        return "clarification"
    if outcome_kind in ("guardrail_blocked", "handed_off"):
        return "blocked"
    if outcome_kind == "clinic_day_exhausted":
        return "clinic_day_exhausted"
    if outcome_kind == "confirmation_ready":
        return "confirmation_ready"
    if outcome_kind == "candidate_selection_required":
        return "candidate_selection_required"
    if outcome_kind == "advisory_warnings_present":
        return "advisory_warnings_only"
    # All other kinds (including interpreted_ready) fall through:
    return payload_status or "blocked"


# -- Hardcoded copy chains in diary.js review functions -------------------------

# From bernieStatusCopyForPayload (lines 1012-1024) and bernieHeadlineCopyForPayload
# (lines 1026-1038). These states are handled by hardcoded strings in the
# review functions, not the COPY dicts.
_HARDCODED_STATUS_COPY: dict[str, str] = {
    "roster_unavailable": "Roster/schedule unavailable",
    "no_slots": "Try another time",
    "no_selectable_candidates": "Needs review",
    "advisory_warnings_only": "Ready to book",
    "clarification": "Clarification required",
}

_HARDCODED_HEADLINE_COPY: dict[str, str] = {
    "roster_unavailable": "Roster/schedule unavailable",
    "no_slots": "No matching times found",
    "no_selectable_candidates": "I could not show a time for this request",
    "confirmation_ready": "BERNIE_HEADLINE_COPY.confirmation_ready",
    "advisory_warnings_only": "BERNIE_HEADLINE_COPY.confirmation_ready",
    "clarification": "Clarification required",
}

# States covered by a schedule explanation payload before the hardcoded chain.
# The schedule_explanation is an alternative frontend path that provides its own
# status and headline copy (see getScheduleExplanationCopy in diary.js).
# These states are still *resolved* even if the dict path is bypassed at runtime.
_SCHEDULE_EXPLANATION_COVERED: set[str] = {"roster_unavailable", "no_slots"}


# -- Frontend fallback for unrecognised states ----------------------------------

_DEFAULT_HEADLINE = "Review this appointment"


# -- Transient-exception allowlist ---------------------------------------------

_TRANSIENT_OUTCOME_EXCEPTIONS: set[str] = {
    "interpreted_ready",
    # Rationale: transient "proceed" outcome immediately advances to context
    # enrichment. End users rarely see it. Falls through to auto-generated
    # copy: formatBernieCode -> "Interpreted Ready" / "Review this appointment".
}


# -- Test -----------------------------------------------------------------------


def test_every_backend_outcome_kind_has_frontend_copy_coverage() -> None:
    """Every BernieBookingOutcomeKind must map to a frontend state that has
    defined copy -- either in the COPY dicts, in the hardcoded review-function
    chains, or explicitly excepted as a transient outcome.
    """
    # Import the backend enum
    from app.services.diary.outcomes import BernieBookingOutcomeKind

    bernie_status_copy = _parse_frontend_copy_object("BERNIE_STATUS_COPY")
    bernie_headline_copy = _parse_frontend_copy_object("BERNIE_HEADLINE_COPY")
    failures: list[str] = []

    for kind in BernieBookingOutcomeKind:
        value = kind.value
        # Determine frontend transition state
        frontend_state = _bernie_review_transition_state(value, payload_status=value)

        # Check 1: BERNIE_STATUS_COPY lookup
        status_covered = frontend_state in bernie_status_copy

        # Check 2: Hardcoded in bernieStatusCopyForPayload
        status_hardcoded = frontend_state in _HARDCODED_STATUS_COPY

        # Check 3: Schedule explanation covers this state
        status_schedule = frontend_state in _SCHEDULE_EXPLANATION_COVERED

        # Check 4: BERNIE_HEADLINE_COPY lookup
        headline_covered = frontend_state in bernie_headline_copy

        # Check 5: Hardcoded in bernieHeadlineCopyForPayload
        headline_hardcoded = frontend_state in _HARDCODED_HEADLINE_COPY

        is_covered = status_covered or status_hardcoded or status_schedule
        is_headline_covered = headline_covered or headline_hardcoded or status_schedule

        if value in _TRANSIENT_OUTCOME_EXCEPTIONS:
            continue  # Deliberate exception

        issues: list[str] = []
        if not is_covered:
            issues.append(f"no status copy for frontend state {frontend_state!r}")
        if not is_headline_covered:
            issues.append(f"no headline copy for frontend state {frontend_state!r}")
        if frontend_state == "blocked" and value not in ("guardrail_blocked", "handed_off"):
            issues.append(
                f"falls through to frontend state 'blocked' (hits else branch in "
                f"bernieReviewTransition). If {value!r} is a new kind, "
                f"add an explicit mapping."
            )

        if issues:
            failures.append(f"{value!r} (-> {frontend_state!r}): {'; '.join(issues)}")

    if failures:
        msg = "\n  ".join([f"{len(failures)} outcome kind(s) missing frontend copy coverage:"] + failures)
        raise AssertionError(msg)
