"""Typed dev-clinic example facts for tests and demos only.

These facts describe the fictional dev-clinic (Dr Shera's practice at
emr4dev.local). Do NOT use in production or seed real PHI. All facts
carry contains_phi=False and authority_tier=advisory.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from app.services.practice_knowledge.facts import (
    PracticeFact,
    PracticeFactKind,
    PracticeFactProvenance,
    PracticeFactSourceKind,
    ReviewStatus,
)


def _authored(source_ref: str) -> PracticeFactProvenance:
    return PracticeFactProvenance(
        source_kind=PracticeFactSourceKind.staff_authored,
        source_ref=source_ref,
        author="dr.shera@emr4dev.local",
        captured_at=datetime(2026, 7, 1, 9, 0, tzinfo=timezone.utc),
        effective_from=date(2026, 7, 1),
        last_reviewed=date(2026, 7, 1),
        review_status=ReviewStatus.current,
    )


DEV_CLINIC_FACTS: list[PracticeFact] = [
    PracticeFact(
        fact_id="roster-001",
        kind=PracticeFactKind.roster,
        subject="Dr Shera Friday availability",
        body="Dr Shera does not work Fridays. No appointments should be booked with Dr Shera on Fridays.",
        tags=["dr_shera", "friday", "unavailable"],
        provenance=_authored("roster-policy-2026"),
    ),
    PracticeFact(
        fact_id="policy-001",
        kind=PracticeFactKind.policy,
        subject="New patient appointment duration",
        body="New patient appointments are 30 minutes. Standard follow-up appointments are 15 minutes.",
        tags=["new_patient", "duration", "booking"],
        provenance=_authored("booking-policy-2026"),
    ),
    PracticeFact(
        fact_id="contact-001",
        kind=PracticeFactKind.contact,
        subject="Clinic phone number",
        body="The clinic phone number is (02) 9000 0000. Calls are answered Monday to Thursday 8:30am-5:30pm.",
        tags=["phone", "contact"],
        provenance=_authored("contact-info-2026"),
    ),
    PracticeFact(
        fact_id="opening-001",
        kind=PracticeFactKind.opening_hours,
        subject="Clinic opening hours",
        body="Open Monday to Thursday 8:30am to 5:30pm. Closed Fridays, weekends, and public holidays.",
        tags=["hours", "opening", "closed"],
        provenance=_authored("hours-policy-2026"),
    ),
    PracticeFact(
        fact_id="reception-001",
        kind=PracticeFactKind.reception_guidance,
        subject="Urgent same-day appointment guidance",
        body="For urgent same-day requests, ask the patient to call the clinic before 9am. After 9am, offer the next available slot or advise the patient to call Healthdirect 1800 022 222.",
        tags=["urgent", "same_day", "guidance"],
        provenance=_authored("reception-guidance-2026"),
    ),
    PracticeFact(
        fact_id="reception-002",
        kind=PracticeFactKind.reception_guidance,
        subject="Repeat prescription booking",
        body="Repeat prescriptions require a telehealth or in-person consultation. Script-only requests cannot be honoured without a consultation.",
        tags=["prescription", "repeat", "telehealth"],
        provenance=_authored("rx-guidance-2026"),
    ),
]


__all__ = ["DEV_CLINIC_FACTS"]
