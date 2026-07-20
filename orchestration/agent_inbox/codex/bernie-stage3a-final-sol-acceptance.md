# Bernie Stage 3A — Extra High Final Sol Acceptance

Date: 2026-07-20

Reasoning level: `Sol Extra High`

Decision: `stage3a_pass`

Claim scope: `yuri_only_local_authored_synthetic_formative_validation`

## Decision

The exact Stage 3A gates pass. Yuri's first full study exposed instrument
defects; the bounded correction tranche repaired only the authorized fixture,
projection, route, copy and observation surfaces; the corrected seven-scenario
v2 export closes that population; and a fresh visible non-intercepted Diary →
FastAPI → isolated PostgreSQL confirmation closes S3A-06.

This is a formative Yuri-only pass. It does not claim representative usability,
provider intelligence, live event delivery, production safety or release
readiness.

## Evidence binding

- final closeout:
  `docs/bernie-stage3a-final-validation-closeout.md`;
- corrected v2 export SHA-256:
  `55146de6b7ad2743acf5ce9505230a39c5ff8a641f366d5018d2689282359ffb`;
- functional evidence: `authored_synthetic_fixture_browser`;
- confirmation evidence: `live_local_browser_backend_postgres`;
- isolated database:
  `gp_pms_stage3a_3af7c33c_20260720_s3a06`;
- post-confirm truth: exactly one appointment, one linked create audit, one
  completed `confirmed_write` command result, and one stored
  `appointment.confirmation_receipt.v1` with outcome `appointment_created`;
- reloaded Diary readback: exactly one appointment; and
- browser console warnings/errors: zero.

Yuri's post-export S3A-06 correction is accepted as an explicit facilitator
clarification, not a rewrite of the raw export. Final understanding is correct;
the mistaken `suppressed_events` selection caused no write and is retained as a
wording finding for any future representative study.

## API Spine and authority

The interpreter and supervised proposal route remain non-authoritative for the
appointment write. The authenticated staff member used the visible control;
the existing REST confirmation command performed backend revalidation,
idempotency, write, audit and receipt storage. GraphQL remained read-only and
no provider or browser client acquired mutation authority.

The one maintenance amendment narrows an obsolete tests-only `db.commit()`
prohibition to the accepted Stage 2 boundary: bounded durable session
persistence is permitted, while provider, appointment confirmation, create and
audit calls remain forbidden in the proposal route. Runtime behaviour is
unchanged. One unused test-only import was also removed for the Ruff gate.

## Verification

- fresh five-source rehydration and post-compaction receipts: pass;
- final closeout post-compaction receipt SHA-256:
  `592ac54c731ae9f552e3786d80733c695fca4b0f81d2d9ed9b3084fc8c99e800`;
- final pre-acceptance receipt SHA-256:
  `78510570e382c4922fc9061e6ba4c93c34e4e41d045bd07ef7ddbe143a12c23f`;
- final integration receipt SHA-256:
  `192163f3398de4a7177278fd4d03939ab85c7e80563655320924ca2167b5c9a8`;
- final pre-commit receipt SHA-256:
  `13e938217fa8007225c7cc3679a8683288fab839a01ef8f39c24d2a473009956`;
- final pre-push receipt SHA-256:
  `c050045a3281b96dabe01fad38b08561f161120cb548ea2c5c7cda85d8d7dc4c`;
- focused stale-assertion rerun: 1 passed;
- final combined protected-safe population: 73 passed;
- post-documentation Stage 3A/API Spine/handover/Ariadne population: 60 passed;
- Node, Ruff and whitespace gates: pass;
- runtime cleanup: pass; and
- protected/provider/historical/PII access: none.

No worker or subagent was used. The run was serial, stateful, acceptance-
sensitive and bound to one mutable synthetic database, so Sol retained it under
the worker-lane economy rule.

## Next boundary

Return the baton to Yuri. A provider-neutral in-house meta-grid concept tranche
is the recommended next design step, with high-fidelity styling deferred, but
it is not opened by this acceptance. Stage 3B and every other deferred surface
remain fresh decisions.
