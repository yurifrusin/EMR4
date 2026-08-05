# C5 Sol recovery lease

Date: 2026-08-05

Rejected worker candidate:
`45a7a76e0705a2b534779847866507017370c557`

Frozen source boundary:
`953073e18ab48420b58d80ed78d41e8033534cb8`

Owner: GPT Sol (`openai-primary-orchestrator`)

Status: active bounded source-recovery lease; no live action

## Provenance and scope

The worker commit and receipt remain rejected as AER-0027. Sol may adopt their
owned-path source only as an untrusted starting point under
`docs/ariadne-orchestrator-recovery-lease.md`; this lease cannot rewrite the
worker closeout, expand the frozen C5 plan or confer live eligibility.

The only mutable implementation paths are the worker-owned C5 scripts, focused
tests, closed schemas/examples/evidence directory and the unmounted API-Spine
document. The recovery may also update AER/receipt/acceptance documentation and
tests required to preserve and verify the rejection. `app/**`, GraphQL,
databases, product/provider runtime, deployment, Pages, protected refs,
`docs/branding/**` and the Context Fabric remain excluded.

## Exact recovery controls

1. Move issuance uniqueness, evidence sequence, provider-call/correction state,
   idempotency, attempt sequence, supersession and cleanup state into the shared
   store and protect them with its one transaction lock.
2. Make execution evidence bind the exact approval, frame, admitted candidate,
   admitted proofreader disposition, provider ledger, command envelope, server-
   held port, target nonce, generation, executable digest and target-artifact
   digest. Revalidate all bindings before consumption.
3. Validate one canonical frame: exactly one fresh healthy generation-1
   baseline and one fresh absent/connection-refused post-fault observation with
   distinct ids/sources; proofreader admission must cite the post-fault facts.
4. Revalidate every frozen approval field during issuance and immediately
   before execution, including basis, fault, provider envelope, reasoning/output
   budget, cost/calls, evidence label, plan, target, runbooks, expiry and one-
   rehearsal limit.
5. Enforce one provider primary and at most one distinct ticket-bound correction
   in shared state; reject schema/transport retry, unchanged candidate, second
   correction and any call after admission. No provider client or call is added.
6. Make runtime admission mechanically equivalent to the closed schemas and
   tighten frame/proofreader schemas against duplicate, contradictory or
   semantically invalid objects.
7. Pin the repository root to the source module's actual repository, verify the
   exact virtual-environment Python and target module resolved paths and hashes,
   validate the fixed argv/environment before start, and reject drift before
   any process call.
8. Complete the real adapter contract for the exact owned handle only. Bind
   handle identity to argv/nonce/generation/port/artifact, implement fresh
   process observation/termination/closure without PID discovery, and validate
   loopback host/path/port arguments in the HTTP observer.
9. Replace the close-before-launch ephemeral-port allocation with an owned
   loopback socket reservation handed to the exact target launch, or an
   equivalently race-free bounded handoff proved by tests. No arbitrary listener
   probing is allowed.
10. Wrap every post-launch operation in terminal rollback handling. Fresh
    success requires both an independently invoked alive/owned-process
    observation and exact HTTP generation-2/port/nonce/artifact/target readback.
11. Generate the task directory beneath a validated OS temporary root, add an
    unforgeable ownership marker, reject caller/workspace/broad/root paths, and
    remove only the exact marked run directory after owned-resource cleanup.
12. Cleanup must terminate/close the exact handle, close the listener, consume
    or close provider and execution ledgers, invalidate capabilities, prove every
    absence predicate and emit `cleanup_verified` only when all are true.
13. Replace constant-zero controller accounting with a truthful append-only
    operation audit for real/live adapters while preserving exact zero counters
    for the provider-free fake-only acceptance run.
14. Tighten the unmounted OpenAPI document so its schemas are closed and
    complete and explicitly defer actor/practice/idempotency/audit fields to any
    future mounted command descendant; it must not imply a current route.

## Mandatory regressions

Provider-free tests must directly deny or contain every audit reproduction:

- attacker runbook/wrong frame/executable or success candidate;
- port different from issuance or health-body port mismatch;
- baseline-only or semantically invalid stopped-process grounding;
- every mutated frozen approval field;
- duplicate issuer over one shared store;
- duplicate/contradictory frame and proofreader objects;
- unchanged, second, post-admission and ineligible correction attempts;
- parser/schema cardinality and uniqueness divergence;
- process-absent success attempt;
- exception from process observation, HTTP readback, audit or terminal receipt;
- incomplete real adapter contract and path/hash drift;
- listener handoff substitution;
- cleanup with any process/listener/directory/ledger/capability proof false; and
- operation-counter claims that disagree with the append-only audit.

The full focused/inherited serial suite, reproducible acceptance, Ruff,
compilation, Bandit, JSON/YAML validation, API-Spine checks and `git diff
--check` must pass. A fresh exact-HEAD Gemini 3.6 Flash/high read-only veto is
mandatory because this is runtime and security-boundary recovery.

## Live stop line

Recovery code and fake-only tests may proceed. Do not start the C5 process,
bind/connect a socket, allocate a live port, create/remove the live task
directory, inspect ADC or invoke Vertex until the repaired implementation and
fresh independent veto pass and a distinct pre-execution receipt is generated.
