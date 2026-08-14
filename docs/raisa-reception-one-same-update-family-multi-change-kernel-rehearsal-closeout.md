# Reception One same-update-family multi-change kernel rehearsal closeout

Date: 2026-08-15

Timestamp: 2026-08-15T00:46:56+10:00 (Australia/Brisbane)

Status: accepted

Accepted reviewed source: `3dd5f3b39ed98a2d562685d1d1567a359930c693`

Result: `raisa_reception_one_same_update_family_multi_change_kernel_rehearsal_pass`

## Lay summary

The appointment kernel can safely treat “change the doctor, time and length” as
one appointment change. It first presents one provisional proposal. Nothing is
altered until the authorised human confirms it. At confirmation, the backend
checks the appointment and the target doctor's current diary again.

If the appointment has changed, the new slot has become occupied, or the target
doctor is no longer active, the whole proposed change is refused. It never
partly changes one or two fields. If the final database transaction fails after
work has begun, the appointment, audit record and request ledger all roll back
together; the same request can then be retried cleanly.

This is the truth-kernel milestone needed before Reception One receives a
combined editor. It does not itself add or change any visible control.

## Technical result

The exact existing appointment update proposal/confirm path passes all seven
frozen authored-synthetic scenarios:

- `M1`: a practitioner, local time and duration proposal carries all three
  values and performs no mutation;
- `M2`: exact confirmation commits all three values with one correlated update
  audit and one completed idempotency result;
- `M3`: intervening authoritative appointment change causes signed freshness
  denial with no candidate effects;
- `M4`: a newly committed target-practitioner interval conflict blocks the
  whole candidate;
- `M5`: target-practitioner deactivation blocks with
  `practitioner_inactive`;
- `M6`: exact same-key replay from a fresh session returns the stored response
  without revalidation or mutation, while different-body reuse conflicts; and
- `M7`: failure at `complete_appointment_command` after update/audit flush but
  before commit rolls back appointment, audit and idempotency state, after
  which one clean same-key retry commits and replay is mutation-free.

The candidate adds only
`tests/test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py`.
No `app/**`, Diary UI, API/OpenAPI/GraphQL, migration, database schema or runtime
source changed.

## Verification

- Core update/API/M1-M7 packet: 109 passed.
- Latch and orchestrator-preflight packet: 69 passed.
- Agent-error register packet: 234 passed.
- Total fresh independent review packet: 412 passed across seven modules.
- Final continuity-inclusive closeout packet: 438 passed across eleven modules.
- Ruff lint and format checks passed; JSON, exact 32-path source scope and Git
  whitespace checks passed.
- Fresh Gemini 3.6 Flash/high returned one schema-constrained `pass` at exact
  unchanged clean source `3dd5f3b39ed98a2d562685d1d1567a359930c693`.
- Evidence label:
  `provider_free_live_local_backend_postgresql_authored_synthetic`.

The first Sol aggregate run was killed only by its too-short 120-second shell
deadline and was admitted as no evidence. The complete rerun under the
repository serial PostgreSQL lock and a 360-second deadline passed.

## Workflow incidents and corrections

- AER-0309 contains DeepSeek's prose-and-fence output-contract breach. Sol
  ignored its self-report, inspected the exact one-file commit and reproduced
  the complete deterministic evidence.
- AER-0310 contains Sol's transient manual expansion of a displayed short Git
  hash. The nonexistent value was corrected from `git rev-parse HEAD` before
  any receipt or acceptance used it.
- AER-0311 contains Sol's direct-path invocation of the import-dependent
  Antigravity help command. It stopped locally before any model or project
  started; the module-form invocation passed before the one real dispatch.

No incident changed candidate behavior, reached protected evidence or broadened
authority.

## Parallelism efficacy: planned versus actual

- **DeepSeek V4 Flash/high:** positive leverage. It supplied the bounded new
  M1-M7 test module in a disposable worktree; Sol independently admitted and
  reproduced it. AER-0309 contains its egress-format defect.
- **Gemini 3.6 Flash/high:** positive leverage. It performed the required fresh
  exact-candidate veto and left the worktree unchanged and clean.
- **Native subagents:** declined as planned. No separable package remained and
  the preceding tranche's scope breaches made another local packet negative
  leverage.
- **Sol:** retained plan, threat, deterministic verification, incident
  correction, integration, acceptance, continuity and Git authority.

## Next tranche

Proceed under standing authority with the narrow provider-free
`raisa_reception_one_same_update_family_multi_change_editor_composition`.
Compose practitioner, local time and duration into one progressive Reception
One draft, one existing update-family proposal, one review and one explicit
confirmation. Status remains a distinct action. Reuse the existing canonical
route and fresh reconciliation; add no new backend command, conversational
execution or external patient/channel authority.

## Claim boundary

This proves the exact combined update kernel in the isolated local PostgreSQL
test environment. It does not prove a browser/editor composition, concurrent
different-key serialization, production RLS or performance, conversational
interpretation, patient or delegated-assistant identity, live channel
revocation, cross-family atomicity, deployment or production readiness.
Provider use, credentials/IAM, real data, watcher runtime, release, Pages and
protected-ref movement remain closed.

Yuri attention required: no.
