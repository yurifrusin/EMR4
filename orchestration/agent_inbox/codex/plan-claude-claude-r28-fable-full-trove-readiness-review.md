# plan-claude-claude-r28-fable-full-trove-readiness-review

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Model | claude-fable-5 (Claude Fable 5, high-reasoning consult) |
| Branch | `claude/fable-full-trove-readiness` |
| Source Task | `claude-r28-fable-full-trove-readiness-review` |
| Status | pending_plan_review |
| Created | 2026-07-06 15:08 +1000 |
| Source HEAD | `5ee23ea1` |

## Plan Summary

Fable full-trove readiness review: do not open broad 58k-file trove processing or the H15 semantic gate yet; neutral evidence has saturated and the blocker is missing consumers, not missing guardrails. Build native Bernie/Diary action grammar and a replay consumer first, then prepare an H15 gate-review packet for Yuri, then run the one-time full-trove mining pass. GraphRAG stays a local fixed-query research runway until post-gate semantic fixtures and an Access AI read capability exist. Full review body follows in this packet.

## My Understanding

R28 asks four questions: (1) when should EMR4 use the full local 58k-file diary
trove, (2) is H15 semantic-gate work ready, (3) what architecture should govern
source-safe aggregate/profile refreshes, GraphRAG-shaped derived memory, and
Bernie/Diary action grammar, and (4) what is the next 2-4 sprint direction.

Evidence reviewed: `AGENTS.md`, `docs/h-series-profile-schema.md`,
`docs/historical-diary-trove-plan.md`, the H15 gate doc
(`docs/historical-diary-trove-semantic-labelling-gate.md`), the H5
de-identification contract, the H17 cross-pilot trend and H20 graph-report
docs, the R26 profile fixture (`tests/fixtures/h_series_profiles/`) and schema,
the R27 consumption guards in `tests/test_h_series_profile_consistency.py`, the
DeepSeek adversarial review
(`docs/adversarial/h_series_profile_consumption_review_r27.md`),
`docs/receptionist_review_r27.md`, `orchestration/protocol_alerts.md`,
`orchestration/phase_programmes.md`, `orchestration/parallel_workstreams.md`,
and `orchestration/sprint_closeout.md`.

Three findings drive the verdict:

1. **The neutral pipeline has saturated.** Across H17 (297 transitions, 3
   roots) plus H21 (156 transitions, 4 roots), roughly 99 percent of adjacent
   transitions are `no_structural_change` or `small_content_delta`; the only
   two notable deltas (one `time_grid_delta`, one `large_unexplained_delta`)
   were shown isolated by H12-H14. H16 (Friday) and H21 (Thursday) reproduced
   the same shape on new roots. More neutral sampling now yields near-zero new
   information. The trove's remaining value is semantic - real event grammar,
   churn rhythms, edge cases - which is exactly what the H15 gate correctly
   blocks.
2. **Runtime reality bounds the full pass.** H11 measured roughly 0.7 seconds
   per file via read-only Word COM, so the full 58k trove is roughly 11 hours
   of single-threaded, fragile COM work. That spend should happen exactly once,
   with a semantic-capable pipeline and checkpointing, not on more neutral
   counts.
3. **The safety substrate is genuinely strong and should not be relitigated.**
   The H5 output validator fails closed; H10 caps default-bound broad runs;
   the H15 gate is blocked by default with an explicit approval shape; the R26
   profile layer is structurally isolated from Bernie scenarios; and R27
   closed the schema-drift and cross-contamination vectors DeepSeek identified
   (schema_version enforcement plus the profile/scenario isolation test).

## Intended Surface / Boundary

This plan/review packet under `orchestration/agent_inbox/codex/`, plus
status-line and completion-note updates to the source task packet, via the
protocol plan/claim/submit path only. No visual surface is affected. Surfaces
that must NOT change: `tests/fixtures/h_series_profiles/`,
`tests/fixtures/bernie_scenarios/`, `tests/test_h_series_profile_consistency.py`,
all `docs/historical-diary-trove-*` and H-series docs, `app/` backend, diary
grid UI, taskpane, command centre, migrations, provider code, raw
`local_data`, and ignored JSON.

## Out Of Scope

Production code, tests, raw `local_data`, ignored JSON, semantic appointment
labelling, provider calls, frontend UI, migrations, `master`/`handoff/current`
movement, and any broad trove processing. Also out of scope: flipping or
editing the H15 gate template, adding profiles or fixtures, and any Bernie
scenario corpus change.

## Files I Expect To Edit

- `orchestration/agent_inbox/codex/plan-claude-claude-r28-fable-full-trove-readiness-review.md` (this packet)
- `orchestration/agent_inbox/claude/claude-r28-fable-full-trove-readiness-review.md` (status + completion notes only)

Nothing else.

## Implementation Steps

This is a consult; the steps are the recommendations.

### 1. Readiness verdict

The full trove is **not ready for broad utilisation now**, and the cause is
missing consumers, not missing guardrails. Broad processing today would spend
roughly 11 hours of COM to reproduce already-known neutral counts. Defer the
full pass until it can mine semantic value for a consumer that exists.

### 2. Ordering principle: grammar before labels, labels before mining, mining before memory

- **(a) Native Bernie/Diary action grammar first.** A typed, versioned
  event/action vocabulary (create, move, resize, cancel, status-change,
  check-in, link-patient, break/roster change) aligned with the existing
  proposal/confirm routes and the deterministic backend write authority. This
  defines the target vocabulary that any future semantic labelling must map
  onto; labelling first would invent a vocabulary that later fights the native
  one.
- **(b) Replay consumer second.** A deterministic harness that replays
  authored synthetic day slices expressed in that grammar - no trove data -
  proving the consumer that H-derived semantic fixtures would eventually feed.
