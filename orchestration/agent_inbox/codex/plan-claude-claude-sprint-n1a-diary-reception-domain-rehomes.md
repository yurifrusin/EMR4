# plan-claude-claude-sprint-n1a-diary-reception-domain-rehomes

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-n1a-diary-reception-domain-rehomes` |
| Status | integrated |
| Created | 2026-07-03 19:29 +1000 |
| Source HEAD | `0debced` |

## Plan Summary

N1a pure rehome: create app/services/diary/ and move four pure modules (capabilities/catalog, canonical temporal policy, reception frames, deterministic reception policy) out of app/services/bernie/, leaving bernie thin re-export facades so all imports resolve to the same objects. Wire strings reception_policy and bernie.reception_context.v1 byte-identical. No envelopes, allowed_authors, symbol renames, UI, routes, schema, or migrations (those are N1b/later).

## My Understanding

Executes accepted Amendment 1 (revised Fable/Ariadne/Yuri plan) as its N1a slice. The four target modules are pure contract code (no DB/LLM/wall-clock/session coupling; policy imports only frames; flat bernie_booking_interpreter already imports temporal from app.services.bernie.temporal). Same proven Sprint-106A pure-move-plus-facade pattern used for interpreter.py/context.py, but implementation lands in app/services/diary/ and app/services/bernie/{capabilities,temporal,frames,policy}.py become facades so existing import paths resolve to identical objects. N1b (envelopes, allowed_authors, authorship/boundary tests) is out of this slice.

## Intended Surface / Boundary

Backend Python service-layer packaging ONLY: new app/services/diary/ package + app/services/bernie/ facades + one new test file. 'diary' here means the backend domain package app/services/diary/, NOT any visual diary surface. Must-not-change (and untouched): diary grid geometry/rendering (docs/diary/diary.js), booking modal/slot UI, Waiting Room cards, status colouring, taskpane, all Word surfaces. Wire contracts held byte-identical: schema_version literal 'bernie.reception_context.v1' and reception_policy response field name.

## Out Of Scope

No DiaryActionIntent/Proposal/Confirmation/Suggestion envelopes, no allowed_authors/author provenance, no suggestion semantics, no explain_schedule/copy catalog, no knowledge substrate/GraphRAG, no migrations, no UI/copy/route/schema changes, no auto-mode, no Python symbol renames (Bernie* names kept this slice; neutral Reception* rename deferred to N1b). No master/handoff movement.

## Files I Expect To Edit

CREATE app/services/diary/__init__.py, app/services/diary/capabilities.py, app/services/diary/temporal.py, app/services/diary/frames.py (owns the bernie.reception_context.v1 literal), app/services/diary/policy.py (internal import -> app.services.diary.frames), tests/test_diary_domain_package.py. EDIT to thin facade: app/services/bernie/capabilities.py, temporal.py, frames.py, policy.py (re-export from app.services.diary.*, preserve __all__). EDIT docstring only: app/services/bernie/__init__.py (import/__all__ block unchanged). NOT touched: app/routers/appointments.py, app/schemas/appointments.py, docs/diary/diary.js, app/services/bernie_booking_interpreter.py, existing bernie tests (must pass unchanged).

## Implementation Steps

1) Create app/services/diary/; move verbatim bodies of capabilities/temporal/frames/policy into it; in diary/policy.py retarget the one internal import to app.services.diary.frames; keep all symbol names and the bernie.reception_context.v1 literal identical. 2) Write app/services/diary/__init__.py re-exporting the four modules' public names. 3) Replace the four app/services/bernie/*.py bodies with thin facades re-exporting from app.services.diary.* (preserve each __all__). 4) Update bernie/__init__.py docstring only; leave import/__all__ block byte-identical. 5) Add tests/test_diary_domain_package.py: cross-package object identity (bernie facade IS diary impl for each moved symbol, evaluate_reception_context, BERNIE_CAPABILITY_REGISTRY, temporal helpers), schema_version byte-identical literal, dumped frame-set JSON carries exact literal, and a 'diary does not import bernie' import-graph guard. 6) Run focused+full verification; fill Completion Notes; submit.

## Visual / Behavioural Acceptance Checks

No visual change whatsoever (docs/diary/diary.js byte-unchanged; grid, booking modal/slots, Waiting Room cards, status colours, taskpane untouched; no frontend files in diff). Full backend suite green UNCHANGED (pytest tests -q count matches pre-change). reception_policy JSON and schema_version literal byte-identical on interpret/supervised routes (existing wire tests pass without edits). New identity test proves bernie facade objects IS diary impl objects. grep invariant: bernie.reception_context.v1 has exactly one definition site (app/services/diary/frames.py); reception_policy field name unchanged. Verification: focused pytest (test_diary_domain_package, test_bernie_domain_package, test_bernie_temporal_policy, test_bernie_context_frames, test_bernie_interpret_booking_instruction, test_bernie_supervised_booking_wrapper) + full pytest tests -q + compileall + git diff --check.

## Risks / Ambiguities

Import ordering/cycles: low - diary never imports bernie; bernie import-graph topology unchanged (bernie.temporal still a module, now facade); guarded by an explicit import test. Wire/naming regression: the load-bearing risk; mitigated by single literal definition site, deferred symbol renames, byte-identical grep + existing wire tests. __pycache__ staleness in app/services/bernie: ensure fresh compileall. Scope creep toward N1b (envelopes/allowed_authors/authorship tests) deliberately excluded.

## Codex Plan Review

- Review result: Accepted by Ariadne. This is the primary N1a implementation
  lane for pure backend service rehomes and compatibility facades.
- Required changes before implementation: Keep this slice strictly
  no-behaviour-change. Do not add envelopes, allowed_authors, suggestion
  semantics, UI changes, route/schema changes, or migrations.
- Approved to proceed: yes, release with `complete sprint task`.
