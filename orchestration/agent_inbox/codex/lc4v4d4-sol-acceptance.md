# LC4V4D4 Sol Acceptance

Date: 2026-07-16

Decision: `versioned_composed_integration_valid`

Conductor, recovery, acceptance, and protected integration owner: GPT Sol.
Bounded implementation/test worker: DeepSeek V4 Flash/high through Claude Code
`--bare`. Independent veto reviewer: Gemini 3.5 Flash/medium through a fresh
Antigravity worktree. DeepSeek Pro was not used.

## Exact provenance

- Frozen D4 contract head:
  `fbcd1c63f7dbbafce8ef96f71a5cdab22b15735e`.
- DeepSeek candidate: `822889f73b82a3cb659c193543e0901b22ef1599`,
  adopted as an untrusted candidate at `73398585`.
- Sol recovered source: `4eb3dc7ff65c0fa298cdd5db99d2827d17f17a96`.
- Exact recovered report source:
  `4218d2ee3aca321fe8169a0f27567945e5fa04ca`.
- Exact recovered report head reviewed by Gemini:
  `bd51caf065bd298b965578ccc89c4615d097b8d5`.
- Gemini review commit: `c4b09a0e0a9812994b156d27395dfedc8d25c36b`,
  integrated at `790bf2f7`.

Evidence hashes:

- D2 report:
  `sha256:3220ac943659ae1449c5c285144b1fa980f659668a705ca7aef98f0aea6d317a`;
- D3 selection/current policy population:
  `sha256:d3c6618cb586f5dc43824ec7a6e9e33957fee587a45c19f89e5a4bb425006e2a`;
- accepted D3 report:
  `sha256:94b751aea657696329c6b6d394253aef3ef0dbe82316e7725efc1c16fac523a8`;
- legacy 60-probe composed baseline:
  `sha256:665851ffe055efb40f2ba1e43291d6b945c4764b4f441837781d4fc964d6ff27`;
- complete D4 report:
  `sha256:dd1ecc077a59bf05e777eda1f3a5450c0a1b97a4c8a3fd21dc0363d473abd653`.

## Accepted behavior

The ordinary deterministic composed harness now exposes exactly two explicit
policy versions. Legacy remains the default and exactly reproduces the direct
60-probe interpretation/replay baseline. Option A is selected explicitly and
runs after one pure utterance extraction.

Option A preserves intended action, action semantics, temporal relation,
normalized values, entity semantics, completion claim, and negation from pure
extraction. Its final clarification requirement, lossless choices, tool
selection, and authority travel through the ordinary typed interpretation.
Outcome, tools, clarification, appointment/audit deltas, simulated-write state,
and forbidden observations travel through ordinary typed replay. Diary relation,
conflicting fields, and resolved identities remain separate typed fields.

All 20 accepted Option A cases pass over 40 complete observations with zero
variance and exact categories `5/2/1/2/5/5`. Complete D4 observations match the
frozen accepted D3 output. The omitted-practitioner and five diary-state-join
cases are recorded as the exact six versioned D1 expectation differences; no
frozen D1 artifact was rewritten or forced green.

All 13 fail-closed gates pass: D2 report, D3 report, current selection hash,
current 20-case population, accepted D3 case population, legacy baseline hash,
legacy runner equivalence, 20/20 Option A, zero variance, pure utterance
preservation, exact replay/policy fields, exact incompatible-D1 differences,
and no forbidden mutation.

## Worker failure and Sol recovery

The Flash candidate supplied useful scaffolding but its evidence compared the
new runner to itself, hashed a static expected selection, checked only that the
probe dictionary contained the expected IDs, hard-coded forbidden observations
empty, retained legacy operational fields in Option A interpretation, and
proved the incompatible-D1 set only by constant length. It also claimed a clean
diff while its commit contained Markdown trailing whitespace.

Those are conceptual acceptance defects, so Sol opened no correction loop.
Under the recovery lease Sol dynamically recovered the current diagnostic
population, bound every complete typed field to frozen D3 output, separated
pure utterance preservation from policy-operational change, computed forbidden
observations, proved concrete six-case differences, and added fail-closed
tamper tests. Full disclosure is in `lc4v4d4-sol-recovery-amendment.md`.

## Verification

- Focused D4 tests: 33/33 passed.
- Fresh Gemini adjacent D3/composed gate: 88/88 selected nodes passed.
- Sol serial D1-D4, semantic extraction, composed-harness, and handover gate:
  329/329 selected nodes passed.
- Exactly one immutable historical LC3 committed-report equality node was
  deselected. Sol reproduced its failure on unchanged contract baseline
  `fbcd1c63`; D4 did not cause it and the historical report was not regenerated.
- `git diff --check fbcd1c63..bd51caf0` passed.
- Gemini independently returned `DECISION: pass` on exact recovered report head
  `bd51caf0`.

## Boundary and next step

D4 is development-only and is not product runtime wiring or certification.
Holdouts v1-v4 remain sealed. T3.1-T3.4 remain intact and blocked; T3.5/live
providers, product/API/UI/database/write authority, historical diary,
deployment, and release remain deferred.

The next ordinary step may be a bounded D5 development-wide Option A adoption
audit over all 60 ordinary probes, preserving the 20-case overlay and
classifying every remaining difference without parser or historical-fixture
repair. A later certification holdout or reuse remains a separate Yuri decision.
