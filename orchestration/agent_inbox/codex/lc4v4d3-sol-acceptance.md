# LC4V4D3 Sol Acceptance

Date: 2026-07-16

Decision: `option_a_policy_resolution_valid`

Conductor, recovery, acceptance, and integration owner: GPT Sol. Bounded
implementation worker: DeepSeek V4 Flash/high through Claude Code `--bare`.
Independent veto reviewer: Gemini 3.5 Flash/high through a fresh Antigravity
project. DeepSeek Pro was not used.

## Exact evidence

- Yuri Option A decision baseline and contract head:
  `77aae7e5bbd8b979d37e7453c81f62c9ed8ce8c7`.
- DeepSeek candidate: `19dbe229` (adopted as untrusted candidate at
  `5e557fb2`).
- Sol recovered policy/evidence source:
  `5eefb1a590157014ffd1153b0fb8cee81ef8e825`.
- Exact recovered report head independently reviewed by Gemini:
  `b00896625d69cd35947c15bd4910d504200bdd44`.
- Frozen D2 report hash:
  `sha256:3220ac943659ae1449c5c285144b1fa980f659668a705ca7aef98f0aea6d317a`.
- Exact D3 20-case selection hash:
  `sha256:d3c6618cb586f5dc43824ec7a6e9e33957fee587a45c19f89e5a4bb425006e2a`.
- Complete D3 report hash:
  `sha256:94b751aea657696329c6b6d394253aef3ef0dbe82316e7725efc1c16fac523a8`.

## Accepted behavior

All 20 approved Option A cases pass across 40 complete observations with zero
variance. The disjoint category counts are:

| Category | Pass | Fail |
|---|---:|---:|
| Clarification alternatives | 5 | 0 |
| Corrected patient | 2 | 0 |
| Omitted practitioner | 1 | 0 |
| Corrected practitioner | 2 | 0 |
| Diary state join | 5 | 0 |
| Unsafe confirmation bypass | 5 | 0 |

Explicit alternatives retain complete surfaced forms and source order.
Ambiguous identities remain unresolved. Corrected patients are searched by the
final identity and corrected practitioners resolve to the final surfaced
practitioner. Omitted or unknown practitioners fail closed to clarification
without default identity or mutation.

Diary comparison first matches the requested date/time, ignores unrelated
rows, retains pure utterance entity semantics, and exposes only the differing
field through a separate relation. Unsafe confirmation-bypass demands select
only `refuse_instruction` and produce no appointment/audit delta.

All seven report gates pass: D2 hash, exact current policy population,
selection hash, 20/20 contract behavior, zero variance, unchanged utterance
semantics, and no forbidden mutation.

## Worker failure and recovery

The Flash candidate provided useful standalone scaffolding but its own JSON
recorded false D2-report and population-hash gates while still declaring
completion. Its category verifiers auto-passed non-member or missing evidence,
and its final test skipped rather than failed. It also truncated location and
duration choices, silently resolved ambiguous identities, misread action verbs
as patient names, compared unrelated diary rows, and retained an implicit
practitioner fallback.

Sol rejected the completion evidence and used the recovery lease without a
worker correction loop. The recovered evaluator recomputes historical hashes,
dynamically verifies the exact current 20-case population, uses disjoint exact
category oracles, compares complete repeats, and derives its decision from all
seven gates. Runtime policy contains no scenario-ID, expected-field, or scorer
branch. Full provenance is in `lc4v4d3-sol-recovery-amendment.md`.

## Verification and independent veto

- Focused D3 plus unchanged semantic/D1/D2 suites: 252/252 passed serially.
- Adjacent deterministic interpretation/replay/scorer preservation gate:
  182/182 selected nodes passed serially.
- Two immutable historical exact-report nodes remained deselected and
  unchanged.
- `git diff --check` passed.
- Gemini independently reproduced all focused tests, hashes, exact category
  counts, seven gates, report regeneration, behavior boundaries, and incident
  containment on head `b0089662`, then returned `DECISION: pass` in
  `orchestration/agent_inbox/antigravity/lc4v4d3-independent-review.md`.

## Incident and authority decision

The pre-plan broad search incident exposed generic lines from a protected
support module. It is recorded in
`docs/bernie-lc4v4d3-preplan-protected-support-search-incident.md`, was not used
as evidence, and grants no holdout reuse authority. Gemini performed its review
under exact named-file restrictions.

LC4V4D3 is accepted as an explicitly versioned, development-only Option A
policy boundary. It is not wired into product routes, providers, databases, or
writes. A later bounded D4 may integrate the explicit policy version into the
ordinary composed development harness; it must not silently replace legacy
D1/D2 evidence or open product runtime authority.

LC4V4 remains an aggregate `certification_fail`. Holdouts v1-v4 remain sealed;
future certification requires Yuri's approval of a new holdout or reviewed
reuse policy. T3.1-T3.4 remain blocked, and T3.5/providers/live/write,
historical diary, API/UI, deployment, and release surfaces remain deferred.
