# Canonical check-in product-adapter extraction — lay and technical summary

Date: 2026-08-18

Timestamp: 2026-08-18T10:22:21+10:00 (Australia/Brisbane)

Status: accepted

Yuri attention required: start the next tranche in a fresh Codex task after
restarting the app, to clear stale task/subagent state and avoid carrying this
multi-tranche context further.

## Lay summary

Raisa now has the reusable inner mechanism for checking in an appointment. It
does considerably more than change the word on an appointment to `Arrived`.
Immediately before acting it checks that the receptionist still has authority,
that the appointment is still in the expected practice and state, that the
human-confirmed evidence is current and unused, and that any waiting area is a
valid assignment rather than a hidden move or removal.

If all of those facts agree, the appointment change, audit record, event and
receipt describe the same act. If something fails before commitment, the
operation rolls back. If the final database outcome becomes uncertain, Raisa
does not pretend that check-in succeeded. A genuine retry returns the original
stored result instead of checking the patient in twice.

Nothing has been switched on for real use. The existing specialist development
route still has its default-off switch and synthetic-practice restriction, and
it has not yet been rewired to this adapter. No patient data, live database,
provider, UI or deployment was opened.

## Technical summary

The accepted `compose_product_check_in` seam uses injected dependencies and
the dedicated check-in confirmation schemas. It enforces ingress and in-
session Receptionist reauthorization; claim/replay/conflict/in-progress and
evidence-reuse classification; exact locked `Booked|Confirmed -> Arrived`;
route-parity state, command, target-area and freshness construction; opaque
evidence verification at aware UTC; compatible waiting-area assignment or
preservation; and the ordered audit/event/private-receipt/idempotency/commit/
readback sequence.

The focused package passes 85 tests including 68 hostile mutations. The wider
provider-free packets pass 101, 152 and 590 checks, and the canonical profile
passes 200 tests plus lint, compilation, JavaScript syntax and whitespace. The
final Gemini 3.7 Flash/high veto passes all eight corrected commands and leaves
the exact candidate clean.

The tranche also explains some of the slower wall-clock progress. From plan
freeze to final veto was about 83 minutes. Roughly 23 minutes were lost to a
DeepSeek transport non-result, and the independent gate required three process
attempts because the first produced no admissible decision and the second
contained a fixture-dependent command selected by Sol. The first defect has
now produced a real Antigravity egress-failure receipt path; the second is
recorded as a recurring manifest-classification error. This is genuine harness
overhead rather than hidden productive subagent work.

The Codex runtime reports no live child agents even though the panel shows six
multi-day cards. Combined with the slow usage change, repeated compactions and
this task's unusually long history, that is consistent with stale UI/lifecycle
state or long-task degradation. It is not proof of a particular internal
OpenAI fault, but it is enough to rotate safely.

After restarting Codex, begin a fresh task on the same branch and ask it to
continue from this closeout. Ariadne's five-source rehydration will recover the
baton. The next narrow product direction is to make the existing default-off
A5.1 route delegate to the accepted adapter without enabling it or changing
the general status path, grammar, either client, waiting-area movement or any
live-data/runtime boundary.
