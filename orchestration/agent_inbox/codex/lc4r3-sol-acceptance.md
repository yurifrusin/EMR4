DECISION: pass

# LC4R3 Sol Acceptance — Aligned Action-Surface Closure

Date: 2026-07-14

Conductor, planner, architecture/acceptance owner, recovery owner, and
protected integrator: GPT Sol.

## Authority and provenance

Sol planned LC4R3 directly. DeepSeek V4 Flash/high through Claude Code `--bare`
implemented the candidate and revision. Its two `DECISION: pass` artifacts are
preserved as worker evidence, not self-acceptance. Sol rejected defects in both
evidence drafts, adopted the bounded candidate under the recovery lease, and
owned the final evidence-only amendment. Gemini 3.5 Flash/medium through a
fresh Antigravity worktree independently reviewed exact head `b5b15e6e` and
returned `DECISION: pass`. DeepSeek Pro was not used.

## Accepted result

The deterministic, text-only extraction boundary now recognizes:

- 16/16 aligned anchored `New booking:` create surfaces;
- 13/13 aligned contextual `call off ... booking/appointment` cancellations;
- 80/80 aligned practitioner schedule/availability questions; and
- 45/45 aligned explicit arrival/status commands.

The frozen target is exactly 154/154. Overall intended-action passes improve
from 720/1,152 to 880/1,152. The six additional passes are the same explicit
cancel/status surface families in cases excluded from the aligned target by
other Silver contract conflicts; they are not regex spillover.

`check in` remains a distinct planned-not-implemented action, and thirteen
aligned check-in plus thirteen bare-arrival adjacent cases remain unpromoted
and non-mutating. Generic availability/calendar/roster/day-view/pull-up/status
language is covered by anti-overmatch tests.

All other semantic baselines are preserved or improved:

- action semantics: 674 -> 730;
- temporal relation: 628 -> 628;
- normalized values: 101 -> 101;
- entity semantics: 255 -> 255; and
- clarification semantics: 642 -> 698.

Safety remains 1,152/1,152. The candidate-quality audit measured zero
per-scenario observation/safety variance over 2,304 samples. The frozen LC4R2
report hash remains `cba97acd3f23d2ec`; LC4R3 has its own report hash
`9ebfcc4a00c8e432` with target/deferred selection hashes.

## Verification

Sol verified:

- 215 focused/existing semantic and action-grammar tests passed;
- the scaled evaluator passed 60/60 with its frozen historical exact-report
  regeneration node excluded;
- the broad composed T1/T2/T3.1-T3.4 preservation suite passed with one
  expected xfail and one skip after deselecting only the LC3 and LC4R2 frozen
  exact-report comparisons;
- the real `tomorrow at 3pm` interpret-then-duplicate route regression passed;
- eight Ariadne preflight/rehydration tests passed;
- the live shadow gate remained `decision: blocked`, external calls false,
  runtime authority false;
- the LC4R3 report check and `git diff --check` passed; and
- master, origin/master, and `handoff/current` remained untouched during the
  sprint.

Gemini independently reproduced 60 focused/report tests, 155 existing
semantic/grammar tests, ten route smoke tests, eight preflight tests, 51 shadow
tests, and the development scale evaluator with the frozen exact-report node
excluded.

## Protected-evidence incident

During Sol's post-compaction orientation, a broad filename command enumerated
protected fixture path names. This violated the no-enumeration process rule.
No protected file was opened, read, imported, evaluated, or tuned against, and
no semantic content or labels were exposed. The incident is explicitly
recorded in the LC4R3 report and was independently reviewed by Gemini. It does
not authorize reuse of protected holdout v1.

## Boundaries and continuation

No development fixture, scenario schema, action grammar/route contract,
provider, API/route, database, UI, deployment, historical diary, memory,
RAG/GraphRAG, T3.5 adapter, or live/write authority changed. T3.1-T3.4 remain
preserved and blocked by default.

Post-LC4R3 development profiling leaves 584 aligned-failure records. Only 26
still miss intended action; the largest remaining semantic gaps are normalized
values (489) and entity semantics (485), followed by clarification (241) and
action semantics (201). The next sprint should be a bounded LC4R4
normalization/entity tranche derived from aligned development surfaces, with
fixture conflicts kept separate and protected holdout v1 sealed.
