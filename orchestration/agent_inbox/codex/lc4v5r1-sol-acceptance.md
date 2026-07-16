# LC4V5R1 Sol Acceptance

Date: 2026-07-16

Decision: `development_three_family_remediation_accepted`

GPT Sol retained contract, architecture, recovery, acceptance, and protected
integration authority. DeepSeek V4 Flash/high ran once through Claude Code
`--bare`; its bounded lane timed out without a receipt or commit and wrote one
unauthorized helper. Sol rejected the complete candidate, preserved its hashes
and scope breach, and independently authored the recovery under the lease.
DeepSeek Pro was not used.

## Provenance

- Contract and initial preflight: `1d7054ef` and `4364a749`.
- Rejected worker state: preserved in the disposable
  `claude/lc4v5r1-development-remediation` worktree and disclosed in
  `lc4v5r1-sol-recovery-amendment.md`.
- Sol recovery source head: `4a27900a478c5351de7ca4c3389bc6fca1e6be34`.
- Independent-review preflight: `012b9af948be502a16b3732739d8123a696bdf90`.
- Gemini review commit: `ed66940f0d65761b855de1c4745f582049075088`,
  integrated at `0d62bcc6`.
- Development report file hash:
  `sha256:3ab20d99c93fb14c528e229752072a969b5190b6fb3fd7cde8755aa40468689c`.
- Frozen probe hash:
  `sha256:e44885916b9790ac858715c7d3d7c43b10231edc5bdfcceeba8486fc077ec55f`.

## Accepted result

The 18 newly authored development probes cover exactly six create-approximate,
six move-interval, and six ambiguous-resize cases. The untouched source base
completed 4/18 and was safe on 14/18. Recovered source completes 18/18, is safe
on 18/18, and has zero variance over two repeats.

- Approximate create retains `14:30`/`15:30` evidence but cannot expose create
  authority until an exact correction resolves it.
- Correcting turns replace stale approximate bounds in both the top-level
  extraction and normalized values.
- Move targets preserve the final interval rather than a source time or an
  exact-point collapse.
- Underspecified resize invents no duration choices; explicit alternatives are
  retained in utterance order and an exact resolving turn clears ambiguity.

No scenario ID is present in product interpretation. Original turns, source
evidence, negation/refusal behavior, and the established Option A replay-only
contract remain intact.

## Verification and historical distinction

Sol's serial focused D1-D4+D5R1+R1 chain passed 201/201. The broader semantic,
temporal, clarification, safety, D2-D4, D5R1, and R1 preservation gate passed
439/439. Python compilation and `git diff --check` passed.

Gemini 3.5 Flash/medium independently reproduced 413/413 focused tests, all
18 repaired probes, the baseline and repaired aggregates, the exact probe
hash, and zero variance on exact recovery head `4a27900a`; it returned
`DECISION: pass`.

The original D5 audit is immutable blocker evidence superseded by accepted
D5R1. Seven LC4V2R1 historical nodes fail identically at untouched pre-sprint
base `4364a749`, so they are not R1 regressions. Neither historical report nor
test was regenerated or edited.

LC4V5 remains consumed and sealed. R1 is ordinary development remediation,
not certification and not permission to reuse or inspect v5. T3.1-T3.4 remain
intact and blocked by default. T3.5/providers, local-model development use,
historical diary material, product/runtime defaults, routes, APIs, UI,
database, deployment, release, and all live/write authority remain deferred.

The next ordinary step is a Sol-owned deterministic development-exit binder.
If it passes, Yuri must decide between a genuinely fresh holdout v6
(recommended) and an explicit reviewed reuse policy.
