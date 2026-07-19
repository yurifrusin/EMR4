# Bernie Stage 2 Durable Authority, Recovery, and Security Closeout

Date: 2026-07-19

Owner: GPT Sol / Extra High

Decision: `stage2_pass_ready_for_protected_integration`

## Outcome

The user-approved local synthetic appointment-create vertical now has durable
PostgreSQL Bernie session/event state, atomic command idempotency, complete
session-command-appointment-audit-receipt correlation, database-enforced
append-only audit, forced row-level security, restart/concurrency/failure/retry
recovery, and the approved retention behavior.

All fifteen frozen acceptance gates pass. The authoritative evidence and exact
gate disposition are in
`orchestration/agent_inbox/codex/bernie-stage2-durable-authority-sol-acceptance.md`.

## Retention implemented

- incomplete session recovery detail slides for 24 hours from its latest
  accepted transition;
- completed session/event detail expires after 30 days;
- expired session cleanup is explicit, bounded, and lock-safe; and
- appointment, append-only audit, completed command/receipt, and minimal
  correlation remain for the life of the development database.

No production scheduler, retention policy, backup behavior, or deletion claim
is made.

## Database and recovery result

Alembic revision `m2n3o4p5q6r7` passed the disposable upgrade/downgrade/
re-upgrade lifecycle and model-drift checks. The preserved development database
upgraded additively; its four historical completed create commands now have
exact direct and reciprocal audit links. Its existing 12 appointments, 9 audit
rows, and 4 commands remain, while the two new session tables begin empty.

A restricted non-bypass role proved fail-closed missing tenant context,
same-practice visibility, foreign-row invisibility/write denial, five
cross-practice opaque-id graft rejections, database-trigger audit immutability,
and retention cascade behavior. The probe transaction and temporary role were
fully rolled back.

Fresh tests prove restart reconstruction, one-winner revision concurrency,
one-winner same-key confirmation concurrency, all-or-nothing injected failure,
stored post-commit replay, exact correlation, JWT/database-practice
consistency, bounded structured event storage, and selective expiry cleanup.

The live handover also returned to its existing compactness contract: duplicated
historical chronology was routed to the already verified ledgers, reducing
`AGENTS.md` from a protected-head baseline of 588 lines to 436 while preserving
the current baton, authority, protected/user boundaries, and required
certification facts. The handover archive/authority tests pass.

## Authority preserved

Bernie remains proposal-only. An authenticated staff member must explicitly
confirm through the existing REST command, after which FastAPI/PostgreSQL owns
revalidation, the sole appointment write, idempotency, append-only audit, and
the authoritative receipt. GraphQL remains read-only. Providers remain
disabled and made no calls.

No protected holdout content, historical diary material, external corpus, PII,
production system, cloud surface, deployment, release, new appointment action,
GraphQL mutation, or autonomous-confirmation surface was opened. A contained
filename-only protected metadata incident exposed path names but no protected
content, hashes, runs, labels, or tuning evidence.

## Remaining boundaries

The local database owner is a superuser; Stage 2 proves RLS with an isolated
restricted role but does not provision a production runtime account. Real PII,
at-rest field encryption, production key management, database-role/GUC
hardening, production retention, backup/restore, monitoring, incident response,
Australian residency, deployment, and release all remain open decisions.

Stage 3 receptionist workflow validation does not begin automatically. It
requires a fresh Yuri decision covering participants, synthetic observation
protocol, and acceptance thresholds. Provider work remains paused.

## Integration state

The candidate is on `codex/bernie-stage2-durable-authority`, based on protected
Stage 1 closeout head `8cadc64c56d014a7f3fbd70d82ac5c041e63fed8`.
Protected PR/check evidence, merge SHA, final ref alignment, and the non-PHI
closeout notification will be appended only after they occur.
