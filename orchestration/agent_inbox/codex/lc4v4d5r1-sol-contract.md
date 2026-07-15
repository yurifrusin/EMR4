# LC4V4D5R1 Sol Contract

Date: 2026-07-16

Decision before implementation: `exact_four_remediation_frozen`

GPT Sol owns planning, taxonomy, acceptance, recovery, and protected
integration. DeepSeek V4 Flash/high through Claude Code `--bare` may produce
one bounded implementation/test candidate. Gemini 3.5 Flash through a fresh
Antigravity project supplies the independent veto. DeepSeek Pro is forbidden.

## Frozen source and evidence

- Integration baseline: `93575762c13bdf7dd7e0969fa5fb8057de9ce0b9`.
- Accepted D5 report hash:
  `sha256:e2c461ee3b1821c94574b33693efa88d21b99ecf9a95b1ac723b24a933c50564`.
- All-60 population hash:
  `sha256:ed65fe7821b0239066c532320bff05cc31a0699674987de8587efd74e05bbd44`.
- Legacy-60 baseline hash:
  `sha256:665851ffe055efb40f2ba1e43291d6b945c4764b4f441837781d4fc964d6ff27`.
- D4 report hash:
  `sha256:dd1ecc077a59bf05e777eda1f3a5450c0a1b97a4c8a3fd21dc0363d473abd653`.
- Exact-four target selection hash:
  `sha256:46325460205305a5a0826f097e21b673ed4fdca9c67c04bd0d387de2dc1685bd`.

The exact targets are:

1. `lc4v4d1_safety_move_safe_03`
2. `lc4v4d1_safety_resize_safe_05`
3. `lc4v4d1_safety_cancel_safe_07`
4. `lc4v4d1_safety_status_safe_09`

## Authorized implementation

Change only the general action-aware Option A resolution boundary. Do not
branch on scenario IDs.

1. A requested resize duration is a mutation target. Exclude it from diary
   identity/conflict comparison for `resize`, while retaining patient,
   practitioner, date, and time comparison and retaining duration comparison
   for other actions.
2. For supported safe `move`, `resize`, `cancel`, and `status_change` actions,
   emit the same deterministic simulated appointment and audit deltas already
   produced by the legacy replay contract:
   - appointment ID `apt-001`, patient ID `p-001`;
   - mapped practitioner ID;
   - normalized target date and start time;
   - normalized duration, defaulting to 15 minutes when omitted;
   - change types `moved`, `resized`, `cancelled`, or `status_changed`;
   - matching one-count audit delta; and
   - `is_simulated_confirmed_write: true`.
3. This is test-harness replay evidence only. It creates no runtime write,
   confirmation, route, API, database, UI, provider, or product authority.
4. Unsafe/prohibited, negated, ambiguous, unknown-practitioner, diary-conflict,
   and unsupported diary-state paths remain fail-closed with no mutation.

## Frozen postconditions

Run all 60 ordinary probes twice under legacy and twice under explicit Option A
and retain all 240 typed observations. The expected taxonomy is exactly:

- 37 `legacy_equivalent`, including the safe move and safe resize repairs and
  all three quarantined authoring-invalid probes;
- 20 `accepted_d4_versioned_change`, byte-for-byte behavior preserved;
- 3 `expected_versioned_relation`, exactly
  `lc4v4d1_diary_exact_duplicate_02`,
  `lc4v4d1_safety_cancel_safe_07`, and
  `lc4v4d1_safety_status_safe_09`, differing only by `diary_relation`;
- zero adoption blockers, unexpected differences, or Option A failures.

The exact three-relation selection hash is
`sha256:98df6544620da87e12df7df0d8afbdf0ad8e0f0eab16eab85385857158ab3188`.
The canonical empty blocker-selection hash is
`sha256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.

All D4 gates, all D5 safety/completeness/variance gates, the legacy-60 hash,
and the committed D4 and D5 historical report hashes must remain unchanged.
The four matched unsafe cases must still refuse with no deltas. The D4
duration-conflict behavior for non-resize actions must remain intact.

## Worker-owned candidate surface

- `app/services/bernie/lc4v4d3_policy_resolution.py`
- `app/services/bernie/lc4v4d5r1_remediation_evidence.py`
- `tests/test_bernie_lc4v4d5r1_remediation.py`
- `orchestration/agent_inbox/claude/lc4v4d5r1-deepseek-candidate.md`

The worker must not edit fixtures, generated D1-D5 reports, historical report
artifacts, the parser/extractor/scorer, AGENTS.md, or any protected surface.
Sol may generate new D5R1 report/acceptance/closeout artifacts only after
source review and serial verification.

## Closed boundaries

Holdouts v1-v4 remain sealed and unavailable. Do not open, enumerate, list,
search, import, run, regenerate, evaluate, hash-check, infer, or tune against
their fixtures, support/authoring modules, manifests, seals, receipts, tests,
filenames, or per-case evidence. T3.1-T3.4 remain intact and blocked; T3.5,
providers, historical diary material, product runtime/default changes, routes,
APIs, UI, database, deployment, release, and all live/write authority remain
deferred.

## Acceptance and recovery

The worker must return a durable candidate artifact with changed files, test
commands/results, exact taxonomy, hashes, and `DECISION: pass` or
`DECISION: revision_required`. A mechanical defect may receive at most one
bounded correction. A conceptual defect moves directly to Sol recovery without
a correction loop. Sol reviews the full diff, runs serial focused and adjacent
preservation gates, then requests a fresh exact-head Gemini veto before
integration acceptance.
