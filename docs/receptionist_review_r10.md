# Sprint R10 — Reason-Code Governance Policy

Sprint R10 defines the governance contract for appointment cancellation and
status-change reason codes. It does not change temporal slot-write policy:
retrospective cancellation/status actions remain administrative writes, but they
need clearer reason capture, safer audit semantics, and receptionist-friendly
copy before a schema migration is introduced.

## Policy Objectives

- Standardise administrative cancellation/status reasons without replacing
  free-text context.
- Preserve the R8/R9 boundary that status and delete writes are not slot writes.
- Keep audit entries useful for clinic operations, reporting, and governance.
- Avoid capturing clinical details in administrative reason fields.
- Defer irreversible migration choices until receptionist workflow feedback has
  validated the taxonomy.

## Proposed Taxonomy

| Group | Code | Staff label | Intended use |
|---|---|---|---|
| Patient initiated | `PATIENT_CANCELLED` | Patient requested cancellation | General patient cancellation. |
| Patient initiated | `PATIENT_RESCHEDULED` | Patient requested reschedule | Appointment moved at patient request. |
| Patient initiated | `PATIENT_UNWELL` | Patient unwell | Short-notice illness cancellation without clinical detail. |
| Patient initiated | `PATIENT_TRANSPORT` | Transport or access issue | Travel, traffic, mobility, or access issue. |
| Clinic initiated | `PRACTITIONER_UNAVAILABLE` | Practitioner unavailable | Doctor/nurse unavailable, emergency, leave, or illness. |
| Clinic initiated | `CLINIC_OPERATIONAL` | Clinic operational issue | Room, equipment, power, IT, or opening-hours disruption. |
| Clinic initiated | `CLINIC_RESCHEDULED` | Clinic requested reschedule | Clinic-initiated move not caused by a patient request. |
| Administrative | `ADMIN_ERROR` | Administrative correction | Wrong slot, typo, test data, or mistaken booking. |
| Administrative | `DUPLICATE_BOOKING` | Duplicate booking | Removal of accidental duplicate appointment. |
| Attendance | `DID_NOT_ATTEND` | Did not attend | Patient did not present for the appointment. |
| Attendance | `LEFT_WITHOUT_SEEN` | Left before being seen | Patient arrived but left before consultation. |
| Fallback | `OTHER` | Other reason | Rare case that needs optional free-text context. |
| Fallback | `LEGACY_UNCLASSIFIED` | Legacy unclassified | Imported or old data that cannot be safely mapped. |

The taxonomy should start as an application-level allow-list, not a database
constraint. That keeps the first implementation reversible while real
receptionist feedback proves whether the list fits the clinic.

## Staff-Facing Copy

Cancellation confirmation:

> Confirm cancellation. Choose the main reason for this cancellation. This does
> not reopen or rewrite diary availability, but it will record a permanent audit
> entry.

Retrospective status update:

> Retrospective status change. You are updating an appointment whose time has
> already passed. This is allowed for diary housekeeping, but the reason and
> audit evidence will be recorded.

Free-text helper:

> Optional note for administrative context only. Do not enter diagnoses,
> symptoms, or other clinical details here.

Suggested control behaviour:

- Make the reason code mandatory for cancellation, NoShow, DNA, and other
  terminal status transitions once all first-party UI entry points support it.
- Keep free text optional, capped, and explicitly non-clinical.
- Use `OTHER` sparingly and require a short note when selected.
- Use `LEGACY_UNCLASSIFIED` only for imported or compatibility-path data.

## Audit Expectations

Every audited cancellation/status mutation should record:

- actor identity, role, practice, and timestamp
- action type and previous/new status
- reason code, if supplied or inferred
- free-text cancellation reason, if supplied
- source route or proposal-confirm provenance
- signed confirmation/freshness evidence where applicable

Reason codes answer why the appointment changed. Existing
`confirmed_warnings` codes answer how the mutation was authorised. They should
remain separate fields.

## Coded Versus Free Text

Use coded reasons for reporting and governance:

- cancellation-rate analysis
- DNA/no-show monitoring
- practitioner unavailability trends
- admin-error cleanup tracking
- audit filtering and retrospective review

Use free text only for short administrative detail that does not belong in the
clinical record. If a note would disclose a diagnosis, sensitive condition, or
clinical judgement, it should not be placed in appointment cancellation reason
text.

## Migration Risks

- Existing `cancellation_reason` values are unconstrained free text and may
  contain spelling variants, ambiguous statements, or sensitive content.
- Status mutation routes currently do not accept a cancellation/status reason.
- Making a new reason-code column non-null immediately would break legacy API
  and worker paths.
- Heuristic backfills can misclassify old text.

Mitigation:

1. Add an optional code field first and validate through a shared helper.
2. Preserve `cancellation_reason` as optional free text.
3. Leave old rows nullable; do not bulk-infer codes as trusted facts.
4. Use `LEGACY_UNCLASSIFIED` when historical text cannot be mapped safely.
5. Tighten UI-level requirements only after all first-party mutation paths can
   supply a code.

## Recommended Implementation Sequence

1. Add an application-level reason-code allow-list and shared validator.
2. Extend delete/status proposal schemas with optional `status_reason_code`.
3. Persist the code to appointment and audit-log records.
4. Add tests for valid code persistence, invalid-code rejection, nullable legacy
   compatibility, and audit exposure.
5. Add taskpane dropdowns and non-clinical helper copy.
6. Review receptionist usage before deciding on enum/reference-table migration.

No part of this sequence should alter past-date or same-day elapsed slot-write
guards.
