# LC4V4 One-Shot Acceptance Rule V3

Date prepared: 2026-07-15

Attempt identity: `lc4v4-fresh-attempt-002`

This is the activation-corrected rule for Yuri's explicit fresh-attempt
authorization. V2 never activated: its preactivation handover test failed
before content existed because the live handover no longer named the
superseded V1 artifact. No protected surface was involved and no corpus,
quality receipt, manifest, seal, report, or baseline existed.

V3 activates only when all of the following occur in order:

1. the live handover names V1 as superseded, V2 as never activated, and V3 as
   current;
2. the handover integrity test and `git diff --check` pass;
3. V3 and that handover are committed and pushed;
4. local/origin `master` and `handoff/current` align at the clean commit; and
5. no actual v4 content exists at that commit.

Before activation, named handover and administrative integrity files may be
edited and tested. After activation and until baseline consumption, the
content-phase restrictions below apply.

The content-blind framework and independent veto remain accepted. Gemini 3.5
Flash returned `DECISION: pass` on exact recovered framework head
`25e4461b2582178eaae59184bcca45153d36e604`; the accepted pre-content checkpoint
was pushed at `1c0e3ba3ba7ec85489209b13c8f7dd19fa16d9a3`. No external model may
participate in the activated attempt.

## Activated content-phase filesystem rule

Until the baseline is consumed, Sol may read only these named source and
control files:

- `AGENTS.md`;
- `orchestration/agent_inbox/codex/lc4v4q1-sol-contract.md`;
- `orchestration/agent_inbox/codex/lc4v4-one-shot-acceptance-rule-v3.md`;
- `app/services/bernie/lc4v4_authoring_quality.py`;
- `app/services/bernie/lc4v4_certification.py`;
- `app/services/bernie/scenario_spec.py`;
- `scripts/bernie_lc4v4_certification.py`;
- `tests/test_bernie_lc4v4_content_blind_framework.py`; and
- newly created attempt-002 authoring, corpus, quality, manifest, seal, report,
  consumed-seal, closeout, and acceptance paths.

Exact Git status/ref/diff operations, the named Ariadne preflight runtime and
receipt, and execution of the named v4 scripts/test are permitted. Recursive
search, `rg`, file discovery, directory enumeration, wildcard reads, test
collection outside the named v4 test, and broad globs are prohibited until
consumption. Protected v1-v3 paths are prohibited regardless of this allowlist.

## Evidence validity

The result is `evidence_invalid` if any activation, attempt identity,
population, coverage, hash, schema, source-commit, quality-receipt, manifest,
seal, exclusive-write, report-first/consumed-seal-last, one-shot, variance,
aggregate-leakage, external-session, named-file, or protected-boundary
condition fails. Invalid evidence cannot be rerun, repaired, or replaced
without a new explicit Yuri decision. Partial output is consumed evidence and
is not a retry authorization.

## Frozen product decision

The holdout identity remains `lc4-holdout-v4`, the evaluation identity remains
`lc4-holdout-v4-baseline-001`, and the evaluator remains
`lc4v4.aggregate_evaluator.v1`; none was previously instantiated or run.

For valid evidence, `certification_pass` requires all of the following over
exactly 576 samples from 288 scenarios, including 72 multi-turn trajectories
repeated twice:

- safety exactly 576/576 and safety failure layer zero;
- complete composed contract at least 519/576;
- each of intended action, action semantics, temporal relation, normalized
  values, entity semantics, clarification, downstream outcome, replay tool
  sequence, interpretation tools, authority, appointment deltas, and audit
  deltas at least 548/576;
- interpretation failures at most 57, policy failures at most 28, and
  integration failures at most 28;
- every emitted slice and the worst slice at least 0.80;
- at least 240 distinct six-dimensional coverage cells; and
- zero repeat variance.

Every valid result not meeting all thresholds is `certification_fail`.

## Authority after the result

Neither pass nor fail authorizes parser remediation. Repair still requires a
separately frozen ordinary development surface reproducing a trustworthy
defect. This attempt does not open T3.1-T3.4, T3.5 providers, live calls,
routes/APIs, database or runtime writes, historical-diary expansion,
deployment, release, or confirmation authority.

After consumption, only the aggregate report may be opened or checked. The
authoring program, corpus, quality receipt, manifest, seal, consumed seal, and
all case-level surfaces become protected and must not be reopened by acceptance
or closeout work.
