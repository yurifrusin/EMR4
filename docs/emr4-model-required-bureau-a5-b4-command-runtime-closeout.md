# EMR4 Bureau A5.1/B4.1 command-runtime closeout

Date: 2026-08-05

Result: `model_required_bureau_a5_b4_command_runtime_pass`

Accepted source HEAD: `c93bbfa7e656a97a85c5b4532525caa362c6c781`

## Accepted result

The paired provider-free command descendant passes without joining its two
domain authority boundaries.

- Bureau A5.1 implements one default-off, authored-synthetic-practice-only
  Receptionist check-in proposal/confirm path for the exact
  `Booked|Confirmed -> Arrived` transition. The server owns the signed one-use
  evidence, current-state and waiting-area revalidation, idempotency,
  appointment truth, immutable audit and patient-free committed event.
- Bureau B4.1 implements one default-off, authored-synthetic-practice-only
  three-step practitioner default-location command family. Davida remains
  proposal provenance only; a current authenticated `Admin` or
  `PracticeOwner` supplies the human attestation and confirmation. One
  transaction owns practitioner truth/version, evidence consumption,
  immutable audit, unpublished patient-free outbox and durable idempotency.

REST/OpenAPI owns both command families. GraphQL remains read-only. Neither a
model, provider response, event, proposal, client role assertion nor client-
supplied practice identifier carries command authority.

## Recovery and integration

The A5.1 worker changed `app/schemas/diary_events.py` outside its packet-owned
path set. Its receipt and commit remain preserved as untrusted provenance under
AER-0021. Sol adopted the necessary closed patient-free event schema through
the named recovery lease, reconciled the route and contract inventories,
resolved A5.1 and B4.1 into one sequential Alembic chain, and repaired the
integrated replay, stable-reference, proposal-bound, regression and canonical
verification seams. AER-0021 is corrected only by the completed recovery lease
and subsequent deterministic and independent gates.

The first final Antigravity transport timed out during Google OAuth restoration
before review admission. It transmitted no review prompt, produced no decision
or receipt, retained no raw authorization material and left the candidate
unchanged. AER-0022 records that transport event. After human authentication
restoration, a fresh process reviewed the same exact clean candidate and
returned one pass.

## Deterministic and independent evidence

- Focused A5.1 acceptance: 36 passed.
- Focused B4.1 acceptance: 38 passed.
- Combined focused API/command acceptance: 152 passed.
- Widened ordinary command/event regression suite: 389 passed.
- Related maintenance and A3 regression suite: 80 passed.
- Canonical fast profile: 69 passed; Ruff, compilation, JavaScript and
  whitespace checks passed.
- Canonical Bandit profile: passed with exactly the two reviewed baseline
  findings and no new medium/high finding.
- Disposable PostgreSQL/Alembic lifecycle: one head, upgrade to
  `v1w2x3y4z5b6`, downgrade to `u0v1w2x3y4z5`, then re-upgrade to
  `v1w2x3y4z5b6`; the disposable database was removed.
- Fresh Gemini 3.6 Flash/high exact-HEAD code veto: 261 passed, no material
  finding, exactly one `DECISION: pass`, unchanged clean worktree.

Agent-error register revision 16 now contains 22 bounded incidents and no open
incident. Failure evidence was preserved; neither worker provenance nor the
OAuth transport failure was rewritten as success.

## Claim boundary

This proves two bounded authored-synthetic development command runtimes and
their deterministic backend authority, atomicity, replay and readback
properties. It does not prove product or patient use, clinical safety, ordinary
practice enablement, autonomous action, external event delivery, a second
administrative or waiting-area-move command, live recovery, production,
deployment, release, Pages or protected-ref movement.

No provider product-runtime call, patient/clinical/product-derived data,
protected evidence, deployment, release, Pages or protected-ref action occurred.
`docs/branding/` and the pre-existing untracked receipt/state files remain
preserved and excluded.

## Planned successor

Standing programme authority opens the dependency-satisfied Bureau C4
controlled-recovery allowlisted-actuator rehearsal. Its exact descendant must
be the narrowest provider-free authored-synthetic simulator: typed one-use
execution evidence for an exact allowlisted runbook, no model-supplied shell or
SQL, no real database, no production target and no external effect. Planning
begins without another permission handback.
