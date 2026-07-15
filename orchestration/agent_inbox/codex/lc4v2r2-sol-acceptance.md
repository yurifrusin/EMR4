# LC4V2R2 Sol Acceptance

## Decision

**DECISION: pass**

GPT Sol accepts the recovered LC4V2R2 development-only safety-language repair
at exact independently reviewed head
`ae4304f8834a008b17a2a211c778c6418da88762`.

## Accepted evidence

- Sol-authored fixture: 28 unique Gold/adjudicated development probes in 14
  matched unsafe/safe pairs;
- fixture SHA-256:
  `a018f060025af3defb2605c514422841834a9370260b51b63ef765408f72ba3a`;
- immutable baseline: 17/28 complete and 11 failures, selection
  `05c3a865bf1df2c2`;
- recovered result: 28/28 for intended action, action semantics, authority,
  action negation, no-completion claims, tool requirement, and complete;
- recovered failure selection: empty, `e3b0c44298fc1c14`;
- canonical report hash:
  `sha256:6cec58fe319a070b2c0f6d2cf0d99f74dc0f4b98352b3268709da2abc400f750`;
- two-repeat variance: zero across 56 fixture evaluations;
- recovered focused/regression suite: 295/295 passed;
- final serial preservation gate: 464 collected nodes, 462 passed, one
  expected xfail, and one expected skip;
- ordinary development semantic counts unchanged at
  `880/814/672/154/330/835`;
- ordinary development safety unchanged at 1,152/1,152;
- ordinary development variance unchanged at zero over 2,304 samples; and
- ordinary development corpus hash unchanged at
  `sha256:af8f3276a50a2defcf4e4f65570a5dd4de0d252544ff6d695792d63e7e518195`.

The accepted parser distinguishes positive safeguard-bypass demands from
explicitly negated guardrails and safe action negation. It resolves double-
negation and `no need` scope, keeps truthful post-confirmation wording safe,
does not confuse appointment-time choice with patient-identity guessing, and
handles a contextual single given name conservatively as ambiguous.

## Worker and recovery decision

DeepSeek V4 Flash/high through Claude Code `--bare` wrote an uncommitted
candidate after its outer launcher timed out, then entered repeated pytest-
summary extraction loops. Sol rejected its self-pass because its candidate hash
was unset, two aggregate claims were wrong, and several regexes overmatched
outside the fixture. The verbatim candidate is preserved at `6c091d59` and
`8ea0f6c4`; Sol recovered under the Ariadne lease without a correction call.

## Independent veto

Gemini 3.5 Flash/medium returned `DECISION: pass` on exact recovered head
`ae4304f8`. It independently reproduced all three checks, 295/295 tests,
fixture/report binding, false-positive guards, staged tool policy, provenance,
and clean-worktree evidence.

## Protected-evidence incident and boundaries

One Sol recovery search unintentionally returned protected v1 fixture path
names. No protected content, label, manifest, seal, receipt, hash-check,
evaluation, inference, or tuning occurred. This metadata-only incident is
recorded in the recovery amendment and does not authorize reuse. Both holdouts
remain sealed.

T3.1-T3.4 remain intact and blocked by default. T3.5, providers, historical
diary, routes/API, database, UI, deployment, runtime, memory, confirmation,
release, and write authority remain closed.

## Next work

Do not predeclare LC4V2R3. First run a bounded development-only exit-gap
reassessment using the frozen R1/R2 evidence and ordinary development aggregate
only. A further repair tranche is authorized only if that reassessment freezes
a new independently surface-supported gap. Any certification requires Yuri's
separate approval for a fresh holdout or reviewed reuse policy.
