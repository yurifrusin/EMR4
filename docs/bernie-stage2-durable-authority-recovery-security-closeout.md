# Bernie Stage 2 Durable Authority, Recovery, and Security Closeout

Date: 2026-07-19

Owner: GPT Sol / Extra High

Decision: `stage2_pass`

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

## Protected integration

The accepted candidate was published as
`codex/bernie-stage2-durable-authority`, based on protected Stage 1 closeout
head `8cadc64c56d014a7f3fbd70d82ac5c041e63fed8`. Its implementation/evidence
commit was `cd3a9e056d8553da9ae339896dd28222b6554a57`.

PR 38's first green check cycle exposed three required-conversation threads
from GitHub Advanced Security: two empty `except` handlers needed explanatory
comments and one test import was unused. The bounded corrections passed 9/9
focused tests, the complete restricted-role database probe, the exact Bandit
gate, leakage lint, compilation, and whitespace checks. On final branch head
`7874271aea160e7539bf61cf238d919c9250dc61`, GitHub automatically resolved all
three threads and the required Python Security, Node/Office baseline, Python
CodeQL, JavaScript/TypeScript CodeQL, and aggregate CodeQL contexts all passed.
No policy or alert was bypassed or dismissed.

Protected PR 38 squash-merged as
`60940f27d50410172f4132416df5e8a20623815b` on 2026-07-19. This
documentation-only closeout carrier records that integration. After its own
required checks and protected merge, `master` and `handoff/current` are aligned
to the carrier head and the required non-PHI notification is delivered
operationally; neither step changes product acceptance.

Its Ariadne integration and pre-commit receipts both pass and explicitly bind
the live baton, current allocation, active plan/acceptance, protected evidence,
and Git/worktree sources. Their SHA-256 values are respectively
`9b589c638bcabe034603df62972da9ea015b17a2e650453510b62d7727a95be8`
and `451d12450f222ab5d497054c6da80c171e30975d4afca285ca8ad2bf812721da`.
The closeout commit is `3c35de865f5af3a3b7b0fa03fae3e3cc56dd8f18`;
its pre-push receipt passes with SHA-256
`e7f080008230b47a12ed08bcd4cae692bedd13d6f6502e177576a783823bed75`.
