# Fifth-recovery durability architecture review — untrusted diagnostic only

Date: 2026-08-06

Candidate: `eda1039b959321ea1e602a6db5b35caf2cc85cb7`

Disposition: procedurally ineligible for acceptance. The reviewer ran one broad
Git diff-name readback against `master`, enumerating forbidden prior-review and
agent-error-register path names without opening their contents. No protected
content, database, provider, network, runtime or application execution was
accessed and the reviewer made no file change. Sol retained the output only as
untrusted diagnostic input and required a new exact-path fresh review after
recovery.

## Diagnostic findings

### P1 — Current-XID provenance is not renderable as frozen

`xmin` is PostgreSQL `xid`, while `pg_current_xact_id()` returns epoch-aware
`xid8`; the plan freezes neither an exact comparison/cast nor its wrap policy.
It also does not address subtransactions: tuples written inside a savepoint can
carry a subtransaction XID rather than the top-level XID returned by the
function. Legitimate same-transaction writes may therefore fail, while an
implementer-selected truncation/cast would add unreviewed semantics. The inert
DDL gate needs an exact PostgreSQL-version-specific expression and an explicit
top-level/subtransaction policy. The non-retention/no-position limitation is
otherwise appropriate.

### P1 — The bidirectional commit fence does not close the no-event path

The proposed deferred checks begin from event, outbox, alias or claim rows and
then conclude that the appointment mutation is atomic. The existing command
emits an event only when the feature is enabled, a command id exists and a
temporal change is detected. No exact deferred trigger on the appointment
transition—or equivalent audit/claim obligation—freezes how a temporal update
with no event is rejected while a reason/notes-only update is allowed. Trigger
targets and `INSERT`/`UPDATE`/`DELETE` coverage are also unspecified, so
inserted-then-deleted claim/event/outbox/alias combinations are asserted as
tests but not architecturally closed.

### P1 — The machine contract omits most claimed architecture

The contract closes the 18 relation names and a small producer/alias subset but
has no exact columns, types, composite keys, foreign-key targets/delete actions,
RLS policies, role/entry-point matrix, admission keys, lifecycle/anchor
constraints, key-interval partition, retention-family membership or trigger-
event surface. Unsafe variations in those omitted surfaces therefore sit
outside schema validation despite the plan's mechanical-closure claim.

### P2 — Existing-model and mutation tests are too shallow

The tests verify nullable columns, local foreign-key column names, two unique
constraints, source constants and assignment substrings. They do not verify
referenced FK targets, event type/schema constraints, appointment/audit linkage,
endpoint flow or one-session behavior. Mutations alter only already-constant
shallow fields and cannot attack absent trigger, RLS, retention or relation
surfaces. Ten tests passed, but they do not establish the claimed closure.

## Reconciled non-findings and limits

- GraphQL remains read-only, REST remains the command plane, and events grant no
  command or fresh-read authority.
- Existing source has the claimed practice-scoped event/command foreign key and
  unique command/audit constraints.
- The update-confirm route uses one SQLAlchemy session through claim, mutation,
  completion and commit.
- Alias bijection, non-delete/non-reuse, complete-census retention, session-
  derived binding, independent anchors and generation-local rotation remain
  directionally fail-closed but were not machine-closed by this candidate.
- The one allowed no-cache/no-bytecode test command passed 10 tests.

The reviewer returned `revision_required`; because of the path-enumeration
breach that decision is not an admissible independent veto. Its findings are
being treated as untrusted challenges and must be resolved and independently
retested.
