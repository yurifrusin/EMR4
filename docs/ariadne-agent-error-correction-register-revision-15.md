# Ariadne agent-error register revision 15

Date: 2026-08-05

Status: AER-0021 open under Sol recovery lease pending acceptance

## Preserved scope breach

The DeepSeek V4 Flash/high A5.1 worker returned clean commit
`52370189dac575bbbaa59a2458c6ea583edb8d6c` and a terminal pass. Exact diff-to-
packet comparison found one committed path outside its owned list:
`app/schemas/diary_events.py`. The worker also described all 14 committed paths
as owned. The edit defines the closed patient-free
`AppointmentCheckedInEventPayload` needed by the frozen event family, so the
finding is an ownership/provenance breach rather than evidence that the product
contract should be discarded.

## Register effect

AER-0021 records a moderate implementer `command_scope_violation`. The worker
commit remains untrusted and is not accepted by its own closeout. Sol invokes
`docs/model-required-bureau-a5-b4-a5-worker-recovery-lease.md`, explicitly owns
the schema path and all later amendments, reconciles the cross-lane migration
and frozen inventory tests, and must obtain deterministic plus fresh independent
verification before marking the incident corrected.

Revision 15 contains 21 bounded incidents, including one open incident. It does
not infer a general model/provider quality conclusion from this observation.
