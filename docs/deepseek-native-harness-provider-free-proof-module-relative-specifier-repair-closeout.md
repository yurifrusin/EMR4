# DeepSeek native Harness provider-free proof-module relative-specifier repair closeout

Date: 2026-08-21
Timestamp: 2026-08-21T13:48:50.6623983+10:00 (Australia/Brisbane)
Reviewed candidate: `3c31f2a9a44713db27b82e338e05374c5d9f62bc`

## Outcome

Accepted as a provider-free two-row profile repair.

The bounded-worker profile now emits:

- `../../../installation/proof/sentinel.mjs`; and
- `../../../installation/proof/runner.mjs`.

The diff against accepted diagnosis source
`f735e6c9f4412aea8e83e410c0292668ebe7853f` contains exactly those two
module-name replacements and removal of the now-unused local `proof` path.
No other generated profile row, runner/controller behavior, retry/tool/preset
contract or product source changed.

## Verification

- provider-free evidence: `passed`;
- source checks: 6/6;
- generated-profile checks: 11/11;
- focused repair plus bounded-profile tests: 30 passed;
- widened repair/profile/attempt/controller/diagnosis tests: 56 passed;
- JSON Schema, Ruff, Python compilation and diff checks: passed; and
- Node, Harness, broker, worker, model, provider and network activity: zero.

Three historical assertions were explicitly deselected: one requires the live
latch still to be attempt 004, and two bind the accepted pre-repair controller
source hash. They remain immutable and were not weakened or regenerated.

Four bounded procedure incidents were caught before acceptance: missing direct-
script import bootstrap, an overbroad dead-local guard, an unsupported wrapper
option and selection of frozen source-binding equality checks. Each is
corrected or contained in revision 587; none remains open.

## Parallelism efficacy

DeepSeek and Gemini were declined because this latch forbade model/provider
activity. Native subagents were declined because current developer policy
prohibits proactive delegation and the exact repair was serial. GPT Sol owned
the implementation and verification. Reassess Gemini only if a later frozen
boot-proof authority permits provider review; the next boot itself remains
provider-free.

## Boundaries preserved

No Node or Harness process ran and no occupied attempt was retried. Attempts
001-004 remain immutable and consumed. No raw terminal material was
reconstructed. No product, data, database, route, feature flag, client,
waiting-area, production, deployment, release, Pages or protected ref changed.
`docs/branding/` and all unrelated untracked files remain preserved.

## Next operation

Freeze `deepseek-native-harness-provider-free-repaired-sentinel-native-boot-proof`.
It may launch exactly one bounded rc7 Node/Harness process with only the
initial repaired sentinel profile, require one HMR-ready event, prohibit the
changed runner, broker, model and provider, then prove exact cleanup. It is not
an occupied DeepSeek worker attempt and cannot establish worker reliability.
