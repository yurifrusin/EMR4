# LC4V5R1 Sol Recovery Amendment

Date: 2026-07-16

Decision: `worker_timeout_candidate_rejected_sol_recovery_invoked`

DeepSeek V4 Flash/high ran through Claude Code `--bare` in the isolated
`claude/lc4v5r1-development-remediation` worktree from base `4364a749`. The
launcher reached its 20-minute bound without returning a worker receipt,
candidate artifact, or commit. Sol stopped only the exact descendant process
tree from that launch. Protected `master` remained clean throughout.

The uncommitted worker state is preserved in its disposable worktree. Its
binary diff hash is
`sha256:3b7973f2420f1258487bc901936c610db7431f140cad7c5ab8913bde99d8b5f6`.
File hashes are:

- `semantic_extraction.py`:
  `sha256:c2e5b186b7f71dd66e163dff8a502320421308849bd89ade9b087bfa45841d57`;
- worker evidence helper:
  `sha256:03ac88413e8accc5ca37ac5a9dd8b9006f81adc1bbf2e4d2aaf91625a187724b`;
- worker test candidate:
  `sha256:922b901047ade63efadd96beeaca360f72a63b6346996433691c7552ed82bfe8`;
  and
- unauthorized `tests/test_content.b64` helper:
  `sha256:5f42cf5781fc0401eece2fa3471043f85a4f6393105b534ef625faecbb15bb9f`.

The `.b64` helper was outside the worker-owned surface and is a recorded scope
breach. It remains only in the failed disposable worktree and is not adopted.

Sol reviewed the ordinary development diff as an untrusted candidate. The
worker had useful bounded ideas for approximate-create clarification and
lossless duration alternatives, but it did not implement final normalized
bound convergence, added a redundant approximate-time parser, broadened the
`no` correction rule, and had not completed its tests. Sol therefore rejected
the candidate as a whole and independently authored the recovery changes.

Sol recovery is limited to:

- a punctuation-scoped `No,` correction cue;
- final move-target/correction-aware temporal convergence;
- approximate-create clarification before create authority; and
- explicit-only resize duration choices.

No worker claim is used as acceptance evidence. The fresh 18-probe runner,
tests, report, acceptance, and closeout are Sol-owned and require independent
exact-head review before integration acceptance.

## Historical-test distinction

The frozen contract's broad preservation wording named both LC4V4D5 and
LC4V4D5R1. The original D5 adoption-audit nodes are immutable failure evidence:
they intentionally retain the four blockers that D5R1 later repaired. They are
not a current dynamic green gate and were not regenerated or edited. The
accepted D5R1 suite is the current dynamic gate.

Seven LC4V2R1 entity-normalization nodes also fail at the untouched pre-sprint
base `4364a749` with the same results seen after recovery. Those expectations
predate the later accepted Option A ambiguity policy and their generated
historical check. A detached baseline worktree reproduced the identical seven
failures before any LC4V5R1 source was present. They are therefore recorded as
pre-existing historical incompatibilities, not LC4V5R1 regressions, and no
historical LC4V2R1 report or test was changed to conceal them.
