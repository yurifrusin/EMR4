# C4 bounded repair independent audit

Date: 2026-08-05

Candidate: `0a60d559ec9a555e038bec5dc428b6c323c2ff04`

Disposition: `revision_required`

## Deterministic baseline

The distinct DeepSeek V4 Flash/high repair commit remained clean and changed
only six worker-owned C4 paths. Its generated evidence reproduced, Ruff,
compilation, Bandit and `git diff --check` passed, and the independently rerun
focused/inherited set passed 148 tests. The worker receipt reported
`DECISION: pass`; that decision is rejected because the residual authority and
one-use failures below were reproduced against the exact commit.

## Material residual findings

### 1. Current reviewer role is not bound

`SimulatorRuntime._revalidate_current_authority` at
`scripts/model_required_bureau_c4_simulator.py:1644` accepts every bounded,
non-empty reviewer role. Replacing current role `reviewer` with
`revoked_but_nonempty` still released `simulated_effect_verified`, retained one
effect record and changed the synthetic service to healthy. This violates the
repair packet's current reviewer-role and role-loss requirements.

### 2. Current-authority mutation is not transactionally excluded

`CurrentAuthorityStore` has no lock or revision, while the runtime takes one
snapshot at `scripts/model_required_bureau_c4_simulator.py:1811` under only the
runtime instance's private lock. A blocked transition permitted another thread
to replace the current authority with an actor-role revocation before the
effect, yet the first thread released success. The claimed fresh execution-time
authority is therefore a time-of-check/time-of-use snapshot rather than a
transactional current source.

### 3. One-use evidence is not atomic across runtime instances

Each `SimulatorRuntime` creates its own `RLock` at
`scripts/model_required_bureau_c4_simulator.py:1460`, even when two instances
share the same evidence, state and audit stores. By synchronising both handlers
after they locally resolved the same issued record but before either consumed
it, two different idempotency keys produced two successful attempts and two
effect audits. The raw shared evidence dictionary owns no transaction lock, and
idempotency plus attempt sequence are also runtime-local. This violates the
single-winner, same-key replay and one-use evidence contract.

## Recovery disposition

This was the single bounded same-lane Flash revision permitted by the active
correction-loop rule. No further DeepSeek correction is eligible. The two
worker commits and receipts remain immutable untrusted source. Sol may adopt
them under `docs/ariadne-orchestrator-recovery-lease.md` and apply only the
narrow corrections required to:

- give the shared in-memory execution/evidence store one transaction lock plus
  shared idempotency and attempt sequencing;
- hold the current-authority store stable for the complete execution critical
  section; and
- require the exact closed reviewer role.

The recovered candidate must add adversarial regressions for all three
failures, regenerate reproducible evidence, pass the full deterministic C4 and
inherited suite, and receive one fresh exact-head Gemini 3.6 Flash/high veto
before acceptance.

No provider, patient/product/protected data, real target, database, product
route, C5 action, deployment, release, Pages or protected-ref boundary was
opened by this audit.
