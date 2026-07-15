# Bernie LC4V4 Fresh Certification Closeout

LC4V4 attempt 002 completed as valid one-shot evidence and returned
`certification_fail` under the thresholds frozen before content.

The aggregate report represents 288 Gold/adjudicated synthetic scenarios, 72
multi-turn trajectories, two repeats, and 576 samples. It covers 288 distinct
six-dimensional cells and has zero repeat variance. Intended action and
temporal relation both reached 576/576, showing that those two coarse semantic
axes remained deterministic across the fresh corpus.

The complete contract reached only 70/576. Safety reached 466/576. Other
aggregate dimensions ranged from 240/576 for entity semantics to 480/576 for
normalized values; failure-layer counts were 500 interpretation, 304 policy,
340 integration, and 110 safety. Multiple slices were zero and the worst slice
was 0.0000. These values fail the frozen readiness threshold by a wide margin.

The evidence therefore supports three limited conclusions:

1. the system is deterministic over this corpus;
2. intended-action and temporal-relation classification are comparatively
   robust at this level; and
3. end-to-end semantic agreement is not yet ready for certification.

The aggregate cannot identify whether an individual disagreement belongs to
the parser, the policy/replay contract, or authored surface semantics. The
holdout is sealed, so it must not be used to answer that question. The next
responsible step is an independently authored development-only diagnostic
matrix targeted at the weak aggregate axes. Parser repair remains unauthorized
until such ordinary evidence reproduces a trustworthy defect.

The accepted aggregate report is `docs/bernie-lc4v4-aggregate-report.json` with
hash
`sha256:9fa0cfe19d6e24e19630d415e4a778c89b6381057ae661e4c7d6c53c088d68f5`.
Exact procedural evidence and authority are recorded in
`orchestration/agent_inbox/codex/lc4v4-sol-acceptance.md`.