- **(c) H15 gate-review packet third.** A local-only semantic extraction
  prototype on one small day slice; extend the H5 validator family with a
  gate-approved semantic allowlist (synthetic IDs, date-shifted dates,
  time-of-day, durations, status labels, transition labels, and the confidence
  enum already defined in the trove plan's Stage 3). Draft the gate payload and
  present it to Yuri as a decision packet. Do not flip the gate inside a
  sprint.
- **(d) Full-trove processing last, and only once.** After Yuri approves H15
  and the replay consumer exists, run the single capped-lifted pass (explicit
  `-AllowLargeRun` with a written justification) with checkpointing/resume,
  mining candidate day slices for fixture promotion and refreshing neutral
  profiles as a side effect.

### 3. H15 readiness

The **mechanics are ready** - the gate script and blocked template are well
designed - but the **decision is not**. Preconditions for a credible gate
packet: a stable native grammar (the target vocabulary), a demonstrated
small-slice semantic extraction passing a strengthened validator, a
consumption-side leakage control, and a named replay consumer. None exist yet,
so H15 stays closed. On leakage: the DeepSeek R27 review correctly showed that
YAML validators cannot catch semantic leakage in test docstrings and test
code; add a merge-time review rule or a repo lint for forbidden vocabulary in
H-derived test files **before** any semantic fixture exists.

### 4. GraphRAG / derived-memory architecture

Keep the layered ladder explicit and one-directional:

```text
raw trove (local, ignored, never sent to any provider)
  -> validator-safe ignored aggregates
  -> committed neutral profiles (R26 layer)
  -> post-gate committed de-identified synthetic semantic fixture families
  -> much later, a read-only derived graph store
```

Preserve the H20 design decision permanently: **fixed typed query IDs only, no
free-text graph search**. If Bernie ever consults derived memory, it must be a
registered Access AI capability (Programme 2F) with entitlement, audit, and
prompt-consumption gates, returning advisory explanation frames only - never
availability evidence, never write authority. GraphRAG remains a local
research runway until semantic fixtures exist and a concrete receptionist
utility question justifies a dedicated retrieval-boundary sprint.

### 5. Fine-tuning position (unchanged)

Never on raw diary content or authoritative state transitions; only ever on
approved synthetic or de-identified derived phrasing examples, and only if
RAG/GraphRAG over approved material proves insufficient - which nothing
observed so far suggests.

### 6. Fable timing

Spending Fable on this checkpoint was the right call: R27 is integrated
locally and the live decision is exactly full-trove/H15/GraphRAG. After access
lapses at the end of July 7, 2026, this packet is the durable decision
framework; future sprints should execute against it without another high-cost
review. If any Fable window remains and a native grammar draft materialises
inside it, a Fable pass over that grammar is the only other high-leverage use.
Do not rush a grammar draft merely to consume the window.

### 7. Next 2-4 sprints

1. **Sprint +1 - Native Diary action grammar foundation.** Typed event
   vocabulary, versioned contract, backend-only; anchored in Programme 2B
   mutation contracts with 2D as consumer. Matches the
   `receptionist_review_r27` product direction.
2. **Sprint +2 - Grammar replay harness skeleton.** Deterministic replay over
   authored synthetic day slices; H-series profiles may guard isolation
   invariants only, per R27 rules.
3. **Sprint +3 - H22 gate-review packet preparation.** Small-slice local
   semantic extraction prototype, semantic-output validator extension, the
   leakage lint, and a draft gate payload for Yuri review. The gate stays
   blocked throughout.
4. **Sprint +4 (conditional on Yuri approving H15).** First bounded semantic
   fixture family from one date-shifted day slice plus replay tests; only then
   schedule the one-time full-trove mining run.

## Visual / Behavioural Acceptance Checks

This review explicitly preserves all four required invariants:

1. No raw trove content is ever sent to an LLM or external provider.
2. No fine-tuning on raw diary files or authoritative state transitions.
3. The H15 semantic gate remains closed unless Yuri explicitly approves a
   reviewed gate payload.
4. The deterministic native backend remains the sole write authority for
   availability, collisions, transitions, signed evidence, audit, and route
   permissions; derived memory is advisory only.

Behavioural acceptance: no production file changes; verification is artifact
inspection plus `git diff --check`. Merge criteria are met when Ariadne holds
the readiness verdict, the grammar-first ordering, the GraphRAG/derived-memory
boundary, the H15 precondition list, and the sprint direction above.

## Risks / Ambiguities

- **Rejected alternative 1: open H15 now to use Fable while available.**
  Rejected because the prerequisite consumers (grammar, replay harness) do not
  exist; semantic fixtures produced now would be evidence without a court, and
  the gate's value is its review discipline.
- **Rejected alternative 2: broad neutral processing of all 58k files now.**
  Rejected on saturation grounds; it burns roughly 11 hours of fragile COM for
  near-zero new information and creates pressure to justify the spend with
  semantic overreach.
- **Risk:** the neutral-profile layer ossifies into ceremony. Keep it to one
  fixture per genuinely new observed shape, not one per sampling run.
- **Risk:** the eventual full-trove COM pass is long and fragile. Run it once,
  with checkpointing/resume and a written `-AllowLargeRun` justification.
- **Risk:** once semantic work begins, leakage moves from YAML (validated)
  into test code and docstrings (unvalidated); the leakage lint in Sprint +3
  must land before any semantic fixture exists.
- **Ambiguity:** whether the grammar sprint belongs to Programme 2B or 2D;
  recommendation is to anchor it in 2B mutation contracts and let 2D consume
  it.
- **Process note:** the packet's own submit commit message reads like the
  dispatch message ("Dispatch Fable full-trove readiness review"); used
  verbatim per protocol.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
