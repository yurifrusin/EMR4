# C5 worker independent Sol/native audit

Date: 2026-08-05

Worker candidate:
`45a7a76e0705a2b534779847866507017370c557`

Source:
`953073e18ab48420b58d80ed78d41e8033534cb8`

Disposition: `revision_required`; the worker self-pass is rejected. The commit
and receipt remain immutable untrusted provenance and no C5 target, socket,
provider or actuator action is eligible.

## Material findings

1. **P1 — execution is not bound to admitted model/proofreader evidence or the
   issued port.** `ExecutionEvidenceRecord` omits port, frame, candidate,
   proofreader and provider-ledger bindings, while `execute_recovery()` merely
   fingerprints caller-supplied candidate/frame values. An independently
   reproduced candidate using `attacker-runbook.v9`, a wrong frame digest and
   executable/success flags, together with a port different from issuance,
   still returned `live_development_recovery_verified`.
2. **P1 — success requires no fresh process observation or handle proof.** The
   success path performs only HTTP readback and hard-codes its process
   observation id. A fake observer reporting the recovered process absent was
   never called and the controller still released success.
3. **P1 — unexpected post-launch failures bypass rollback.** A probe exception
   propagated after launch, leaving the fake process running, launch state
   `launching`, consumed evidence and no terminal receipt.
4. **P1 — cleanup can falsely claim verification.** Cleanup does not terminate
   the last owned handle, close the handle, consume the ledger/capability or
   condition its result on the proof booleans. Independent reproduction
   returned `cleanup_verified` while process, listener, ledger and reusable-
   capability checks were false. Task-directory operations also trust a
   caller-supplied root/path and have no generated root or ownership marker.
5. **P1 — issuance is not globally one-use across a shared store.** Issuance
   uniqueness and sequencing are issuer-instance fields. Two issuers sharing
   one `C5SharedStore` minted two distinct valid evidence records.
6. **P1 — the real process adapter cannot satisfy the controller contract.** It
   implements only `start()`, not the required `observe_process`, `terminate`
   or `any_running` operations. The allocator also closes its socket reservation
   before process handoff, retaining the frozen port-race risk.
7. **P1 — executable and artifact pinning is declarative only.** Repository root
   remains caller-selectable, `hash_file()` is unused, and neither the exact
   virtual-environment executable nor target artifact hash is revalidated
   before `Popen`. The generated readiness evidence also names a worker-
   worktree Python path that does not exist.
8. **P1 — the proofreader does not require the stopped-process evidence.** It
   accepts citations to any frame observation and never requires post-fault
   `process=absent` plus `health=connection_refused`. Frame construction itself
   admits arbitrary baseline/post-fault semantics, so a candidate citing only
   the healthy baseline can be admitted with a hard-coded stopped-process cause.
9. **P1 — evidence issuance does not revalidate the full approval envelope.**
   Minting omits approval basis, exact fault, provider/model/project/identity/
   region/endpoint, thinking/output budgets and evidence label. Mutated approval
   fields can therefore mint evidence and become self-consistent only through
   the mutated approval digest.
10. **P2 — provider-visible frame semantics are not canonical.** The closed
    schema permits two to eight arbitrarily ordered observations, duplicate ids
    and contradictory kind/process/health tuples rather than exactly one
    healthy generation-1 baseline and one absent/refused post-fault frame.
11. **P2 — proofreader receipts can be contradictory.** The schema admits
    `admitted: true` with false grounding, reasons and an open correction ticket,
    as well as a denied result with no reasons or ticket.
12. **P2 — correction-call rules are prose, not enforced state.** Every invalid
    candidate receives the same open ticket. No shared provider-attempt ledger
    binds the rejected candidate/frame, consumes the one correction, rejects an
    unchanged request or prevents a call after admission.
13. **P2 — parser and schema admission can diverge.** Runtime parsing does not
    enforce all array cardinality/uniqueness bounds and does not validate the
    exact Draft 2020-12 candidate schema before constructing a typed candidate.
14. **P2 — live operation accounting is not truthful.** Controller counters
    stay at zero and are copied into receipts despite fake process/HTTP/cleanup
    operations; cleanup asserts `ledger_consumed: true` without consuming it.

## Recovery disposition

These are material authority, state-machine, admission and resource-ownership
defects rather than a bounded mechanical omission. No same-lane Flash repair is
eligible. Sol may adopt the worker source only as an untrusted candidate under
`docs/ariadne-orchestrator-recovery-lease.md`, add direct adversarial
regressions for every reproduced invariant, and amend only inside the frozen C5
provider-free implementation boundary. The recovered candidate must pass the
serial deterministic suite, API-Spine/security/static gates and one fresh exact-
HEAD Gemini 3.6 Flash/high veto before any live C5 action can be considered.

## Checks and protected boundaries

- The worker worktree remained clean at the exact candidate.
- The worker-focused 27 tests and its reproducible acceptance check passed;
  those authored checks did not cover the material failures above.
- The target artifact digest matched its frozen constant, but runtime pinning
  remained absent.
- Independent reproductions used in-memory fakes only.
- No process, socket, port, temporary directory, provider, ADC, app/product
  route, database, patient/product/protected data, deployment, release, Pages or
  protected-ref action occurred.
