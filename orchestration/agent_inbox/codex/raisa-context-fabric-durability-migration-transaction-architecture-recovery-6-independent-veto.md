# Independent veto — durability migration/transaction architecture recovery 6

Date: 2026-08-06

- Candidate: `a0ffc10a97cec23399724e56e6479932f029ab00`
- Review worktree: `C:/Users/sarashera/EMR4-worktrees/r29`
- Review branch: `codex/review-durability-migration-transaction-plan-recovery-6-a0ffc10a`
- Review mode: fresh native, read-only, exact-path, no Git commands, provider-free

## P1 findings

1. **The temporal trigger surface does not enforce “non-temporal update implies no event/projection.”** The appointment trigger fires only for `UPDATE OF start_time,duration_minutes`. A transaction can update only a non-temporal field and insert an event/outbox; the event trigger cannot reconstruct `OLD` temporal values, and the audit model stores no old/new time or duration. The claimed bidirectional fence therefore needs an all-`UPDATE` appointment trigger or another exact database obligation mechanism.

2. **The catalogue is not DDL-ready or machine-closed.** It omits domain/enum definitions, executable RLS `USING`/`WITH CHECK` predicates, function output signatures, concrete composite input types, trigger-function signatures, defaults, and enforcement mechanisms for cross-relation invariants. Several constraints are descriptive pseudo-syntax: partial uniques such as `entry_kind=PRIMARY`, cross-table checks such as `watermark_position <= checkpoint.last_contiguous_position`, and unquoted discriminator prose. The receipt has the right conceptual columns and composite locator, but its `PRIMARY` discriminator remains an unparsed string rather than a fully renderable constraint.

3. **The admission function’s owner cannot perform its declared effect.** `admit_proofread_observation_v1` is owned by `context_admission_receiver`, while that role is declared to own no objects and possess no table DML. PostgreSQL `SECURITY DEFINER` executes with the function owner’s privileges, so the function cannot insert admission rows without contradicting the role matrix.

4. **The tests do not validate the claimed semantics.** `validate_machine_contract` rejects every mutated fixture through the unchanged canonical hash; consequently the adversarial mutation loop proves snapshot immutability, not that unsafe variants are semantically rejected. The schema accepts arbitrary strings for keys, foreign keys, checks, RLS, mutation semantics, and inputs. The focused test passed, but cannot support the machine-closure claim.

## P2 findings

5. **The plan overclaims savepoint detection.** It requires every savepoint attempt to be rejected, but the XID predicate can reject only tuples authored by subtransactions; it cannot detect a savepoint created and released without relevant writes. The PostgreSQL-16 low-XID32 expression itself is otherwise suitable for ephemeral same-transaction tuple comparison and is not retained as authority.

6. **The outbox pins the existing committed event without a lifecycle contract.** Its `RESTRICT` foreign key to product-bearing `diary_committed_events` prolongs those existing rows beyond their declared expiry, yet that relation is absent from the source-retention family and purge signature. The retention renderer would have to invent the ownership and cleanup semantics.

## Confirmed non-findings

- The existing update-confirm source provides the operation, route and request digest; one SQLAlchemy session; the ordered claim-lock-update-audit-complete-commit flow; and no nested transaction on this path.
- The API Spine remains intact: GraphQL is query-only, REST remains the command plane, and no route, subscription, acknowledgement, provider, command or fresh-read authority is added.
- The rejected review worktree remained clean and unchanged at the exact candidate HEAD. Its postflight passed.
- Local and origin `master` and `handoff/current` remained exactly `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

## Decision

`revision_required`

No rejected-candidate claim is admitted. The six findings are inputs to the seventh bounded recovery under Sol ownership.
