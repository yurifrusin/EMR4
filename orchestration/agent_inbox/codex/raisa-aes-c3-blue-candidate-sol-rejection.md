# Sol rejection: Raisa AES-C3 DeepSeek blue candidate

Date: 2026-08-11

Decision: `revision_required`

Candidate: `480a0301a1102108fa0779efb98809d55adf0ffa`

Candidate state: `untrusted_partial_worktree`

Recovery owner: GPT Sol through `docs/ariadne-orchestrator-recovery-lease.md`

## Decision

The bounded worker candidate is not accepted. It reproduces the frozen
61-scenario totals, but several outer containment outcomes are supplied from
the scenario family or mutation label rather than derived from the exact
inherited C1/C2 result and replay identity. That is a conceptual containment
and evidence-integrity defect, so the frozen Flash correction-loop rule sends
the candidate directly to Sol's recovery lease without a same-lane revision.

The worker closeout remains immutable implementation provenance. Any adopted
source is untrusted until separately amended, tested, independently vetoed and
accepted under Sol ownership.

## Deterministic findings

1. Replay fixtures are descriptive, not controlling. The exact
   `stale-alias-replay-stop` attempt still passes `validate_attempt` and returns
   `generation_superseded` when `replay_artifact` is replaced with `null`.
   The fixture contains only kind, ID, digest and a synthetic-noncredential
   flag; it has no generation, manifest, Bureau, work-cell or authority binding
   to compare. This does not prove stale alias/token or cross-Bureau replay
   rejection.
2. The declared inherited base is cosmetic. Replacing the same stale-alias
   attempt's `base_scenario_id` with `exact-inert-dispatch-simulated` also
   passes validation and returns the same result because `_base_c2_attempt`
   calls the C2 builder with the outer C3 scenario ID rather than the declared
   inherited base.
3. Malformed input is not fail closed. Deleting `scenario_id` produces the
   validation error `$:missing:scenario_id`, but direct `evaluate_attempt`
   raises `KeyError` before returning a closed minimized rejection. The frozen
   containment precedence requires malformed/open input to reject.
4. Outer evidence can contradict the inherited evaluator. With the imported
   C2 evaluator replaced by a deterministic probe returning
   `allow`/`simulated`, one invocation and non-null invocation/result digests,
   both a stale-alias attempt and an egress-budget attempt still return the
   planned outer stop and report zero pure calls. The resulting objects retain
   the contradictory C2 digests. The stale, egress and supply-chain branches do
   not establish that the inherited result actually stopped with the required
   reason and zero release before building their outer result.
5. The cumulative sequences have the same evidence-integrity gap. The denial
   sequence discards the third C1 result after calling it. The repeated-failure
   sequence increments its local failure count independently of whether each
   C2 result actually stopped, released nothing and carried the required
   malformed-result reason. Both then construct the planned outer terminal
   label.
6. The focused tests assert the hard-coded outer labels and separately repeat
   selected inherited calls. They do not challenge contradictory inherited
   results, missing replay bindings, cosmetic base IDs or malformed evaluator
   inputs, so their 93/93 pass cannot close these findings.

## Required Sol recovery

The recovery must:

- bind every scenario to one exact family, carrier, inherited base, mutation,
  expectation and replay-presence rule;
- make the exact declared C1/C2 base object control evaluation;
- give inert replay fixtures exact generation, manifest, manifest-digest,
  Bureau, work-cell and authority bindings and compare them to current state;
- validate before evaluation and return a closed minimized rejection for every
  malformed/open attempt;
- derive status, reason, call count and release count from exact checked C1/C2
  results, rejecting contradictory inner evidence;
- prove both cumulative terminal transitions from each exact returned result;
  and
- add adversarial regressions for every finding above before fresh Gemini
  review.

No real runtime, adapter, provider, credential, network, filesystem,
database/source, executable tool, command, patient/product data, deployment,
release, Pages or protected ref was opened or moved by this review.
