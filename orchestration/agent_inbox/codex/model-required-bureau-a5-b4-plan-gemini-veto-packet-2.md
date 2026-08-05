# Fresh independent veto — EMR4 A5.1/B4.1 plan revision 2

You are the fresh Gemini 3.6 Flash/high architecture/security veto reviewer.
Work read-only in the exact worktree and branch supplied by the launcher. Verify
that the candidate head is exactly
`37c22d7d076af7913c2fca4d65f8c9d63e38195f` and keep it clean and unchanged.

## Mandatory rehydration

Read `AGENTS.md` completely, then read these current authority and source files:

- `docs/emr4-model-required-bureau-a5-b4-command-runtime-plan.md`
- `docs/security/emr4-model-required-bureau-a5-b4-command-runtime-threat-model-delta.md`
- `docs/emr4-rayleen-davida-controlled-recovery-development-plan.md`
- `orchestration/api_spine_adr.md`
- `orchestration/api_spine_programme.md`
- `orchestration/bernie_release_gates.md`
- `docs/davida-practice-administration-default-location-command-boundary-plan.md`
- `docs/davida-practice-administration-default-location-command-boundary-design.md`
- `docs/security/davida-practice-administration-default-location-command-boundary-threat-model-delta.md`
- `docs/api-spine/openapi/practice-administration-default-location-commands.yaml`
- relevant current implementation in `app/routers/appointments.py`,
  `app/routers/diary_events.py`, `app/models/appointments.py`,
  `app/models/diary_events.py`, `app/services/appointment_idempotency.py`,
  `app/services/diary_committed_events.py`, `app/models/tenancy.py`,
  `app/dependencies.py`, `app/config.py` and the current Alembic head.

Exclude all prior candidate review/analysis artifacts from your reasoning,
including every file matching
`orchestration/agent_inbox/**/*a5-b4-plan*receipt*`,
`*a5-b4-plan*packet*` or `*a5-b4-plan*preflight*`. Do not inspect historical
Antigravity projects, protected holdouts, `docs/branding/`, patient/clinical/
product-derived data, secrets or runtime provider configuration.

## Exact review question

Decide whether revision 2 is now sufficiently exact, internally consistent and
architecture-strengthening to dispatch separable A5.1 and B4.1 implementation
without widening authority.

Adversarially test at least:

1. A5.1 dedicated default-off Receptionist-only routes, exact
   `Booked|Confirmed -> Arrived`, compatible same-location waiting area,
   patient-free schemas/receipt and unchanged generic status-confirm behavior.
2. The opaque expiring signed nonce evidence; exact key/request/evidence hash
   ordering; same-key stored replay; deterministic unique-index handling for
   concurrent different-key reuse; replay after appointment state restoration;
   row lock and zero-effect failure paths.
3. Command-bound audit, conditional checked-in event schema/payload, all three
   named PostgreSQL constraint replacements, atomic rollback and preservation
   of the reschedule producer/feed/cursor by exact event-type filtering.
4. B4.1 proposal zero-write semantics, explicit human-attestation evidence
   route, server-held evidence binding/retry/expiry/consumption and current
   role reauthorization.
5. Exact server mapping `Admin -> practice_manager` and
   `PracticeOwner -> practice_owner` before body assertion equality, with no
   aliases or client-selected authority.
6. B4 transaction ordering, aggregate version, canonical hashing,
   idempotency/replay/in-progress semantics, one-way evidence consumption,
   append-only patient-free audit/outbox, forced RLS, unpublished event and
   deterministic readback.
7. Exact OpenAPI/async-manifest changes, one sequential Alembic head, current
   source collision risks and whether each acceptance claim is locally provable
   with authored-synthetic fixtures and zero product-provider calls.

## Output contract

Report only fresh findings, highest severity first, with exact current paths and
line references. A material ambiguity, security omission or scope conflict
requires revision. If there are no material findings, say so. End with exactly
one terminal line and no other `DECISION:` line:

`DECISION: pass`

or

`DECISION: revision_required`

Do not edit, write receipts, implement, commit, push, deploy or move refs.
