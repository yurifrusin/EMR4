# Provider-free read-only unmounted delete-confirm physical representability review

Date: 2026-08-15

Timestamp: 2026-08-15T13:51:59+10:00 (Australia/Brisbane)

Status: `deterministically_admitted_pending_independent_veto`

Review baseline: `a02e424eac89c12d42ff2c25cfafcc80f3fef077`

Target result: `raisa_provider_free_read_only_unmounted_delete_confirm_physical_representability_review_pass`

Evidence label: `provider_free_exact_file_read_only_unmounted_review`

Overall verdict: `implementation_not_admitted`

## Findings by severity

### Material — product authority is not yet a delete-command fence

The repository contains the right architectural primitive: a positive
practice-user principal-generation row can be locked with `SELECT FOR UPDATE`
inside a caller-owned transaction, and authored-synthetic current truth already
distinguishes role and active user, practice and membership state. A
role-scoped adapter also binds transaction-local practice and row-security
context.

Those structures remain authored-synthetic and read-oriented. They do not yet
bind the current product `User`/practice identities and
`appointment.cancel.confirm` capability into the appointment transaction.
Route-role admission is therefore not the accepted current-authority fence.

Verdict: `representable_with_additive_change`.

### Material — current delete-confirm ordering is not the accepted kernel

The mounted precursor claims and may disclose the idempotency result before it
loads the appointment. The appointment lookup is practice-scoped and
non-disclosing, but it is not explicitly locked. No practice-authority fence or
second all-locks-held authority check is present, and the route does not advance
`appointment_state_version`.

The ingredients for one transaction exist separately: caller-owned auth
transactions, principal and idempotency row locks, staged appointment/audit
writes, generic completion and one final commit. A later physical design must
compose them in exact `practice -> appointment -> idempotency_record` order and
must not treat the current route as proof of that ordering.

Verdict: `representable_with_additive_change`.

### Material — the private durable receipt is status-specific

The idempotency model already carries operation, route, actor, key/request
digests, target, audit identity, session-binding digest, pre/post versions and
canonical response bytes. Its strong complete private-receipt constraint is
explicitly limited to `confirmAppointmentStatusProposal` / `status-confirm`.

The current delete route calls generic completion with the target only. It does
not pass the audit identity or populate the session digest, pre/post versions
or canonical response bytes. Delete-confirm therefore needs an additive
receipt constraint and completion path rather than a new ledger.

Verdict: `representable_with_additive_change`.

### Moderate — audit and reason storage exist but the exact proof is incomplete

Appointment truth and the audit row both carry `status_reason_code` and nullable
`cancellation_reason`; the current helper also stages waiting-area clearing and
a delete audit in the same SQLAlchemy session. Audit can correlate command and
session identities.

The audit does not yet explicitly bind pre/post appointment versions and
waiting-area state, and the current helper merges internal evidence codes with
confirmed warnings. The public proposal also requires a generic
`delete_reason` while leaving `status_reason_code` optional, which does not
express the accepted mandatory structured-reason plus nullable bounded
free-text policy exactly.

Verdict: `representable_with_additive_change`.

### Moderate — fresh readback lacks an explicit appointment-read action

A separate practice-scoped appointment GET exists and is suitable as the
reconciliation surface. Its visible dependency is generic current-user
authentication, not a fresh explicit practice/action/resource appointment-read
decision. That decision must be added and remain separate from commit proof.

Verdict: `representable_with_additive_change`.

### Positive foundation — appointment truth is already representable

One practice-scoped appointment row already carries status, waiting-area state,
structured reason, nullable cancellation text and a positive
`appointment_state_version`, with a unique `(practice_id, id)` identity. No
timestamp surrogate is needed.

The current route's failure to lock or advance that row belongs to transaction
composition, not representability of appointment truth.

Verdict: `already_represented`.

## Closed verdict table

| Domain | Verdict | Essential next obligation |
|---|---|---|
| Practice authority fence | `representable_with_additive_change` | Bind product identity and cancel capability to a lockable current generation in the command transaction. |
| Appointment truth and lock | `already_represented` | Select the existing practice-scoped row with the later design's exact lock and version-advance rule. |
| Operation idempotency and private receipt | `representable_with_additive_change` | Extend private receipt completeness and population to delete-confirm after authority/target checks. |
| Attributable audit and exact reasons | `representable_with_additive_change` | Bind pre/post versions and waiting-area truth and align the public reason envelope. |
| Ordered atomic boundary | `representable_with_additive_change` | Compose practice, appointment and idempotency locks plus two authority checks and one atomic commit. |
| Fresh readback separation | `representable_with_additive_change` | Add an explicit current appointment-read action/resource decision after commit. |

## Cross-domain conclusion

All six domains are at least representable with additive change. No accepted
abstract kernel obligation needs to be weakened, and no second cancellation
kernel or ledger is required. The dominant gap is safe composition and current
authority, not a fundamental inability of PostgreSQL or the existing ORM model
to carry the required truth.

Raw compatibility DELETE and the status-confirm family remain separate ingress
paths. Neither may inherit the dedicated kernel's authority by analogy.

## Deterministic evidence

- Thirteen exact non-protected hashes pass.
- Twenty-six observations are bound to exact literal sources and inclusive line
  ranges.
- All six domain verdicts validate against the closed schema.
- Fifty-two hostile mutations fail closed.
- Application and database modules were not imported or executed.
- No directory enumeration or source expansion followed the AER-0325 control.

DeepSeek was allocated one mechanical inventory lane, but its exact transport
timed out without a result, owned artifact or tracked change. AER-0326 contains
that transport event; no worker source or claim was admitted, and Sol completed
the exact-file inventory without broadening the allowlist.

## Claim boundary and next gate

This review authorizes no physical design, column/default/backfill, migration,
source edit, route mount or execution, SQL/database access, product command,
UI, provider, patient/product/clinical data, credential, deployment,
production, release, Pages or protected-ref movement.

The dependency-satisfied next gate is a provider-free unmounted delete-confirm
physical-design architecture. It may select exact additive representation and
transaction contracts, but it still cannot edit or execute application or
database code.
