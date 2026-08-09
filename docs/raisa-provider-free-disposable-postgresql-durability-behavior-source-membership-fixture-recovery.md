# Context Fabric durability source-membership fixture recovery

Date: 2026-08-10

Status: candidate recovery; no additional database run authorised by this document

## Failure preserved

Behavior attempt 033 is immutable at
`provider-free-behavior-transaction-failure-evidence-033.json`, SHA-256
`5a6d5bcc18cd23f0fa528e5cdd33e53e9f0b90c0415a8f86ca326cf47980c8ad`.
It reached `BTR-E03` and was correctly rejected by
`admit_proofread_observation_v1` with `CF201`. The exact owned disposable
container was removed and its absence verified; zero scenarios were admitted.

## Deterministic diagnosis

The accepted body defines `source_membership_digest` as the canonical
`emr4_context_fabric.source_membership_digest_v1` digest over all eleven fields
of the same-locator payload-free outbox row. The behavior fixture instead
supplied only that row's `source_contract_digest`, which is one of those eleven
inputs. Its readback repeated the same mistaken equality.

The database guard therefore behaved correctly: the supplied packet did not
prove membership in the exact immutable source row. No function, trigger, RLS
policy, SQLSTATE, principal or scenario is weakened.

## Bounded repair

The harness now derives the packet value from the accepted typed body node and
the same renderer that produced the bound inert artifact. It refuses any drift
in the digest profile, source relation, ordered eleven-field tuple or rendered
artifact expression before Docker contact. The fixed SQL subquery selects only
the exact authored-synthetic practice, contract, stream, epoch and position.

`BTR-E03` readback independently recomputes that full-row canonical digest and
compares it with the admitted value. The contract/schema rule and the accepted
plan/design wording are corrected accordingly. The twenty scenario objects,
their order and `6/4/3/4/3` category counts remain byte-identical.

The repaired behavior contract canonical SHA-256 is
`d3355c4459042b97518cba6dcb54c8b861aaa502ab6cf7a096cd948fbaefcbc7`.
The unchanged canonical scenario/order/coverage population remains
`eec93b0d67bd70a9640b3000bc63d43a08aa6817b438e0c99dbf2595a69c4c19`.

## Acceptance required before another run

The repair must pass the diagnosis tests, contract/schema tests, hostile
renderer and behavior tests, the complete frozen deterministic packet, Ruff,
diff checks and one fresh exact-HEAD Gemini 3.6 Flash/high veto. Only then may
one new fixed-path attempt run in one newly owned networkless disposable
PostgreSQL 16 container.

## Closed boundaries

This recovery opens no applied migration, operational database or credential,
watcher/listener/feed/source wiring, application/API/Diary change, product or
patient data, provider call, command/write capability, deployment, production,
release, Pages or protected-ref movement.
