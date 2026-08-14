# Reception One same-update-family multi-change kernel rehearsal plan

Date: 2026-08-14

Timestamp: 2026-08-14T22:44:44+10:00 (Australia/Brisbane)

Status: `frozen_for_provider_free_authored_synthetic_execution`

Task baseline: `704f2827c7b914792c43c12f026149ce25f70882`

Target result: `raisa_reception_one_same_update_family_multi_change_kernel_rehearsal_pass`

Reasoning level: High. The accepted orientation already fixes command-family
meaning and authority. This tranche supplies bounded deterministic evidence
over the unchanged existing route; it does not revise architecture or user
behaviour.

## Objective

Prove that one authorised appointment update request changing practitioner,
local time and duration is proposed without mutation and confirmed through the
existing `POST /api/v1/appointments/proposals/update/confirm` path as one
practice-scoped, idempotent and auditable command transaction.

Exercise the exact combination against current-truth staleness, newly created
schedule conflict, target-practitioner inactivation, exact same-key replay and
an injected pre-commit failure. No individual-field update sequence is an
acceptable substitute.

## Boundary classification

- The proposal is a command-style read that returns typed provisional evidence
  and performs no appointment mutation.
- Confirmation is the existing explicit REST/OpenAPI appointment-update
  command. It must bind the authenticated practice and actor, signed evidence,
  proposal freshness, one idempotency claim, one appointment row, one audit row
  and one stored result.
- GraphQL, events and Context Frames supply no write or confirmation authority.
- Status is absent from the update patch. No cross-family execution is in
  scope.

## Exact source contract

The rehearsal uses, but does not initially change:

- `AppointmentUpdateProposalIn`, `AppointmentUpdateCommand` and
  `BernieUpdateProposalConfirmationIn` in `app/schemas/appointments.py`;
- `propose_update_appointment`, `confirm_update_proposal_route`,
  `confirm_update_proposal` and `_apply_appointment_update` in
  `app/routers/appointments.py`;
- the closed `AppointmentUpdateProposalCommand.patch` in
  `docs/api-spine/openapi/appointment-commands.yaml`; and
- the existing update-proposal and update-confirm idempotency tests.

The route already claims idempotency before mutation, locks the exact
practice-scoped appointment, verifies signed freshness evidence, re-proposes the
full command, exact-matches it, flushes one update/audit, completes the ledger
and commits once. This is structural evidence only until the exact combined
scenarios below pass.

## Frozen authored-synthetic scenario matrix

| ID | Scenario | Required result |
|---|---|---|
| `M1` | Propose a new active practitioner, new local time and new duration together | One safe full command and confirm payload contain all three values; appointment, audit and idempotency counts remain unchanged. |
| `M2` | Confirm the exact `M1` payload | One appointment contains all three new values; exactly one update audit and one completed idempotency row share the command/appointment correlation; response is one `confirmed_write`. |
| `M3` | Mutate authoritative appointment truth after proposal but before confirmation | Signed freshness revalidation blocks; the combined candidate performs no appointment, audit or idempotency mutation beyond the separately committed intervening change. |
| `M4` | Insert a conflicting appointment for the proposed target practitioner and interval after proposal | Confirm-time re-proposal returns the typed conflict block; the subject appointment and command/audit counts do not change. |
| `M5` | Deactivate the target practitioner after proposal | Confirm-time re-proposal returns `practitioner_inactive`; the subject appointment and command/audit counts do not change. |
| `M6` | Replay the successful `M2` confirmation with the exact same key and body from a fresh database session | The stored response is returned exactly; there is no second revalidation, update, audit or ledger row. Reuse of that key with a different validated body remains a typed conflict. |
| `M7` | Inject failure at idempotency completion after the combined update and audit have flushed but before commit, then retry with the same key | The failed transaction leaves the appointment, audit and idempotency state exactly as before; the clean retry commits one correlated update/audit/ledger result and a later replay is mutation-free. |

All fixtures are newly authored synthetic people, practitioners, appointments
and times inside the isolated test database. No historical Diary or product
population is admissible.

## Implementation surface

The first candidate may add only:

- `tests/test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py`;
- this plan and its threat-model delta;
- bounded worker/reviewer packets and receipts;
- acceptance, continuity, closeout and Yuri mailbox artifacts.

No `app/**`, `docs/diary/**`, OpenAPI, GraphQL, migration or runtime file may
change in the initial candidate. If a frozen scenario exposes a genuine current
kernel defect, preserve the failing evidence and create a separately named,
exact-source recovery amendment before any product repair. Do not weaken an
assertion or silently broaden this plan.

## Acceptance

The tranche passes only when:

1. `M1-M7` pass through the ordinary existing proposal/confirm functions or
   their real FastAPI route boundary as appropriate;
2. the successful result proves all three requested values changed in one
   committed appointment version and one correlated command outcome;
3. every pre-confirmation block proves zero subject mutation, zero new update
   audit and zero retained idempotency claim;
4. the injected failure proves transaction-wide rollback before a clean
   same-key retry and exact replay;
5. the existing update proposal/idempotency suite and API Spine artifact
   invariants remain green;
6. source-scope checks show no product, API schema, UI or database surface
   changed;
7. Ruff, JSON validation, Git whitespace and active latch/preflight checks pass;
8. one fresh Gemini 3.6 Flash/high review returns exactly one decision at an
   unchanged clean exact-candidate worktree; and
9. Sol independently reconciles all counts, failure injection semantics and
   claim boundaries before acceptance.

Evidence label: `provider_free_live_local_backend_postgresql_authored_synthetic`.
This is direct local route/kernel/PostgreSQL evidence, not browser, adapter,
provider, patient, deployment or production evidence.

## Parallelism-efficacy allocation

- **DeepSeek V4 Flash/high — planned:** implement only the new test module from
  this frozen matrix in a disposable worktree. It owns no product source,
  acceptance, plan or Git integration.
- **Gemini 3.6 Flash/high — reserved:** review one deterministic-admitted exact
  candidate from a fresh read-only worktree.
- **Native subagents — declined:** the exact source inspection is already
  complete and the prior tranche recorded two command-scope breaches; a new
  native packet has negative leverage here.
- **Sol — serial owner:** plan/threat freeze, worker packet, candidate review,
  serial PostgreSQL tests, recovery, acceptance, continuity and Git.

DeepSeek may run while Sol prepares non-overlapping review and continuity
scaffolding. All PostgreSQL-loading pytest runs remain serial. Reassess at
pre-dispatch, worker return, any failing scenario, pre-verifier admission and
closeout.

## Stop and recovery conditions

- Stop candidate admission on any `app/**`, UI, OpenAPI, GraphQL, migration or
  runtime change.
- Stop and preserve evidence if rollback requires a product correction; derive
  an exact recovery amendment rather than smuggling code into this test tranche.
- Stop on any patient/product/protected evidence contact, provider or external
  network use, credential/IAM need, database outside the isolated test schema,
  or protected-ref movement.
- A test-harness defect may receive one bounded mechanical repair. A semantic or
  transactional contradiction returns to Sol for recovery and fresh review.

## Closed surfaces

No UI or compound editor; no new route, schema, command family, database
migration, event/watcher or Context Fabric runtime; no status-plus-update
transaction; no external patient, email, SMS, WhatsApp, voice or delegated-
assistant runtime; no patient/product/clinical data; no provider/ADC,
credential/IAM/network; no deployment, production, release, Pages or protected
ref authority. `docs/branding/` and every unrelated untracked file remain
preserved; staging is explicit-path only.
