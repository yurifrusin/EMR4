# Bernie Stage 3A — Yuri Formative Observation Review

Date: 2026-07-20

Owner: Yuri / GPT Sol Extra High

Decision: `revision_required_pending_bounded_rerun_and_s3a06`

## Evidence received

Yuri completed and explicitly downloaded one Stage 3A structured observation
export. Its exact identity is:

- filename: `bernie-stage3a-stage3a-dafd72af-a948-456e-92bb-8a1d6267e57c(1).json`;
- SHA-256: `2e162be00132e2a8cf149d506de24015a571011b98206e5078c6db9eff5da3ba`;
- size: 11,419 bytes;
- schema: `bernie.stage3a.study-export.v1`;
- evidence mode: `authored_synthetic_fixture_browser`; and
- observations: 14, one for every S3A-01 through S3A-14 scenario.

The export passed a field-level safety screen. It declares
`contains_prompt_or_transcript_text: false` and contains no typed prompt,
transcript, audio, credential, header, provider output, free-text comment, or
real patient/practice field. The raw download remains outside the repository;
only its hash and bounded aggregate findings are retained here.

## What the first run established

The product direction received encouraging formative evidence:

- 11 scenarios were recorded as completed, one as completed after
  clarification, and two as safely blocked;
- no scenario was recorded as failed or as requiring a grid fallback;
- 11 projections were rated useful, two neutral, and one not recorded;
- the proposal scenario was correctly identified as a proposal rather than a
  write;
- the ambiguity scenario recorded one clarification rather than a silent
  identity choice; and
- the stale/replay and fixture-confirmation boundaries were safely blocked in
  the study surface.

These are Yuri-only formative observations. They do not establish a
representative-staff usability threshold, a language-model result, or a live
event/runtime result.

## Why Stage 3A cannot pass yet

The first run exposed correctable study-instrument problems that contaminate
part of the evidence:

1. **Scenario state carried over.** The selected grid date, prior projection,
   enabled routes, and attention delivery state could remain visible after the
   next scenario began. S3A-04 visibly inherited S3A-03 context, and the event
   fired while exploring S3A-01 caused S3A-12 to be classified as a duplicate.
2. **Required comparisons were not enforced.** S3A-03 and S3A-11 were recorded
   without visiting their ordinary-grid route; single-route tasks could also
   receive unintended grid visits.
3. **Appointments were not guaranteed to be chronological.** Yuri specifically
   identified this in the practitioner projection.
4. **Event tasks were underspecified.** S3A-13 exercised only the unrelated
   roster fixture instead of its full suppression population. S3A-14 happened
   to exercise the intended replay/ordering population correctly.
5. **Event scope was too easy to misread.** The notice omitted its appointment
   date, which made the July fixture appear capable of changing the separate
   January six-month answer.
6. **Observation language was unclear.** “State understood”, “committed
   action”, “completed with clarification”, and the fixture-only meaning of
   S3A-06 required facilitator explanation. The event scenarios also lacked an
   appropriate committed-change-notice/suppression choice.
7. **Qualitative issues could not be retained.** Yuri had no approved place to
   record the chronology or state-carryover observations.

S3A-06 also still lacks its separately labelled visible local Diary → FastAPI →
PostgreSQL confirmation check. Therefore neither `stage3a_pass` nor
`stage3a_partial` is currently supported.

## Bounded corrections

The following corrections stay inside section 10 of the frozen Stage 3A plan:

- each scenario now begins with a clean input, projection, grid-date,
  observation, and attention baseline;
- only the routes authorized for the active scenario are enabled;
- paired tasks cannot be recorded until both routes have been visited;
- Margaret's full upcoming task cannot be recorded until each authored date
  has been inspected in the grid;
- practitioner and patient projections are sorted by date and start time;
- authored availability is visible in the ordinary-grid comparison;
- S3A-12 through S3A-14 display and enforce their exact fixture order;
- S3A-12 and S3A-14 require the current-view projection before recording;
- the event notice now includes Friday 31 July 2026;
- S3A-06 and the observation labels explain answer, proposal, confirmed Diary
  change, committed-change notice, suppression, and separate safety check;
- optional allowlisted structured issue flags capture chronology, carried-over
  context, instruction, label, scanning, and route-comparison problems without
  accepting free text; and
- the export is versioned as `bernie.stage3a.study-export.v2` and upserts one
  observation per scenario.

No API call, mutation, event runtime, provider, PII, voice, persistence,
telemetry, transcript, or free-text retention was added.

## Exact bounded rerun

Yuri need not repeat the whole study. The affected functional population is:

`S3A-03, S3A-04, S3A-06, S3A-11, S3A-12, S3A-13, S3A-14`.

This rerun checks chronological ordering, clean scenario transitions, the
fixture/authoritative-confirmation boundary, complete patient-grid coverage,
and the three exact event-attention populations. The comprehension findings
from S3A-02, S3A-07, and S3A-09 remain valuable formative evidence and are not
erased; their triggering copy has been corrected and is represented in the
rerun where the new state choices matter.

After Yuri downloads and returns the new v2 export, Sol runs the separate
S3A-06 `live_local_browser_backend_postgres` check. Only then can the final
Stage 3A decision be `stage3a_pass`, `stage3a_partial`, or a continuing
`revision_required`.

## Final addendum — 2026-07-20

Yuri returned the exact corrected v2 export at SHA-256
`55146de6b7ad2743acf5ce9505230a39c5ff8a641f366d5018d2689282359ffb`.
The seven-scenario rerun and separate visible local confirmation/database check
both passed. Yuri's immediate post-export correction of S3A-06 from
`suppressed_events` to `Separate safety check — not run here` is preserved as a
facilitator clarification and wording finding; the raw export was not altered.

The final authoritative decision is `stage3a_pass` in
`docs/bernie-stage3a-final-validation-closeout.md` and
`orchestration/agent_inbox/codex/bernie-stage3a-final-sol-acceptance.md`.
