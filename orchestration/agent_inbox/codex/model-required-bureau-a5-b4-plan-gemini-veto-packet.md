# Independent architecture/security veto — EMR4 A5.1/B4.1 plan

You are the independent Gemini 3.6 Flash/high veto reviewer. Work read-only in
the exact bound worktree and branch supplied by the launcher. Verify both before
review. The candidate head must be exactly
`7bcd7cc46eff549300dfd60e6a269781e820b9e8` and the worktree must remain clean
and unchanged.

## Mandatory rehydration and sources

Read `AGENTS.md` completely, then read:

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
  `app/models/appointments.py`, `app/models/diary_events.py`,
  `app/services/appointment_idempotency.py`,
  `app/services/diary_committed_events.py`, `app/models/tenancy.py`,
  `app/dependencies.py` and the current Alembic head.

Do not inspect historical Antigravity review artifacts, protected holdouts,
`docs/branding/`, patient/clinical/product-derived data, secrets or runtime
provider configuration.

## Exact review question

Decide whether the two new documents are sufficiently exact, internally
consistent and architecture-strengthening to authorize separable implementation
without accidentally widening command authority.

Adversarially test at least:

1. A5.1 reuse of existing signed status evidence, its exact
   `Booked|Confirmed -> Arrived` event branch, row locking/current-state
   revalidation, command-bound audit/idempotency/event atomicity, event payload
   privacy and preservation of the existing reschedule event family.
2. Whether the explicit Davida human-attestation route soundly closes the
   historical gap between a zero-write proposal and a confirm request that must
   already contain server-held one-use evidence.
3. Whether evidence issuance/retry/expiry/consumption, role revocation,
   proposal/path/body/hash equality and cross-key replay are exact enough to
   implement without ambiguity or a client-minted authority path.
4. The deliberate runtime role mapping `Admin -> practice_manager` and
   `PracticeOwner -> practice_owner`, authorization-before-disclosure, and the
   separation of the A4 read token from command authority.
5. Davida transaction ordering, aggregate versioning, canonical request
   hashing, idempotency replay/conflict/in-progress rules, append-only audit and
   unpublished patient-free outbox, forced RLS and rollback semantics.
6. Any collision with current models/routes/Alembic head, any hidden provider or
   autonomous action path, or any acceptance claim not locally provable with
   authored-synthetic fixtures.

## Output contract

Report findings first, highest severity first, with exact document/source paths
and line references. A material ambiguity, missing security invariant or scope
conflict requires revision. If there are no material findings, say so. End with
exactly one terminal line and no other `DECISION:` line:

`DECISION: pass`

or

`DECISION: revision_required`

Do not edit files, run provider/product runtime, write receipts, commit, push or
move refs.
