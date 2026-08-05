# C4 worker independent Sol/native review

Date: 2026-08-05

Worker candidate:
`c56267d23c24dd9e4fe642df85e74cc95de07a6e`

Source:
`b66b37a81120b1abd655ce65c42daf7518b8f7d5`

Disposition: `revision_required`; the worker self-pass is rejected and the
commit remains untrusted until a distinct repair and fresh final veto pass.

## Material findings

1. **P1 — malformed scalar input can consume evidence before a crash.**
   `parse_request` checks closed key sets but admits values such as a numeric
   `idempotency_key`. The handler then seals idempotency and consumes evidence
   before `.encode()` raises `AttributeError`. Reproduction observed admitted
   parse, consumed evidence, no terminal receipt and zero attempt records.
2. **P1 — fresh readback can certify the wrong actual target.** A state store
   seeded with `target_id=synthetic:wrong-service` still returned
   `simulated_effect_verified`, retained the wrong target and emitted a receipt
   hard-coded to `synthetic:api-service`, because success compared only health
   and revision.
3. **P1 — execution-time authority is not freshly sourced.** Runtime
   revalidation compares the request only with the frozen evidence snapshot.
   The constructor's catalog is never consulted and there is no current plan,
   decision, actor/role, reviewer or observation-content source. Catalog
   replacement, role loss and observation-content drift therefore cannot be
   detected.
4. **P2 — failed-readback/rollback attempts retain an effect audit.** The
   effect audit is appended before fresh readback, and the rollback path accepts
   but does not restore the effect-audit snapshot. Committed evidence reports
   one effect record for rollback cases, contrary to the frozen rule that the
   effect audit is retained only for verified success.
5. **P2 — receipt counter schemas require only 18 arbitrary zero-valued
   properties.** Replacing the named capability counters with
   `arbitrary_0`…`arbitrary_17` still validates. Exact names must be closed and
   required.
6. **P2 — callers may choose evidence reference and nonce.** `mint()` exposes
   public `reference` and `nonce` parameters and uses `secrets` only when they
   are omitted. Production issuance must always generate both cryptographically;
   deterministic fixtures belong only in acceptance/test monkeypatching.
7. **Additional hardening — issuance is not concurrency-locked.** The
   check-then-add sequence around the unique `(plan_revision,
   supersession_key)` key can race. The repaired issuer must make issuance
   single-winner under one lock and prove it adversarially.

## Checks and boundaries

- The exact 15-path worker diff stayed within the owned boundary.
- The worker's own acceptance, Ruff, compilation and Bandit checks pass.
- Independent combined C4/C3/Gate-zero/API-spine suite passed 173 tests after
  correcting the local test-runner checkout path.
- Passing tests do not override the reproduced material findings.
- The worker worktree remained clean at the exact candidate.
- No product/runtime provider call, real target, patient/product/protected
  data, deployment, release, Pages or protected-ref action occurred.
