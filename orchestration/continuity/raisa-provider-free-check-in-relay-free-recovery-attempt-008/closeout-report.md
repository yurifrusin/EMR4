# Check-in relay-free recovery attempt 008 technical report

Date: 2026-08-23

Timestamp: 2026-08-23T07:19:39.9791037+10:00 (Australia/Brisbane)

Status: `accepted_candidate`

## Exact result

Attempt 008 passed at occupied source
`9f37ede79a915172e449c1f2d19bdba3eb592b44` and is preserved in terminal
commit `0e50f7f48d9c8622341a1679db507de78b1260a5`.

The closed execution envelope records:

- result `raisa_provider_free_check_in_relay_free_recovery_attempt_008_pass`;
- one occupied invocation and zero automatic retries, resumes or fallbacks;
- no ambiguous success release, ordinary admission or product record;
- finalized cleanup projection preserved with `cleanup_verified`; and
- exact terminal evidence and attestation SHA-256 bindings.

## Transaction and isolation evidence

The exact authored-synthetic packet staged one effect, receipt and audit member
then explicitly rolled back. Fresh restricted-role readback observed zero of
all three. A disjoint packet then committed, the caller exited 42 after the
observer terminated the exact post-commit backend, and no complete terminal
response or success was released. Fresh restricted-role authoritative readback
observed one effect, one receipt and one audit member, no duplicate effect and
no other-practice visibility.

The ephemeral login was non-superuser, non-owner and `NOBYPASSRLS`, with zero
memberships, owned objects or product privileges. All three admin-owned
non-product relations had RLS enabled and forced. The run used one internal
network, no published port, host relay, Docker-exec bridge, external network,
bind, volume, multiprocessing process or queue. Postterminal inspection found
zero matching containers and networks.

## Deterministic admission and execution economy

P06-P14 all passed in order. Before the checkpoint, the committed wrapper bound
the current repaired base, immutable attempt-007 terminal, accepted repair,
verification-envelope and plan-admissibility evidence. Static admission
matched all 67 prospective/runtime success paths, rejected 66 hostile
forbidden-field mutations, rejected all 366 contract, 96 manifest, 96 state
and 24 classifier mutations, and validated the closed terminal schema.

The candidate and governance packets passed through the provider-free closed-
database runner. Ruff, compilation, JSON Schema, full Git ancestry, tracked-
clean and diff hygiene passed. Read-only Docker inspection matched the exact
cached `postgres:16-bookworm` image and found zero owned residue. A fresh
five-source receipt passed with zero manual Git IDs. The clockwork checkpoint
published with zero canonical drift, zero dual ownership and zero caller-
authored derived fields before the single invocation.

The occupied command completed in 7.4 seconds wall time; the base evidence
records 5.703905 seconds. No occupied retry or recovery loop occurred.

## API Spine steward review

Boundary classification is a provider-free security/audit/idempotency
rehearsal of an existing REST/OpenAPI command shape, not an API change. The
mixed API Spine remains exact:

- GraphQL remains read-only and received no mutation authority;
- the command remains explicit, practice-scoped, idempotent and auditable;
- restricted authoritative readback, not an event or model, decides the
  unknown response;
- the audit/effect/receipt packet is transactionally consistent; and
- default-off A5.1, authored-synthetic allowlisting, staff confirmation,
  generic-status `Arrived` exclusion and waiting-area separation remain exact.

The API Spine artifact and canonical route-convergence packet passed 52/52
through the provider-free runner. No OpenAPI, GraphQL, REST route, application
schema, client or configuration artifact changed.

## Workflow efficacy and contained lapses

The implementation and its first focused packet needed zero correction. The
sole occupied invocation passed once. Three process lapses remain visible:

1. the preceding decision's first postpublication assertion represented only
   its prepublication latch; the exact phase-aware replacement passed;
2. the first broad P12 invocation yielded without the caller retaining its
   session identifier; the process completed and exact bounded replacement
   packets were captured; and
3. one protected-ref guard command used an unbraced PowerShell variable before
   a colon and failed at parse time; the braced form passed before push.

None created a Docker object, started PostgreSQL, executed SQL, changed product
state or caused an occupied rerun. AER-1033 through AER-1035 retain them.

## Claim and continuation boundary

This result closes the previously open bounded evidence question for atomic
rollback and relay-free unknown-response exactly-once recovery. It does not by
itself revise the twelve-dimension ordinary-practice admission verdict. A
separate provider-free read-only convergence review must bind this terminal
and decide that dimension while retaining the operational environment-manifest
and secret-posture gap.

No ordinary-practice enablement, feature-flag/allowlist change, product route
call, product/patient/appointment/clinical/protected data, provider/worker,
reusable runtime, production, deployment, release, Pages or protected-ref
authority opens.
