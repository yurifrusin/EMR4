# LC4V5R1 Sol Contract

Date: 2026-07-16

Decision before implementation: `development_only_three_family_repair_frozen`

Yuri authorized a fresh inspectable development-only remediation tranche after
the valid LC4V5 one-shot certification fail. GPT Sol owns the contract,
architecture, acceptance, recovery, and protected integration. DeepSeek V4
Flash/high through Claude Code `--bare` may produce one bounded candidate.
Gemini 3.5 Flash through a fresh Antigravity project supplies the independent
veto. DeepSeek Pro is forbidden.

## Evidence boundary

This contract is derived only from the aggregate LC4V5 closeout and newly
authored ordinary development probes. V5 is permanently consumed and sealed.
Do not open, enumerate, list, search, run, regenerate, hash-check, infer from,
or tune against any v5 case, fixture, authoring source, manifest, filename,
label, failure selection, or per-case evidence.

The three authorized aggregate families are handled in risk order:

1. create-approximate safety;
2. move-interval lossless normalization; and
3. ambiguous-resize clarification choices and tools.

No other semantic family is authorized by this tranche.

## Fresh development matrix

All probes use reference date `2026-07-16`, synthetic patient Margaret
Thompson, synthetic practitioner Dr Shera, and only test-owned diary state.
They are ordinary authored regression evidence, not holdout or promoted corpus
evidence.

### A. Create with approximate time

The first four one-shot requests must retain relation `approximate`, date
`2026-07-17`, and bounds `14:30`/`15:30`. Approximation is not an exact booking
target: extraction and Option A must require clarification with no invented
choices, authority `clarify`, tool sequence `request_clarification` only, no
completion claim, no appointment/audit delta, and no simulated confirmed write.

1. `Book Margaret Thompson with Dr Shera tomorrow around 3pm`
2. `Please make an appointment for Margaret Thompson with Dr Shera tomorrow about 3 pm`
3. `Book Margaret Thompson with Dr Shera tomorrow at around 3.00pm`
4. `Make an appointment for Margaret Thompson with Dr Shera tomorrow at about 15:00`

The two dialogues below must resolve to exact time, clear stale approximate
bounds from normalized values, and retain the established safe create tool and
replay contract only after the exact correction:

5. `Book Margaret Thompson with Dr Shera tomorrow around 3pm` then
   `Actually, make it exactly 3:15pm` -> exact `15:15`/`15:15`.
6. `Book Margaret Thompson with Dr Shera tomorrow about 3pm` then
   `No, make it exactly 15:20` -> exact `15:20`/`15:20`.

### B. Move to an interval

All six requests must retain relation `interval`; `normalized_values` must
contain the same final earliest/latest bounds as the top-level extraction.
Option A retains the established read-authority move contract and uses the
earliest bound as the replay-only simulated target start. No interval may be
collapsed into an exact point.

1. `Move Margaret Thompson's appointment with Dr Shera to tomorrow between 3pm and 4pm`
   -> `15:00`/`16:00`.
2. `Reschedule Margaret Thompson's appointment with Dr Shera tomorrow to between 15:00 and 16:00`
   -> `15:00`/`16:00`.
3. `Shift Margaret Thompson's appointment with Dr Shera to tomorrow from 3 pm to 4 pm`
   -> `15:00`/`16:00`.
4. `Move Margaret Thompson's appointment with Dr Shera tomorrow after 3pm but before 4:30pm`
   -> `15:00`/`16:30`.
5. `Move Margaret Thompson's appointment with Dr Shera tomorrow` then
   `Between 3pm and 4pm` -> `15:00`/`16:00`.
6. `Move Margaret Thompson's appointment with Dr Shera to tomorrow at 3pm`
   then `Actually, between 3:30pm and 4:30pm` -> `15:30`/`16:30`.

### C. Ambiguous resize duration

The first four requests must remain `resize`/`ambiguous`, require
clarification, retain no normalized duration, expose no invented choices,
select only `request_clarification`, and produce no deltas or simulated write:

1. `Make Margaret Thompson's appointment with Dr Shera longer`
2. `Shorten Margaret Thompson's appointment with Dr Shera`
3. `Change Margaret Thompson's appointment with Dr Shera duration`
4. `Give Margaret Thompson's appointment with Dr Shera more time`

Explicit alternatives and a resolved correction must remain lossless:

5. `Resize Margaret Thompson's appointment with Dr Shera to 30 or 45 minutes`
   -> ambiguous duration, choices exactly `30 minutes`, `45 minutes`, and
   `request_clarification` only.
6. `Make Margaret Thompson's appointment with Dr Shera longer` then
   `Make it 30 minutes` -> exact duration `30`, no clarification, and the
   established safe resize/update replay contract.

## Authorized implementation

- Make final top-level temporal evidence and `normalized_values` converge on
  the same latest relation and bounds after one-shot target extraction or a
  later correction. This must be general semantic reduction, not prompt- or
  scenario-specific branching.
- Treat a one-shot approximate create time as unresolved booking authority.
  Preserve its approximate relation and bounds as evidence, but require
  clarification before any create tool or simulated write.
- For under-specified resize duration, do not invent duration choices. Preserve
  explicitly surfaced numeric alternatives in utterance order, and clear them
  after an exact resolving turn.
- Preserve original utterances, normalized turns, action/entity semantics,
  source evidence, and all established negation/refusal rules.

## Frozen postconditions

- Baseline and repaired observations are retained for all 18 probes with two
  deterministic repeats each.
- Repaired result: 18/18 complete, 18/18 safe, and zero repeat variance.
- All one-shot create-approximate and unresolved resize probes have zero
  appointment/audit deltas and no simulated confirmed write.
- Existing exact, open-bound, interval, approximate, correction, safety,
  LC4V4D4, LC4V4D5, and LC4V4D5R1 tests remain green.
- No historical report, generated corpus fixture, or sealed artifact is
  regenerated or edited.

## Worker-owned candidate surface

- `app/services/bernie/semantic_extraction.py`
- `app/services/bernie/lc4v5r1_development_evidence.py`
- `tests/test_bernie_lc4v5r1_development.py`
- `orchestration/agent_inbox/claude/lc4v5r1-deepseek-candidate.md`

The worker must not edit fixtures, generated reports, existing historical
artifacts, policy resolution unless a concrete failing probe proves it is
strictly necessary, AGENTS.md, routes, APIs, UI, database code, provider code,
or any protected surface. Sol alone may amend adjacent runtime code under the
recovery lease, generate the final report, and write acceptance/closeout.

## Closed boundaries

Holdouts v1-v5 remain sealed and unavailable. T3.1-T3.4 remain intact and
blocked by default. T3.5, provider calls, local-model development use,
historical diary access, product runtime/default changes, routes, APIs, UI,
database writes, deployment, release, and all live/write authority remain
deferred.

## Acceptance and recovery

The worker returns a durable candidate artifact naming changed files, focused
and adjacent tests, before/after counts, repeat variance, and `DECISION: pass`
or `DECISION: revision_required`. One mechanical correction is permitted; a
conceptual defect moves directly to Sol recovery. Sol reviews the complete
diff, runs serial focused and preservation gates, and requests a fresh
exact-head Gemini independent review before final acceptance.
