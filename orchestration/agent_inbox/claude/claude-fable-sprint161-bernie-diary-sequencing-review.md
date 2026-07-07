# Fable Sprint 161 - Bernie/Diary Sequencing Review

## Mission

Ask Fable for a bounded strategic second opinion on the next Bernie/Diary
sprints after Yuri's first hands-on Diary review.

The specific decision is whether prompt-thread automation should start now, or
whether another workstream should still take priority before that automation
becomes useful.

## Current State

- Sprint 160 produced a Bernie/Diary review-readiness packet:
  `orchestration/bernie_diary_review_readiness_sprint160.md`.
- Yuri then ran the Diary/Bernie surface and reported that the basic
  `Margaret Thompson` prompt worked as well as the basic `bernie-diary`
  response.
- Two local review blockers were corrected before this consultation:
  - `run_dev.ps1 -LiveAiSurface Diary -SkipAdcLogin` no longer forces the live
    Bernie provider by default while the runtime/provider gate is blocked.
  - The local database was migrated to Alembic head after the Diary appointments
    endpoint returned 500 due to the missing appointment status reason column.
- Yuri suggested building a series of prompts, including clarifications and
  changes to initial requests, possibly informed later by the historical diary
  trove, so Bernie/Diary can be exercised automatically.
- Codex agreed this is important, but Yuri challenged whether it is the right
  immediate priority given the larger sprint plan.

This packet asks Fable to adjudicate that sequencing question.

## Yuri's Added Readiness Question

Please answer this directly, not only by implication:

Does the current Diary/Bernie system have strong and able enough bones, sinews,
and muscles to make automatic prompt testing and troubleshooting worthwhile at
this stage?

In more operational terms:

- Are the current route contracts, proposal/confirm paths, fake-provider
  interpreter, clarification merge behavior, route-intercepted Diary review
  surface, and scenario/replay fixtures mature enough that automated prompt
  testing would produce useful troubleshooting signal rather than mostly noise?
- If not yet, what exact missing structural capability, behavior, or evidence
  threshold would make prompt automation worthwhile?
- Should the threshold be framed as a technical gate, such as stable
  clarification/change-request semantics, selected-slot pivot behavior, live
  backend evidence, provider-boundary review, or a minimum route-level scenario
  corpus?
- Which defects should still be found by Yuri's hands-on review before a prompt
  automation harness can carry meaningful weight?

## Existing Relevant Surfaces

Please treat these as source context:

- `AGENTS.md`
- `orchestration/bernie_diary_review_readiness_sprint160.md`
- `orchestration/bernie_release_gates.md`
- `orchestration/api_spine_adr.md`
- `orchestration/api_spine_programme.md`
- `orchestration/access_ai_api_design.md`
- `tests/bernie_scenarios/README.md`
- `tests/test_bernie_clarification_merge.py`
- `tests/fixtures/bernie_scenarios/`
- `tests/fixtures/h_series_profiles/stable_grid_small_delta_h21.yaml`
- `tests/test_h_series_profile_consistency.py`

Codex note: the API steward skill references `references/review-checklist.md`,
but that file is not present in the current checkout.

## Gate Constraints

Do not recommend any step that opens these gates incidentally:

- no raw historical diary trove files outside local ignored processing;
- no committed raw, extracted, or PHI-bearing diary text;
- no broad 58k-file trove processing;
- no H15/H-series runtime imports into Bernie, Access AI, providers, memory, RAG,
  GraphRAG, routes, or UI;
- no historical diary material in prompts, provider calls, memory, or executable
  Bernie scenarios;
- no provider prompt wiring, provider dry-run wiring, or live-provider
  enablement unless the provider-boundary gate is explicitly reviewed first;
- no model-to-database writes, GraphQL mutations, or bypass of signed
  proposal/confirm commands;
- no weakening of staff confirmation, idempotency, audit, freshness, or
  route-authority boundaries.

The H-series neutral profile layer may be considered only as a source of very
coarse coverage categories, such as stable-grid review, refresh/no-write
posture, small neutral change, or layout stability. It must not supply
appointment semantics, patient/practitioner/resource parameters, prompt text, or
provider context.

## Decision Options To Rank

Please rank the next 3-5 sprints among these or propose a better sequence:

1. **Review friction triage first**
   Fix any concrete Diary/Bernie issues from Yuri's review before building a
   larger prompt corpus.

2. **Small authored prompt-thread automation now**
   Build a deliberately small, hand-authored, source-safe test harness for
   multi-turn receptionist prompts: initial request, clarification, change of
   date/time/practitioner/duration, selected-slot pivot, confirm-required
   boundary, and no-write assertions.

3. **Live backend/provider evidence next**
   Move toward narrower non-intercepted backend or provider evidence before
   investing in prompt automation.

4. **Historical-diary-informed coverage taxonomy only**
   Use H-series neutral profiles only to name coverage categories, while keeping
   all prompt strings and executable semantics hand-authored synthetic.

5. **Delay prompt automation**
   Continue API-spine or command-surface work first, and revisit prompt
   automation after another readiness milestone.

## Questions For Fable

1. Is prompt-thread automation the right next sprint after Yuri's first basic
   review, or is it one layer too early?
2. If it is early, what should be completed first?
3. If it is right now, what is the minimum useful scope that avoids pretending
   to be a full training harness?
4. Which existing surfaces should the automation consume: current
   `tests/bernie_scenarios`, route-level interpret endpoint tests,
   route-intercepted Diary UI tests, or a new small harness?
5. How should clarification and change-request behavior be prioritized relative
   to live-provider/backend evidence?
6. When, if ever, should H-series neutral profiles influence the prompt
   automation? Please distinguish coverage taxonomy from executable prompt
   semantics.
7. What acceptance criteria should make Yuri's next review meaningful without
   opening provider, memory, H15/H-series, or broad-trove gates?
8. Does the current implementation have enough structural maturity for prompt
   automation to be diagnostic now? If not, name the concrete point at which it
   becomes diagnostic.

## Requested Output

Write a concise recommendation packet under:

`orchestration/agent_inbox/codex/plan-claude-fable-sprint161-bernie-diary-sequencing-review.md`

The packet should include:

- a clear verdict: prompt automation now, after one or two prerequisite sprints,
  or later;
- a direct answer to Yuri's "bones, sinews, and muscles" readiness question;
- ranked next 3-5 sprint recommendations;
- explicit no-go boundaries for historical diary/trove usage;
- the smallest useful prompt-thread automation scope if recommended;
- risks and acceptance criteria;
- any concrete files/tests Fable thinks should be touched first.
