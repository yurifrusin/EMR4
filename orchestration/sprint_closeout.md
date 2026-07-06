# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint H31: Access-AI and Read-Only Memory Boundary Review |
| Integrated through | Ariadne implementation |
| Status | Integrated locally; focused verification passed; not yet pushed |
| Last updated | 2026-07-06 |

## What Changed

- Added `schema_version: h_series.neutral_profile.v1` to the committed H-series profile fixture.
- Updated `tests\test_h_series_profile_consistency.py` to require the schema version and assert H-series profiles are not duplicated or referenced by Bernie scenario fixtures.
- Added `docs\adversarial\h_series_profile_consumption_review_r27.md` as the source-safe adversarial review artifact.
- Added `docs\receptionist_review_r27.md` as the source-safe receptionist acceptance note.
- Updated `docs\h-series-profile-schema.md`, `AGENTS.md`, and `orchestration\protocol_alerts.md` with the future full-trove/Fable review gate.
- Added the Fable review packet `orchestration\agent_inbox\codex\plan-claude-claude-r28-fable-full-trove-readiness-review.md`.
- Added the corresponding review request `orchestration\agent_inbox\codex\review-claude-claude-r28-fable-full-trove-readiness-review.md`.
- Added `app\services\diary\action_grammar.py`, a pure versioned action grammar scaffold.
- Added `app\services\bernie\action_grammar.py`, a compatibility facade.
- Exported grammar symbols from `app\services\diary\__init__.py` and `app\services\bernie\__init__.py`.
- Added `tests\test_diary_action_grammar.py` with 31 focused tests.
- Added `docs\adversarial\r29_action_grammar_adversarial_review.md`.
- Added `docs\receptionist_review_r29.md`.
- Added `tests\action_grammar_replay\`, a pure test-only replay consumer.
- Added `tests\fixtures\action_grammar_replay\`, hand-authored synthetic JSON scripts.
- Added `docs\adversarial\r30_replay_consumer_adversarial_review.md`.
- Added `docs\receptionist_review_r30.md`.
- Added `docs\historical-diary-trove-h22-semantic-gate-review-packet.md`.
- Added semantic-mode validation to `scripts\historical_diary_output_safety.py`.
- Added `scripts\historical_diary_leakage_lint.py`.
- Added `tests\test_historical_diary_leakage_lint.py`.
- Wired the leakage lint into `.github\workflows\python-security.yml`.
- Added `docs\adversarial\h23_semantic_guardrails_review.md`.
- Tightened semantic guardrails so semantic action names track `DiaryActionVerb` and approval expiry must be `YYYY-MM-DD`.
- Added blocked draft files `docs\historical-diary-trove-h15-approval-payload-draft.json` and `docs\historical-diary-trove-h15-approval-payload-draft.md`.
- Hardened the H15 gate validator so any future semantic approval requires bounded scope and `YYYY-MM-DD` expiry.
- Added approved gate files `docs\historical-diary-trove-h15-approved-gate.json` and `docs\historical-diary-trove-h15-approval-decision.md`.
- Added tests proving the draft remains blocked and the approved payload passes with the bounded scope.
- Added `scripts\historical_diary_semantic_candidate_builder.py`.
- Added `tests\test_historical_diary_semantic_candidate_builder.py`.
- Added `docs\historical-diary-trove-h15-bounded-semantic-prototype.md`.
- Ran the approved local prototype into ignored `local_data\historical-diary-trove\inventory\semantic_h15_*` outputs.
- Added `docs\adversarial\h28_semantic_candidate_builder_review.md`.
- Downgraded generated candidates from mutating `status_change` to read-only `explain_schedule`.
- Added `tests\fixtures\h15_semantic_candidates\read_only_explain_schedule_candidates.json`.
- Added `tests\test_h15_semantic_candidate_fixtures.py`.
- Wired H15 synthetic candidates through the R30 action-grammar replay harness as expected `route_read_only` actions.
- Added `docs\historical-diary-trove-access-ai-memory-boundary.md`.
- Added `tests\test_historical_diary_memory_boundary.py`.
- No raw diary files, ignored local JSON, filenames, exact source timestamps, patient/staff labels, document text, live-provider calls, database writes, routes, frontend assets, migrations, or runtime prompts were added.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile tests\test_h_series_profile_consistency.py`.
- Focused pytest passed: `.venv\Scripts\pytest.exe tests\test_h_series_profile_consistency.py -q` (3 passed; existing warnings only).
- `git diff --check` passed.
- Fable worker verification: plan/review artifact only; `git diff --check` clean on `claude/fable-full-trove-readiness`.
- R29 compile check passed: `.venv\Scripts\python.exe -m py_compile app\services\diary\action_grammar.py app\services\bernie\action_grammar.py tests\test_diary_action_grammar.py`.
- R29 focused pytest passed: `.venv\Scripts\pytest.exe tests\test_diary_action_grammar.py -q` (31 passed).
- Adjacent regression cluster passed: `.venv\Scripts\pytest.exe tests\test_diary_action_envelopes.py tests\test_diary_confirm_gate.py tests\test_diary_confirm_actions.py tests\test_bernie_diary_capability_manifest.py tests\test_bernie_domain_package.py tests\test_bernie_diary_rehome_compatibility.py -q` (98 passed).
- R30 compile check passed: `.venv\Scripts\python.exe -m py_compile tests\action_grammar_replay\loader.py tests\action_grammar_replay\replay.py tests\action_grammar_replay\test_grammar_replay.py`.
- R30 focused pytest passed: `.venv\Scripts\pytest.exe tests\action_grammar_replay tests\test_diary_action_grammar.py tests\test_h_series_profile_consistency.py -q` (44 passed).
- H22 blocked gate validation passed: `.venv\Scripts\python.exe scripts\historical_diary_deidentification_gate.py docs\historical-diary-trove-semantic-gate-template.json`.
- H22 focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_deidentification_gate.py tests\action_grammar_replay tests\test_h_series_profile_consistency.py -q` (21 passed).
- H23 compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_output_safety.py scripts\historical_diary_leakage_lint.py tests\test_historical_diary_output_safety.py tests\test_historical_diary_leakage_lint.py`.
- H23 leakage lint passed: `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- H23 focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_output_safety.py tests\test_historical_diary_leakage_lint.py tests\test_historical_diary_deidentification_gate.py tests\action_grammar_replay tests\test_h_series_profile_consistency.py -q` (41 passed).
- H24 compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_output_safety.py scripts\historical_diary_leakage_lint.py tests\test_historical_diary_output_safety.py tests\test_historical_diary_leakage_lint.py`.
- H24 leakage lint passed: `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- H24 blocked gate validation passed: `.venv\Scripts\python.exe scripts\historical_diary_deidentification_gate.py docs\historical-diary-trove-semantic-gate-template.json`.
- H24 focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_output_safety.py tests\test_historical_diary_leakage_lint.py tests\test_historical_diary_deidentification_gate.py tests\action_grammar_replay tests\test_h_series_profile_consistency.py -q` (43 passed).
- H25 compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_deidentification_gate.py scripts\historical_diary_output_safety.py scripts\historical_diary_leakage_lint.py tests\test_historical_diary_deidentification_gate.py tests\test_historical_diary_output_safety.py tests\test_historical_diary_leakage_lint.py`.
- H25 gate validation passed for both blocked template and blocked draft: `.venv\Scripts\python.exe scripts\historical_diary_deidentification_gate.py docs\historical-diary-trove-semantic-gate-template.json docs\historical-diary-trove-h15-approval-payload-draft.json`.
- H25 leakage lint passed: `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- H25 focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_deidentification_gate.py tests\test_historical_diary_output_safety.py tests\test_historical_diary_leakage_lint.py tests\action_grammar_replay tests\test_h_series_profile_consistency.py -q` (46 passed).
- H26 compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_deidentification_gate.py scripts\historical_diary_output_safety.py scripts\historical_diary_leakage_lint.py tests\test_historical_diary_deidentification_gate.py tests\test_historical_diary_output_safety.py tests\test_historical_diary_leakage_lint.py`.
- H26 gate validation passed for default template, blocked draft, and approved payload: `.venv\Scripts\python.exe scripts\historical_diary_deidentification_gate.py docs\historical-diary-trove-semantic-gate-template.json docs\historical-diary-trove-h15-approval-payload-draft.json docs\historical-diary-trove-h15-approved-gate.json`.
- H26 leakage lint passed: `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- H26 focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_deidentification_gate.py tests\test_historical_diary_output_safety.py tests\test_historical_diary_leakage_lint.py tests\action_grammar_replay tests\test_h_series_profile_consistency.py -q` (47 passed).
- H27 local neutral aggregate validation passed: `.venv\Scripts\python.exe scripts\historical_diary_output_safety.py local_data\historical-diary-trove\inventory\semantic_h15_prototype_neutral_aggregate.json`.
- H27 semantic candidate builder produced validator-safe ignored candidates at `local_data\historical-diary-trove\inventory\semantic_h15_candidate_fixtures.json`.
- H27 compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_semantic_candidate_builder.py scripts\historical_diary_deidentification_gate.py scripts\historical_diary_output_safety.py scripts\historical_diary_leakage_lint.py tests\test_historical_diary_semantic_candidate_builder.py`.
- H27 gate validation passed for default template, blocked draft, and approved payload.
- H27 leakage lint passed: `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- H27 semantic candidate validation passed: 80 ignored candidate fixtures.
- H27 focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_semantic_candidate_builder.py tests\test_historical_diary_deidentification_gate.py tests\test_historical_diary_output_safety.py tests\test_historical_diary_leakage_lint.py tests\action_grammar_replay tests\test_h_series_profile_consistency.py -q` (52 passed).
- H28 regenerated ignored semantic candidates as 80 `explain_schedule` candidates and validated them.
- H28 leakage lint passed: `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- H28 neutral aggregate validation passed: `.venv\Scripts\python.exe scripts\historical_diary_output_safety.py local_data\historical-diary-trove\inventory\semantic_h15_prototype_neutral_aggregate.json`.
- H28 focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_semantic_candidate_builder.py tests\test_historical_diary_deidentification_gate.py tests\test_historical_diary_output_safety.py tests\test_historical_diary_leakage_lint.py tests\action_grammar_replay tests\test_h_series_profile_consistency.py -q` (52 passed).
- H29 focused fixture pytest passed: `.venv\Scripts\pytest.exe tests\test_h15_semantic_candidate_fixtures.py -q` (3 passed).
- H29 leakage lint passed: `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- H29 focused guard pytest passed: `.venv\Scripts\pytest.exe tests\test_h15_semantic_candidate_fixtures.py tests\test_historical_diary_semantic_candidate_builder.py tests\test_historical_diary_deidentification_gate.py tests\test_historical_diary_output_safety.py tests\test_historical_diary_leakage_lint.py tests\action_grammar_replay tests\test_h_series_profile_consistency.py -q` (55 passed).
- H30 leakage lint passed: `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- H30 focused guard pytest passed: `.venv\Scripts\pytest.exe tests\test_h15_semantic_candidate_fixtures.py tests\action_grammar_replay tests\test_historical_diary_semantic_candidate_builder.py tests\test_historical_diary_deidentification_gate.py tests\test_historical_diary_output_safety.py tests\test_historical_diary_leakage_lint.py tests\test_h_series_profile_consistency.py -q` (56 passed).
- H31 leakage lint passed: `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- H31 focused guard pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_memory_boundary.py tests\test_h15_semantic_candidate_fixtures.py tests\action_grammar_replay tests\test_historical_diary_semantic_candidate_builder.py tests\test_historical_diary_deidentification_gate.py tests\test_historical_diary_output_safety.py tests\test_historical_diary_leakage_lint.py tests\test_h_series_profile_consistency.py tests\test_practice_knowledge_advisory_boundary.py -q` (92 passed).

## Local Result

- R27 now consumes the H-series profile layer only as source-safe metadata and isolation evidence.
- The validator blocks raw/semantic keys, requires committed H-series doc provenance, requires the H15 semantic-label boundary to stay explicit, and guards against profile/scenario cross-contamination.
- DeepSeek's adversarial review shaped the schema-version and isolation guard recommendations.
- The receptionist acceptance note explicitly rejects semantic promotion from neutral movement into appointment intent.
- R29 gives EMR4 a native typed action vocabulary without adding write authority.
- Implemented confirm verbs map to existing `DiaryConfirmAction` entries; planned check-in/waiting-area/link-patient verbs remain unavailable scaffolds.
- The grammar is not wired into routes, prompts, UI, provider calls, or full-trove processing.
- R30 now proves the action grammar can be consumed by hand-authored synthetic fake day/action scripts.
- The replay consumer resolves actions, refuses planned-unavailable and unknown actions, checks read-only/meta routing, and calls the runtime confirm-affordance gate instead of only scanning notes text.
- `DRIFT.md` records why this pure grammar consumer is separate from route-level DB replay until grammar verbs are wired into backend routes.
- H22 now defines the human-readable review packet for a future H15 decision without approving semantic labelling or touching raw trove material.
- H23 now gives H22 its first executable tripwires: semantic-mode payload validation and repo-path leakage lint for H-series semantic drift.
- H24 records an adversarial review of those tripwires and adds grammar-drift and approval-expiry guards.
- H25 provides a concrete approval-payload draft while deliberately keeping `decision: blocked`.
- H26 records Yuri's explicit H15 approval for the bounded local-only prototype scope.
- H27 proves the approved local pipeline can produce validator-safe low-confidence candidates from validator-safe neutral aggregates.
- H28 corrects the candidate semantics: neutral aggregates may support read-only explanation candidates, not mutating diary action candidates.
- H29 commits only a small hand-authored synthetic read-only fixture family, not generated local payloads.
- H30 proves those fixtures are consumed by the deterministic action-grammar replay harness as read-only actions.
- H31 keeps historical diary candidates out of runtime Access AI, practice-knowledge, Diary authority, and Bernie memory modules until a separate boundary is implemented.

## Bernie Memory Result

- The 58k-file trove should not be raw fine-tuning, raw retrieval, or provider-prompt material.
- RAG is useful over approved docs, policies, aggregate stats, and de-identified/synthetic examples.
- GraphRAG is likely the best future fit once source-safe derived graph memory has a reviewed boundary.
- Bernie can use derived memory to clarify and propose; the deterministic diary backend remains the write authority.
- Fable's R28 verdict is now integrated: grammar before labels, labels before mining, mining before memory.
- Do not run broad 58k-file processing or open H15 yet. Build native Bernie/Diary action grammar, then a deterministic synthetic replay consumer, then an H22 semantic gate-review packet for Yuri.

## Recommended User Review

No required manual review before continuing. Yuri review is required only if a future sprint proposes approving semantic labelling, raw/de-identified examples, broad full-trove processing, or provider-visible prompt consumption from historical diary material.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required; raw diary files must not be sent to external providers.
- No database migration or test DB reset is required.
- No manual diary-content review is required because R27 commits only safe metadata/profile-boundary documentation and tests.

## Known Follow-Up

- Add route-level read-only explanation tests or an advisory-only adapter proposal, still without provider/memory integration.
- Do not use the full trove broadly until H22 is reviewed and Yuri explicitly approves H15.
- Do not infer appointment create/delete/status semantics from the trove until the H15 gate is approved.

## Previous Closeout - Sprint H21

| Item | Value |
|---|---|
| Batch | Sprint H21: Historical Diary Trove Thursday Neutral Sampling |
| Integrated through | Ariadne local-only neutral trove pipeline; no external workers used because scope was privacy-sensitive and raw-data-adjacent |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; Python Security green at `f1b1de0`; fresh manual Pages deployment green at `f1b1de0` after the initial push Pages run failed on duplicate artifact metadata during rerun |
| Last updated | 2026-07-06 |

## What Changed

- Processed Yuri's local `pilot_03` Thursday sample with the existing neutral classifier pipeline.
- Produced ignored `ordered_snapshots_h21.json`, `event_summary_h21.json`, `cross_pilot_event_trends_h21.json`, `neutral_derived_graph_h21.json`, and `neutral_graph_report_h21.json`.
- Added `docs\historical-diary-trove-thursday-neutral-sampling.md`.
- Updated `AGENTS.md` with H21 state and the recommendation to turn neutral movement profiles into deterministic diary/Bernie regression scenarios.
- No raw diary files, filenames, paths, exact source timestamps, patient/staff labels, document text, external-provider calls, database writes, routes, frontend, migrations, or GitHub Pages assets were added.

## Verification

- H21 ignored local outputs passed `scripts\historical_diary_output_safety.py`.
- Compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_event_summary_dry_run.py scripts\historical_diary_cross_pilot_event_trends.py scripts\historical_diary_neutral_graph_export.py scripts\historical_diary_neutral_graph_report.py scripts\historical_diary_output_safety.py`.
- Focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_event_summary_dry_run.py tests\test_historical_diary_neutral_graph_export.py tests\test_historical_diary_neutral_graph_report.py tests\test_historical_diary_output_safety.py -q`.

## Local Result

- `pilot_03` contains 637 local files and was sampled at the same capped 40-snapshot, one-dense-day level as the other roots.
- The H21 four-root refresh represented 160 snapshots and 156 adjacent transitions.
- The recomputed H21 slice found only `no_structural_change` and `small_content_delta` event classes across all four roots.
- The predefined H21 graph report found no `large_unexplained_delta` or `time_grid_delta` roots in this capped four-root slice.
- Interpretation: the Thursday sample strengthens the case for using the trove to build safe deterministic diary scenario fixtures, while keeping semantic labelling blocked.

## Previous Closeout - Sprint H20

| Item | Value |
|---|---|
| Batch | Sprint H20: Historical Diary Trove Neutral Graph Report |
| Integrated through | Ariadne local-only predefined graph report tooling; no external workers used because scope was privacy-sensitive and narrow |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Pages, Python Security, and CodeQL workflows green at `101c3222` |
| Last updated | 2026-07-06 |

## What Changed

- Added `scripts\historical_diary_neutral_graph_report.py`, a predefined safe graph report helper.
- Added `tests\test_historical_diary_neutral_graph_report.py`.
- Extended `scripts\historical_diary_output_safety.py` with report-neutral keys only.
- Produced ignored `neutral_graph_report_h20.json` from the H19 graph output.
- Added `docs\historical-diary-trove-neutral-graph-report.md`.
- Updated `AGENTS.md` with H20 state and the recommendation to broaden only if more neutral roots are ready.
- No raw diary files, filenames, paths, exact source timestamps, patient/staff labels, document text, external-provider calls, database writes, routes, frontend, migrations, or GitHub Pages assets were added.

## Verification

- H20 neutral graph report output passed `scripts\historical_diary_output_safety.py`.
- Compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_neutral_graph_report.py scripts\historical_diary_output_safety.py`.
- Focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_neutral_graph_report.py tests\test_historical_diary_output_safety.py -q` (11 passed; existing warnings only).

## Local Result

- Produced 9 predefined query result groups from the ignored H19 graph.
- Notable event queries identify `pilot_01` for `large_unexplained_delta` and `pilot` for `time_grid_delta`.
- Delta-bucket queries identify shared movement buckets across the three pilot roots.
- Interpretation: the graph/report substrate is useful for safe aggregate questions, but remains local-only and not Bernie runtime memory.

## Previous Closeout - Sprint H19

| Item | Value |
|---|---|
| Batch | Sprint H19: Historical Diary Trove Neutral Graph Delta Buckets |
| Integrated through | Ariadne local-only graph enrichment tooling; no external workers used because scope was privacy-sensitive and narrow |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Pages, Python Security, and CodeQL workflows green at `f1b6c6f9` |
| Last updated | 2026-07-06 |

## What Changed

- Enriched `scripts\historical_diary_neutral_graph_export.py` with derived delta-bucket nodes and edges.
- Updated `tests\test_historical_diary_neutral_graph_export.py`.
- Produced ignored `neutral_derived_graph_h19.json` from the H17 trend output.
- Added `docs\historical-diary-trove-neutral-graph-delta-buckets.md`.
- Updated `docs\historical-diary-trove-neutral-derived-graph.md`.
- Updated `AGENTS.md` with H19 state and the next graph-query recommendation.
- No raw diary files, filenames, paths, exact source timestamps, patient/staff labels, document text, external-provider calls, database writes, routes, frontend, migrations, or GitHub Pages assets were added.

## Verification

- H19 neutral derived graph output passed `scripts\historical_diary_output_safety.py`.
- Compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_neutral_graph_export.py scripts\historical_diary_output_safety.py`.
- Focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_neutral_graph_export.py tests\test_historical_diary_output_safety.py -q` (11 passed; existing warnings only).

## Local Result

- Derived graph contains 3 root nodes, 4 event-class nodes, 7 delta-bucket nodes, 8 event-class edges, and 15 delta-bucket edges.
- Represented transitions: 297.
- The graph is aggregate-only and semantic-label-free.
- Interpretation: the trove now has a safe first GraphRAG-shaped substrate for aggregate movement questions, but not appointment-level memory.

## Bernie Memory Result

- The 58k-file trove should not be raw fine-tuning material.
- RAG is useful over approved docs, policies, aggregate stats, and de-identified/synthetic examples.
- GraphRAG is likely the best future fit once we have a derived neutral transition graph.
- Bernie can use derived memory to clarify and propose; the deterministic diary backend remains the write authority.

## Recommended User Review

No required manual review before continuing neutral work. Yuri review is required only if a future sprint proposes approving semantic labelling or using raw/de-identified examples for provider-visible prompts.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required; raw diary files must not be sent to external providers.
- No database migration or test DB reset is required.
- No manual diary-content review is required because H19 commits only safe aggregate documentation, tooling, tests, and handover notes.

## Known Follow-Up

- H20 should add a safe predefined graph query/report helper.
- Do not infer appointment create/delete/status semantics from the trove until the H15 gate is approved.

## Previous Closeout - Sprint H18

| Item | Value |
|---|---|
| Batch | Sprint H18: Historical Diary Trove Neutral Derived Graph |
| Integrated through | Ariadne local-only graph export tooling; no external workers used because scope was privacy-sensitive and narrow |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Pages, Python Security, and CodeQL workflows green at `2cc76dab` |
| Last updated | 2026-07-06 |

## What Changed

- Added `scripts\historical_diary_neutral_graph_export.py`, a safe graph export prototype.
- Added `tests\test_historical_diary_neutral_graph_export.py`.
- Extended `scripts\historical_diary_output_safety.py` with graph-neutral keys only.
- Produced ignored `neutral_derived_graph_h18.json` from the H17 trend output.
- Added `docs\historical-diary-trove-neutral-derived-graph.md`.
- Updated `AGENTS.md` with H18 state and the next graph-enrichment recommendation.
- No raw diary files, filenames, paths, exact source timestamps, patient/staff labels, document text, external-provider calls, database writes, routes, frontend, migrations, or GitHub Pages assets were added.

## Verification

- H18 neutral derived graph output passed `scripts\historical_diary_output_safety.py`.
- Compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_neutral_graph_export.py scripts\historical_diary_output_safety.py`.
- Focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_neutral_graph_export.py tests\test_historical_diary_output_safety.py -q` (11 passed; existing warnings only).

## Local Result

- Derived graph contains 3 root nodes, 4 event-class nodes, and 8 counted root-to-event-class edges.
- Represented transitions: 297.
- The graph is aggregate-only and semantic-label-free.
- Interpretation: the trove now has a safe first GraphRAG-shaped substrate, but not appointment-level memory.

## Bernie Memory Result

- The 58k-file trove should not be raw fine-tuning material.
- RAG is useful over approved docs, policies, aggregate stats, and de-identified/synthetic examples.
- GraphRAG is likely the best future fit once we have a derived neutral transition graph.
- Bernie can use derived memory to clarify and propose; the deterministic diary backend remains the write authority.

## Recommended User Review

No required manual review before continuing neutral work. Yuri review is required only if a future sprint proposes approving semantic labelling or using raw/de-identified examples for provider-visible prompts.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required; raw diary files must not be sent to external providers.
- No database migration or test DB reset is required.
- No manual diary-content review is required because H18 commits only safe aggregate documentation, tooling, tests, and handover notes.

## Known Follow-Up

- H19 should enrich the neutral graph with derived delta-bucket nodes and edges.
- Do not infer appointment create/delete/status semantics from the trove until the H15 gate is approved.

## Previous Closeout - Sprint H17

| Item | Value |
|---|---|
| Batch | Sprint H17: Historical Diary Trove Cross-Pilot Event Trends |
| Integrated through | Ariadne local-only safe comparison tooling; no external workers used because scope was privacy-sensitive and narrow |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Pages, Python Security, and CodeQL workflows green at `12ed94d0` |
| Last updated | 2026-07-06 |

## What Changed

- Added `scripts\historical_diary_cross_pilot_event_trends.py`, a safe multi-summary trend reporter.
- Added `tests\test_historical_diary_cross_pilot_event_trends.py`.
- Produced ignored `cross_pilot_event_trends_h17.json` from H13 and H16 event summaries.
- Added `docs\historical-diary-trove-cross-pilot-event-trends.md`.
- Updated `AGENTS.md` with H17 state and the next neutral graph-export recommendation.
- No raw diary files, filenames, paths, exact source timestamps, patient/staff labels, document text, external-provider calls, database writes, routes, frontend, migrations, or GitHub Pages assets were added.

## Verification

- H17 cross-pilot trend output passed `scripts\historical_diary_output_safety.py`.
- Compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_cross_pilot_event_trends.py scripts\historical_diary_output_safety.py`.
- Focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_cross_pilot_event_trends.py tests\test_historical_diary_output_safety.py -q` (12 passed; existing warnings only).

## Local Result

- Compared 300 sampled snapshots and 297 adjacent transitions across `pilot`, `pilot_01`, and `pilot_02`.
- 295/297 transitions are either `no_structural_change` or `small_content_delta`.
- The only notable transitions are the previously known one `time_grid_delta` in `pilot` and one `large_unexplained_delta` in `pilot_01`.
- Interpretation: the trove looks highly useful for deterministic replay and graph mining, but semantic labelling remains blocked.

## Bernie Memory Result

- The 58k-file trove should not be raw fine-tuning material.
- RAG is useful over approved docs, policies, aggregate stats, and de-identified/synthetic examples.
- GraphRAG is likely the best future fit once we have a derived neutral transition graph.
- Bernie can use derived memory to clarify and propose; the deterministic diary backend remains the write authority.

## Recommended User Review

No required manual review before continuing neutral work. Yuri review is required only if a future sprint proposes approving semantic labelling or using raw/de-identified examples for provider-visible prompts.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required; raw diary files must not be sent to external providers.
- No database migration or test DB reset is required.
- No manual diary-content review is required because H17 commits only safe aggregate documentation, tooling, tests, and handover notes.

## Known Follow-Up

- H18 should prototype a neutral derived graph export for Bernie memory research.
- Do not infer appointment create/delete/status semantics from the trove until the H15 gate is approved.

## Previous Closeout - Sprint H16

| Item | Value |
|---|---|
| Batch | Sprint H16: Historical Diary Trove Friday Neutral Sampling |
| Integrated through | Ariadne local-only capped neutral sampling; no external workers used because scope was privacy-sensitive and read-only |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean at `691b0ab8` |
| Last updated | 2026-07-06 |

## What Changed

- Ran the H16 capped read-only neutral export over ignored `pilot_02` Friday files.
- Produced ignored H16 ordered snapshots, event summary, large-delta triage, and transition-neighborhood outputs.
- Added `docs\historical-diary-trove-friday-neutral-sampling.md`.
- Updated `AGENTS.md` with H16 state and the safe Bernie memory posture for the 58k-file trove.
- No raw diary files, filenames, paths, exact source timestamps, patient/staff labels, document text, external-provider calls, database writes, routes, frontend, migrations, or GitHub Pages assets were added.

## Verification

- H16 raw folder count confirmed: 667 local files under ignored `pilot_02`.
- H16 classifier opened 100/100 sampled files read-only with zero errors.
- H16 ordered snapshot, event summary, large-delta triage, and transition-neighborhood outputs passed `scripts\historical_diary_output_safety.py`.
- Compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_output_safety.py scripts\historical_diary_event_summary_dry_run.py scripts\historical_diary_large_delta_triage.py scripts\historical_diary_transition_neighborhoods.py`.
- Focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_output_safety.py tests\test_historical_diary_event_summary_dry_run.py tests\test_historical_diary_large_delta_triage.py tests\test_historical_diary_transition_neighborhoods.py -q` (16 passed; existing warnings only).

## Local Result

- `pilot_02`: 100 `strong_diary_grid` classifications.
- Event classes: 65 `no_structural_change`, 34 `small_content_delta`.
- Large-delta triage count: 0.
- Transition-neighborhood count: 0.
- Interpretation: the Friday slice strengthens the stable-grid hypothesis and does not reproduce the isolated H12/H14 notable events.

## Bernie Memory Result

- The 58k-file trove should not be raw fine-tuning material.
- RAG is useful over approved docs, policies, aggregate stats, and de-identified/synthetic examples.
- GraphRAG is likely the best future fit once we have a derived neutral transition graph.
- Bernie can use derived memory to clarify and propose; the deterministic diary backend remains the write authority.

## Recommended User Review

No required manual review before continuing neutral work. Yuri review is required only if a future sprint proposes approving semantic labelling or using raw/de-identified examples for provider-visible prompts.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required; raw diary files must not be sent to external providers.
- No database migration or test DB reset is required.
- No manual diary-content review is required because H16 commits only safe aggregate documentation and handover notes.

## Known Follow-Up

- H17 should add a cross-pilot comparison reporter for safe event summaries.
- H18 can prototype a neutral derived graph export for Bernie memory research.
- Do not infer appointment create/delete/status semantics from the trove until the H15 gate is approved.

## Previous Closeout - Sprint H15

| Item | Value |
|---|---|
| Batch | Sprint H15: Historical Diary Trove Semantic Labelling De-Identification Gate |
| Integrated through | Ariadne local-only gate tooling; no external workers used because scope was privacy-policy/tooling and narrowly bounded |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Pages, Python Security, and CodeQL workflows green |
| Last updated | 2026-07-06 |

## What Changed

- Added `scripts\historical_diary_deidentification_gate.py`, an executable validator for the privacy gate required before semantic diary labelling.
- Added `tests\test_historical_diary_deidentification_gate.py` using synthetic-only payloads.
- Added blocked-by-default gate template `docs\historical-diary-trove-semantic-gate-template.json`.
- Added `docs\historical-diary-trove-semantic-labelling-gate.md`.
- Updated `docs\historical-diary-trove-deidentification-contract.md` to distinguish H5 output safety from H15 semantic-labelling approval.
- No raw diary files, filenames, paths, exact source timestamps, patient/staff labels, document text, external-provider calls, database writes, routes, frontend, migrations, or GitHub Pages assets were added.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_deidentification_gate.py tests\test_historical_diary_deidentification_gate.py`.
- Focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_deidentification_gate.py tests\test_historical_diary_output_safety.py -q` (17 passed; existing warnings only).
- Gate template validation passed: `.venv\Scripts\python.exe scripts\historical_diary_deidentification_gate.py docs\historical-diary-trove-semantic-gate-template.json`.
- Post-push audit passed: master, `handoff/current`, and durable worker mirrors aligned at `74055204`.
- GitHub workflows passed for the H15 push: Deploy GitHub Pages, Python Security, and CodeQL.

## Gate Result

- The committed semantic gate template is intentionally `blocked`.
- Neutral structural work remains allowed.
- Committed semantic appointment fixtures remain blocked until a future reviewed gate payload explicitly approves semantic fixture promotion.
- Raw diary data remains local-only and must not be sent to external providers.

## Recommended User Review

No required manual review before continuing neutral work. Yuri review is required only if the next sprint proposes changing the gate decision from `blocked`.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required; raw diary files must not be sent to external providers.
- No database migration or test DB reset is required.
- No manual diary-content review is required for H15 because it uses synthetic tests and policy templates only.

## Known Follow-Up

- H16 should either continue neutral broadening under H10 caps or prepare a Yuri review packet for changing the semantic gate from `blocked`.
- Do not infer appointment create/delete/status semantics from the trove until the H15 gate is approved.

## Previous Closeout - Sprint H14

| Item | Value |
|---|---|
| Batch | Sprint H14: Historical Diary Trove Neutral Transition Neighborhoods |
| Integrated through | Ariadne local-only transition-neighborhood tooling; no external workers used because scope was raw-free and narrowly bounded |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Pages, Python Security, and CodeQL workflows green |
| Last updated | 2026-07-06 |

## What Changed

- Added `scripts\historical_diary_transition_neighborhoods.py`, a validator-safe local report for notable transition neighborhoods.
- Extended `scripts\historical_diary_output_safety.py` with neutral neighborhood keys only.
- Added `tests\test_historical_diary_transition_neighborhoods.py`.
- Ran H14 against ignored H13 ordered neutral snapshots.
- Produced ignored `transition_neighborhoods_h14.json` and validated it through H5.
- Added `docs\historical-diary-trove-transition-neighborhoods.md`.
- No raw diary files, filenames, paths, exact source timestamps, patient/staff labels, document text, external-provider calls, database writes, routes, frontend, migrations, or GitHub Pages assets were added.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_transition_neighborhoods.py scripts\historical_diary_output_safety.py tests\test_historical_diary_transition_neighborhoods.py`.
- Focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_transition_neighborhoods.py tests\test_historical_diary_large_delta_triage.py tests\test_historical_diary_timeline_events.py tests\test_historical_diary_output_safety.py -q` (19 passed; existing warnings only).
- Local neighborhood report passed against ignored H13 ordered snapshots.
- Safety validation passed for ignored H14 transition-neighborhood output.
- Post-push audit passed: master, `handoff/current`, and durable worker mirrors aligned.
- GitHub workflows passed for the H14 push: Deploy GitHub Pages, Python Security, and CodeQL.

## Local Neighborhood Result

- `pilot`: one neighborhood centered on transition 68, `time_grid_delta`; previous neighbor is `small_content_delta`, next neighbor is `no_structural_change`.
- `pilot_01`: one neighborhood centered on transition 54, `large_unexplained_delta`; previous and next neighbors are both `small_content_delta`.
- Interpretation: both notable events are isolated in the immediate neutral neighborhood and remain structural/count signals only.

## Recommended User Review

No required manual review before continuing. H14 is local tooling/tests/docs only and reads ignored neutral H13 output, not raw diary content.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required; raw diary files must not be sent to external providers.
- No database migration or test DB reset is required.
- No user manual diary review is required because no visible diary behaviour changed.

## Known Follow-Up

- H15 should either broaden to another capped dense-day/root set or design the de-identification review gate before semantic appointment labelling.
- Do not infer appointment create/delete/status semantics from H14.

## Previous Closeout - Sprint H13

| Item | Value |
|---|---|
| Batch | Sprint H13: Historical Diary Trove Broadened Neutral Sampling |
| Integrated through | Ariadne local-only capped neutral sampling; no external workers used because scope was raw-free and narrowly bounded |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Pages and Python Security workflows green; CodeQL not triggered for docs-only H13 |
| Last updated | 2026-07-06 |

## What Changed

- Ran a capped H13 ordered neutral export over 100 snapshots from each ignored pilot root, with H10 guardrails active and without `-AllowLargeRun`.
- Produced ignored `ordered_snapshots_h13.json`, `event_summary_h13.json`, and `large_delta_triage_h13.json`.
- Validated each ignored H13 output through H5.
- Added `docs\historical-diary-trove-broadened-neutral-sampling.md`.
- No raw diary files, filenames, paths, exact source timestamps, patient/staff labels, document text, external-provider calls, database writes, routes, frontend, migrations, or GitHub Pages assets were added.

## Verification

- Local export passed: 200/200 read-only Word COM opens, zero classifier errors.
- Safety validation passed for ignored H13 ordered snapshots, event summary, and large-delta triage output.
- Existing H12/H13 helper checks passed earlier in the sequence: focused pytest 24 passed with existing warnings only.
- Post-push audit passed: master, `handoff/current`, and durable worker mirrors all aligned at `21648441`.
- GitHub workflows passed for the clean H13 push: Deploy GitHub Pages and Python Security. CodeQL did not trigger for this docs-only H13 change.

## Local Sampling Result

- `pilot`: 100 snapshots, 99 transitions: 61 `no_structural_change`, 37 `small_content_delta`, 1 `time_grid_delta`; large-delta triage count 0.
- `pilot_01`: 100 snapshots, 99 transitions: 60 `no_structural_change`, 38 `small_content_delta`, 1 `large_unexplained_delta`; large-delta triage count 1.
- The `pilot_01` large transition is the same neutral sequence pair as H12, sequence 54 to 55.
- Interpretation: H13 did not reveal a new large unexplained transition; the one `pilot` time-grid event is a neutral future structural-question signal only.

## Recommended User Review

No required manual review before continuing. H13 is local tooling/docs only and touches raw diary files only through read-only local Word COM extraction.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required; raw diary files must not be sent to external providers.
- No database migration or test DB reset is required.
- No user manual diary review is required because no visible diary behaviour changed.

## Known Follow-Up

- H14 should add a neutral transition-neighborhood reporter for large/time-grid events.
- Do not infer appointment create/delete/status semantics from H13.

## Previous Closeout - Sprint H12

| Item | Value |
|---|---|
| Batch | Sprint H12: Historical Diary Trove Neutral Large-Delta Triage |
| Integrated through | Ariadne local-only large-delta triage; no external workers used because scope was raw-free and narrowly bounded |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Pages, Python Security, and CodeQL workflows green |
| Last updated | 2026-07-06 |

## What Changed

- Added `scripts\historical_diary_large_delta_triage.py`, a validator-safe local triage report for neutral large-delta transitions.
- Extended `scripts\historical_diary_output_safety.py` to allow only the neutral triage keys required by H12.
- Added `tests\test_historical_diary_large_delta_triage.py`.
- Ran H12 triage against ignored H11 ordered neutral snapshots.
- Produced ignored `large_delta_triage_h12.json` and validated it through H5.
- Added `docs\historical-diary-trove-large-delta-triage.md`.
- No raw diary files, filenames, paths, exact source timestamps, patient/staff labels, document text, external-provider calls, database writes, routes, frontend, migrations, or GitHub Pages assets were added.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_large_delta_triage.py scripts\historical_diary_output_safety.py tests\test_historical_diary_large_delta_triage.py`.
- Focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_large_delta_triage.py tests\test_historical_diary_runtime_report.py tests\test_historical_diary_event_summary_compare.py tests\test_historical_diary_event_summary_dry_run.py tests\test_historical_diary_timeline_events.py tests\test_historical_diary_output_safety.py -q` (24 passed; existing warnings only).
- Local triage passed against ignored H11 ordered snapshots.
- Safety validation passed for ignored H12 large-delta triage output.
- Post-push audit passed: master, `handoff/current`, and durable worker mirrors all aligned at `4a17974f`.
- GitHub workflows passed for the H12 push: Deploy GitHub Pages, Python Security, and CodeQL.

## Local Triage Result

- The single H11 large transition occurs in `pilot_01`, transition index 54, sequence pair 54 to 55.
- The transition is large because character count moved by 547, crossing the current `>500` threshold.
- Structure stayed `strong_diary_grid`; table count stayed `2`; table cell count stayed `14`; table signature stayed `1x11+1x3`; time-like token count stayed `78`.
- Paragraph count moved by 6, non-empty line count moved by 6, and date-like token count moved by 1.
- Interpretation: shape-stable content-volume movement inside the same diary structure, not a template/layout break and not a semantic appointment event.

## Recommended User Review

No required manual review before continuing. H12 is local tooling/tests/docs only and reads ignored neutral H11 output, not raw diary content.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required; raw diary files must not be sent to external providers.
- No database migration or test DB reset is required.
- No user manual diary review is required because no visible diary behaviour changed.

## Known Follow-Up

- H13 should broaden ordered-snapshot sampling cautiously under H10 caps and compare large-delta frequency before any semantic labelling work.
- Do not infer appointment create/delete/status semantics from H12.

## Previous Closeout - Sprint H11

| Item | Value |
|---|---|
| Batch | Sprint H11: Historical Diary Trove Bounded Multi-Day Runtime Probe |
| Integrated through | Ariadne local-only runtime probe; no external workers used because scope was raw-free and narrowly bounded |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Pages, Python Security, and CodeQL workflows green |
| Last updated | 2026-07-06 |

## What Changed

- Added `scripts\historical_diary_runtime_report.py`, a validator-safe runtime report generator for neutral probe output.
- Added `tests\test_historical_diary_runtime_report.py`.
- Ran a bounded two-dense-day local Word COM probe using `SampleSize=80`, `DenseDays=2`, and `MaxDenseDays=2`, without `-AllowLargeRun`.
- Produced ignored `ordered_snapshots_h11.json`, `runtime_report_h11.json`, and `event_summary_h11.json`, each validated through H5.
- Added `docs\historical-diary-trove-bounded-runtime-probe.md`.
- No raw diary files, filenames, paths, exact source timestamps, patient/staff labels, document text, external-provider calls, database writes, routes, frontend, migrations, or GitHub Pages assets were added.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_runtime_report.py scripts\historical_diary_output_safety.py tests\test_historical_diary_runtime_report.py`.
- Focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_runtime_report.py tests\test_historical_diary_event_summary_compare.py tests\test_historical_diary_event_summary_dry_run.py tests\test_historical_diary_timeline_events.py tests\test_historical_diary_output_safety.py -q` (22 passed; existing warnings only).
- Local probe passed: 160/160 read-only Word COM opens, zero errors, elapsed 112.224 seconds.
- Safety validation passed for ignored H11 ordered snapshots, runtime report, and event summary.
- Post-push audit passed: master, `handoff/current`, and durable worker mirrors all aligned at `26c59c5d`.
- GitHub workflows passed for the H11 push: Deploy GitHub Pages, Python Security, and CodeQL.

## Local Runtime Result

- `pilot`: 80 sampled/opened, 0 errors, 79 transitions: 40 `no_structural_change`, 39 `small_content_delta`.
- `pilot_01`: 80 sampled/opened, 0 errors, 79 transitions: 50 `no_structural_change`, 28 `small_content_delta`, 1 `large_unexplained_delta`.
- The `large_unexplained_delta` is neutral count movement only and must not be interpreted as an appointment event.

## Recommended User Review

No required manual review before continuing. H11 is local tooling/tests/docs only and touches raw diary files only through read-only local Word COM extraction.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required; raw diary files must not be sent to external providers.
- No database migration or test DB reset is required.
- No user manual diary review is required because no visible diary behaviour changed.

## Known Follow-Up

- H12 should triage the single neutral `large_unexplained_delta` using only sequence-index pairs and before/after neutral counts.
- Do not infer appointment create/delete/status semantics from H11.

## Previous Closeout - Sprint H10

| Item | Value |
|---|---|
| Batch | Sprint H10: Historical Diary Trove Broad-Run Guardrails |
| Integrated through | Ariadne local-only guardrail/comparer sprint; no external workers used because scope was raw-free and narrowly bounded |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Pages, Python Security, and CodeQL workflows green |
| Last updated | 2026-07-06 |

## What Changed

- Added default broad-run caps to `scripts\historical_diary_structure_classifier.ps1`: `MaxRootCount=2`, `MaxSampleSize=100`, and `MaxDenseDays=1`.
- Added explicit `-AllowLargeRun` as the only bypass path for those caps, intended only after documented safety/runtime review.
- Added `scripts\historical_diary_event_summary_compare.py`, a safe comparer for two validator-approved neutral event summaries.
- Extended `scripts\historical_diary_output_safety.py` to allow neutral comparison keys only.
- Added `tests\test_historical_diary_event_summary_compare.py`.
- Ran local H8-vs-H9 comparison and validated ignored `local_data\historical-diary-trove\inventory\event_summary_compare_h10.json`.
- Added `docs\historical-diary-trove-broad-run-guardrails.md`.
- No raw diary files, filenames, paths, exact source timestamps, patient/staff labels, document text, external-provider calls, database writes, routes, frontend, migrations, or GitHub Pages assets were added.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_event_summary_compare.py scripts\historical_diary_event_summary_dry_run.py scripts\historical_diary_output_safety.py tests\test_historical_diary_event_summary_compare.py`.
- Focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_event_summary_compare.py tests\test_historical_diary_event_summary_dry_run.py tests\test_historical_diary_timeline_events.py tests\test_historical_diary_output_safety.py -q` (20 passed; existing warnings only).
- Guardrail smoke passed: classifier refused `SampleSize 101` before opening Word.
- Local comparison passed: `.venv\Scripts\python.exe scripts\historical_diary_event_summary_compare.py local_data\historical-diary-trove\inventory\event_summary_h8.json local_data\historical-diary-trove\inventory\event_summary_h9.json`.
- Safety validation passed for ignored H10 comparison output.
- Post-push audit passed: master, `handoff/current`, and durable worker mirrors all aligned at `333ee3f1`.
- GitHub workflows passed for the H10 push: Deploy GitHub Pages, Python Security, and CodeQL.

## Local Comparison Result

- `pilot`: H9 ordered output shifted 8 transitions from `no_structural_change` to `small_content_delta` compared with H8 grouped replay.
- `pilot_01`: H9 ordered output shifted 1 transition from `no_structural_change` to `small_content_delta` compared with H8 grouped replay.
- Interpretation: ordered neutral snapshots are the better substrate for future temporal work.

## Recommended User Review

No required manual review before continuing. H10 is local tooling/tests/docs only and does not touch raw diary files.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required; raw diary files must not be sent to external providers.
- No database migration or test DB reset is required.
- No user manual diary review is required because no visible diary behaviour changed.

## Known Follow-Up

- H11 should run a bounded multi-day/runtime probe without casually bypassing H10 caps.
- Do not infer appointment create/delete/status semantics from H10; it is guardrail/comparison tooling only.

## Previous Closeout - Sprint H9

| Item | Value |
|---|---|
| Batch | Sprint H9: Historical Diary Trove Ordered Neutral Event Export |
| Integrated through | Ariadne local-only ordered neutral export; no external workers used because scope was raw-free and narrowly bounded |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Pages, Python Security, and CodeQL workflows green |
| Last updated | 2026-07-06 |

## What Changed

- Extended `scripts\historical_diary_structure_classifier.ps1` with opt-in `-IncludeOrderedSnapshots`.
- Added validator allowlist coverage for `ordered_neutral_snapshots` and `sequence_index`.
- Extended `scripts\historical_diary_event_summary_dry_run.py` so ordered neutral snapshots are preferred over grouped signature replay when present.
- Added synthetic tests for ordered snapshot validation and ordered event-summary sequencing.
- Ran a bounded local Word COM export over 40 dense-day samples from each ignored pilot root.
- Produced ignored `local_data\historical-diary-trove\inventory\ordered_snapshots_h9.json` and `local_data\historical-diary-trove\inventory\event_summary_h9.json`, both H5-validator safe.
- Added `docs\historical-diary-trove-ordered-event-export.md`.
- No raw diary files, filenames, paths, exact source timestamps, patient/staff labels, document text, external-provider calls, database writes, routes, frontend, migrations, or GitHub Pages assets were added.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_event_summary_dry_run.py scripts\historical_diary_output_safety.py tests\test_historical_diary_event_summary_dry_run.py tests\test_historical_diary_output_safety.py`.
- Focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_event_summary_dry_run.py tests\test_historical_diary_timeline_events.py tests\test_historical_diary_output_safety.py -q` (18 passed; existing warnings only).
- Local ordered export passed: `.\scripts\historical_diary_structure_classifier.ps1 -Root @('local_data\historical-diary-trove\raw\pilot','local_data\historical-diary-trove\raw\pilot_01') -Output local_data\historical-diary-trove\inventory\ordered_snapshots_h9.json -SampleSize 40 -DenseDays 1 -IncludeOrderedSnapshots`.
- Safety validation passed for ignored ordered snapshots and ignored event summary.
- Post-push audit passed: master, `handoff/current`, and durable worker mirrors all aligned at `7e9462a2`.
- GitHub workflows passed for the H9 push: Deploy GitHub Pages, Python Security, and CodeQL.

## Local Ordered Result

- `pilot`: 40 ordered snapshots, 39 transitions, 21 `no_structural_change`, 18 `small_content_delta`; character absolute delta range 0-114.
- `pilot_01`: 40 ordered snapshots, 39 transitions, 32 `no_structural_change`, 7 `small_content_delta`; character absolute delta range 0-109.
- H9 restores true adjacent neutral count deltas for the bounded sample, unlike H8's grouped-signature replay.

## Recommended User Review

No required manual review before continuing. H9 is local tooling/tests/docs only and does not touch raw diary files beyond read-only local Word COM extraction.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required; raw diary files must not be sent to external providers.
- No database migration or test DB reset is required.
- No user manual diary review is required because no visible diary behaviour changed.

## Known Follow-Up

- H10 should add explicit larger-run guardrails and comparer tooling before broad trove processing.
- Do not infer appointment create/delete/status semantics from H9; it is still neutral count/signature movement only.

## Previous Closeout - Sprint H8

| Item | Value |
|---|---|
| Batch | Sprint H8: Historical Diary Trove Local Event Summary Dry Run |
| Integrated through | Ariadne local-only aggregate dry-run; no external workers used because scope was raw-free and narrowly bounded |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Pages green after rerun; Python Security and CodeQL workflows green |
| Last updated | 2026-07-06 |

## What Changed

- Added `scripts/historical_diary_event_summary_dry_run.py`, a CLI that consumes only H5-safe aggregate JSON and writes an ignored validator-safe event summary.
- Added `tests/test_historical_diary_event_summary_dry_run.py`, using synthetic aggregate fixtures only.
- Ran the dry-run locally against ignored `local_data\historical-diary-trove\inventory\timeline_delta_h6.json`.
- Produced ignored `local_data\historical-diary-trove\inventory\event_summary_h8.json` and validated it through `scripts\historical_diary_output_safety.py`.
- Documented that H8 is a representative aggregate replay, not true chronological reconstruction, because H6 groups identical neutral signatures.
- No raw diary files, filenames, paths, exact source timestamps, patient/staff labels, document text, external-provider calls, database writes, routes, frontend, migrations, or GitHub Pages assets were added.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_event_summary_dry_run.py tests\test_historical_diary_event_summary_dry_run.py`.
- Focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_event_summary_dry_run.py tests\test_historical_diary_timeline_events.py tests\test_historical_diary_output_safety.py -q` (16 passed; existing warnings only).
- Local dry run passed: `.venv\Scripts\python.exe scripts\historical_diary_event_summary_dry_run.py local_data\historical-diary-trove\inventory\timeline_delta_h6.json`.
- Safety validation passed: `.venv\Scripts\python.exe scripts\historical_diary_output_safety.py local_data\historical-diary-trove\inventory\event_summary_h8.json`.
- Post-push audit passed: master, `handoff/current`, and durable worker mirrors all aligned at `5653dc3e`.
- GitHub workflows passed for the H8 push: Python Security and CodeQL were green; the push-triggered Pages deploy hit the known transient "try again later" failure and a fresh `workflow_dispatch` Pages run passed.

## Local Dry-Run Result

- `pilot`: 40 representative snapshots, 39 transitions, all `no_structural_change` or `small_content_delta`.
- `pilot_01`: 40 representative snapshots, 39 transitions, all `no_structural_change` or `small_content_delta`.
- Character-delta ranges are zero by design in H8 because H6 aggregate signatures do not retain per-signature character counts.

## Recommended User Review

No required manual review before continuing. H8 is local tooling/tests/docs only and does not touch raw diary files.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required; raw diary files must not be sent to external providers.
- No database migration or test DB reset is required.
- No user manual diary review is required because no visible diary behaviour changed.

## Known Follow-Up

- H9 should emit an ignored ordered neutral snapshot sequence before using event counts as evidence about actual temporal edit flow.
- Do not infer appointment create/delete/status semantics from H8; it is only a safety-gated aggregate replay.

## Previous Closeout - Sprint H7

| Item | Value |
|---|---|
| Batch | Sprint H7: Historical Diary Trove Synthetic Timeline Event Model |
| Integrated through | Ariadne synthetic-only model/tests; no external workers used because scope was small and raw-free |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Pages, Python Security, and CodeQL workflows green |
| Last updated | 2026-07-06 |

## What Changed

- Added `scripts/historical_diary_timeline_events.py`, a synthetic neutral event model for adjacent aggregate snapshot deltas.
- Added `tests/test_historical_diary_timeline_events.py`, using synthetic snapshots only.
- Extended `scripts/historical_diary_output_safety.py` to allow neutral event-summary fields while keeping raw/text/path/label fields blocked.
- Added `docs/historical-diary-trove-synthetic-event-model.md`.
- Event classes are deliberately non-semantic: `no_structural_change`, `small_content_delta`, `layout_shape_change`, `time_grid_delta`, and `large_unexplained_delta`.
- Event-summary payloads are validated through the H5 safety gate.
- No raw diary files, filenames, patient content, document text, document metadata strings, external-provider calls, database writes, routes, frontend, migrations, or GitHub Pages assets were added.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile scripts\historical_diary_timeline_events.py scripts\historical_diary_output_safety.py tests\test_historical_diary_timeline_events.py tests\test_historical_diary_output_safety.py`.
- Focused pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_timeline_events.py tests\test_historical_diary_output_safety.py -q` (14 passed; existing warnings only).
- Post-push audit passed: master, `handoff/current`, and durable worker mirrors all aligned at `5d26158f`.
- GitHub workflows passed for the H7 push: Deploy GitHub Pages, Python Security, and CodeQL.

## Recommended User Review

No required manual review before continuing. H7 is synthetic code/tests/docs only and does not touch raw diary files.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required; raw diary files must not be sent to external providers.
- No database migration or test DB reset is required.
- No user manual diary review is required because no visible diary behaviour changed.

## Known Follow-Up

- H8 may run a local event-summary dry run over ignored H6 aggregate data only.
- H8 outputs must pass `scripts/historical_diary_output_safety.py`.
- H8 should keep labels non-semantic and avoid inferring real appointment creation/deletion/status events.
- Do not process the full 58k-file trove until extraction and de-identification boundaries are proven on the pilots.

## Next Sprint Candidate

| Item | Value |
|---|---|
| Name | Sprint H8: Historical Diary Trove Local Event Summary Dry Run |
| Status | Proposed |
| Recommended agents | Ariadne local-first for raw PHI inspection; external workers only on non-PHI parser code, synthetic fixtures, or safe summaries |

Recommended scope: convert ignored H6 aggregate deltas into neutral event summaries in memory, validate the output, and commit only safe findings.

## Previous Closeout - Sprint H6

Sprint H6 reused `scripts/historical_diary_structure_classifier.ps1` over 40
dense-day files from each pilot and validated the ignored aggregate JSON through
the H5 safety gate. Both pilots remained `strong_diary_grid` in 40/40 samples,
with stable table signatures and small adjacent neutral deltas. Raw files,
filenames, exact document timestamps, document text, and metadata strings were
not committed.

## Previous Closeout - Sprint H5

Sprint H5 added `scripts/historical_diary_output_safety.py`,
`tests/test_historical_diary_output_safety.py`, and
`docs/historical-diary-trove-deidentification-contract.md`. The validator uses a
committed-output allowlist and rejects raw paths, filenames, exact document
timestamps, document text, likely person/staff labels, and long free-form
strings. Tests are synthetic-only; raw files and PHI were not committed.

## Previous Closeout - Sprint H4

Sprint H4 added `scripts/historical_diary_structure_classifier.ps1` and safe
aggregate classifier docs. Both pilots classified as `strong_diary_grid` in 8/8
tiny samples, with stable `1x11+1x3` table signatures, 2-table/14-cell layout,
dense time/date-like counts, and an inferred 10-minute interval mode. Raw files,
filenames, exact document timestamps, document text, and metadata strings were
not committed.

## Previous Closeout - Sprint H3

Sprint H3 added `scripts/historical_diary_word_extract_probe.ps1` and safe
aggregate local extraction docs. Microsoft Word COM opened 5/5 dense-day samples
from each pilot read-only with macros disabled, and emitted only aggregate
structure ranges. Raw files, filenames, document text, and metadata strings were
not committed.

## Previous Closeout - Sprint H2

Sprint H2 added `scripts/historical_diary_doc_probe.py` and safe aggregate OLE
parser feasibility docs. Both pilot dense samples were valid legacy Word/OLE
documents with `WordDocument`, `1Table`, `Data`, and summary-information streams
present in 10/10 sampled files; Word header `nFib=193` was consistent. Raw
files, filenames, document text, and metadata strings were not committed.

## Previous Closeout - Sprint H1

Sprint H1 added `scripts/historical_diary_inventory.py` and safe aggregate
inventory docs for `pilot` and `pilot_01`. The two pilot sets contain 411 and
584 `.doc` files respectively; 990 files have classic Word/OLE signatures and 5
tiny `.doc` files have non-OLE signatures. Raw files and detailed JSON stayed
ignored under `local_data/`; no filenames, document text, or PHI were committed.

## Previous Closeout - Sprint R25

Sprint R25 added `app/services/ai/evals/provider_sampling_harness.py`, static
Gemini/Vertex/adversarial provider-style sample sets, and tests proving
default-disabled/no-write/no-live-call behaviour through the R24 manifest gate.
Ariadne also hardened `manifest_eval.py` so `allow_write=True` is a
write-authority claim. Validation passed with 109 manifest/provider tests plus
`git diff --check`; Pages, Python Security, and CodeQL workflows were green.

## Previous Closeout - Sprint R24

Sprint R24 hardened `app/services/ai/evals/manifest_eval.py` for provider-style
dry-run outputs, added `tests/test_provider_readiness_dry_run_gate.py`, and
preserved Gemini/DeepSeek provider-readiness review artifacts. Validation passed
with 176 manifest tests plus `git diff --check`; no live calls, frontend,
database, route, or migration changes were made.

## Previous Closeout - Sprint R23

| Item | Value |
|---|---|
| Batch | Sprint R23: Frame-Aware Fake-Provider Validator |
| Integrated through | Antigravity/Gemini frame-shape semantics review, two DeepSeek Flash planning/review lanes, Ariadne implementation |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Python Security and CodeQL workflows green |
| Last updated | 2026-07-05 |

## What Changed

- Added `FrameSchema`, `FRAME_SCHEMAS`, and `validate_response_frame_shape()` to `app/services/ai/evals/manifest_eval.py`.
- `evaluate_manifest_response()` now reports `malformed_frame` violations and exposes `malformed_frame_detected` while preserving all R21/R22 safety detectors.
- R23 validates declared fake-provider frame kinds for `proposal`, `clarify`, `refusal`, and `read_request`; undeclared legacy responses still use the existing detector path.
- Added frame-shape tests to `tests/test_bernie_manifest_receptionist_scenarios.py` for missing staff confirmation, confirmation-envelope smuggling, malformed clarification, reason-code defaulting, refusal gaps, read-request availability claims, and unknown frame kinds.
- Preserved Antigravity/Gemini's receptionist-facing frame-shape acceptance criteria in `orchestration/fake_provider_frame_shape_acceptance_criteria.md`.
- Preserved DeepSeek Flash's adversarial frame-review concerns in `orchestration/r23_deepseek_adversarial_frame_review.md`.
- Recorded Yuri's schema-aware Bernie principle in `AGENTS.md`: Bernie may be made deeply literate in the Diary grammar through read-only source-derived context, but backend routes/signed confirmation remain the only write authority.
- No live Gemini/Bernie runtime prompt wiring was added; R23 remains fake-provider/test-only.

## Verification

- Focused R23 compile and scenario pytest passed: `.venv\Scripts\python.exe -m py_compile app\services\ai\evals\manifest_eval.py tests\test_bernie_manifest_receptionist_scenarios.py` and `.venv\Scripts\pytest.exe tests\test_bernie_manifest_receptionist_scenarios.py -q` (36 passed; existing warnings only).
- Broader manifest compile/regression passed: `.venv\Scripts\python.exe -m py_compile app\services\ai\evals\manifest_eval.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_bernie_manifest_prompt_evaluation.py tests\test_bernie_fake_provider_adversarial_prompt.py tests\test_bernie_manifest_prompt_consumption.py tests\test_bernie_diary_capability_manifest.py` and `.venv\Scripts\pytest.exe tests\test_bernie_diary_capability_manifest.py tests\test_bernie_manifest_prompt_consumption.py tests\test_bernie_manifest_prompt_evaluation.py tests\test_bernie_fake_provider_adversarial_prompt.py tests\test_bernie_manifest_receptionist_scenarios.py -q` (151 passed; existing Starlette/Google GenAI warnings only).
- Whitespace check passed: `git diff --check`.

## Recommended User Review

No required manual review before continuing if validation and post-push workflows pass. R23 is backend/test/orchestration-only and does not change visible Diary UI, Office assets, GitHub Pages content, database schema, or live provider behaviour.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required because runtime Bernie prompt wiring is still deferred.
- No database migration or test DB reset is required.
- No user manual diary review is required because no visible diary behaviour changed.

## Known Follow-Up

- Run a provider-readiness dry-run sprint before live Gemini wiring, still without granting write authority or connecting to mutation routes.
- Add real-output samples from dry-run providers only after proving they cannot mutate state.
- Extend claimed-action, availability, and frame-shape detectors as real provider outputs reveal new unsafe wording or structures.
- Consider Unicode homoglyph normalization for model-output key scanning if provider-output risk increases.

## Next Sprint Candidate

| Item | Value |
|---|---|
| Name | Sprint R24: Provider-Readiness Dry-Run Gate |
| Status | Proposed |
| Recommended agents | Check Claude availability first; use Claude if healthy, Antigravity/Gemini for receptionist/product semantics, and DeepSeek Flash workers for adversarial provider-output fixtures |

Recommended scope: add a no-write provider-readiness dry-run gate that can evaluate sampled model-style outputs against manifest, scenario, and frame-shape validators without connecting to mutation routes or treating the model as authoritative.

## Previous Closeout - Sprint R22

| Item | Value |
|---|---|
| Batch | Sprint R22: Fake-Provider Receptionist Scenario Gates |
| Integrated through | Claude plan, Antigravity/Gemini UX acceptance review, DeepSeek Flash adversarial gap analysis, Ariadne implementation |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Python Security and CodeQL workflows green |
| Last updated | 2026-07-05 |

## What Changed

- Extended `app/services/ai/evals/manifest_eval.py` with deterministic receptionist scenario gates for proposal, clarify, refusal, and backend read-request frames.
- Added `ReceptionistScenario`, `ReceptionistScenarioUnsafeResponse`, `ReceptionistScenarioEvalResult`, `RECEPTIONIST_SCENARIO_GATES`, `evaluate_receptionist_scenario()`, and `run_receptionist_scenario_gates()`.
- Hardened fake-provider output evaluation for claimed completed actions, live availability claims, ambiguous-patient defaulting, invalid/defaulted reason-code claims, and strict model-output `writes_authorized=True` detection.
- Added `tests/test_bernie_manifest_receptionist_scenarios.py`, covering the ordinary Margaret Thompson/Dr Shera proposal path, ambiguous patient clarification, invalid reason-code clarification, envelope-injection refusal, and availability/collision deflection.
- Preserved Antigravity/Gemini's receptionist-facing acceptance criteria in `orchestration/fake_provider_scenario_ux_acceptance_review.md`.
- Preserved DeepSeek Flash's adversarial response gap analysis and future test specification in `orchestration/r22_deepseek_adversarial_test_spec.md`.
- Claude produced the accepted implementation plan but hit the session cap during implementation; Ariadne implemented the seam locally using the accepted plan plus DeepSeek/Ariadne amendments.
- No live Gemini/Bernie runtime prompt wiring was added; R22 remains fake-provider/test-only.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile app\services\ai\evals\manifest_eval.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_bernie_manifest_prompt_evaluation.py tests\test_bernie_fake_provider_adversarial_prompt.py tests\test_bernie_manifest_prompt_consumption.py tests\test_bernie_diary_capability_manifest.py`.
- Focused R22/R21 pytest passed: `.venv\Scripts\pytest.exe tests\test_bernie_manifest_receptionist_scenarios.py tests\test_bernie_manifest_prompt_evaluation.py tests\test_bernie_fake_provider_adversarial_prompt.py -q` (99 passed; existing Starlette/Google GenAI warnings only).
- Broader manifest regression pytest passed: `.venv\Scripts\pytest.exe tests\test_bernie_diary_capability_manifest.py tests\test_bernie_manifest_prompt_consumption.py tests\test_bernie_manifest_prompt_evaluation.py tests\test_bernie_fake_provider_adversarial_prompt.py tests\test_bernie_manifest_receptionist_scenarios.py -q` (138 passed; existing Starlette/Google GenAI warnings only).
- Whitespace check passed: `git diff --check`.

## Recommended User Review

No required manual review before continuing if post-push workflows pass. R22 is backend/test/orchestration-only and does not change visible Diary UI, Office assets, GitHub Pages content, database schema, or live provider behaviour.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required because runtime Bernie prompt wiring is still deferred.
- No database migration or test DB reset is required.
- No user manual diary review is required because no visible diary behaviour changed.

## Known Follow-Up

- Add a frame-aware fake-provider validator if scenario gates need deeper semantic checks than `frame_kind` plus safety flags.
- Run a provider-readiness dry-run sprint before live Gemini wiring, still without granting write authority or connecting to mutation routes.
- Extend claimed-action and availability phrase lists as real provider outputs reveal new unsafe wording.
- Consider Unicode homoglyph normalization for model-output key scanning if provider-output risks increase.

## Previous Closeout - Sprint R21

| Item | Value |
|---|---|
| Batch | Sprint R21: Manifest Fake-Provider Prompt Evaluation |
| Integrated through | Claude implementation, Antigravity/Gemini prompt UX safety review, DeepSeek Flash adversarial tests, Ariadne integration |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Python Security and CodeQL workflows green |
| Last updated | 2026-07-05 |

## What Changed

- Added `app/services/ai/evals/manifest_eval.py`, a deterministic fake-provider evaluation seam for the Bernie Diary Capability Manifest prompt block.
- Added `ManifestPromptInput`, `ManifestFakeProvider`, `ManifestResponseViolation`, `ManifestEvalResult`, `assemble_manifest_prompt_input()`, `evaluate_manifest_response()`, and `run_manifest_prompt_eval()`.
- Added `tests/test_bernie_manifest_prompt_evaluation.py` with pure-Python coverage for prompt assembly determinism, no live provider construction, fake-provider protocol conformance, safe/compliant responses, write-authority claims, PHI-like response keys, confirmation-bypass language, and full fake-provider round trips.
- Added DeepSeek's adversarial `tests/test_bernie_fake_provider_adversarial_prompt.py`, repaired by Ariadne for syntax/diff hygiene, covering confirmation-bypass structure, bounded reason codes, source-leak prevention, live-availability deflection, safety assertion hardening, and compact/verbose field contracts.
- Preserved Antigravity/Gemini's receptionist/product-safety review in `orchestration/fake_provider_prompt_ux_safety_review.md`, including acceptance scenarios for ambiguity clarification, invalid reason-code clarification, envelope injection refusal, and roster/collision deflection.
- Recorded Yuri's architecture principle in `AGENTS.md` and `orchestration/bernie_release_gates.md`: Bernie should become schema-literate and native to the Diary state grammar through read-only source-derived context, while backend routes/signed confirmation remain the only write authority.
- No live Gemini/Bernie runtime prompt wiring was added; R21 remains a fake-provider/test-only gate.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile app\services\ai\evals\manifest_eval.py tests\test_bernie_manifest_prompt_evaluation.py tests\test_bernie_fake_provider_adversarial_prompt.py`.
- Focused R21 pytest passed: `.venv\Scripts\pytest.exe tests\test_bernie_manifest_prompt_evaluation.py tests\test_bernie_fake_provider_adversarial_prompt.py -q` (76 passed; existing Starlette/Google GenAI warnings only).
- Broader manifest regression pytest passed: `.venv\Scripts\pytest.exe tests\test_bernie_diary_capability_manifest.py tests\test_bernie_manifest_prompt_consumption.py tests\test_bernie_manifest_prompt_evaluation.py tests\test_bernie_fake_provider_adversarial_prompt.py -q` (115 passed; existing Starlette/Google GenAI warnings only).
- Whitespace check passed: `git diff --check`.

## Recommended User Review

No required manual review before continuing if post-push workflows pass. R21 is backend/test/orchestration-only and does not change visible Diary UI, Office assets, GitHub Pages content, database schema, or live provider behaviour.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required because the manifest is still not wired into runtime Bernie prompts.
- No database migration or test DB reset is required.
- No user manual diary review is required because no visible diary behaviour changed.

## Known Follow-Up

- Add fake-provider receptionist scenario gates that exercise the ordinary Margaret Thompson/Dr Shera happy path, ambiguity clarification, invalid reason-code clarification, envelope injection refusal, and availability/collision deflection as structured model-output scenarios.
- Add Unicode homoglyph normalization to `assert_manifest_prompt_safe()` if future adversarial testing proves model/provider output can use confusable key names.
- Continue deferring live Gemini wiring until fake-provider scenario gates prove proposal/clarify/refusal envelopes remain non-authoritative.
- Decide whether and where to enforce capability `allowed_authors` at route/envelope boundaries.

## Next Sprint Candidate

| Item | Value |
|---|---|
| Name | Sprint R22: Fake-Provider Receptionist Scenario Gates |
| Status | Proposed |
| Recommended agents | Check Claude availability first; use Claude if healthy for backend eval harness, Antigravity/Gemini for receptionist scenario/product-safety review, and one or more DeepSeek Flash workers for adversarial scenario cases |

Recommended scope: promote Antigravity's R21 acceptance scenarios into deterministic fake-provider tests that validate structured proposal/clarify/refusal envelopes before any live Gemini prompt integration.

## Previous Closeout - Sprint R20

| Item | Value |
|---|---|
| Batch | Sprint R20: Bernie Manifest Prompt Consumption Gate |
| Integrated through | Claude implementation, DeepSeek Flash adversarial tests, Antigravity/Gemini prompt-safety review, Ariadne integration |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Python Security and CodeQL workflows green |
| Last updated | 2026-07-05 |

## What Changed

- Added a non-runtime prompt-consumption scaffold in `app/services/diary/capability_manifest.py`: `build_manifest_prompt_context()`, `assert_manifest_prompt_safe()`, `render_manifest_prompt_block()`, and `MANIFEST_PROMPT_CONTEXT_MAX_CHARS`.
- The compact prompt context is JSON-serializable, deterministic, size-budgeted, PHI/credential-key guarded, and still preserves the explicit staff-confirmed confirmation write boundary.
- Added `tests/test_bernie_manifest_prompt_consumption.py` with deterministic tests for prompt-context safety, compactness, write-authority isolation, poison payload rejection, and render stability.
- Extended `tests/test_bernie_diary_capability_manifest.py` with DeepSeek adversarial prompt-consumption tests for write-authority phrasing, PHI/credential leakage, raw-code/source dumping, confirm-grade evidence leakage, backend-policy bypass phrasing, author/tier coherence, schema-version separation, and prompt-injection patterns.
- Preserved Gemini's prompt-safety principles, refusal/clarification rules, and acceptance criteria in `orchestration/manifest_prompt_safety_review.md`.
- No live Gemini/Bernie prompt path was wired; R20 deliberately ships a safe no-runtime-change gate first.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile app\services\diary\capability_manifest.py tests\test_bernie_diary_capability_manifest.py tests\test_bernie_manifest_prompt_consumption.py`.
- Focused R20 pytest passed: `.venv\Scripts\pytest.exe tests\test_bernie_diary_capability_manifest.py tests\test_bernie_manifest_prompt_consumption.py -q` (39 passed; existing Starlette/Google GenAI warnings only).
- Whitespace check passed: `git diff --check`.

## Recommended User Review

No required manual review before continuing if post-push workflows pass. R20 is backend/test/orchestration-only and does not wire the manifest into live prompts, change Diary UI, touch Office assets, migrate the database, or call Gemini.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required because the prompt-consumption helper is not yet wired into runtime Bernie prompts.
- No database migration or test DB reset is required.
- No user manual diary review is required because no visible diary behaviour changed.

## Known Follow-Up

- Add a fake-provider prompt assembly/evaluation sprint before any live Gemini wiring.
- Test refusal behavior for ambiguous patient/practitioner identity, invalid status/reason-code pairs, and attempts to bypass confirmation envelopes.
- Decide whether to make reason codes non-null-required for `Cancelled`, `DNA`, and `NoShow` after a migration/backfill policy.
- Unify duplicated frontend/backend schedule-explanation copy catalogs.
- Decide whether and where to enforce capability `allowed_authors` at route/envelope boundaries.

## Next Sprint Candidate

| Item | Value |
|---|---|
| Name | Sprint R21: Manifest Fake-Provider Prompt Evaluation |
| Status | Proposed |
| Recommended agents | Check Claude availability first; use Claude if healthy, Antigravity/Gemini for receptionist/prompt-safety review, and DeepSeek Flash for adversarial fake-provider tests |

Recommended scope: add a fake-provider-only prompt assembly/evaluation harness that uses `render_manifest_prompt_block()` without live Gemini calls, proving Bernie-facing prompt instructions preserve schema literacy without granting authority or bypassing backend confirmation.

## Previous Closeout - Sprint R19

| Item | Value |
|---|---|
| Batch | Sprint R19: Bernie Manifest Drift Guardrails |
| Integrated through | Ariadne integration, two DeepSeek Flash lanes replacing capped Claude, Antigravity/Gemini domain review |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit clean; Pages, UI Review, Python Security, and CodeQL workflows green after hotfix |
| Last updated | 2026-07-05 |

## What Changed

- Added `STATUS_SPECIFIC_REASON_CODE_POLICY` in `app/schemas/appointments.py` as the backend source of truth for terminal status/reason-code combinations.
- Added schema validators so new `Cancelled`, `DNA`, and `NoShow` writes reject mismatched non-null reason codes while preserving null/grandfathering semantics.
- Aligned `docs/diary/diary.js` so `Cancelled` options include `PATIENT_RESCHEDULED`, `PATIENT_UNWELL`, and `CLINIC_RESCHEDULED`; cache-busted `docs/diary/diary.html` to `diary.js?v=173`.
- Added backend/frontend drift tests in `tests/test_reason_code_backend.py` for valid/invalid status-code pairs and frontend `STATUS_SPECIFIC_REASON_CODE_OPTIONS` parity.
- Added `tests/test_bernie_outcome_copy_drift_guard.py`, parsing `diary.js` copy dictionaries to ensure every backend `BernieBookingOutcomeKind` has frontend copy coverage or an explicit transient exception.
- Updated the capability manifest so Bernie-facing reason-code policy is source-derived from `STATUS_SPECIFIC_REASON_CODE_POLICY`.
- Preserved Gemini's R19 domain review in `orchestration/manifest_drift_review.md`.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile app\schemas\appointments.py app\services\diary\capability_manifest.py tests\test_reason_code_backend.py tests\test_bernie_outcome_copy_drift_guard.py tests\test_bernie_diary_capability_manifest.py`.
- Focused R19 pytest passed: `.venv\Scripts\pytest.exe tests\test_reason_code_backend.py tests\test_bernie_outcome_copy_drift_guard.py tests\test_bernie_diary_capability_manifest.py -q` (41 passed; existing Starlette/Google GenAI warnings only).
- JS syntax passed: `node --check docs\diary\diary.js`.
- Frontend asset version check passed: `.venv\Scripts\python.exe scripts\check_frontend_versions.py`.
- Targeted UI review hotfix test passed: `.venv\Scripts\pytest.exe review\test_diary_smoke.py -q --tb=short -k "reason_code_dropdown_no_default"`.
- Full local UI Review harness passed after hotfix: `.venv\Scripts\pytest.exe review\test_diary_smoke.py -q --tb=short --junitxml=review\diary-review.xml` (121 passed).
- Whitespace check passed: `git diff --check`.

## Recommended User Review

No required manual review before continuing. The only visible change is adding three legitimate cancellation reason options to the existing Diary reason-code dropdown; deterministic backend/frontend parity tests and the UI Review harness cover the option set.

## Not Required Before Moving On

- No browser/Office smoke is required because the frontend change is a constant-only dropdown option alignment with cache-bust and syntax/version checks.
- No live Gemini/Vertex call is required because the manifest is not yet injected into a runtime Bernie prompt.
- No database migration or test DB reset is required.
- No user manual diary review is required before the next sprint; optional later live check is to confirm the Cancelled reason dropdown includes patient rescheduled, patient unwell, and clinic requested reschedule.

## Known Follow-Up

- Decide whether to make reason codes non-null-required for `Cancelled`, `DNA`, and `NoShow` after a migration/backfill policy.
- Unify duplicated frontend/backend schedule-explanation copy catalogs.
- Decide whether and where to enforce capability `allowed_authors` at route/envelope boundaries.
- Add shared typed confidence bands for patient/practitioner recognition before representing those bands as authoritative manifest facts.
- Design a safe prompt/context injection path for Bernie to read the manifest after remaining authority-boundary checks.

## Previous Closeout - Sprint R18

| Item | Value |
|---|---|
| Batch | Sprint R18: Bernie Diary Capability Manifest v1 |
| Integrated through | Ariadne implementation, two DeepSeek Flash review lanes, Antigravity/Gemini domain review |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit and GitHub Python Security/CodeQL workflows clean |
| Last updated | 2026-07-05 |

## What Changed

- Added `app/services/diary/capability_manifest.py`, a JSON-serializable, source-derived, read-only manifest builder for Bernie's native Diary schema literacy.
- Manifest sections cover appointment statuses, booking channels, diary template and waiting-area fields, Bernie session states/events, capability tiers, outcome kinds, reason codes, evidence/confirmation boundaries, and explicit non-authority boundaries.
- Added drift-watch notes for frontend outcome copy, frontend-only status-specific reason-code option lists, declared-but-not-enforced `allowed_authors`, and untyped patient/practitioner confidence bands.
- Added deterministic tests in `tests/test_bernie_diary_capability_manifest.py` proving manifest source parity, non-authority wording, capability registry immutability/uniqueness, staff-only confirm capabilities, outcome coverage, and confirmation-only write authority.
- Preserved Gemini's domain/safety critique in `orchestration/bernie_diary_manifest_review.md`.
- Updated `orchestration/bernie_native_diary_agent_notes.md` with the implemented version of Yuri's "Bernie knows the diary body map but does not rule it" architecture.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile app\services\diary\capability_manifest.py tests\test_bernie_diary_capability_manifest.py`.
- Focused manifest pytest passed: `.venv\Scripts\pytest.exe tests\test_bernie_diary_capability_manifest.py -q` (10 passed; existing Starlette/Google GenAI warnings only).
- Whitespace check passed: `git diff --check`.

## Recommended User Review

No required manual review before continuing. This is backend data-contract/test/orchestration work only: no live prompt path, frontend route, Office taskpane, GitHub Pages asset, database migration, or appointment mutation behaviour changes.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required because the manifest is not yet injected into a runtime Bernie prompt.
- No database migration or test DB reset is required.
- No user manual diary review is required because no visible diary behaviour changed.

## Known Follow-Up

- Add drift guardrails that bind frontend Bernie outcome copy to backend `BernieBookingOutcomeKind`.
- Promote status-specific reason-code display policy into backend source-of-truth policy before exposing it as authoritative manifest content.
- Decide whether and where to enforce capability `allowed_authors` at route/envelope boundaries.
- Add shared typed confidence bands for patient/practitioner recognition before representing those bands as authoritative manifest facts.
- Only after the drift guards are in place, design a safe prompt/context injection path for Bernie to read the manifest.

## Previous Closeout - Sprint R17

| Item | Value |
|---|---|
| Batch | Sprint R17: Expired-Session Diary UX Banner |
| Integrated through | Ariadne implementation, DeepSeek Flash auth-banner plan, Antigravity/Gemini receptionist-domain review |
| Status | Pushed to `master`/`handoff/current`; mirrors realigned; audit and GitHub workflows clean |
| Last updated | 2026-07-05 |

## What Changed

- Added a visible `[data-testid="diary-auth-banner"]` in `docs/diary/diary.html` for missing, locally expired, or backend-rejected Diary auth.
- Styled the banner in `docs/diary/diary.css` as a calm, staff-facing session notice that sits above the Diary body.
- Updated `docs/diary/diary.js` so auth loss clears the token, hides stale grid content, suppresses generic `401` diary errors, stops background refresh polling, and hides the banner again after valid re-auth.
- Cache-busted `docs/diary/diary.html` to `diary.css?v=135` and `diary.js?v=172`.
- Added three deterministic non-smoke auth-banner tests to `review/test_diary_smoke.py` for missing token, expired local token, and backend `401`.
- Preserved Gemini's receptionist-domain review in `docs/receptionist_review_r17.md`.
- Captured Yuri/Ariadne's "schema-literate, not code-authoritative" Bernie architecture note in `orchestration/bernie_native_diary_agent_notes.md`.

## Verification

- JS syntax passed: `node --check docs\diary\diary.js`.
- Focused auth-banner smoke passed: `.venv\Scripts\pytest.exe review\test_diary_smoke.py -q --tb=short -k "auth_banner" --junitxml=review\auth-banner-review.xml` (3 passed).
- Full Diary smoke passed: `.venv\Scripts\pytest.exe review\test_diary_smoke.py -q --tb=short --junitxml=review\diary-review.xml` (121 passed).
- Frontend asset check passed: `..\.venv\Scripts\python.exe ..\scripts\check_frontend_versions.py`.
- Whitespace check passed: `git diff --check`.

## Recommended User Review

No required manual review before continuing. This is covered by deterministic non-smoke auth tests, full Diary smoke coverage, and static asset checks. Optional live review after deploy: open the Diary with an expired/stale session and confirm the banner appears instead of a blank grid.

## Not Required Before Moving On

- No backend/API/database verification is required because no backend files, schemas, or migrations changed.
- No Office taskpane build is required because the changed production surface is `docs/diary`, not bundled taskpane source.
- No live Gemini/Vertex call is required; Gemini's contribution was a documentation-only domain review.
- No user manual auth-expiry test is required before the next sprint because the three auth-loss paths are covered by deterministic Playwright route interception.

## Known Follow-Up

- Consider richer connecting/unauthorized copy variants and explicit offline-network handling as separate UX hardening.
- Consider a live Office dialog re-auth/reopen affordance only if the taskpane can safely support it.

## Previous Closeout - Sprint R4

| Item | Value |
|---|---|
| Batch | Sprint R4: Backdated/Past-Date Safety |
| Integrated through | DeepSeek Flash implementation lane, DeepSeek Flash adversarial review lane (superseded into Ariadne route tests), Antigravity/Gemini domain-policy artifacts, and Ariadne verification/polish |
| Status | Pushed to `master`/`handoff/current`, mirrors realigned, audit clean; disposable DeepSeek worktrees retired |
| Last updated | 2026-07-05 |

## What Changed

- Added `requested_date_in_past` to the shared Bernie slot-search normalizer when `date_from < reference_date`.
- Aligned the interpret route's temporal confidence axis so past requested dates are reported as `block`, not merely generic slot-validity failure.
- Added route regressions proving the interpret and supervised-booking paths block before executable slot search for absolute past dates.
- Added unit coverage for past, same-day, future, relative today/tomorrow, and no-reference normalizer boundaries.
- Integrated Gemini's R4 receptionist policy note in `docs/receptionist_review_r4.md`.
- Added three natural-language scenario fixtures for absolute past dates, same-day past windows, and stale reference-date confirmation memory under `tests/fixtures/bernie_scenarios/`.
- Superseded the second DeepSeek adversarial test branch because it intentionally captured pre-fix fail-open behavior; useful findings were folded into Ariadne's route tests and closeout follow-ups.
- No Diary UI, taskpane, Word assets, GitHub Pages assets, database migrations, live provider calls, GraphRAG/MCP/indexer automation, or raw appointment mutation endpoints changed.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile app\services\bernie_slot_normalizer.py app\routers\appointments.py tests\test_bernie_slot_normalizer.py tests\test_bernie_confidence_policy.py tests\test_bernie_supervised_booking_wrapper.py tests\test_bernie_scenario_integrity.py`.
- Focused R4/D8/scenario suite passed: `.venv\Scripts\python.exe -m pytest tests\test_bernie_slot_normalizer.py tests\test_bernie_confidence_policy.py tests\test_bernie_supervised_booking_wrapper.py tests\test_bernie_d8_patient_collision_source_hardening.py tests\test_bernie_d8_collision_source_hardening.py tests\test_bernie_scenario_integrity.py -q` (106 passed, 1 skipped; existing Starlette/Google GenAI warnings only).

## Recommended User Review

No required manual review for Sprint R4. This is backend guard/test/domain-memory work and does not change visible Diary UI, taskpane, Word add-in, GitHub Pages assets, or live provider behavior.

## Not Required Before Moving On

- No browser/Office/GitHub Pages smoke is required because no frontend or deployed static asset changed.
- No live Gemini/Vertex call is required; this sprint used deterministic tests and domain fixtures only.
- No database migration or test database reset is required; the R4 verification used existing pytest fixtures only.

## Known Follow-Up

- Promote selected R3/R4 natural-language scenario fixtures into executable replay coverage where the harness can express revision conflicts, past-date guardrails, and session freshness cleanly.
- Decide product policy for direct raw appointment mutation/create-proposal endpoints: R4 intentionally guards Bernie's new-booking slot-search path, not every administrative or retrospective appointment write surface.
- Future frontend/session UX work should preserve typed receptionist input on stale-session errors where clinically safe while still blocking stale mutation.

## Next Sprint Candidate

| Item | Value |
|---|---|
| Name | Sprint R5: Executable Scenario Promotion |
| Status | Dispatched after R4 push/mirror/audit |
| Recommended agents | Two DeepSeek Flash workers under the Claude-recuperation fallback rule, plus Antigravity/Gemini for domain-priority/test-design |

R5 turns the best R3/R4 natural-language fixtures into executable replay coverage where the current harness can express them cleanly, while leaving session-freshness or direct mutation policy gaps as documented corpus memory.

## Previous Closeout - Sprint R2

| Item | Value |
|---|---|
| Batch | Sprint R2: Clarification Merge Semantics |
| Integrated through | Claude backend/session implementation, Antigravity/Gemini receptionist-domain acceptance review, DeepSeek Flash regression lane, and Ariadne verification/polish |
| Status | Integrated, pushed to `master`/`handoff/current`, mirrors realigned, audit clean |
| Last updated | 2026-07-05 |

## What Changed

- Added clarification-reply merge semantics to the Bernie interpret route so a follow-up answer can carry forward prior resolved appointment fields from a `requested_appointment` context frame.
- Added a request-frame payload for resolved command fields including practitioner, patient, date, time window, duration, appointment type, and location.
- Preserved new-reply-wins behaviour: explicitly supplied fields in the clarification reply override carried-forward fields, while silent fields are gap-filled from the prior frame.
- Added focused backend tests in `tests/test_bernie_clarification_merge.py` proving patient/date/time/duration preservation, practitioner-name clarification, new-reply-wins override, no merge without a prior frame, and no appointment/audit writes.
- Integrated Gemini's receptionist-domain review in `docs/receptionist_review_r2.md` and added the intent-switch scenario fixture `booking_to_extension_switch_during_clarification.yaml`.
- Integrated DeepSeek Flash regression tests in `tests/test_deepseek_clarification_regression.py` after Ariadne repaired one false-positive static import assertion.
- Codified Graphify usage: Ariadne may use it autonomously for known-symbol impact/orientation, but not as broad search, MCP memory, hooks, or auto-indexing yet.
- No Diary UI, taskpane, Word assets, migrations, live provider prompts, GraphRAG, PHI/log ingestion, or auto-mode behaviour changed.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile app\routers\appointments.py tests\test_bernie_clarification_merge.py tests\test_deepseek_clarification_regression.py tests\test_bernie_scenario_integrity.py tests\bernie_scenarios\loader.py tests\bernie_scenarios\replay.py`.
- R2 focused suite passed: `.venv\Scripts\python.exe -m pytest tests\test_bernie_clarification_merge.py tests\test_deepseek_clarification_regression.py tests\test_bernie_scenario_integrity.py tests\bernie_scenarios -q` (47 passed, 1 skipped, 1 xfailed; existing Starlette/Google GenAI warnings only).
- Adjacent interpret suite passed: `.venv\Scripts\python.exe -m pytest tests\test_bernie_interpret_booking_instruction.py -q` (24 passed; existing warnings only).
- Adjacent normalizer/slot-search suite passed after resetting the local test database and rerunning sequentially: `.venv\Scripts\python.exe -m pytest tests\test_bernie_slot_normalizer.py tests\test_slot_search_normalize_endpoint.py tests\test_slot_search_normalized_execution.py -q` (45 passed; existing warnings only).
- `git diff --check` passed.
- A parallel adjacent pytest attempt caused the known PostgreSQL test-schema race (`userrole` enum duplicate) and left `gp_pms_test` half-dropped. Ariadne reset only the local `gp_pms_test` database and reran the suites sequentially; they passed.

## Recommended User Review

No required manual review for Sprint R2. This is backend/test-domain work for the Bernie interpret route and does not change the visible Diary UI, taskpane, Word add-in, GitHub Pages assets, or confirmed appointment mutation path.

## Not Required Before Moving On

- No live Diary/Office/Chrome smoke is required; no frontend asset changed.
- No live Gemini/Vertex call is required; tests use deterministic/fake provider paths and source/fixture checks.
- No database migration, seed reset beyond the local test DB repair, GraphRAG, production log ingestion, PHI handling review, or GitHub Pages deployment check is required.

## Known Follow-Up

- Gemini flagged correction-vs-clarification ambiguity: explicit corrected fields must override preserved fields, while silent fields should carry forward.
- Gemini also flagged stale-session/session-revision hardening: future session append flows should reject stale revision coordinates rather than blending stale client context.
- The new intent-switch fixture is accepted as natural-language project memory; it is not yet executable replay coverage.
- The test database concurrency race remains a tooling/test-harness issue: avoid running DB-backed pytest sessions in parallel against the same `gp_pms_test` schema.
- Keep the headless `codex exec -c 'model_provider="deepseek_bridge"' -m deepseek-flash` path as the trusted DeepSeek Flash worker route; Ariadne still needs to verify and submit when workspace-write blocks git/Python.

## Next Sprint Candidate

| Item | Value |
|---|---|
| Name | Sprint R3: Stale Session / Revision Hardening |
| Status | Dispatched; plan gate pending |
| Recommended agents | Claude backend/session lane, Antigravity/Gemini domain acceptance lane, DeepSeek Flash regression lane, Ariadne integration |

R3 is proceeding with server-side stale session/revision hardening as the primary product-safety slice. Scenario promotion remains useful when it directly proves stale browser, two-receptionist, correction-vs-clarification, or intent-switch behavior.

## Previous Closeout - Sprint R1

| Item | Value |
|---|---|
| Batch | Sprint R1: Reception Scenario Corpus Foundation |
| Integrated through | Claude replay-harness implementation, Antigravity/Gemini receptionist scenario corpus, DeepSeek Flash validator lane, and Ariadne schema integration repair |
| Status | Integrated, pushed, mirrors realigned, and audited |
| Last updated | 2026-07-05 |

R1 established the version-controlled Bernie receptionist scenario corpus under
`tests/fixtures/bernie_scenarios/`, the `tests/bernie_scenarios/` replay
harness, and fixture integrity validation. It changed no production backend,
frontend Diary UI, taskpane, migrations, GraphRAG, live provider prompts,
PHI/log ingestion, or auto-mode behaviour.

## Previous Closeout - Sprint D6

| Item | Value |
|---|---|
| Batch | Sprint D6: Patient Advisory Collision Semantics |
| Integrated through | Claude implementation tests, Antigravity/Gemini domain-policy review, DeepSeek Flash scout/test branch review, and Ariadne integration cleanup |
| Status | Integrated, pushed, mirrors realigned, and audited at `ca375c5` |
| Last updated | 2026-07-04 |

## What Changed

- Added a dedicated D6 regression suite proving Bernie only emits the `existing_future_follow_up` warning when a recognised patient's future booking is on the requested appointment day.
- Preserved the broad `patient_booking_context.existing_future_follow_up` flag as advisory context: it can say the patient has some future booking, but it is not itself permission to show a collision warning.
- Locked the interpret route and supervised booking route against the reported regression where today's Margaret bookings blocked or warned against a request for tomorrow/Saturday.
- Added a warning-shape assertion so the same-day advisory remains a warning, not a hard block.
- Accepted Claude's consolidated D6 test module and folded in DeepSeek's unique warning-structure assertion; reverted duplicate DeepSeek scatter added to older test files during integration cleanup.
- Used Antigravity/Gemini as an independent backend/domain-policy review lane, not a UX-only worker. Gemini agreed with the broad-context/narrow-warning split and surfaced useful follow-up risks.
- No production backend code, frontend code, schema, migration, GraphRAG, persisted session state, or staff-facing copy was changed in D6.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile tests/test_bernie_d6_patient_advisory_collision.py tests/test_bernie_patient_context.py tests/test_bernie_interpret_booking_instruction.py tests/test_bernie_supervised_booking_wrapper.py`.
- Focused/adjacent pytest passed after Ariadne integration cleanup: `.venv\Scripts\python.exe -m pytest tests/test_bernie_d6_patient_advisory_collision.py tests/test_bernie_patient_context.py tests/test_bernie_interpret_booking_instruction.py tests/test_bernie_supervised_booking_wrapper.py tests/test_bernie_booking_outcomes.py -q` (103 passed; existing Starlette/Google GenAI warnings only).
- Claude's submitted D6 tests were reviewed and accepted as the canonical regression suite.
- Antigravity/Gemini review artifact was inspected and integrated as domain-policy evidence.
- DeepSeek Flash branch was reviewed; its duplicate file-local additions were superseded by the canonical D6 suite, with its unique warning-shape check preserved.

## Recommended User Review

No required manual review for D6. It is backend regression-test hardening only and does not change live Diary/Bernie UI behaviour yet.

## Not Required Before Moving On

- No UI retest is required for this sprint because no frontend asset changed.
- No Vertex/Gemini live call is needed; tests use deterministic fake/interpreted paths.
- No database migration, GraphRAG integration, persisted Bernie session table, or broad root-to-branch API review was touched.

## Known Follow-Up

- Frontend `docs/diary/diary.js` still has hardcoded/overridden `existing_future_follow_up` display copy. A near-term frontend/domain-copy sprint should render backend `issue.message` instead of scripted patient-specific text.
- `has_existing_booking_on_requested_day` currently checks compact `future_bookings`, which is capped. A later backend hardening sprint should add an exact requested-day DB lookup so collisions outside the compact context cap cannot be missed.
- Reschedule/extend workflows will need a `source_appointment_id` or equivalent so Bernie's duplicate-day warning does not flag the appointment being edited as a separate collision.
- Keep expanding Antigravity/Gemini usage beyond UX where it can provide domain-policy critique, test-design review, architecture dissent, and bounded implementation on clear file boundaries.

## Next Sprint Candidate

| Item | Value |
|---|---|
| Name | Sprint D7: Backend-Supplied Patient Advisory Copy and Collision Source Hardening |
| Status | In local review as Sprint D7 |
| Recommended agents | Claude or DeepSeek implementation lane for backend/source hardening, Antigravity/Gemini for Diary UI copy review, Ariadne final integration; native Codex worker optional when OpenAI usage allows |

D7 should likely fix the visible Bernie copy path first: the UI should show backend-authored advisory text and stop hardcoding Margaret/scripted language. If the user prioritises backend safety first, D7 can instead add direct requested-day duplicate lookup plus source-appointment exclusion.


## Previous Closeout - Sprint D5

| Item | Value |
|---|---|
| Batch | Sprint D5: Route-Builder Search Horizon Threading |
| Integrated through | Claude implementation, DeepSeek Flash scout, Antigravity/Gemini domain-policy review, and Ariadne review/polish |
| Status | Integrated, pushed, mirrors realigned, and audited at `eff7cdd` |
| Last updated | 2026-07-04 |

## What Changed

- Added `_derive_search_horizon(reference_date, normalization)` in `appointments.py` to derive `same_day`, `advance`, or `None` from normalized slot-search date context without reading wall-clock state.
- Threaded `search_horizon` into route-built `BernieSlotSearchFrame` records for real searched results: `searched_with_candidates` and `searched_no_candidates`.
- Left `not_run` and `blocked` slot-search frames at `None`, because those do not represent an executed deterministic search against a resolved date.
- Added focused D5 tests for helper derivation, frame-level tagging, untagged skipped/blocked frames, and unchanged outcome semantics for same-day, advance, and `None` horizons.
- Preserved the D4/Ariadne invariant: `search_horizon` is metadata only; policy/outcome logic does not read it, and genuine `searched_no_candidates` remains `no_matching_times`.
- Integrated Antigravity/Gemini as a real non-UX review lane. Gemini agreed with threading by `reference_date`, recommended route-level tests, and preserved the no-advisory-downgrade invariant.
- No frontend/UI, API schema, migration, GraphRAG, persisted session table, or staff-facing copy change was added.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile app/routers/appointments.py tests/test_bernie_d5_route_builder_search_horizon.py`.
- Focused D5/D4/adjacent suite passed after Ariadne polish: `.venv\Scripts\python.exe -m pytest tests/test_bernie_d5_route_builder_search_horizon.py tests/test_bernie_d4_diary_domain_frames_policy.py tests/test_diary_schedule_explanations.py tests/test_bernie_booking_outcomes.py tests/test_bernie_context_frames.py -q` (90 passed; existing Starlette/Google GenAI warnings only).
- Antigravity/Gemini review lane ran `tests/test_bernie_d4_diary_domain_frames_policy.py` successfully before submitting its review artifact.
- `git diff --check` passed.
- Full `.venv\Scripts\python.exe -m pytest tests -q` was not rerun for D5; previous full runs showed pre-existing/global failures outside these diary-domain slices.

## Recommended User Review

No required manual review. D5 is backend route/domain metadata threading only. User-facing diary and Bernie UI behaviour should be unchanged.

## Not Required Before Moving On

- No frontend behaviour changed.
- `search_horizon` does not yet alter copy or outcome routing.
- No persisted Bernie session table, GraphRAG/vector store, auto-mode, taskpane, Command Centre, or broad API rewrite was implemented.

## Known Follow-Up

- Continue moving reception facts and policy into the diary domain before adjusting staff-facing copy.
- Consider a later UI/copy sprint only after the backend frame set can distinguish roster gaps, true searched no-candidates, patient advisory context, and same-day/advance search horizon.
- Use Antigravity/Gemini as a routine independent domain/test-design lane when Gemini quota is available, not only for UX.

## Next Sprint Candidate

| Item | Value |
|---|---|
| Name | Sprint D6: Patient Advisory Context Collision Semantics |
| Status | Completed as Sprint D6 |
| Recommended agents | Claude implementation lane, Antigravity/Gemini domain-policy review, DeepSeek Flash scout/review; native Codex worker only if OpenAI usage allows |

D6 should likely focus on the patient future-booking advisory issue that started this thread: distinguish same requested day/window collision from unrelated future bookings, keeping patient context advisory unless it genuinely conflicts with the requested booking. Keep it backend-domain bounded before changing Bernie UI copy.


## Previous Closeout - Sprint D4

| Item | Value |
|---|---|
| Batch | Sprint D4: Native Diary Domain Frames and Reception Policy Foundation |
| Integrated through | Claude implementation on `claude/current`, DeepSeek Flash semantic scout, and Ariadne review/polish on `codex/review-d4-claude` |
| Status | Integrated locally; pending push/mirror/audit in this closeout |
| Last updated | 2026-07-04 |

## What Changed

- Added optional metadata-only `search_horizon` to `BernieSlotSearchFrame` so future route work can label same-day versus advance searches without changing current outcome semantics.
- Added a diary policy fallback: `roster_schedule` frames with `status="unavailable"` and no `reason_code` now synthesize `no_roster_row` into `schedule_reason_codes`, ensuring `roster_unavailable` outcomes self-explain.
- Added focused D4 tests proving `search_horizon` round-trips, does not alter no-candidate outcome classification, roster-unavailable self-explains, explicit roster reason codes are not clobbered, advisory-only frames cannot produce `no_matching_times`, and legacy frames classify as before.
- Ariadne rejected the risky original idea of downgrading future searched-no-candidates results to advisory. A deterministic slot search that ran and found zero candidates remains `no_matching_times` regardless of horizon.
- Ariadne normalized new test comments/docstrings to ASCII after Claude implementation.
- No frontend/UI, API schema, migration, GraphRAG, persisted session table, or broad API review was added.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile app/services/diary/frames.py app/services/diary/policy.py tests/test_bernie_d4_diary_domain_frames_policy.py`.
- Focused D4/adjacent suite passed after Ariadne polish: `.venv\Scripts\python.exe -m pytest tests/test_bernie_d4_diary_domain_frames_policy.py tests/test_diary_schedule_explanations.py tests/test_bernie_booking_outcomes.py tests/test_bernie_context_frames.py -q` (74 passed; existing Starlette/Google GenAI warnings only).
- `git diff --check` passed.
- DeepSeek Flash performed an independent semantic scout and agreed that genuine searched-no-candidates should not be downgraded to advisory.
- Full `.venv\Scripts\python.exe -m pytest tests -q` was not rerun for D4; previous full runs showed pre-existing/global failures outside these diary-domain slices.

## Recommended User Review

No required manual review. D4 is backend diary-domain contract/policy work only. User-facing diary and Bernie UI behaviour should be unchanged.

## Not Required Before Moving On

- No frontend behaviour changed.
- `search_horizon` is not yet threaded through the appointment route/frame builder; it is a safe typed field for the next route-aware sprint.
- No persisted Bernie session table, GraphRAG/vector store, auto-mode, taskpane, Command Centre, or broad API rewrite was implemented.

## Known Follow-Up

- Decide whether a narrow D5 should thread `search_horizon` through `_build_reception_context()` / route builders now that the typed field exists.
- Keep `no_matching_times` reserved for real slot-search evidence; use roster/schedule explanation frames for unavailable or unknown roster states.
- Continue moving reception facts and policy into the diary domain before adjusting staff-facing copy.

## Next Sprint Candidate

| Item | Value |
|---|---|
| Name | Sprint D5: Route-Builder Horizon Threading / Reception Fact Source Alignment |
| Status | Candidate after D4 push/mirror/audit |
| Recommended agents | Claude implementation lane while quota is healthy, DeepSeek Flash review/parallel bounded lane, Antigravity only if UI copy or visible diary affordances enter scope |

D5 should stay backend-bounded unless Yuri chooses otherwise: either thread `search_horizon` from route/date context into `BernieSlotSearchFrame`, or choose the next small reception fact that helps Bernie reason from diary-native structures without scripted UI strings.

## Previous Closeout - Sprint D3

| Item | Value |
|---|---|
| Batch | Sprint D3: Raw Appointment Compatibility Guard |
| Integrated through | DeepSeek Flash worker implementation on codex/d3-raw-compat-guard plus Ariadne review/polish |
| Status | Integrated branch reviewed and verified; pending master push/mirror/audit in this closeout |
| Last updated | 2026-07-04 |

## What Changed

- Added `appointment_raw_compat_mode` to settings with three modes: `audit` (default), `header`, and `off`.
- Marked the four raw appointment compatibility endpoints with explicit audit evidence tags when compatibility guard mode is enabled:
  - `raw_compat_create` for `POST /appointments`
  - `raw_compat_update` for `PUT /appointments/{appointment_id}`
  - `raw_compat_status` for `PATCH /appointments/{appointment_id}/status`
  - `raw_compat_delete` for `DELETE /appointments/{appointment_id}`
- Added a small centralized helper in `appointments.py` to attach raw-compat evidence and optional `Deprecation` headers without changing response models or endpoint payload shape.
- Preserved default raw endpoint behaviour. The default `audit` mode records compatibility evidence only; existing callers still succeed.
- Added focused backend tests for audit mode, header mode, off mode, and continued raw endpoint success.
- Ariadne repaired worker polish issues before integration: FastAPI `Response` is now injected as a normal required parameter, the DELETE deprecation-header assertion is real, and non-ASCII/mangled test section dividers were removed.
- No Bernie/UI/frontend, migrations, GraphRAG, persisted session state, taskpane, Command Centre, or broad API review was added.

## Verification

- Compile check passed: `.venv\Scripts\python.exe -m py_compile app/config.py app/routers/appointments.py tests/test_appointment_raw_compat.py`.
- Focused D3 suite passed after Ariadne polish: `.venv\Scripts\python.exe -m pytest tests/test_appointment_raw_compat.py tests/test_appointment_conflicts.py tests/test_appointment_status_mutations.py tests/test_appointment_proposals.py tests/test_appointment_update_proposal.py tests/test_appointment_audit.py -q` (125 passed; existing Starlette/Google GenAI warnings only).
- `git diff --check` passed after polish.
- DeepSeek Flash implemented the core slice on an isolated branch; Ariadne reviewed, repaired, and reran the focused suite before integration.
- Full `.venv\Scripts\python.exe -m pytest tests -q` was not rerun for D3; previous full runs showed pre-existing/global failures outside these diary compatibility slices.

## Recommended User Review

No required manual review. D3 is backend compatibility instrumentation only. User-facing diary and Bernie UI behaviour should be unchanged.

## Not Required Before Moving On

- No frontend behaviour changed.
- Raw compatibility routes are not retired or blocked by default.
- No persisted Bernie session table, Alembic migration, GraphRAG/vector store, auto-mode, taskpane, Command Centre, or broad API rewrite was implemented.
- No model-authored write or limited Bernie auto-mode was implemented.

## Known Follow-Up

- Decide later when to change `appointment_raw_compat_mode` from `audit` to `header`, and much later whether to turn any raw route off after all native diary action paths are envelope/confirm based.
- Keep using raw-compat audit evidence to identify any remaining frontend/backend callers that bypass native proposal/confirm flows.
- Continue moving toward Bernie as a native diary-domain copilot: diary frames, policy, roster/scheduling facts, and render-from-state should live in the diary domain rather than being patched into Bernie as one-off UI strings.

## Next Sprint Candidate

| Item | Value |
|---|---|
| Name | Sprint D4: Native Diary Domain Frames and Reception Policy Foundation |
| Status | Candidate after D3 push/mirror/audit |
| Recommended agents | DeepSeek Flash implementation lane, Ariadne integration/review, Claude only for architecture review if quota/value warrants it, Antigravity only if a visible diary UI artifact is in scope |

D4 should return to the native-Bernie architecture direction: move the first bounded slice of diary frames/policy/scheduling facts into a backend diary-domain module so Bernie can reason from shared diary-native structures instead of scripted UI strings. Keep it small and testable; do not start GraphRAG integration or broad API review in D4.

## Previous Closeout - Sprint D2

| Item | Value |
|---|---|
| Batch | Sprint D2: Shared Confirm Evidence Helper |
| Integrated through | DeepSeek Flash worker implementation on codex/d2-deepseek-confirm-helper, DeepSeek self-review/repair, and Ariadne review/polish |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-04 |

## What Changed

- Added `verify_signed_confirmation_evidence_block()` to `app/services/diary/confirm_actions.py` so the shared signed-evidence verification pattern lives with the diary confirm action descriptors.
- Refactored the staff create, Bernie update, status, delete, and Bernie create confirm routes in `appointments.py` to use the helper while preserving each route's expected payload, evidence purpose, block builder, audit evidence tag, and response flow.
- Kept the D1 descriptor/capability contract tests and added helper tests for valid evidence, invalid evidence, required-but-missing evidence, optional-and-missing evidence, and optional valid evidence.
- Used DeepSeek Flash through `codex-deepseek-bridge` as a real implementation sprint worker. The worker produced the core refactor and tests, then repaired deleted tests, BOM/import issues, and a temporary file after Ariadne review.
- Ariadne added a final polish commit for import placement and helper/module docstrings before integration.
- No frontend assets changed; no `diary.js` cache-bust or GitHub Pages redeploy-specific check is required for D2.
- No raw compatibility endpoint retirement, persisted Bernie session table, GraphRAG/vector store, auto-mode, taskpane, Command Centre, or broad API rewrite was added.

## Verification

- Compile check passed: `.\.venv\Scripts\python.exe -m py_compile app/services/diary/confirm_actions.py app/routers/appointments.py tests/test_diary_confirm_actions.py`.
- Focused D2 backend suite passed: `.\.venv\Scripts\python.exe -m pytest tests/test_diary_confirm_actions.py tests/test_appointment_status_mutations.py tests/test_appointment_audit.py -q` (68 passed; existing Starlette/Google GenAI warnings only).
- Bernie signed-confirm evidence suite passed: `.\.venv\Scripts\python.exe -m pytest tests/test_bernie_signed_confirmation_evidence.py -q` (7 passed; existing warnings only).
- `git diff --check master..origin/codex/d2-deepseek-confirm-helper` passed before Ariadne's local polish commit; local tests passed again after polish.
- DeepSeek final read-only review found no remaining route behaviour drift after repair.
- Full `.\.venv\Scripts\python.exe -m pytest tests -q` was not rerun for D2; previous full runs showed pre-existing/global failures outside these diary evidence slices.

## Recommended User Review

No required manual review. D2 is a backend-internal refactor of repeated signed-evidence verification code, and the focused backend suites passed. User-facing diary and Bernie UI behaviour should be unchanged.

## Not Required Before Moving On

- No frontend behaviour changed.
- Raw delete/status/create/update compatibility routes still exist for older or missing-envelope callers.
- No persisted Bernie session table, Alembic migration, GraphRAG/vector store, auto-mode, taskpane, Command Centre, or broad API rewrite was implemented.
- No model-authored write or limited Bernie auto-mode was implemented.
- No broad root-to-branch API review or GraphQL/context-graph redesign was started.

## Known Follow-Up

- Future native diary actions should consume this descriptor/catalog pattern rather than adding fresh route-local endpoint or signed-purpose literals.
- Consider when to start constraining raw compatibility endpoints now that update/create/status/delete have signed-confirm paths and their shared verification helper is in place.
- A later persisted-session sprint should still choose TTL, cleanup, transcript-storage, and concurrency policy before adding PHI-bearing tables.

## Next Sprint Candidate

| Item | Value |
|---|---|
| Name | Sprint D2: Confirm Pipeline Helper / Native Action Envelope Tail |
| Status | Candidate after D1 push/mirror/audit |
| Recommended agents | Claude backend review, Codex invariant worker, optional Antigravity only if UI affordance changes are in scope |

D2 should stay small: either unify the repeated confirm-route validation/block-response scaffolding behind descriptor-aware helpers, or defer that and move the internal `DiaryActionProposal`/`DiaryActionConfirmation` envelopes closer to the current proposal-confirm routes. Avoid UI work unless a visible affordance actually changes.

## Previous Closeout - Sprint G6

| Item | Value |
|---|---|
| Batch | Sprint G6: Human Cancel/Delete Confirm Migration |
| Integrated through | Codex/Rawls invariant packet and Ariadne implementation |
| Status | Integrated, verified, pushed, mirrored, audited, and live on GitHub Pages |
| Last updated | 2026-07-04 |

G6 added signed delete-confirm evidence, `POST /api/v1/appointments/proposals/delete-confirm`, edit-modal cancel submission through signed delete-confirm when present, and backend/UI tests proving failed signed delete confirms do not mutate or fall back to raw `DELETE`. `diary.js` was cache-busted from v166 to v167.

## Previous Closeout - Sprint G5

| Item | Value |
|---|---|
| Batch | Sprint G5: Human Status Confirm Migration |
| Integrated through | Codex/Lagrange invariant plan, Claude lane superseded by session cap, Antigravity lane superseded after no artifact, and Ariadne implementation |
| Status | Integrated, verified, pushed, mirrored, audited, and live on GitHub Pages |
| Last updated | 2026-07-04 |

G5 moved safe status and waiting-area proposals onto signed staff
status-confirm evidence, added `/appointments/proposals/status-confirm`,
made Diary status controls post signed confirms when present, and verified
failed/stale/tampered confirms do not write or fall back to raw `PATCH`.
`diary.js` was cache-busted from v165 to v166.

## Previous Closeout - Sprint G4

| Item | Value |
|---|---|
| Batch | Sprint G4: Human Create Modal Create Confirm Migration |
| Integrated through | Claude create-confirm plan, Codex invariant plan, Antigravity lane superseded, and Ariadne implementation |
| Status | Integrated, verified, pushed, mirrored, audited, and live on GitHub Pages |
| Last updated | 2026-07-04 |

G4 moved safe human create-booking proposals onto a neutral staff
create-confirm envelope and made the Diary create-booking modal write through
`/appointments/proposals/create/confirm` when evidence is present. It preserved
status-after-create as a separate transition, kept raw `POST /appointments` as
bounded compatibility only, and cache-busted `diary.js` from v164 to v165.

## Previous Closeout - Sprint G3

| Item | Value |
|---|---|
| Batch | Sprint G3: Edit Modal Update Confirm Migration |
| Integrated through | Claude edit-modal plan, Codex invariant plan, and Ariadne implementation |
| Status | Integrated, verified, pushed, mirrored, audited, and live on GitHub Pages |
| Last updated | 2026-07-04 |

G3 moved the Diary edit-booking modal onto fresh signed update proposals for
edit-mode Save, preserved status changes as a separate
`PATCH /appointments/{id}/status`, and added deterministic smoke coverage for
signed update confirm, no raw PUT from signed-capable edit saves, and
failed-confirm/no-status-patch behavior. `diary.js` was cache-busted from v163
to v164.

## Previous Closeout - Sprint G2

| Item | Value |
|---|---|
| Batch | Sprint G2: Human Diary Update Confirm Migration |
| Integrated through | Claude backend/domain plan, Codex invariant plan, Antigravity lane superseded after no submitted artifact, and Ariadne implementation |
| Status | Integrated, verified, pushed, mirrored, audited, and live on GitHub Pages |
| Last updated | 2026-07-04 |

G2 made ordinary safe appointment update proposals return `confirm_endpoint`,
`confirm_payload`, update freshness id, and update-purpose signed confirmation
evidence. Human Diary drag/drop/resize kept the existing proposal/confirm dialog
flow, but after staff confirmation posts the signed confirm payload to
`/appointments/proposals/update/confirm`; deterministic smoke coverage proves
the path does not emit raw `PUT`. `diary.js` was cache-busted from v162 to v163.

## Previous Closeout - Sprint G1

| Item | Value |
|---|---|
| Batch | Sprint G1: Unified Diary Update Confirm Grammar |
| Integrated through | Claude backend/domain plan, Antigravity Diary UX plan with scoped UI amendment, Codex invariant plan, and Ariadne implementation |
| Status | Integrated, verified, pushed, mirrored, audited, and live on GitHub Pages |
| Last updated | 2026-07-04 |

G1 added `POST /api/v1/appointments/proposals/update/confirm`, update-purpose
signed evidence, stale/current-appointment-state binding, shared update writer,
and Diary Bernie `Confirm change` submission through signed update-confirm
instead of raw PUT. `diary.js` was cache-busted from v161 to v162.

## Previous Closeout - Sprint V2

| Item | Value |
|---|---|
| Batch | Sprint V2: Bernie Visible Tool-Intent UX |
| Integrated through | Claude route/UI contract plan, Antigravity visible UX plan with Ariadne authority-boundary amendment, Codex invariant plan captured after protocol stop, and Ariadne implementation |
| Status | Integrated, verified, pushed, mirrored, audited, and live on GitHub Pages |
| Last updated | 2026-07-04 |

V2 routed explicit `extend`/`lengthen` requests from the Diary `Ask Bernie`
composer to the backend tool-intent route, rendered backend proposal evidence in
a visible appointment-change card, and prevented clarification/blocked/text-only
states from showing confirm controls. `diary.css` was cache-busted from v131 to
v132 and `diary.js` from v160 to v161.

## Previous Closeout - Sprint V1

| Item | Value |
|---|---|
| Batch | Sprint V1: Bernie Reception Voice And Tool-Intent Routing |
| Integrated through | Claude lane superseded by session cap, Antigravity Diary UX plan accepted for V2, Codex invariant plan accepted, and Ariadne backend/frame implementation |
| Status | Integrated, verified, pushed, mirrored, audited, and live on GitHub Pages |
| Last updated | 2026-07-04 |

V1 added `POST /api/v1/appointments/proposals/bernie/tool-intent`, the first typed non-booking Bernie diary tool-intent route. It supports explicit appointment-extension requests, resolves exactly one visible diary appointment from context frames, delegates to the deterministic appointment-update proposal contract, carries source attribution, and never writes directly. Diary context frames now include visible appointment ids. `diary.js` was cache-busted from v159 to v160.

## Previous Closeout - Sprint K1b

| Item | Value |
|---|---|
| Batch | Sprint K1b: Advisory Retrieval Wiring |
| Integrated through | Claude lane superseded by session cap, Antigravity Diary UX plan accepted, Codex/Aristotle invariant plan accepted, and Ariadne backend/UI implementation |
| Status | Integrated, verified, pushed, mirrored, audited, and live on GitHub Pages |
| Last updated | 2026-07-04 |

K1b wired typed practice-knowledge retrieval into Bernie as advisory-only reception context, added weekday guarding, rendered separate "Practice reference" cards in the Diary panel, and kept retrieved facts out of slot/search/confirm/write authority. `diary.css` was cache-busted from v130 to v131 and `diary.js` from v158 to v159. No Graph/vector store, persisted PHI/session table, Alembic migration, auto-mode, taskpane, Command Centre, broad UI redesign, or broad API rewrite was added.

## Previous Closeout - Sprint N11

| Item | Value |
|---|---|
| Batch | Sprint N11: Bernie Roster Outcome Explanations |
| Integrated through | Claude lane superseded by session cap, Antigravity Diary UX plan accepted, Codex/Banach invariant plan accepted, and Ariadne backend/UI implementation |
| Status | Integrated, verified, pushed, mirrored, audited, and live on GitHub Pages |
| Last updated | 2026-07-04 |

## What Changed

- Backend outcome precedence now preserves typed schedule truth: a generic
  `blocked` route result no longer erases `roster_unavailable`, and
  `clinic_day_exhausted` remains distinct from ordinary searched-zero-slot
  `no_matching_times`.
- Accepted interpretation route results remain `interpreted_ready` even when
  conservative soft confidence checks are present; explicit clarification
  route results still enter `clarification_required`.
- The supervised booking staff-review confirm affordance now maps
  `no_practitioner_schedule` to `blocked_schedule_or_roster`, not the generic
  `blocked_no_proposal`.
- Diary rendering now reads `outcome.reason_codes` before legacy issue fields
  for schedule copy, so typed roster outcomes can render "No roster found" and
  "Check the practitioner roster..." without UI inference.
- Advisory-only outcomes without selected-slot evidence remain advisory in the
  panel and do not produce fake prepared-booking headlines or confirm buttons.
- `diary.js` was cache-busted from v156 to v157.
- No persisted session table, Alembic migration, GraphRAG wiring, auto-mode,
  taskpane, Command Centre, broad UI redesign, or broad API rewrite was added.

## Verification

- JavaScript syntax check passed:
  `node --check docs\diary\diary.js`.
- Compile check passed:
  `.\.venv\Scripts\python.exe -m py_compile app\services\diary\outcomes.py app\routers\appointments.py`.
- Frontend asset version check passed:
  `.\.venv\Scripts\python.exe scripts\check_frontend_versions.py`.
- Focused N11 backend outcome/schedule/frame tests passed:
  `.\.venv\Scripts\pytest.exe tests\test_bernie_booking_outcomes.py tests\test_bernie_supervised_booking_wrapper.py::test_no_practitioner_schedule_is_roster_unavailable_not_no_free_slots tests\test_diary_schedule_explanations.py tests\test_bernie_context_frames.py -q`.
- Broader adjacent Bernie backend suite passed:
  `.\.venv\Scripts\pytest.exe tests\test_bernie_booking_outcomes.py tests\test_bernie_supervised_booking_wrapper.py tests\test_bernie_confirm_create_proposal.py tests\test_bernie_evidence_contract.py tests\test_bernie_signed_confirmation_evidence.py tests\test_bernie_route_outcome_events.py tests\test_diary_confirm_gate.py tests\test_diary_schedule_explanations.py tests\test_bernie_context_frames.py -q`.
- Full deterministic Diary smoke harness passed:
  `.\.venv\Scripts\pytest.exe review\test_diary_smoke.py -q`.
- `git diff --check` passed.
- Post-push orchestration audit passed: `master`, `handoff/current`,
  `codex/current`, `claude/current`, and `antigravity/current` are all aligned
  at `1d18961`.
- Live GitHub Pages check passed: `diary.html` is serving `diary.js?v=157`
  and `diary.css?v=130`.
- Full `.\.venv\Scripts\python.exe -m pytest tests -q` was not rerun for N11;
  previous full runs showed pre-existing/global failures outside these
  diary-domain/session endpoint/evidence slices.

## Recommended User Review

No required manual review before moving on. N11 changes the live Diary asset and
backend Bernie outcome/confirm-affordance precedence, but roster/no-slot,
advisory, interpretation-route, confirm-affordance, and deterministic Diary
rendering behaviours were verified with focused backend and UI harnesses. A
later live-user Bernie behaviour review is still useful once Pages serves v157,
but it is not required to close N11.

## Not Required Before Moving On

- No persisted Bernie session table, Alembic migration, GraphRAG/vector store,
  practice-knowledge route/UI wiring, UI redesign, or frontend deployment was
  implemented.
- No auto-confirm or limited Bernie auto-mode was implemented.
- No broad root-to-branch API review or GraphQL/context-graph redesign was
  started.
- No XState/runtime state-machine dependency was added.
- No Medicare Online, HI/IHI, OPV/PVM, Caller ID, voice/headset, or production
  GCP change is included.

## Known Follow-Up

- A later persistence sprint should add the real session/event table only after
  Yuri/Ariadne choose TTL, retention, cleanup, and transcript-storage policy.
- A later render-from-state sprint should decide how far the visible chat and
  latest status should be reconstructed from server session events rather than
  the current browser-owned transcript.
- A later domain sprint should enrich typed schedule/roster outcome payloads
  with safe practitioner/date wording so Bernie can naturally say when a
  requested practitioner is not rostered without the UI inventing facts.
- Continue to keep `session_binding` backend-authored only; the browser should
  echo it unchanged or fail closed.
- The signed path remains additive; a later sprint can decide when to retire or
  further constrain `legacy_unsigned_confirmation_compat`.
- Any future K1b route/UI retrieval integration must preserve the advisory-only
  boundary: retrieved facts may help Bernie explain or suggest, but must not
  set availability, policy hard-blocks, confirm affordances, freshness/audit
  evidence, or write payloads.
- Continue agentic Diary/Taskpane state-machine/API-pattern sprints before the
  broad root-to-branch API-spine review.

## Next Sprint Candidate - Rich Schedule Explanation / Domain Module Tail

| Item | Value |
|---|---|
| Name | N12: Rich schedule/roster explanation payloads, or K1b Advisory Retrieval Wiring |
| Status | Recommended, not launched |
| Recommended agents | Codex/Ariadne orchestration; Claude usual sprint model if session window allows; Antigravity for visible Diary UX review; Codex worker for state/session invariants |

N11 keeps schedule/no-slot/advisory outcomes semantically distinct. The next
narrow slice can enrich roster/schedule explanations with safe typed display
payloads and continue extracting Bernie into the bounded Diary reception domain
module. Alternatively, K1b can wire advisory retrieval into Bernie responses
while preserving the advisory-only boundary.

## Previous Closeout - Sprint N10

| Item | Value |
|---|---|
| Batch | Sprint N10: Bernie Outcome Intelligence And Diary Outcome UX |
| Integrated through | Claude backend classifier work recovered from timed-out worker branch, Antigravity Diary UX review implementation, Codex/Socrates invariant plan accepted, and Ariadne integration repairs |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-04 |

N10 added the typed Bernie booking outcome classifier, attached optional
`outcome` fields to interpretation and supervised-booking envelopes, made Diary
prefer `outcome.kind` for confirmation/advisory/clarification/no-slot/roster
rendering, and added deterministic Diary smoke coverage for clarification,
advisory-only, stale-conflict, and no-PHI-storage behaviours. `diary.css` was
cache-busted from v129 to v130 and `diary.js` from v155 to v156. No persisted
session table, Alembic migration, GraphRAG wiring, auto-mode, taskpane, Command
Centre, or broad API rewrite was added.

## Previous Closeout - Sprint N9

| Item | Value |
|---|---|
| Batch | Sprint N9: Diary Route-Coordinate Wiring |
| Integrated through | Claude lane superseded by quota cap, Antigravity stood down after CLI timeout/no artifact, Codex/Ampere invariant plan accepted, and Ariadne backend/UI implementation |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-04 |

N9 wired Diary Bernie route calls to carry active server-session coordinates
into interpretation and supervised-booking requests, echoed `server_session`
snapshots from backend route outcomes, hardened stale-conflict handling, and
kept `session_binding` backend-authored only. `diary.js` was cache-busted from
v154 to v155. No persisted session table, Alembic migration, GraphRAG wiring,
auto-mode, taskpane, Command Centre, or broad API rewrite was added.

## Previous Closeout - Sprint N8

| Item | Value |
|---|---|
| Batch | Sprint N8: Route-Level Outcome Event Wiring |
| Integrated through | Claude lane superseded by quota cap, Antigravity stood down after no-artifact CLI result, Codex/Sartre invariant plan accepted, and Ariadne backend/session implementation |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-04 |

N8 added optional `server_session_*` coordinates to Bernie interpretation and
supervised-booking request schemas, appended compact route-outcome events into
server-owned Bernie sessions, stamped backend-built `session_binding` into
proposal/confirm evidence, and added focused backend route outcome tests. No
Diary asset, persisted session table, Alembic migration, GraphRAG wiring,
auto-mode, taskpane, Command Centre, or broad API rewrite was added.

## Previous Closeout - Sprint N7

| Item | Value |
|---|---|
| Batch | Sprint N7: Bernie Server Outcome Events And Confirmation Binding |
| Integrated through | Claude lane superseded by quota cap, Antigravity stood down after no-artifact CLI attempts, Codex/Boole invariant plan recovered by Ariadne, and Ariadne backend/session implementation |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-03 |

N7 added server-owned Bernie outcome event types, process-local
`append_server_outcome_event()` semantics, optional signed confirmation
`session_binding`, and focused backend/session tests. No Diary asset, backend
persistence table, Alembic migration, GraphRAG wiring, auto-mode, taskpane,
Command Centre, or broad API rewrite was added.

## Previous Closeout - Sprint N6

| Item | Value |
|---|---|
| Batch | Sprint N6: Diary Render From Bernie Session Endpoint |
| Integrated through | Accepted Antigravity Diary render/refetch plan, accepted Codex/Lorentz UI invariant plan, Claude lane superseded by quota cap, Ariadne implementation and verification |
| Status | Integrated, verified, pushed, deployed, mirrored, and audited |
| Last updated | 2026-07-03 |

## Previous Closeout - Sprint N5

| Item | Value |
|---|---|
| Batch | Sprint N5: Bernie Session Endpoint Contract |
| Integrated through | Ariadne backend implementation replacing the capped Claude lane, accepted Antigravity Diary render-tail plan deferred to follow-up, accepted Codex/Peirce endpoint invariant plan, and Ariadne verification |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-03 |

## Previous Closeout - Sprint N4

| Item | Value |
|---|---|
| Batch | Sprint N4: Bernie Server-Side Session/Event Foundation |
| Integrated through | Ariadne backend implementation replacing the capped Claude lane, accepted Antigravity render-from-state tail plan, accepted Codex/McClintock invariant plan, and Ariadne verification |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-03 |

## Previous Closeout - Sprint S1

| Item | Value |
|---|---|
| Batch | Sprint S1: Signed Confirmation Evidence |
| Integrated through | Ariadne backend implementation replacing the capped Claude lane, accepted Antigravity UI evidence-echo review plan, accepted Codex/Turing invariant plan, and Ariadne verification |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-03 |

## Previous Closeout - Sprint K1

| Item | Value |
|---|---|
| Batch | Sprint K1: Typed Practice Knowledge Substrate |
| Integrated through | Claude backend/domain implementation, Antigravity advisory-UX plan accepted for a later wiring lane, Codex/Laplace boundary review, and Ariadne integration verification |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-03 |

## Previous Closeout - Sprint N3

| Item | Value |
|---|---|
| Batch | Sprint N3: Unified Evidence-Gated Confirm |
| Integrated through | Claude backend/domain implementation, Antigravity UI plan plus Ariadne UI integration, Codex/Lovelace boundary review, and Ariadne verification/hotfixes |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-03 |

## Previous Closeout - Sprint N2

| Item | Value |
|---|---|
| Batch | Sprint N2: Schedule Explanation And Copy Catalog |
| Integrated through | Claude/Opus plan, Codex/Hubble backend invariant lane, Antigravity Diary UI lane, and Ariadne integration/review |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-03 |

## Previous Closeout - Sprint N1b

| Item | Value |
|---|---|
| Batch | Sprint N1b: Diary Action Envelopes And Boundary Tests |
| Integrated through | Codex/Halley envelope contract lane, Antigravity boundary review, and Ariadne implementation while Claude remained in session-limit cooldown |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-03 |

## Previous Closeout - Sprint 106D

| Item | Value |
|---|---|
| Batch | Sprint 106D: Bernie Route Context Frame Wiring |
| Integrated through | Ariadne/Codex backend route adapter implementation after replacing the blocked Claude lane with Codex-owned execution |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-03 |

## Previous Closeout - Sprint 106C

| Item | Value |
|---|---|
| Batch | Sprint 106C: Bernie Typed Context Frames And Reception Policy Foundation |
| Integrated through | Antigravity UX plan accepted with amendments, Codex invariant/backend plans accepted, and Ariadne backend contract implementation for typed receptionist frames plus deterministic policy predicates |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-03 |

## Previous Closeout - Sprint 106B

| Item | Value |
|---|---|
| Batch | Sprint 106B: Bernie Temporal Policy Consolidation |
| Integrated through | Ariadne implementation of the accepted Claude Fable 5 plan: pure Bernie temporal policy module, shared week-relative/date-time helpers, and shared same-day window decisions |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-03 |

## What Changed

- Made `app/services/bernie/temporal.py` the canonical home for pure Bernie
  temporal policy: natural time parsing, natural date extraction, week-relative
  date resolution, and same-day window decisions.
- Changed `app/services/bernie_booking_interpreter.py` to import those helpers
  from the bounded Bernie temporal module while preserving the legacy private
  helper names for existing callers/tests.
- Changed the two duplicated same-day clamp/exhaustion paths in
  `app/routers/appointments.py` to delegate to the shared
  `evaluate_same_day_window()` predicate while keeping response assembly,
  public JSON, and existing user-facing copy stable.
- Exported the temporal helpers through `app/services/bernie/__init__.py`.
- Added `tests/test_bernie_temporal_policy.py` covering week-relative dates,
  business-hours time parsing, non-same-day, fully-past, partial-past clamp,
  open-ended clamp, and boundary cases.

## Previous Closeout - Sprint 106A

| Item | Value |
|---|---|
| Batch | Sprint 106A: Bernie Bounded Domain Extraction Foundation |
| Integrated through | Claude Fable 5 bounded `app/services/bernie/` package foundation, capability registry skeleton, and persistence-shaped session/event contracts |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-07-03 |

## What Changed

- Added `app/services/bernie/` as the bounded backend domain package for Bernie.
- Re-exported the current interpreter, patient booking context, turn evidence,
  slot normalizer, pilot gate, and date transition helpers through that package,
  preserving existing behaviour while creating a stable domain boundary.
- Added `app/services/bernie/session.py` with persistence-shaped session/event
  contracts and static transition tables, but no database table or endpoint yet.
- Added `app/services/bernie/capabilities.py` with a typed receptionist-domain
  capability registry covering read-only, propose, confirm, and meta actions.
- Updated `app/routers/appointments.py` to import Bernie services through the
  new bounded package.
- Added `tests/test_bernie_domain_package.py` to prove facade identity,
  session-transition invariants, JSON round-tripping, and capability registry
  shape.

## Previous Closeout - Sprint 104

| Item | Value |
|---|---|
| Batch | Sprint 104: Bernie Conversational State Memory And Patient Context |
| Integrated through | Backend patient_booking_context/no-slot contract, Diary chat-turn state surface, stale-state clearing, no-slot suggestions, and executable state-memory invariant harness |
| Status | Integrated, verified, pushed, deployed, mirrored, audited, and closed |
| Last updated | 2026-07-02 |

## What Changed

- Added compact deterministic `patient_booking_context` only after patient
  recognition, with freshness metadata for the active request reference date.
- Added typed no-slot suggestions so the UI can offer useful alternatives
  instead of rendering an empty candidate list.
- Changed the Diary Bernie panel from a stale single prompt into a chat-style
  turn surface with a New Session action and visible staff/Bernie transcript.
- Added a positive auto-preview toggle while preserving manual candidate
  selection.
- Made Today, date navigation, date picker changes, and Refresh clear stale
  candidate/proposal state while preserving the transcript.
- Added `tests/test_bernie_sprint104_state_memory.py` as executable invariant
  coverage for reference-date memory, stale proposal ownership, patient
  recognition/context separation, no-slot suggestions, and confirmation evidence.
- Updated diary assets to `diary.js?v=144` and `diary.css?v=125`.

## Verification

- Sprint 104 focused backend suite passed: `66 passed`.
- Full diary review harness passed.
- `node --check docs\diary\diary.js` passed.
- Frontend version check passed after Pages deploy.
- `git diff --check` passed.

## Recommended User Review

Sprint 104 user review was completed during live testing and followed by the
Sprint 104 post-review hotfix.

## Not Required Before Moving On

- No auto-confirm, limited Bernie auto-mode, broad API review, XState/runtime
  dependency, Medicare/HI/PVM/OPV, Caller ID, voice/headset, or production GCP
  change was included.

## Known Follow-Up

- Make turn metadata backend-owned, convert no-slot suggestion clicks fully end
  to end, and add backend-owned freshness evidence before any future auto-mode
  branch.
- Continue agentic Diary/Taskpane state-machine/API-pattern sprints before the
  broad root-to-branch API-spine review.

## Previous Closeout - Sprint 103

| Item | Value |
|---|---|
| Batch | Sprint 103: Bernie Compact Request And Auto Preview |
| Integrated through | Compact understood-request card, ordinary-mode best-candidate auto-preview, sensitive appointment details disclosure, and review harness updates |
| Status | Integrated, verified, pushed, mirrored, audited, and user-tested |
| Last updated | 2026-07-02 |

## What Changed

- Changed the ordinary *bernie* `UNDERSTOOD` request card so it no longer shows
  the verbose summary/date/window line on the main reception surface.
- Renamed the request disclosure from `Details` to `Need to clarify anything?`.
  The full interpreted command, assumptions, warnings, and technical detail remain
  available inside that disclosure.
- Added ordinary-mode best-candidate auto-preview: after *bernie* finds candidate
  times, the first/best candidate is immediately staged on the diary and the
  confirmation panel is prepared.
- Kept manual candidate selection available through an explicit
  `bernie_auto_preview=false` harness/manual mode so the list-selection branch is
  still testable.
- Added a closed-by-default `See more` disclosure under appointment details for
  sensitive patient identifiers such as Medicare, IHI, and phone details when the
  API supplies them.
- Updated the diary smoke harness so it tests both the new ordinary-mode
  auto-preview behaviour and the retained manual candidate path.
- Updated diary assets to `diary.js?v=143`; `diary.css` remains `v=124`.

## Verification

- `node --check docs\diary\diary.js` passed.
- `python scripts\check_frontend_versions.py` passed; local diary JS is correctly
  bumped from `v=142` to `v=143`.
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q -k "sprint103 or bernie_pilot_ordinary_mode_requires_real_context or bernie_pilot_instruction_first_without_selected_appointment or bernie_candidate_click_stages_provisional_diary_preview or bernie_route_intercepted_selected_slot_can_return_to_candidates"` passed: `6 passed`.
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q` passed:
  full diary review harness green.
- `git diff --check` passed with only the existing `review/test_diary_smoke.py`
  CRLF normalization warning.

## Recommended User Review

After GitHub Pages deploys:

1. Hard refresh the live Diary/Office dialog and confirm it loads
   `diary.js?v=143` and `diary.css?v=124`.
2. Open `Bernie` and try `Make an appointment for Margaret Thompson with Dr
   Shera after 3 tomorrow and before 4.30`.
3. Expected result: the `REQUEST` card should only show `UNDERSTOOD` plus the
   `Need to clarify anything?` disclosure, not the verbose date/window line.
4. Expected result: the first suitable candidate should automatically appear on
   the diary as a proposed appointment, with the confirmation panel ready.
5. Open `See more` under appointment details. Expected result: any extra patient
   identifiers supplied by the API are visible there, but not on the main card.
6. Click `Choose another time`. Expected result: the candidate list returns
   without changing the intended date.
7. Confirm a booking. Expected result: the confirmed appointment replaces the
   proposed diary card and the compact green confirmation state appears.
8. Suspicious signs: the old verbose `Booking instruction needs staff
   clarification...` copy appears outside disclosure, the diary does not
   auto-stage a first candidate, sensitive identifiers are visible by default,
   or `Choose another time` reintroduces the extra-day jump.

## Not Required Before Moving On

- No backend API contract was changed in this sprint.
- No new state-machine library dependency was added.
- No Medicare Online, HI/IHI, OPV/PVM, Caller ID, voice/headset integration, or
  production GCP change is included.

## Known Follow-Up

- Add the receptionist-facing auto-preview toggle promised in the UX model.
- Implement backend `patient_booking_context` so *bernie* can warn about existing
  future appointments for the same patient.
- Add explicit conversational state memory so prompt entry becomes a fresh
  chat/clarification turn after each transition instead of a stale single text
  box.
- Treat diary navigation, Today, Refresh, candidate selection, proposal preview,
  confirmation, and cancellation as first-class state transitions with clear
  stale-state rules.
- Replace no-slot UI copy with a direct "no times are available" state and
  clickable next-prompt suggestions.
- Decide whether the compact request disclosure should become a tabbed details
  panel once the details payload grows.
- Defer the root-to-branch API-spine design sprint until the next few
  agentic-mode Diary/Taskpane sprints have produced more concrete statechart and
  API-contract patterns.

## Next Sprint Candidate - Sprint 104

| Item | Value |
|---|---|
| Name | Bernie Conversational State Memory And Patient Context |
| Status | Proposed; not launched |
| Recommended agents | Claude for backend/API context contract, Antigravity/Gemini for Diary chat/state UI, Codex worker for statechart/acceptance invariants |

Sprint 104 should start from the concrete live-test findings:

- The prompt box should become a new input turn after *bernie* responds; prior
  user and *bernie* messages belong in chat history/state memory.
- "Need to clarify anything?" should not imply that clarification is mandatory
  when the request is understood.
- When no slots are available, *bernie* should say so plainly and offer useful
  next actions rather than showing "Bernie found these times".
- If the diary date changes through Today/Prev/Next/date picker/Refresh, stale
  *bernie* candidates and proposals must be cleared or marked stale by rule.
- If a patient is recognised, fetch compact `patient_booking_context` so
  *bernie* can notice existing recent/future bookings before offering slots.
- Limited auto-mode belongs in architecture as a future branch; do not implement
  auto-confirm in Sprint 104.

## Previous Closeout - Sprint 102

| Item | Value |
|---|---|
| Batch | Sprint 102: Bernie Date Context Transition Table |
| Integrated through | Deterministic date-resolution transition table, visible diary page context frame, compact clarification preview, and future follow-up seed fixtures |
| Status | Integrated and verified |
| Last updated | 2026-07-02 |

## What Changed

- Added `app/services/bernie_transition_table.py` as the first explicit *bernie*
  transition-table helper.
- Changed omitted-date handling:
  - explicit dates are preserved;
  - selected proposal/appointment dates are preferred where available;
  - otherwise the visible diary page date is assumed;
  - if no date context exists, *bernie* asks `Which day would you like me to check?`.
- Removed the old rule where a time constraint without a date silently assumed today.
- Updated the Diary client to send a `visible_diary_page` context frame with every
  *bernie* interpretation/supervised-booking request.
- Compact ordinary clarification UI so the clarifying question is the main text,
  while routine assumptions such as 15-minute default and diary-date assumption
  sit behind Details.
- Seeded future dev appointments for `2026-07-09`:
  - Billy Frusin with Dr Alex Shera at 14:30;
  - Margaret Thompson with Dr Alex Shera at 15:00.
- Documented the reusable rule: LLM extracts intent, transition tables resolve
  world-state assumptions, API contracts enforce writes.
- Updated diary assets to `diary.js?v=142`; `diary.css` remains `v=124`.

## Verification

- `python -m py_compile app\routers\appointments.py app\schemas\appointments.py app\services\bernie_transition_table.py seed.py` passed. Existing seed docstring escape warning remains unrelated.
- `node --check docs\diary\diary.js` passed.
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_transition_table.py tests\test_bernie_confidence_policy.py -q -k "date_transition or omitted_date or same_day or ordinary_release_gate"` passed: `12 passed`.
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py::test_sprint102_bernie_interpret_request_includes_visible_diary_context -q` passed.
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q -k "sprint102_bernie_interpret_request or sprint101_bernie_details_toggle or sprint99_bernie_raw_code_exclusion or sprint99_bernie_no_write_before_confirm or sprint99_bernie_choose_another_time_suppression or sprint99_bernie_asset_version_checks"` passed: `6 passed`.
- `python scripts\check_frontend_versions.py` passed; local diary JS is correctly bumped from `v=141` to `v=142`.
- `.venv\Scripts\python.exe seed.py` passed and seeded the future follow-up fixtures locally.
- `git diff --check` passed; Git reported only existing CRLF normalization warnings on touched files.

## Recommended User Review

After GitHub Pages deploys:

1. Hard refresh the live Diary/Office dialog and confirm it loads `diary.js?v=142` and `diary.css?v=124`.
2. Open `Bernie` on the diary page for today, `2026-07-02`.
3. Try `Make an appointment for Junior Atkinson at 11:15 with Dr Shera.`
4. Expected result: *bernie* should assume the visible diary page date rather than ask which day. It may still ask if the patient is not recognised, which is fine.
5. Navigate to another diary date, then try the same omitted-date request. Expected result: *bernie* should use the visible page date for that new request.
6. Try a genuinely context-free/backend-only omitted-date case only if you are calling the API directly. Expected result: it should ask `Which day would you like me to check?`.
7. Try `Make an appointment for Margaret Thompson with Dr Shera after 3 tomorrow and before 4.30`. Expected result: normal candidate/confirm behaviour, no extra jump forward when choosing another time.
8. For the seeded future-context fixture, inspect `2026-07-09`: Billy Frusin should have a 14:30 appointment and Margaret Thompson a 15:00 appointment. *Bernie* does not yet warn about those existing appointments; that is the next patient-booking-context sprint.
9. Suspicious signs: omitted date defaults to today instead of the visible page, `Duration: 15 mins` dominates ordinary clarification copy, raw `date_assumed_from_visible_diary` appears outside Details, or choosing another time mutates the date again.

## Not Required Before Moving On

- No XState dependency was added. This sprint deliberately proves the plain
  transition-table pattern first.
- No patient appointment-history context provider is implemented yet; the seed
  data prepares the next sprint's deterministic `patient_booking_context` work.
- No Medicare Online, HI/IHI, OPV/PVM, Caller ID, voice/headset integration, or
  production GCP change is included.

## Known Follow-Up

- Implement the backend `patient_booking_context` provider so *bernie* can notice
  existing future follow-ups such as the new `2026-07-09` seed fixtures.
- Add a visible receptionist toggle for automatic best-guess diary preview versus list-only suggestions.
- Continue the root-to-branch API-spine design sprint with GraphQL/context graph,
  command mutations, event contracts, YAML capability manifests, cybersecurity,
  and statechart modelling.
- Reassess XState only after the plain transition-table/session-state approach
  has exposed enough repeated nested workflow complexity to justify it.

## Previous Closeout - Sprint 101

| Item | Value |
|---|---|
| Batch | Sprint 101: Bernie Recognition Context And Statechart Practice |
| Integrated through | Patient recognition vs details verification split, compact recognition UI, current-day diary context practitioner inference, refresh-state cleanup, and patient-specific context-frame design rule |
| Status | Integrated and verified; awaiting GitHub Pages deployment after push |
| Last updated | 2026-07-02 |

## What Changed

- Split booking workflow language into **patient recognition** and **patient details verification**:
  - recognition is enough to prepare/confirm ordinary bookings when the patient is uniquely recognised in the practice register;
  - Medicare/HI/OPV/PVM-style verification remains a separate later workflow and is not mandatory before every booking.
- Updated the *bernie* backend confidence policy so unique current-register patient matches can proceed as recognised, without routine DOB-check copy blocking the reception flow.
- Added same-day diary context frames from the visible diary so *bernie* can infer a likely practitioner from a named patient's earlier appointment when the instruction omits the doctor/nurse.
- Kept that inference reversible and visible as a confidence assumption rather than a silent hard fact.
- Updated the Diary *bernie* panel so ordinary recognised-patient evidence is compact, while low/ambiguous recognition still expands the details needed by staff.
- Made the top `Refresh` action keep the *bernie* panel open but clear stale response/proposal state.
- Documented the next state-machine design practice:
  - context enrichment is its own nested subchart;
  - patient-specific appointment context should be fetched after recognition;
  - avoid broad diary dumps into the model context window;
  - keep patient appointment history context separate from deterministic availability context.
- Updated diary assets to `diary.js?v=141`; `diary.css` remains `v=124`.

## Verification

- `python -m py_compile app\routers\appointments.py app\schemas\appointments.py` passed.
- `node --check docs\diary\diary.js` passed.
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_confidence_policy.py tests\test_bernie_interpret_booking_instruction.py tests\test_bernie_supervised_booking_wrapper.py review\test_diary_smoke.py -q -k "patient_unique_exact_match or patient_exact_match_can or practitioner_can_be_inferred or complete_interpreter_policy or mocked_live_provider_returns_validated or mocked_live_provider_invalid or mocked_live_provider_autonomous or identity_evidence_reports_linked_patient_and_caller_id_context or sprint101_bernie_details_toggle_and_recognition_prompt or sprint99_bernie_raw_code_exclusion"` passed: `9 passed`.
- `python scripts\check_frontend_versions.py` passed; local diary JS is correctly bumped from `v=140` to `v=141`.
- `git diff --check` passed.
- One earlier parallel pytest attempt hit the known PostgreSQL enum create race; the same wrapper test passed immediately when rerun by itself and in the sequential targeted sweep.

## Recommended User Review

After GitHub Pages deploys:

1. Hard refresh the live Diary/Office dialog and confirm it loads `diary.js?v=141` and `diary.css?v=124`.
2. Open `Bernie`.
3. Try a normal recognised-patient booking such as `Find an appointment for Margaret Thompson with Dr Shera after 3 tomorrow and before 4.30.`
4. Expected result: routine recognised-patient evidence should be compact. It should not ask you to confirm DOB as a mandatory step before booking.
5. Try an omitted-practitioner case for a patient who has an appointment visible on the current diary day, such as `Find an appointment for Billy Frusin after 2 today`.
6. Expected result: *bernie* may infer the same practitioner from the diary context and explain that assumption calmly, or ask for the doctor/nurse if the context is not unique.
7. Click `Refresh` while the *bernie* panel is open. Expected result: the panel stays open, stale response/proposal content clears, and the instruction text remains available.
8. Suspicious signs: mandatory DOB prompt for a uniquely recognised patient, raw `patient_id`/`practitioner_id` copy in ordinary mode, stale candidate/proposal content after Refresh, or a practitioner inferred from unrelated diary context.

## Not Required Before Moving On

- No Medicare Online, HI/IHI, OPV/PVM, phone-system Caller ID, or voice/headset integration is implemented in Sprint 101.
- The new patient-specific appointment-history context frame is documented as the next backend/API contract. Sprint 101 only adds current-day diary context frames and statechart/API design rules.
- No database migration or production GCP change is required.

## Known Follow-Up

- Add a deterministic backend `patient_booking_context` provider: after patient recognition, fetch that patient's recent bookings and future bookings, derive usual practitioner/existing follow-up signals, and pass the compact frame into *bernie*.
- Continue the API-spine design sprint with GraphQL/context graph, command mutations, event contracts, YAML capability manifests, cybersecurity, and statechart modelling.
- Keep refining the *bernie* session chart so UI element state, context snapshot freshness, and proposal confirmation are explicit states rather than ad hoc flags.
- The known moderate Dependabot alert remains unrelated to this sprint.

## Previous Closeout - Sprint 100

| Item | Value |
|---|---|
| Batch | Sprint 100: Bernie Booking Session State Machine |
| Integrated through | Immutable request reference dates, same-day clinic exhaustion, explicit Bernie UI session state, candidate snapshot reuse, post-confirm cleanup, and regression harness for tomorrow navigation |
| Status | Integrated, verified, pushed, deployed, mirrored, and audited |
| Last updated | 2026-07-01 |

## What Changed

- Added a design guide for the coming API-spine revision: `orchestration/event_driven_statechart_architecture.md`.
- Added backend `request_reference_date` echoing to Bernie interpretation and supervised booking responses so relative dates are resolved against one immutable intake date.
- Added backend `clinic_day_exhausted` handling for same-day requests whose requested or clamped time window has already passed the clinic day.
- Preserved useful in-hours clamping: partly-past same-day requests can still search from now when slots remain.
- Added a diary-side Bernie session object separating instruction entry, interpretation, candidate selection, slot preview, confirming, and confirmed states.
- Changed `Choose another time` to reuse the existing candidate snapshot rather than reinterpreting the original prompt or re-resolving relative dates.
- Preserved selected booking details through confirmation, then clears stale confirm controls into a compact terminal confirmed state.
- Updated review harness expectations so confirmation success is a terminal state, not a hidden success message beside stale controls.
- Added a focused diary regression test proving a `tomorrow` candidate remains anchored to the original reference date after the diary jumps to the candidate day.
- Updated diary assets to `diary.css?v=124` and `diary.js?v=140`.

## Verification

- `.venv\Scripts\python.exe -m py_compile app\routers\appointments.py app\schemas\appointments.py tests\test_bernie_sprint100_state_contract.py` passed.
- `node --check docs\diary\diary.js` passed.
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_sprint100_state_contract.py -q` passed: `10 passed`.
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_sprint100_state_contract.py tests\test_bernie_confidence_policy.py -q` passed: `38 passed`.
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py::test_sprint100_bernie_tomorrow_reference_date_survives_diary_navigation -q` passed.
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q` passed: `73 passed`.
- Existing `pytest_asyncio` loop-scope deprecation warning remains unrelated.

## Recommended User Review

After GitHub Pages deploys, one live Diary check is still useful because this sprint fixes the exact temporal/session behaviour Yuri saw:

1. Hard refresh the live Diary/Office dialog and confirm it loads `diary.js?v=140` and `diary.css?v=124`.
2. Open `Bernie`.
3. Try `Make an appointment for Margaret Thompson for after 3 today with Dr Shera.` when the current clinic time is already after the useful booking window.
4. Expected result: Bernie should not show past slots or silently advance to tomorrow. It should ask for another day/later window with calm copy.
5. Try `Make an appointment for Margaret Thompson for after 3 tomorrow with Dr Shera.`
6. Choose a suggested time. Expected result: the diary jumps to the proposed date and shows the proposed appointment, but the underlying request remains anchored to the original reference date.
7. Click `Choose another time`. Expected result: the same candidate list returns without reinterpreting the original prompt or jumping another day forward.
8. Choose a time and click `Confirm booking` only if you are happy to create a dev booking. Expected result: after confirmation, old verbose request/details and confirm controls are cleared into a compact confirmed state.
9. Suspicious signs: tomorrow jumps forward two days, `Choose another time` calls a new interpretation/search unexpectedly, past slots appear for today, raw `clinic_day_exhausted`/UUID/snake_case copy appears in ordinary mode, or a booking is created before explicit confirmation.

## Not Required Before Moving On

- No Caller ID, OPV/PVM, Medicare Online, phone-system integration, voice/headset input, GraphQL API-spine implementation, or production GCP change is required for Sprint 100.
- No database migration or manual data repair is required.
- No taskpane, Command Centre, billing, SMS, resource-admin, Cochrane/RACGP, *davida*, or *consultant* implementation is included here.

## Known Follow-Up

- The next major programme remains the root-to-branch API-spine design sprint: GraphQL read/context graph, command mutation contracts, YAML capability/policy layer, statechart/event modelling, audit/evidence spine, cybersecurity model, and dev/prod profile strategy.
- Add a visible receptionist toggle for automatic best-guess diary preview versus list-only suggestions.
- Add more explicit model/state documentation for nested clarification submachines and cross-agent workflows.
- Add live/browser verification after deploy if the local harness passes but the Office/GitHub Pages surface behaves differently.
- The known moderate Dependabot alert remains unrelated to this sprint.

## Previous Closeout - Sprint 99

| Item | Value |
|---|---|
| Batch | Sprint 99: Bernie Confidence And Response Policy |
| Integrated through | Typed confidence axes, first-person receptionist responses, compact Details disclosure, same-day temporal validity, and confidence-aware provisional diary preview |
| Status | Integrated, verified, pushed, deployed, mirrored, and audited |
| Last updated | 2026-07-01 |

## What Changed

- Added a typed *bernie* confidence contract with separate axes for intent, temporal meaning, practitioner match, patient identity, slot validity, and a future speech/transcription placeholder.
- Made the categorical axis band the API guardrail: `assume`, `proceed_with_check`, `ask`, or `block`; the old scalar `confidence` remains advisory/display-only and is not used for gating.
- Added first-person clarification and assumption copy so ordinary staff see language such as `I've assumed...`, `I think you mean...`, and `I need...` rather than raw internal field names.
- Added same-day temporal validity:
  - explicit or inferred today never proposes past slots.
  - fully-past same-day windows ask for a later time or another day.
  - partly-past windows clamp forward.
  - open-ended requests such as `after 3 today` at 15:55 clamp forward to now rather than offering past times or blocking unnecessarily.
- Added fuzzy patient handling as candidate proposal only. Exact unique patient names can proceed with staff DOB/identity verification; fuzzy/ambiguous names ask the receptionist to choose or supply another identifier and never silently link.
- Updated the Diary *bernie* panel:
  - ordinary mode is titled `Bernie`.
  - routine high/medium confidence evidence is compact, with a `Details` disclosure for full evidence.
  - low/ambiguous or ask/block states expand supporting evidence.
  - confidence-permitting selected slots auto-preview as proposed diary cards, unless staff choose another time or manually interact with the diary.
  - block copy is calm and action-oriented, for example `I need a practitioner before I can search.`
- Updated diary assets to `diary.css?v=123` and `diary.js?v=139`.

## Verification

- `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest tests\test_bernie_interpret_booking_instruction.py tests\test_bernie_sprint98_release_gates.py tests\test_bernie_confidence_policy.py -q` passed: `45 passed`.
- `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m py_compile app\config.py app\schemas\appointments.py app\services\bernie_booking_interpreter.py app\routers\appointments.py tests\test_bernie_confidence_policy.py tests\test_bernie_sprint98_release_gates.py` passed.
- `node --check docs\diary\diary.js` passed.
- `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q` passed: `72 passed`.
- `python scripts\check_frontend_versions.py` passed; local asset versions are `diary.css?v=123` and `diary.js?v=139`.
- `git diff --check` passed.

## Recommended User Review

After GitHub Pages deploys, one live Diary check is useful because this sprint changes *bernie*'s ordinary receptionist interaction:

1. Hard refresh the live Diary/Office dialog and confirm it loads `diary.js?v=139` and `diary.css?v=123`.
2. Open `Bernie`.
3. Try `Make an appointment for Margaret Thompson for after 3 today with Dr Shera.`
4. Expected result: if it is already after 3 pm, *bernie* should search from the current time onward, not show earlier slots and not ask for `practitioner_id`.
5. Try `Make an appointment for Margaret Thompson with Dr Shera for after 3pm but before 4.30pm.`
6. Expected result: if the date is omitted, *bernie* should either assume today with clear `I've assumed today...` copy when confidence is adequate, or ask a human-like clarification if the time/date context is too weak.
7. Check that routine patient details are compact with a `Details` control, and that ambiguous or low-confidence identity information expands enough for the receptionist to decide.
8. Suspicious signs: raw UUIDs, snake_case codes, `Please provide practitioner_id`, past slots for today, no proposed diary preview when a confident slot is selected, or any appointment created before `Confirm booking`.

## Not Required Before Moving On

- No Caller ID, OPV/PVM, Medicare Online, phone-system integration, voice/headset input, or production GCP change is required for Sprint 99.
- No database migration or manual data repair is required.
- No taskpane, Command Centre, billing, SMS, resource-admin, Cochrane/RACGP, *davida*, or *consultant* implementation is included here.

## Known Follow-Up

- Add the receptionist toggle for automatic best-guess diary preview versus list-only suggestions.
- Add real patient-candidate selection/linking flow; Sprint 99 only renders candidates and preserves the no-silent-link rule.
- Add voice/transcription confidence when headset input exists.
- Begin the root-to-branch API-spine design sprint next: GraphQL read/context graph, command mutation contracts, YAML capability/policy layer, agent capability manifests, audit/evidence spine, cybersecurity model, and dev/prod profile strategy.
- The known moderate Dependabot alert remains unrelated to this sprint.

## Previous Closeout - Sprint 98

| Item | Value |
|---|---|
| Batch | Sprint 98: Bernie Booking Loop Integrity and API Release Gates |
| Integrated through | Typed backend confirm failure contract, calm Diary confirmation recovery, Choose another time loop, and blocking release gates for the simplest booking prompt path |
| Status | Integrated, verified, pushed, deployed, mirrored, and audited; live hotfix for confirm endpoint and ordinary copy applied |
| Last updated | 2026-07-01 |

## What Changed

- Incorporated the API/YAML design direction into the API-spine programme: YAML remains a declarative operating layer for capability manifests, setup plans, agent charters, evidence-source policies, and deployment/profile values, while GraphQL/REST/event contracts remain the executable API spine.
- Added Sprint 98 release gates so *bernie* booking work cannot close if the simple Margaret Thompson / Dr Shera prompt path fails, if backend confirm leaks raw `Not Found`, or if the selected-slot state gives reception no route back to candidate times.
- Updated the backend confirm path for *bernie* create proposals so stale or out-of-scope patient, practitioner, appointment type, and location references return structured blocked review payloads instead of surfacing raw HTTP 404 exceptions.
- Kept those backend failures precise: for example an invalid practitioner now returns `practitioner_not_found`, not a generic wrapper code.
- Updated the Diary review UI so ordinary reception mode shows calm confirm-failure copy:
  - `This slot is no longer available. Please choose a different time.`
  - `We couldn't confirm this booking. Please try again or select another time.`
- Added a `Choose another time` action from confirmation-ready review state back to candidate selection without making a confirm call.
- Kept developer diagnostics behind debug/dev mode; ordinary mode continues to avoid raw snake_case setup codes.
- Preserved the staged provisional diary-card pulse in the dedicated visual smoke path, with reduced-motion coverage.
- Hotfix after live review: normalized backend-provided confirm endpoints before calling `apiFetch`, preventing `/api/v1/api/v1/...` confirm requests from being misreported as stale slots.
- Hotfix after live review: changed ordinary *bernie* clarification copy from internal `practitioner_id` wording to receptionist-facing language and hid interpret warning-code prefixes outside debug mode.

## Verification

- `.venv\Scripts\python.exe -m pytest tests\test_smoke_bernie_interpreter_script.py tests\test_bernie_sprint98_release_gates.py tests\test_bernie_sprint98_confirm_contract.py -q` passed: `16 passed`; existing pytest-asyncio loop-scope deprecation warning remains.
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q` passed: `63 passed`; existing pytest-asyncio loop-scope deprecation warning remains.
- `node --check docs\diary\diary.js` passed.
- `.venv\Scripts\python.exe -m py_compile scripts\smoke_bernie_interpreter.py tests\test_smoke_bernie_interpreter_script.py tests\test_bernie_sprint98_release_gates.py tests\test_bernie_sprint98_confirm_contract.py app\routers\appointments.py` passed.
- `git diff --check` passed.
- Hotfix verification:
  - `.venv\Scripts\python.exe -m pytest tests\test_bernie_interpret_booking_instruction.py tests\test_bernie_confirm_create_proposal.py tests\test_bernie_sprint98_confirm_contract.py tests\test_bernie_sprint98_release_gates.py -q` passed: `28 passed`.
  - `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q` passed: `63 passed`.
  - `node --check docs\diary\diary.js` passed.
  - `git diff --check` passed.

## Recommended User Review

One live Diary check remains useful after deployment because Sprint 98 deliberately targets the screenshot-level failure Yuri reported:

1. Hard refresh the live Diary/Office dialog after GitHub Pages deploys and confirm the page loads `diary.js?v=137` and `diary.css?v=122`.
2. Open `Bernie`.
3. Type `Make an appointment for Margaret Thompson for after 3 today with Dr Shera.`
4. Click `Find times`.
5. Expected result: *bernie* should understand the patient/practitioner names, search available times, and avoid showing `Please provide practitioner_id`, raw UUID language, or `Live booking-instruction interpretation failed closed`.
6. Click one candidate time.
7. Expected result: the selected slot appears clearly in the Diary as a proposed appointment, the review pane shows patient and appointment details, and there is both a `Confirm booking` button and a `Choose another time` button.
8. Click `Choose another time` and confirm the candidate list returns and no booking is created.
9. Repeat if desired and click `Confirm booking` only when you are happy to create a dev booking. Expected result: either the booking is confirmed or, if the slot has gone stale, reception sees calm retry/select-another-time copy rather than raw backend text.

## Not Required Before Moving On

- No Caller ID, OPV/PVM, Medicare Online, phone-system integration, or production GCP setup is required for Sprint 98.
- No practice-manager *davida*, *consultant*, Cochrane, RACGP, or broader API-spine implementation is included in this sprint beyond programme documentation and release-gate framing.

## Known Follow-Up

- After Yuri's live check, the next recommended sprint is the root-to-branch API-spine design sprint: GraphQL read/context graph, command mutation contracts, agent capability manifests, audit/evidence spine, and dev/prod profile strategy.
- Add a temporal-validity layer for same-day *bernie* searches: if the request is for today, clamp earliest candidate search to the next valid future slot; if the requested window has already passed, ask for a later time/day instead of offering past slots. Future-date requests should preserve the stated window.
- Add a receptionist preview policy for *bernie*: default behaviour should show *bernie*'s best-guess candidate automatically on the Diary as a proposed appointment, but the panel needs a clear toggle to keep suggestions in-list only before the receptionist prompts *bernie*.
- Add confidence-based evidence density to the *bernie* panel: above a configurable confidence threshold, keep REQUEST/PATIENT DETAILS supporting text compact and expose the full evidence through a `Details`/`See more` control; below that threshold, expand the evidence by default so the receptionist has enough information to resolve uncertainty.
- The known moderate Dependabot alert remains unrelated to this sprint.

## Previous Closeout - Sprint 97

| Item | Value |
|---|---|
| Batch | Sprint 97: Bernie Basic Prompt Reliability and Release Gates |
| Integrated through | Deterministic fallback for live interpreter outages, receptionist-friendly provider-unavailable UI, route-intercepted test labeling, and blocking Bernie release gates |
| Status | Integrated, verified, pushed, deployed, mirrored, and audited |
| Last updated | 2026-07-01 |

## What Changed

- Added deterministic fallback for the `gemini_vertex` Bernie booking interpreter when the live provider path is unavailable, with strict fail-closed still available by explicitly disabling fallback.
- Added natural receptionist time parsing for phrases such as `after 3`, `after 2 pm`, `before 3:45`, `before 3.45`, and `between 2 pm and 3:45`, normalizing to `HH:MM` before slot-search validation.
- Kept the interpreter route non-mutating: it still does not search slots, create proposals, confirm bookings, or write appointment audit rows.
- Added provider readiness metadata so release checks can distinguish live-provider availability from deterministic fallback readiness.
- Updated Bernie ordinary-mode UI so provider-unavailable/setup failures do not expose raw internal codes, structured-field instructions, or manual-ID language to reception staff.
- Kept developer diagnostics visible only behind `bernie_debug=true` or `bernie_dev_review=true`.
- Renamed route-intercepted Bernie diary smoke helpers/tests so they are no longer described as live checks.
- Added `orchestration/bernie_release_gates.md` and a protocol alert making the Margaret Thompson / Dr Shera ordinary prompt a blocking release gate for Bernie booking work.
- Added smoke-script assertions for provider readiness, interpreter mode, and parsed earliest/latest times.

## Verification

- `.venv\Scripts\python.exe -m pytest tests\test_smoke_bernie_interpreter_script.py tests\test_bernie_sprint97_interpreter_readiness.py tests\test_bernie_interpret_booking_instruction.py tests\test_bernie_slot_normalizer.py -q` passed: `71 passed`; existing pytest-asyncio loop-scope deprecation warning remains.
- `.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py --provider fake --instruction "Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45" --reference-date 2026-07-01 --expect-result clarification_required --expect-earliest-time 14:00 --expect-latest-time 15:45 --expect-mode mocked` passed.
- `.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py --provider gemini_vertex --allow-live --check-readiness --expect-ready true` passed and reported `live_provider_ok: true`, `fallback_active: true`, `mode: live`.
- `node --check docs\diary\diary.js` passed.
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` passed: `57 passed`; existing pytest-asyncio loop-scope deprecation warning remains.
- `.venv\Scripts\python.exe -m py_compile app\config.py app\schemas\appointments.py app\services\bernie_booking_interpreter.py scripts\smoke_bernie_interpreter.py tests\test_bernie_sprint97_interpreter_readiness.py` passed.
- `git diff --check origin/master...HEAD` passed.
- GitHub Pages deploy for commit `55f63c1` completed successfully, and `.venv\Scripts\python.exe scripts\check_frontend_versions.py` confirmed the deployed Diary is serving `diary.js?v=135` and `diary.css?v=121`.
- `python scripts\agent_worktrees.py audit --fetch` confirmed `master`, `handoff/current`, `codex/current`, `claude/current`, and `antigravity/current` all aligned at `55f63c1` with clean worktrees.

## Recommended User Review

One live Diary check remains useful after deployment because this sprint targets the exact browser failure Yuri reported:

1. Hard refresh the live Diary/Office dialog after GitHub Pages deploys and confirm the page loads `diary.js?v=135` and `diary.css?v=121`.
2. Open `Bernie`.
3. Type `Make an appointment for Margaret Thompson for after 3 today with Dr Shera.`
4. Click `Find times`.
5. Expected result: Bernie should search and show available times, not `Live booking-instruction interpretation failed closed`, not `Please use structured booking fields`, and not raw provider/setup codes.
6. Click one time and confirm the proposed slot is shown on the diary with calm provisional styling. Do not click `Confirm booking` unless you genuinely want the dev booking created.
7. Suspicious signs: `Booking Interpreter Provider Unavailable`, raw snake_case codes in ordinary mode, no available times when Dr Shera has free slots, proposed slot not visible after choosing a time, or any booking created before clicking `Confirm booking`.

## Not Required Before Moving On

- No live Caller ID, phone-system, OPV/PVM/IHI, Medicare Online, taskpane, Command Centre, billing, SMS, or resource-admin review is required for Sprint 97.
- No database migration or manual data repair is required.
- No production GCP console action is required by this sprint; provider readiness is now checked locally and fallback is deterministic.

## Known Follow-Up

- True provider invocation can still fail for quota, credentials, or API enablement despite readiness import/construction passing; deterministic fallback keeps basic booking interpretation usable while that is repaired.
- The Bernie panel still needs a later product pass around patient identity evidence and appointment-type duration selection once the basic prompt path is stable.
- The known moderate Dependabot alert remains unrelated to this sprint.

## Recommended Next Direction

After Yuri confirms the live Diary no longer reproduces the screenshot failure, step back to the broader implementation plan and tighten the Bernie API surface around patient/practitioner evidence display and appointment-type/duration choice before expanding to Caller ID or Medicare/OPV/PVM integrations.

## Previous Closeout - Sprint 96

| Item | Value |
|---|---|
| Batch | Sprint 96: Bernie Reception Assistant UX and API Evidence Contract |
| Integrated through | Calm Bernie reception UI, explicit Confirm booking path, staged diary pulse, structured practitioner/patient evidence, and bounded identity-confidence audit |
| Status | Integrated, verified, pushed, deployed, mirrored, and audited |
| Last updated | 2026-07-01 |

## What Changed

- Replaced scary staff-facing Bernie language with calm reception copy: `Bernie`, `Find times`, `Choose a time`, `Ready to book`, `Confirm booking`, and `Booking confirmed`.
- Removed robot/masked-supervision framing from the diary Bernie panel and launch affordance.
- Mapped internal API states such as `blocked`, `candidate_selection_required`, and `confirmation_ready` to receptionist-friendly labels while keeping the backend contract unchanged.
- Changed candidate actions to `Show on diary`, marked selected candidates with `aria-pressed`, and preserved the non-mutating candidate-selection flow.
- Changed the staged diary card from `Bernie provisional booking` to `Proposed appointment` and made it information-first: patient, time, duration, practitioner, and identity prompt.
- Added the restrained staged-card pulse Yuri approved: finite shadow/border pulse only, no scale/layout shift, and disabled under `prefers-reduced-motion: reduce`.
- Removed the extra approval checkbox. The explicit staff confirmation action is now the visible `Confirm booking` button, with `Ctrl+Alt+Enter` supported only when the confirm button is visible/enabled and focus is not in an input.
- Hid live-provider/debug metadata from normal receptionist flow unless `bernie_debug=true`.
- Added structured backend evidence fields to Bernie staff-review payloads:
  - `practitioner_evidence` with display name, provider number where set, and optional location label.
  - `patient_evidence` with patient label, DOB where linked, masked phone where available, confidence, and provisional flag.
- Kept supervised Bernie review non-mutating; confirmed writes still go only through the confirm endpoint.
- Added bounded identity-confidence audit codes to confirmed Bernie writes, derived again server-side at confirmation rather than trusted from client payload.
- Marked the rejected Antigravity/Gemini UX plan as superseded; Sprint 96 UX implementation followed the accepted Codex/Ariadne replacement plan.

## Verification

- `node --check docs\diary\diary.js` passed.
- `.venv\Scripts\python.exe scripts\check_frontend_versions.py` passed; local/HEAD diary assets are `diary.js?v=134` and `diary.css?v=120`, deployed Pages was still on the previous versions before push.
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q --tb=short` passed: `56 passed`; existing pytest-asyncio loop-scope deprecation warning remains.
- `.venv\Scripts\python.exe -m py_compile app\schemas\appointments.py app\routers\appointments.py tests\test_bernie_confirm_create_proposal.py tests\test_bernie_evidence_contract.py` passed.
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_supervised_booking_wrapper.py tests\test_bernie_confirm_create_proposal.py tests\test_bernie_evidence_contract.py -q --tb=short` passed: `27 passed`; existing pytest-asyncio loop-scope deprecation warning remains.
- `git diff --check HEAD` passed.

## Sprint 97 Release-Gate Correction

The Sprint 96 closeout below left the simplest receptionist happy path as
residual user review. Treat that as a process bug, not a precedent. For Sprint
97 and later Bernie booking work, the ordinary Margaret Thompson / Dr Shera
prompt is a blocking release gate, route-intercepted checks must be labelled as
route-intercepted rather than live, and any reproducible screenshot/visual
failure blocks closeout. The standing rule lives in
`orchestration/bernie_release_gates.md`.

## Recommended User Review

Residual user review is useful because this sprint changes the live receptionist surface and the exact visual feel of Bernie.

1. Hard refresh the live Diary/Office dialog and confirm the page loads `diary.js?v=134` and `diary.css?v=120`.
2. Open the Diary and confirm the top-bar button says `Bernie`, not `Supervised Booking Review`.
3. Open Bernie and type a simple request such as `Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45`.
4. Confirm the panel says `Find times`, `Bernie found these times`, and `Available times`, with no robot/masked-supervision framing.
5. Click one suggested time and confirm the diary scrolls to the proposed slot.
6. Confirm the staged diary card says `Proposed appointment`, gently pulses once, and shows useful details rather than raw UUIDs or scary internal warnings.
7. In the Bernie panel, confirm the selected appointment details and patient details are readable, then click `Confirm booking` only when the details look right.
8. Suspicious signs: raw UUIDs or snake_case codes visible to reception, red safety-theatre blocks in normal candidate/confirm states, confirm write before clicking `Confirm booking`, pulse looping forever, card resize/layout jump, or `Ctrl+Alt+Enter` confirming while typing in the instruction field.
9. Evidence to report: screenshots of any suspicious state plus the instruction entered and whether the appointment was actually created.

## Not Required Before Moving On

- No live Caller ID, phone-system, OPV/PVM/IHI, Medicare Online, or GCP provider setup was added or needs review in this sprint.
- No taskpane, Command Centre, clinical scribe, billing, SMS, resource admin, or knowledge-base workflow review is required.
- No database migration or manual data repair is required.

## Known Follow-Up

- Live phone-system Caller ID and Medicare/OPV/PVM verification remain placeholder/context-frame work only.
- ONLYNAME Medicare mapping still needs exact integration confirmation before production identity rules rely on it.
- Confirm-time identity-confidence audit currently records baseline EMR4 evidence, not caller-session or future external-verification evidence.
- The known moderate Dependabot alert remains unrelated to this sprint.

## Recommended Next Direction

Step back and review the broader implementation plan in light of the last Bernie sprints. The next technical slice should be a small API/UX tightening sprint rather than live phone/Medicare integration: make the structured `patient_evidence` and `practitioner_evidence` fields the primary source for the diary panel/card and add any missing keyboard shortcut harness coverage before expanding Bernie’s operational scope.

## Previous Closeout - Sprint 95

| Item | Value |
|---|---|
| Batch | Sprint 95: Caller-ID / OPV Readiness Contracts |
| Integrated through | Provider-neutral non-mutating identity-verification adapter contract and Bernie OPV context-frame consumption |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-06-30 |

## What Changed

- Added `app/services/identity_verification.py`, a provider-neutral non-mutating identity verification boundary.
- Added method/status enums for OPV, PVM, PVF, OVV, and IHI-style checks.
- Added `IdentityVerificationRequest` and `IdentityVerificationResult` contracts with PHI-minimised result metadata and `raw_response_stored=false` by default.
- Added a disabled adapter that fails closed and performs no network access.
- Added a deterministic dev/test adapter that verifies only when required identity fields and consent are present.
- Added `IdentityVerificationResult.to_context_frame()` so verified checks can be passed into Bernie as an `identity_verification` context frame.
- Taught Bernie identity evidence to consume verified identity context frames, raising confidence to high and recording method-specific matched evidence such as `opv_verified`.
- Documented the boundary in `docs/bernie-identity-verification-readiness.md`.

## Verification

- `.venv\Scripts\python.exe -m py_compile app\services\identity_verification.py app\routers\appointments.py` passed.
- `.venv\Scripts\python.exe -m pytest tests\test_identity_verification_adapter.py tests\test_bernie_supervised_booking_wrapper.py -q --tb=short` passed: `13 passed`; existing pytest-asyncio loop-scope deprecation warning remains.
- `git diff --check` passed.

## Known Follow-Up

- No live phone-system Caller ID provider is integrated yet.
- No live Medicare Online / OPV / PVM / DVA / IHI provider call is integrated yet.
- Live verification needs practice credentials, consent workflow, provider error-code mapping, logging policy, and exact ONLYNAME contract confirmation before implementation.
- The known moderate Dependabot alert remains unrelated to this sprint.

## Recommended Next Direction

Pause for product/integration input: identify the real phone system that can provide Caller ID to EMR4, and identify the intended Medicare/OPV/PVM integration route or test environment. After that, Sprint 96 can implement the first live or mocked-provider connector behind the adapter boundary.

## Previous Closeout - Sprint 94

| Item | Value |
|---|---|
| Batch | Sprint 94: Bernie Identity-Confidence Frames |
| Integrated through | Supervised Bernie booking reviews now carry typed patient identity evidence for staff verification |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-06-30 |

## What Changed

- Added `BernieIdentityEvidence` to the supervised Bernie staff-review payload.
- Added optional `context_frames` to the supervised booking wrapper so selected-appointment and future caller-ID evidence can travel into the deterministic proposal stage.
- The backend now produces conservative identity evidence for linked, unlinked, duplicate, caller-ID-supported, and ONLYNAME-like patient records.
- Linked patient evidence includes matched fields such as patient id, name, DOB, Medicare-on-record, and caller-ID phone match where available.
- Same-name/same-DOB duplicates are flagged as ambiguous and prompt Medicare/card verification before staff confirmation.
- ONLYNAME-like records are flagged for claim-contract verification rather than treated as a final billing rule.
- The Diary now renders a Patient Identity Check panel in Bernie review and carries the same staff prompt into the highlighted provisional diary card.
- Diary assets were cache-busted to `diary.js?v=133` and `diary.css?v=119`.

## Verification

- `.venv\Scripts\python.exe -m py_compile app\schemas\appointments.py app\routers\appointments.py` passed.
- `node --check docs\diary\diary.js` passed.
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_supervised_booking_wrapper.py -q --tb=short` passed: `9 passed`; existing pytest-asyncio loop-scope deprecation warning remains.
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q --tb=short` passed: `56 passed`; existing pytest-asyncio loop-scope deprecation warning remains.
- `.venv\Scripts\python.exe scripts\check_frontend_versions.py` passed.
- `git diff --check` passed.

## Known Follow-Up

- No live phone-system Caller ID source is integrated yet; `caller_id` is a supported context-frame shape only.
- No Medicare Online / OPV / PVM adapter was implemented in this sprint. The evidence frame is ready to receive those results later.
- ONLYNAME remains a verified-research item before EMR4 should canonicalise Medicare claim export mapping.
- The known moderate Dependabot alert remains unrelated to this sprint.

## Recommended Next Direction

Next recommended step: Sprint 95 caller-ID/OPV readiness. Add the inbound caller-ID context source for Bernie where available, design the Medicare/OPV verification adapter boundary as a non-mutating identity check, and finalize the ONLYNAME claim-mapping evidence before production booking identity rules rely on it.

## Previous Closeout - Sprint 93

| Item | Value |
|---|---|
| Batch | Sprint 93: Bernie Candidate Click-Through Diary Preview |
| Integrated through | Clickable Bernie candidate slots now stage a highlighted provisional diary preview before staff confirmation |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-06-30 |

## What Changed

- Bernie candidate slot cards in the supervised review panel are now clickable buttons.
- Clicking a candidate records the selected candidate index, reloads the relevant diary date when necessary, scrolls to the proposed time, and renders a highlighted provisional booking card in the matching practitioner column.
- The staged card is local review state only: it does not write an appointment or audit row before the existing staff-confirmed Bernie confirmation endpoint succeeds.
- After a successful staff confirmation, the staged preview is cleared and the diary refreshes back to the normal appointment view.
- Existing selected-appointment context remains optional evidence. Tests now assert that changing selected appointment context does not submit a supervised booking request by itself.
- Diary assets were cache-busted to `diary.js?v=132` and `diary.css?v=118`.

## Verification

- `node --check docs\diary\diary.js` passed.
- `.venv\Scripts\python.exe scripts\check_frontend_versions.py` passed.
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q --tb=short` passed: `56 passed`; existing pytest-asyncio loop-scope deprecation warning remains.
- `git diff --check` passed.

## Known Follow-Up

- The provisional card currently displays conservative identity-warning copy rather than structured DOB/Medicare/caller-ID confidence evidence.
- Patient identity matching is still based on the interpreter/resolver output, not a full receptionist-grade identity-confidence decision.
- Caller ID should become an optional context frame that can raise confidence but does not prove identity by itself.
- ONLYNAME handling needs verification against the exact Medicare Online / Services Australia claim format before EMR4 canonicalises one-name patient matching.
- The known moderate Dependabot alert remains unrelated to this sprint.

## Recommended Next Direction

Next recommended step: Sprint 94 Bernie identity-confidence frames. Add a typed identity-evidence contract for booking proposals, covering registered-patient self-identification, surname/full-name plus DOB, duplicate-name ambiguity, Medicare/card check prompts, caller-ID as supporting context, and an explicit ONLYNAME verification spike before production mapping.

## Previous Closeout - Sprint 92

| Item | Value |
|---|---|
| Batch | Sprint 92: Bernie Instruction-First Context Frames |
| Integrated through | Free-text Bernie booking instructions no longer require selected appointment context; selected appointment context is now optional evidence |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-06-30 |

## What Changed

- Added optional `context_frames` to the Bernie booking-instruction interpreter request.
- The Diary now opens Bernie to an instruction-first panel even when no appointment is selected.
- Selected diary appointment context remains useful: when an appointment is active, staff can import it as optional evidence rather than as a prerequisite.
- Stale selected-appointment context now clears back to instruction-first mode instead of blocking Bernie with `stale_selected_appointment_context`.
- The backend interpreter route now resolves simple practice-local names before slot search:
  - unique practitioner surname/full-name matches such as `Dr Shera` resolve to `practitioner_id`
  - unique patient full-name matches such as `Margaret Thompson` resolve to `patient_id`
  - ambiguous patient/practitioner names produce warnings/clarification rather than silent selection
- Booking/confirmation language such as "book it" is now treated as a supervised-confirmation warning, not as a hard block, because Bernie still only prepares a proposal and the final write remains staff-confirmed.
- Diary assets were cache-busted to `diary.js?v=131`.

## Verification

- `.venv\Scripts\python.exe -m py_compile app\routers\appointments.py app\services\bernie_booking_interpreter.py app\schemas\appointments.py` passed.
- `node --check docs\diary\diary.js` passed.
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_interpret_booking_instruction.py tests\test_bernie_supervised_booking_wrapper.py -q --tb=short` passed: `20 passed`; existing pytest-asyncio loop-scope deprecation warning remains.
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py::test_bernie_pilot_instruction_first_without_selected_appointment review\test_diary_smoke.py::test_bernie_pilot_selected_appointment_instruction_readiness_and_resets review\test_diary_smoke.py::test_bernie_review_candidate_selection_empty_state -q --tb=short` passed: `3 passed`; existing pytest-asyncio loop-scope deprecation warning remains.

## Known Follow-Up

- This sprint does not yet create a highlighted provisional diary card from a clicked Bernie candidate slot.
- This sprint does not yet navigate the diary to a candidate date/time/practitioner column after staff clicks a candidate option.
- Patient identity is still a first-pass unique full-name resolver. Add DOB, phone/caller-ID, Medicare/DVA/IHI/MRN/address confidence tiers before production use.
- Services Australia ECLIPSE guidance says one-name patients should place the actual one-part name in `PatientFamilyName` and `Onlyname` in `PatientFirstName`; verify this against the exact Medicare Online / billing integration EMR4 implements before canonical database or claim-export mapping.
- Caller ID should be added as an optional context frame, not as verified identity.
- The known moderate Dependabot alert remains unrelated to this sprint.

## Recommended Next Direction

Next recommended step: Sprint 93 Bernie candidate click-through and provisional diary highlight. Candidate options should be clickable, navigate the diary to the proposed date/time/practitioner column, stage an enlarged highlighted provisional booking card with identity-confidence details, and require receptionist confirmation before the normal appointment write/appearance.

## Previous Closeout - Sprint 91

| Item | Value |
|---|---|
| Batch | Sprint 91: Multi-Provider Knowledge-Base Adapter Groundwork |
| Integrated through | Provider-neutral knowledge-base query/citation contracts behind Access AI with fake-provider tests only |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-06-29 |

## What Changed

- Added `clinical.knowledge.query` to the Access AI capability contract.
- Registered the capability as retrieval-generation, clinician-facing,
  non-PHI, metadata-only, and backed by the Copilot dev project namespace.
- Allowed `ai.clinical_user` actors to invoke knowledge queries while reception
  roles still fail closed.
- Added `app/services/ai/knowledge_base.py` with provider-neutral
  `KnowledgeBaseQuery`, `KnowledgeBaseCitation`, `KnowledgeBaseAnswer`,
  `KnowledgeBaseAdapter`, and `AccessAiKnowledgeBaseService` contracts.
- Routed knowledge-base retrieval through `AccessAiService` via a small provider
  shim, so future AWS/Wiley/Cochrane-style adapters do not bypass product
  entitlement or invocation audit.
- Required transient-only retrieved text posture and citations by default.
- Added PHI refusal before adapter invocation, because this groundwork does not
  yet include a licensed patient-specific retrieval policy.
- Added knowledge-query audit events that record safe metadata such as
  knowledge-base id, adapter provider, citation count, citation ids, and
  transient-storage posture without storing query text or retrieved passages.

## Verification

- `.venv\Scripts\python.exe -m py_compile app\services\ai\contracts.py app\services\ai\registry.py app\services\ai\entitlements.py app\services\ai\knowledge_base.py` passed.
- `.venv\Scripts\python.exe -m pytest tests\test_ai_knowledge_base_adapter.py tests\test_ai_capability_registry.py tests\test_ai_entitlements.py tests\test_access_ai_service.py tests\test_ai_audit_events.py -q --tb=short` passed: `36 passed`; existing pytest-asyncio loop-scope deprecation warning remains.

## Known Follow-Up

- No live AWS, Wiley, Cochrane, Bedrock, Vertex Search, or external licensed
  provider integration was added in this sprint.
- Before real licensed content is connected, define licence scope, provider
  identity, PHI query policy, citation display contract, retention/caching
  policy, and clinician-facing safety wording.
- Persisted Access AI audit storage already exists, but no runtime route calls
  the knowledge-base service yet.

## Recommended Next Direction

Next recommended step: choose between caller-context booking proposal groundwork
for Bernie, or a Wiley/Cochrane licensed knowledge-base spike that maps the real
provider contract into this adapter boundary.

## Previous Closeout - Sprints 79-89

| Item | Value |
|---|---|
| Batch | Sprints 79-89: Access AI Foundation and AI Route Migration |
| Integrated through | Bernie booking-instruction, clinical extraction, audio scribe, and letter drafting paths routed through Access AI with persisted metadata audit events |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-06-29 |

## What Changed

- Added Access AI enum contracts for modality, method, risk tier, and provider class.
- Changed `AiCapability` values to stable dotted capability ids such as `clinical.scribe.transcribe` and `admin.booking.interpret`.
- Added `app/services/ai/registry.py`, a static fail-closed capability registry for initial Access AI metadata.
- Captured initial metadata for clinical extraction, audio scribe, letter drafting, Bernie booking interpretation, Bernie slot/proposal capabilities, and live provider smoke.
- Added tests proving expected registry contents, PHI policy, project selection, risk tiers, human-confirmation metadata, live-smoke constraints, explicit method allowlists, and unknown-capability fail-closed behavior.
- Added `app/services/ai/entitlements.py`, a static Access AI entitlement gate that maps today's practice roles onto future-oriented AI access roles.
- Added role separation for clinical AI users, reception AI users, reception supervisors, dev operators, platform admins, and disabled actors.
- Added entitlement decisions for unknown capabilities, unknown methods, disabled actors, registry method allowlists, environment allowlists, and role/capability mismatches.
- Added tests proving GP, receptionist, admin, dev-operator, disabled, unknown, and method-denial behaviours.
- Added `app/services/ai/audit_events.py`, a typed Access AI audit event catalog for invocation, entitlement, Bernie proposal, caller identity, and knowledge-query events.
- Added audit event validation for timezone-aware timestamps, compact reason codes, required capability/method on AI events, blocked/failed reason codes, correlation ids, and PHI-averse bounded metadata.
- Added tests proving allowed/blocked event shape, missing required fields, raw prompt/patient identifier metadata rejection, non-AI identity events, and timestamp validation.
- Added `app/services/ai/access_service.py`, the first Access AI invocation service.
- The service combines entitlement decisions, capability metadata, injected provider calls, and audit events without changing existing router behaviour.
- Added fake-provider-only tests proving deny-before-provider-call, successful allowed invocation, dry-run-without-provider-call, provider failure events, and audit metadata rejection before provider calls.
- Added `app/services/ai/costing.py`, a bounded Access AI usage/cost estimator that records numeric request/response units and estimated cost without storing prompt, transcript, generated note, patient, or raw payload text.
- Access AI invocation results now carry `cost_envelope` and `latency_ms`.
- Invocation audit metadata now includes provider/project/location/model, request units, response units, estimated cost, optional max-estimated-cost, and latency.
- Added tests proving numeric-only cost metadata, zero-cost local deterministic provider estimates, success/failure/blocked envelope behaviour, shared failure correlation ids, and no provider call when audit metadata is unsafe.
- Added `app/services/ai/external_identity.py`, a small seam mapping external Cloud Identity/WorkOS-style groups into EMR4-owned Access AI roles.
- Updated the Access AI design record to use the implemented role names and document initial Little Star Digital group names.
- Added tests proving Cloud Identity group mapping, unknown-group fail-closed behaviour, WorkOS-style role mapping into the same entitlement contract, and disabled-group override.
- Routed the live Gemini/Vertex Bernie booking-instruction interpreter through `AccessAiService`.
- The route now passes the signed-in EMR4 user into an Access AI actor context while preserving existing endpoint access semantics.
- Disabled and fake Bernie interpreter modes remain local and do not construct live providers.
- Added migration coverage proving Access AI denial fails closed before a live provider call, and source-level no-mutation assertions now require the Access AI path.
- Added `app/models/ai_audit.py` with `AccessAiAuditLog`, a metadata-only Access AI audit table.
- Added Alembic migration `j0k1l2m3n4o5_add_access_ai_audit_log.py`.
- Added `app/services/ai/audit_store.py` to persist typed Access AI audit events without committing transaction boundaries inside the helper.
- Added DB-backed tests proving bounded metadata persistence, actor/resource/capability/method/decision fields, and shared correlation ids across allowed/failed event pairs.
- Wired the Bernie booking-instruction route to collect and persist Access AI audit events emitted by the live interpreter path.
- Fake and disabled Bernie interpreter modes still emit no Access AI audit rows and do not construct live providers.
- Live interpreter calls now commit metadata-only Access AI audit rows while preserving no appointment creation, no slot search, no confirmation, and no appointment audit writes.
- Updated tests to prove live interpreter audit persistence, no fake/disabled Access AI audit writes, and unchanged appointment/audit row counts.
- Routed `AiService.analyze_consultation_text` through `AccessAiService` with the `clinical.note.extract` capability.
- Extended `AiResult` to carry Access AI audit events, cost envelope, and latency metadata while preserving existing `.raw` and `.data` behaviour.
- Updated `/api/v1/analyze-consultation` to pass the signed-in user as an Access AI actor context and persist metadata-only Access AI audit events.
- Added tests proving clinical extraction Access AI metadata, fail-closed denied actor behaviour before provider calls, unchanged scribe/letter direct paths, and route-level audit persistence without encounter finalization.
- Routed audio scribe and letter drafting through Access AI with `clinical.scribe.transcribe` and `clinical.letter.draft` capabilities.
- Updated `/api/v1/scribe-consultation` and patient letter drafting to pass signed-in user Access AI context and persist metadata-only audit events.
- Added tests proving letter route audit persistence and service-boundary Access AI metadata for scribe and letters while preserving raw/data response contracts.
- Kept runtime provider invocation behavior unchanged.

## Verification

- `.venv\Scripts\python.exe -m py_compile app\services\ai\service.py app\routers\consultation.py app\routers\letters.py` passed.
- `.venv\Scripts\python.exe -m pytest tests\test_letter_access_ai_audit.py tests\test_analyze_consultation_access_ai_audit.py tests\test_access_ai_audit_store.py tests\test_bernie_interpret_booking_instruction.py tests\test_ai_external_identity.py tests\test_ai_costing.py tests\test_access_ai_service.py tests\test_ai_audit_events.py tests\test_ai_capability_registry.py tests\test_ai_entitlements.py tests\test_ai_service_boundary.py -q --tb=short` passed: `67 passed`; existing pytest-asyncio loop-scope deprecation warning remains.
- `git push origin master handoff/current` succeeded at `00fcdd5`.
- `python scripts\agent_worktrees.py realign --agent claude --apply`, `--agent antigravity --apply`, and `--agent codex --apply` succeeded from their worker worktrees.
- `python scripts\agent_worktrees.py audit --fetch` showed `master`, `handoff/current`, `codex/current`, `claude/current`, and `antigravity/current` aligned and clean at `00fcdd5`.
- `python scripts\agent_worktrees.py retire-stale` reported no stale disposable worktrees.
- Pushover closeout pings were sent for each sprint after the user requested them.

## Known Follow-Up

- Next step should push and realign the local Access AI sprint batch before starting caller-context booking proposals, multi-provider knowledge-base adapters, or further UI work.
- The static project/provider metadata should be wired to environment/config only after entitlement and invocation service boundaries exist.
- The entitlement role mapping is intentionally static for now; later Cloud Identity groups, WorkOS-style org roles, or database-backed practice entitlements should feed the same contract rather than bypass it.
- Existing Bernie/Copilot routes still use the older AI services directly; do not migrate live routes until the audit/cost envelope is stable.
- GitHub still reports the known moderate Dependabot alert on push; Sprint 71 triaged it as not product-runtime-actionable.

## Recommended Next Direction

Next recommended step: push and realign the local Access AI sprint batch. Do not route caller-ID booking proposals or Wiley/Cochrane knowledge-base calls through Access AI runtime until this migration batch is pushed, audited, and stable.

## Previous Closeout - Sprints 77-78

| Item | Value |
|---|---|
| Batch | Sprints 77-78: Access AI API Architecture and Keyless GCP Dev Auth |
| Integrated through | Programme 2F design record, keyless GCP AI setup runbook, and removal of default JSON-key guidance |
| Status | Integrated, verified, pushed, mirrored, and audited |
| Last updated | 2026-06-29 |

## What Changed

- Added `orchestration/access_ai_api_design.md` for Programme 2F.
- Defined Access AI as the internal role/identity/capability gate for AI modalities, with LLMs treated as one substrate behind EMR4-owned contracts.
- Added `docs/gcp-keyless-ai-setup.md` covering Little Star Digital Cloud Identity, dev project layout, service-account impersonation, ADC quota project setup, smoke order, and JSON-key retirement.
- Added Bernie caller-ID context and pending booking proposal workflow to the Access AI design.
- Added multi-provider retrieval/knowledge-base posture for future Wiley/Cochrane-style AWS integrations.
- Folded in WorkOS-inspired enterprise-readiness primitives: organization-scoped roles, resource-scoped authorization, typed audit events, self-service admin seams, and future SSO/SCIM/FGA compatibility without adopting WorkOS as a dependency.
- Folded in Vercel-inspired deployment-readiness primitives: immutable preview URLs, protected preview deployments, promotion/rollback discipline, deploy metadata, and smoke evidence attached to deploys without committing EMR4 to Vercel hosting.
- Updated dev/new-PC docs away from `GOOGLE_APPLICATION_CREDENTIALS=gcp-key.json`.
- Changed the default `google_application_credentials` setting to `None` so normal local dev follows ADC/keyless auth unless explicitly overridden.
- Updated the phase programme map with Programme 2F and its sprint roadmap.

## Verification

- `.venv\Scripts\python.exe -m py_compile app\config.py app\services\ai\contracts.py app\services\bernie_booking_interpreter.py scripts\drive_agent_headless.py` passed.
- `.venv\Scripts\python.exe -m pytest tests\test_ai_service_boundary.py tests\test_bernie_interpret_booking_instruction.py -q --tb=short` passed: `25 passed`; existing pytest-asyncio loop-scope deprecation warning remains.
- `git diff --check` passed.
- Stale credential scan found no active setup docs still instructing normal local dev to use `GOOGLE_APPLICATION_CREDENTIALS=gcp-key.json`; remaining mentions are historical, retirement, or "do not commit" references.

## Known Follow-Up

- Configure actual Little Star Digital dev projects and service accounts in GCP: `scribe-emr4-dev` and `bernie-emr4-dev`.
- Replace any remaining legacy local `.env` values that point to old projects or JSON key paths.
- Decide whether `scribe-emr4-dev` and `bernie-emr4-dev` need separate billing/quota handling immediately or can share the current billing account while trust history builds.
- Future phone-system integration should feed caller context as candidate identity evidence, not verified identity.
- Future Wiley/Cochrane knowledge-base integration should be treated as licensed clinical decision support with citations and separate retrieval/provider policy, not as a generic chat model.
- Future deployment work should copy Vercel's preview/promotion ergonomics while keeping clinical backend/runtime placement on GCP unless a separate architecture review decides otherwise.
- GitHub still reports the known moderate Dependabot alert on push; Sprint 71 triaged it as not product-runtime-actionable.

## Recommended Next Direction

Next recommended step: Sprint 79 AI capability registry, followed by Sprint 80 entitlement model, Sprint 81 typed audit event catalog, and Sprint 82 Access AI invocation service. A deployment-readiness Sprint 84 preview deployment harness is also queued under Programme 2C; schedule it when frontend review friction becomes the priority.

## Previous Closeout - Sprint 76

| Item | Value |
|---|---|
| Batch | Sprint 76: Bernie Interpreter Smoke Tooling |
| Integrated through | Repeatable fake/live booking-instruction interpreter smoke command with explicit live-provider guard |
| Status | Integrated and verified locally; push/audit pending |
| Last updated | 2026-06-28 |

## What Changed

- Added `scripts/smoke_bernie_interpreter.py`, a non-mutating Bernie interpreter smoke command.
- The command defaults to the deterministic fake provider and prints a compact redacted result summary.
- Live Gemini/Vertex smoke now requires both `--provider gemini_vertex` and `--allow-live`, making accidental live calls harder.
- Added pytest coverage for fake-provider compact output, live-provider refusal without `--allow-live`, and non-zero expectation failure output.

## Verification

- `.venv\Scripts\python.exe -m py_compile scripts\smoke_bernie_interpreter.py tests\test_smoke_bernie_interpreter_script.py` passed.
- `.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py --provider fake --reference-date 2026-06-28 --expect-result interpreted` passed with a redacted `interpreted` payload.
- `.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py --provider gemini_vertex` refused live use without `--allow-live`, as intended.
- `.venv\Scripts\python.exe -m pytest tests\test_smoke_bernie_interpreter_script.py tests\test_bernie_interpret_booking_instruction.py -q --tb=short` passed: `14 passed`.
- Live non-PHI Gemini interpreter smoke passed with `--provider gemini_vertex --allow-live`: ordinary dummy instruction returned `interpreted`.
- Live non-PHI Gemini safety smoke passed with `--expect-result blocked`: dummy instruction ending in `book it` returned `staff_confirmation_required` and `autonomous_booking_language`.

## Known Follow-Up

- Google auth emitted the ADC warning that local Cloud SDK end-user credentials have no quota project. Live calls worked, but a later setup pass should set an ADC quota project or move Bernie smoke to the intended service-account posture.
- The diary UI remains deliberately diagnostic; conversational clarification polish is deferred until the basics are firmer.
- GitHub still reports the known moderate Dependabot alert on push; Sprint 71 triaged it as not product-runtime-actionable.

## Recommended Next Direction

Next recommended step: keep the strict diagnostic Bernie UI and harden the selected-context-to-live-interpreter path, or first tidy Google ADC quota-project setup if live-provider warnings become noisy.

## Previous Closeout - Sprint 75

| Item | Value |
|---|---|
| Batch | Sprint 75: Bernie Interpreted Context Guard |
| Integrated through | Interpreted-practitioner mismatch block and empty-candidate explanatory message |
| Status | Integrated, verified, pushed, mirrored, audited, deployed, and closed |
| Last updated | 2026-06-28 |

## What Changed

- If the interpreted booking instruction returns a practitioner that differs from the imported selected appointment context, the diary now blocks before calling supervised booking and shows `interpreted_practitioner_context_mismatch`.
- Candidate-selection review with zero candidate slots now shows a clear empty-state message instead of a blank `Candidate Slots` section.
- Existing selected-appointment import, readiness copy, explicit staff submit, and approval-gated confirmation behaviour remain unchanged.
- Diary assets were cache-busted to `diary.css?v=117` and `diary.js?v=130`.

## Verification

- `C:\Users\sarashera\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe --check docs\diary\diary.js` passed.
- `python scripts\check_frontend_versions.py` passed locally with `diary.css?v=117` and `diary.js?v=130`.
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py::test_bernie_pilot_blocks_interpreted_practitioner_mismatch_before_supervised_call review\test_diary_smoke.py::test_bernie_review_candidate_selection_empty_state review\test_diary_smoke.py::test_bernie_pilot_selected_appointment_instruction_affordances review\test_diary_smoke.py::test_bernie_pilot_selected_appointment_instruction_readiness_and_resets -q --tb=short` passed: `4 passed`.
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` passed: `54 passed`.
- `git diff --check` passed.
- GitHub Pages deployment for `ef677b8` completed successfully: run `28305009904`, `Deploy GitHub Pages`, `master`, `success`.
- Live Pages served `diary.css?v=117` and `diary.js?v=130` from `https://yurifrusin.github.io/EMR4/diary/diary.html`.
- `python scripts\agent_worktrees.py audit --fetch` showed `master`, `handoff/current`, `codex/current`, `claude/current`, and `antigravity/current` aligned and clean at `f2cc857`.
- `python scripts\agent_worktrees.py retire-stale` reported no stale disposable worktrees.

## Not Required Before Moving On

- No backend, provider, schema, migration, taskpane, Command Centre, billing, SMS, resource admin, or live Gemini action is required for this UI hardening slice.
- No manual live test is required before push; deterministic route-intercepted checks cover the mismatch guard, no-supervised-call behaviour, empty-candidate copy, and adjacent selected-appointment instruction flows.

## Known Follow-Up

- The local dev smoke has `BERNIE_BOOKING_INTERPRETER_PROVIDER=fake` in `.env`; keep this as fake/non-live until the live Gemini interpreter smoke is explicitly chosen.
- GitHub still reports the known moderate Dependabot alert on push; Sprint 71 triaged it as not product-runtime-actionable.

## Recommended Next Direction

Next recommended step: rerun the live fake-interpreter staff-pilot smoke that previously exposed the practitioner mismatch and empty-candidate states. If clean, choose whether to enable a live Gemini interpreter smoke behind the same gates.

## Previous Closeout - Sprint 74

Sprint 74 integrated safe readiness copy and clean reset behaviour for selected-appointment Bernie instructions. The deterministic harness verified selected-appointment import, readiness copy for chip and typed instructions, typed-text preservation across valid rerender, Change reset, re-import reset, stale-selection reset/no chips/no call, no browser/URL instruction persistence, explicit submit, and unchanged confirmation gating. Live GitHub Pages served `diary.js?v=129` and `diary.css?v=116` after push.

## Previous Closeout - Sprint 73

Sprint 73 integrated staff-safe suggested instruction chips for imported selected-appointment Bernie context. The deterministic harness verified selected-appointment import, chip rendering, chip click as fill-only, no pre-submit API calls, no URL/browser-storage instruction persistence, explicit submit, stale-selection chip removal, and unchanged confirmation gating. Live GitHub Pages served `diary.js?v=127` and `diary.css?v=115` after push.

## Previous Closeout - Sprint 72

| Item | Value |
|---|---|
| Batch | Sprint 72: Bernie Imported Context Stale-Selection Guard |
| Integrated through | Staff-visible Bernie pilot now blocks imported appointment context when the active diary selection changes |
| Status | Integrated, verified, pushed, mirrored, audited, deployed, and closed |
| Last updated | 2026-06-27 |

Sprint 72 made imported Bernie pilot context fail closed with `stale_selected_appointment_context` when the active diary selection changes, preventing interpretation/supervised-booking POSTs until staff re-import the current selected appointment.

## Previous Closeout - Sprint 71

| Item | Value |
|---|---|
| Batch | Sprint 71: Dependabot uuid Alert Triage |
| Integrated through | GitHub REST and local static triage of Dependabot alert 5 (`npm uuid`, GHSA-w5hq-g745-h8pq / CVE-2026-41907) |
| Status | Triaged, documented, no runtime code changes |
| Last updated | 2026-06-27 |

## What Changed

- No production/runtime code changed.
- Ariadne verified GitHub CLI auth from Codex through `C:\Program Files\GitHub CLI\gh.exe`.
- Dependabot alert 5 targets `EMR4 Sidebar/package-lock.json`, `uuid` `8.3.2`, development scope, transitive relationship.
- Static lockfile review shows the vulnerable package is dev-only, pulled by Office/Microsoft build tooling (`@azure/msal-node`, `@microsoft/teamsfx-core`, `office-addin-manifest`, `sockjs`); the only nested modern `uuid` copy is `13.0.2` under `@microsoft/kiota`.
- Static source search found no EMR4 JavaScript/TypeScript imports or calls to the npm `uuid` APIs named in the advisory (`v3`, `v5`, `v6` with caller-provided buffers/offsets).

## Verification

- GitHub REST intake: `gh api /repos/yurifrusin/EMR4/dependabot/alerts?classification=general&state=open&per_page=100`.
- Local static package-lock parse with bundled Node confirmed `node_modules/uuid` is `8.3.2` and `dev: true`.
- Local static source search over non-`node_modules` JS/TS found no npm `uuid` use.
- No repo-root `SECURITY.md` was found; this remains a security-policy documentation gap, not evidence of exploitability.
- `python scripts\agent_worktrees.py audit --fetch` showed `master`, `handoff/current`, and all durable worker mirrors aligned and clean at `bb3e86b`.
- `git status --short --branch` showed a clean `master` before documentation edits.

## Triage Verdict

`not_actionable` for EMR4 product runtime security. The alert is worth clearing as dependency housekeeping later, but the advisory's exploit path requires application use of affected npm `uuid` APIs with caller-controlled buffers or offsets. EMR4 has no such JS/TS call path, and the dependency is dev-only build tooling.

## Not Required Before Moving On

- No emergency production fix, backend restart, GitHub Pages deploy, or user live test is required.
- Do not dismiss the GitHub alert without an explicit housekeeping decision; it is still useful as a reminder to modernise or override the Office add-in build dependency tree when safe.

## Known Follow-Up

- Consider a later dependency-maintenance sprint to trial safe `uuid` override/lockfile updates in the Office add-in tooling and run `npm run validate-all`.
- Add a repo-root `SECURITY.md` when the public/open-source security intake process is ready.
- Antigravity CLI still exits with no stdout and no worktree changes in this Codex session; Ariadne should treat that channel as suspect until it is separately repaired.

## Recommended Next Direction

Next recommended sprint: continue Bernie pilot refinement with a narrow staff-visible usability/safety slice now that the open dependency alert has been triaged.

## Previous Closeout - Sprint 70

| Item | Value |
|---|---|
| Batch | Sprint 70: Bernie Staff-Visible Pilot Entry Path |
| Integrated through | Allowlisted non-default staff launcher that requires selected linked appointment context and hides manual ID entry outside smoke/dev |
| Status | Integrated, verified, pushed, mirrored, audited, deployed, and closed |
| Last updated | 2026-06-27 |

## What Changed

- Ordinary allowlisted staff mode no longer accepts `practitioner_id` or `patient_id` query-string context.
- Manual practitioner/patient ID fields and the manual context submit button now render only in smoke/dev review modes.
- Staff-visible Bernie launch now requires importing context from a selected linked diary appointment before instruction entry becomes usable.
- The existing smoke/dev manual context path remains available for deterministic harness coverage.

## Verification

- `C:\Users\sarashera\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe --check docs\diary\diary.js` passed.
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` passed: `49 passed`.
- `.venv\Scripts\python.exe scripts\check_frontend_versions.py` passed locally with `diary.js?v=124` bumped from `v=123`.
- `git diff --check` passed.

## Not Required Before Moving On

- No manual live UI test is required before push; deterministic Playwright coverage now proves default hidden/no-call, allowlisted launcher, no manual ID exposure in staff-visible mode, selected linked appointment import, instruction readiness, summary persistence, and confirmation gating.
- No backend, provider, schema, migration, taskpane, Command Centre, billing, SMS, resource admin, or live Gemini action is required.

## Known Follow-Up

- Antigravity CLI still exits with no stdout and no worktree changes in this Codex session; Ariadne should treat that channel as suspect until it is separately repaired.
- The moderate Dependabot alert was triaged after this sprint as Sprint 71.

## Recommended Next Direction

Next recommended sprint: triage the moderate Dependabot alert before further production-facing Bernie exposure.

## Previous Closeout - Sprint 69

| Item | Value |
|---|---|
| Batch | Sprint 69: Bernie Context Readiness Summary |
| Integrated through | Context-ready instruction gating and persistent selected-context summary in Bernie pilot review |
| Status | Integrated, verified, pushed, mirrored, audited, deployed, and closed |
| Last updated | 2026-06-27 |

## What Changed

- Disabled the Bernie instruction textarea and submit button until valid practitioner/patient context is ready.
- Added a compact context summary once staff import a linked selected appointment or enter valid context.
- The context summary persists through instruction entry and confirmation-ready review so staff can see the patient/time/practitioner context being used.
- Added a `Change` action that clears in-memory Bernie context and returns to the existing context-required state.
- Kept all safety mechanics unchanged: explicit selected-context import, explicit instruction submit, and explicit approval checkbox/button before confirmation.
- Kept context in memory only; no URL, `localStorage`, `sessionStorage`, cookie, backend, or appointment mutation change.
- Bumped diary assets to `diary.css?v=113` and `diary.js?v=123`.
- Ariadne repaired an uncommitted worker bug where smoke appointment summaries could render `undefined` for date, then reran verification and rendered review.

## Recommended User Review

Residual user review/testing after closeout: none required.
Ariadne verified this as a gated, route-intercepted diary UI readiness/summary change. The tests and rendered review prove instruction controls are disabled before context, selected context enables instruction entry, the context summary persists into confirmation, and confirmation still requires the existing approval checkbox.

## Not Required Before Moving On

- No manual live UI test is required; the deterministic Playwright harness covers blocked, candidate-selection, confirmation-ready, pilot eligibility, selected appointment context, context readiness, and instruction paths.
- No live API write test is required; confirm-Bernie remains route-intercepted in review checks.
- No real Gemini/Vertex smoke is required for this UI sprint.
- No database migration, backend schema change, taskpane, Command Centre, Office dialog, resource admin, billing, SMS, or security-console action is required.

## Known Follow-Up

- Next product sprint can move toward a staff-visible non-default Bernie pilot entry path.
- The known moderate Dependabot alert remains outside this sprint.
- Existing unrelated diary CSS letter-spacing rules remain future visual hygiene.
- The known moderate Dependabot alert remains outside this sprint.
- The existing Python/Starlette and Google GenAI deprecation warnings remain future test-hygiene items.

## Verification

- Ariadne reviewed Antigravity's plan packet and accepted it with a guardrail that `Change` may only clear in-memory context and return to the existing context-required state.
- Antigravity left implementation changes uncommitted; Ariadne reconciled the worker branch from the orchestrator side, repaired the `undefined` date bug, and pushed the worker branch before integration.
- `C:\Users\sarashera\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe --check docs\diary\diary.js` -> passed.
- `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 49 passed.
- `C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\check_frontend_versions.py` -> passed; diary assets bumped to `diary.css?v=113` and `diary.js?v=123`.
- Rendered product review with route-intercepted Playwright screenshots -> passed; before context, instruction controls are disabled; after context, summary shows Margaret Thompson, 2026-06-27 @ 09:00, and Alex Shera; summary persists into confirmation; no console errors.
- `git diff --check` -> passed.

## Recommended Next Direction

Next recommended sprint: continue to a staff-visible non-default Bernie pilot entry path with allowlist gating and no manual ID exposure.

## Previous Closeout - Sprint 68

| Item | Value |
|---|---|
| Batch | Sprint 68: Bernie Pilot Review Ergonomics |
| Integrated through | Staff-supervised wording and compact ergonomics for the Bernie pilot review panel |
| Status | Integrated, verified, pushed, mirrored, audited, deployed, and closed |
| Last updated | 2026-06-27 |

Sprint 68 refined Bernie pilot/review wording and compact ergonomics so the panel reads as a supervised staff workflow while preserving existing gates and behaviour.

## Previous Closeout - Sprint 67

| Item | Value |
|---|---|
| Batch | Sprint 67: Bernie Selected Appointment Context |
| Integrated through | Pilot-gated use-selected-appointment context for Bernie review |
| Status | Integrated, verified, pushed, mirrored, audited, deployed, and closed |
| Last updated | 2026-06-27 |

Sprint 67 added the explicit "use selected appointment" context path for linked diary appointments while preserving manual ID fallback, in-memory-only context, staff instruction submit, and confirmation gating.

## Previous Closeout - Sprint 66

| Item | Value |
|---|---|
| Batch | Sprint 66: Bernie Staff Instruction Input Surface |
| Integrated through | Pilot-gated staff-entered booking instruction input for Bernie review |
| Status | Integrated, verified, pushed, mirrored, audited, deployed, and closed |
| Last updated | 2026-06-27 |

Sprint 66 added the compact staff instruction textarea and explicit submit button inside the existing Bernie Booking Review panel. Instruction text is sent only in the authenticated POST body, with no URL or browser-storage persistence, and the existing approval gate remains unchanged.

## Previous Closeout - Sprint 65
| Item | Value |
|---|---|
| Batch | Sprint 65: Bernie Interpret Review UI Adapter |
| Integrated through | Gated diary Bernie review preview for interpreted booking instructions |
| Status | Integrated, verified, pushed, mirrored, audited, and live-smoke hardened |
| Last updated | 2026-06-27 |

## What Changed

- Added a compact `Interpreted Intent` preview inside the existing Bernie Booking Review panel.
- The preview appears only behind explicit `bernie_interpret=true` plus the existing smoke/dev/pilot launch/context gates.
- The preview renders interpreted, clarification-required, and blocked interpretation envelopes before supervised booking review proceeds.
- Clarification/blocked interpretation states hold the supervised review path and do not call confirm-Bernie.
- Existing confirmation-ready supervised review and approval checkbox behaviour remain unchanged.
- Added route-intercepted Playwright/pytest coverage for interpreted, clarification, blocked, and no-explicit-gate states.
- Ariadne removed the proposed `bernie_instruction` URL query intake so free-text booking instructions are not encouraged into browser history; the preview builds a bounded structured instruction from explicit non-PHI context instead.
- Bumped diary assets to `diary.css?v=107` and `diary.js?v=117`.

## Recommended User Review

Residual user review/testing after closeout: none required.
Ariadne verified this frontend-only, gated UI adapter with deterministic route-intercepted Playwright checks. The tests prove no live provider call or confirm-Bernie write occurs before explicit approval, and ordinary diary loads do not request interpretation.

## Not Required Before Moving On

- No manual live UI test is required; the route-intercepted review harness covers the new preview states and existing review regression path.
- No manual live API write test is required; confirm-Bernie remains gated and intercepted in tests.
- No real Gemini/Vertex smoke is required yet; live cloud execution should wait until the Bernie service-account/ADC setup is intentionally exercised.
- No database migration, service-account key, Word taskpane, Command Centre, Office dialog, resource admin, billing, SMS, or security-console action is required for this sprint.

## Known Follow-Up

- Run a future explicit live Gemini/Vertex smoke using the Bernie service account or ADC/service-account impersonation once Yuri wants to validate real provider behaviour.
- A future sprint can replace the temporary structured-context instruction builder with a proper staff-entered instruction source that avoids query strings and PHI-heavy logs.
- The known moderate Dependabot alert remains outside this sprint.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- Post-closeout live smoke with Bernie service-account impersonation succeeded using dummy/non-PHI IDs only. The smoke caught a provider-summary UUID echo, so Ariadne added summary redaction and a regression assertion before treating the live path as safe.

## Verification

- Ariadne reviewed Cicero's plan and implementation packets, inspected the branch diff against `master`, and reran the worker's verification locally using the shared project venv before integration.
- Ariadne applied a bounded privacy hardening repair to remove URL free-text instruction intake before integration.
- `node --check docs\diary\diary.js` -> passed.
- `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q -k "bernie_interpret or bernie_pilot_ordinary_mode or bernie_review_live_confirmation_ready" --tb=short` -> 7 passed.
- `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 46 passed.
- `rg -n "diary\.css\?v=107|diary\.js\?v=117" docs\diary\diary.html` -> passed.
- Post-closeout live provider smoke with `GCP_PROJECT=project-2893b749-f3af-4449-a61` and `BERNIE_BOOKING_INTERPRETER_PROVIDER=gemini_vertex` -> succeeded with dummy data; autonomous booking language blocked and provider summary redacted IDs.
- `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest tests\test_bernie_interpret_booking_instruction.py -q --tb=short -p no:randomly` after redaction hardening -> 11 passed.
- `git diff --check` -> passed.
- `pytest_asyncio` emitted the existing fixture-loop-scope deprecation warning only.

## Recommended Next Direction

Next recommended sprint: either run a narrow explicit live-provider smoke once Yuri has completed ADC/service-account impersonation setup, or add a proper staff instruction input surface that avoids query strings and keeps the flow pilot-gated.

## Previous Closeout - Sprint 64
| Item | Value |
|---|---|
| Batch | Sprint 64: Bernie Interpret Live Provider Runway |
| Integrated through | Default-off Gemini/Vertex provider seam for Bernie booking-instruction interpretation |
| Status | Integrated, verified, pushed, mirrored, audited, and closed |
| Last updated | 2026-06-27 |

Sprint 64 added an explicit default-off `gemini_vertex` provider path behind the existing Bernie booking-instruction interpreter seam, with mocked-live backend tests and no live cloud calls in ordinary verification.

## Previous Closeout - Sprint 63
| Item | Value |
|---|---|
| Batch | Sprint 63: Bernie Interpret Booking Instruction Endpoint |
| Integrated through | Read-only mocked/default-disabled Bernie booking-instruction interpreter |
| Status | Integrated, verified, pushed, mirrored, audited, and closed |
| Last updated | 2026-06-27 |

Sprint 63 added the first read-only Bernie booking-instruction interpreter endpoint with disabled/default-safe and deterministic fake-provider behaviour. No manual user review was required.

## Previous Closeout - Sprint 58
| Item | Value |
|---|---|
| Batch | Sprint 58: Bernie Dev Selector Help Affordance |
| Integrated through | Dev-only explanatory help for Bernie fixture-state selector |
| Status | Integrated, verified, pushed, mirrored, audited, deployed, and closed |
| Last updated | 2026-06-27 |

## What Changed

- Added a compact `State help` details affordance beside the dev-only Bernie fixture-state selector.
- Help copy explains `blocked`, `candidate_selection_required`, and `confirmation_ready` without implying autonomous booking.
- The selector/help wrapper remains hidden unless `bernie_dev_review=true`.
- Opening or reading the help text makes no backend fixture calls and no confirm-Bernie calls.
- Existing selector behavior remains intact, and confirmation-ready review still requires explicit staff checkbox approval before any confirm-Bernie POST.
- Bumped diary asset cache busting to `diary.css?v=104` and `diary.js?v=113`.
- Poincare implemented the narrow Codex-worker UI/test slice after an accepted plan gate.

## Recommended User Review

Residual user review/testing after closeout: none required before continuing.
Ariadne verified this as an explicit dev/query-gated explanatory affordance with deterministic route-intercepted Playwright checks. No production/default diary exposure or live write path changed.

## Not Required Before Moving On

- No manual live UI test is required; route-intercepted Playwright verifies help visibility/gating, static no-call behavior, selector behavior, and explicit approval before confirm POST.
- No manual live API write test is required; confirm-Bernie remains intercepted in the harness and no live writes are performed.
- No database migration, data repair, GCP/Gemini, Word taskpane, Command Centre, Office dialog, resource admin, billing, SMS, or security-console action is required.
- No manual review is needed for Sprint 58 itself; a product direction decision is still needed before moving Bernie review from dev/query-gated tooling toward ordinary staff-visible exposure.

## Known Follow-Up

- A later product decision remains before exposing Bernie review in ordinary production mode without explicit dev/query gating.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert remains outside this sprint.
- The existing dev-only nature of this surface remains; a later product decision is still needed before any ordinary production exposure.

## Verification

- Ariadne reviewed Poincare's Codex-worker plan and implementation packets and inspected the final branch diff against `master`.
- `node --check docs\diary\diary.js` -> passed.
- `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe scripts\check_frontend_versions.py` -> passed with `diary.css` bumped from `v=103` to `v=104` and `diary.js` bumped from `v=112` to `v=113`.
- `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 37 passed.
- `git diff --check` -> passed.
- `pytest_asyncio` emitted the existing fixture-loop-scope deprecation warning only.

## Recommended Next Direction

Next sprint should likely shift from dev-only review tooling back toward product behavior: decide whether Bernie review should remain dev/query-only for a little longer, or start a narrow staff-visible non-default pilot surface with explicit safety gating.

## Previous Closeout - Sprint 55

Sprint 55 added the backend-only deterministic non-PHI Bernie review fixture route for dev tooling.

- Added authenticated `GET /api/v1/appointments/dev/bernie-review-fixtures`, gated to `ENVIRONMENT=dev`.
- The route returns deterministic `BernieSupervisedBookingOut` fixtures keyed by `blocked`, `candidate_selection_required`, and `confirmation_ready`.
- Optional `?state=` returns a single keyed fixture payload for that state.
- Fixture `staff_review` values are built through the live `_bernie_staff_review_payload` helper so the dev fixture contract tracks the real supervised Bernie wrapper output.
- Confirmation-ready fixtures use the existing confirm-Bernie endpoint `/api/v1/appointments/proposals/create/confirm-bernie` and keep `confirm_payload.confirmed` false until explicit staff approval.
- Added focused tests proving auth/dev gating, deterministic shape, no appointment writes, no audit writes, no LLM/provider imports, and non-PHI fixture content.
- Claude implemented the backend slice; Ariadne caught and corrected route/helper drift via a recovery nudge before final integration.

Residual user review/testing after Sprint 55 closeout: none required. Ariadne verified this as a backend-only deterministic dev fixture route with focused and adjacent pytest coverage.


## Previous Closeout - Sprint 54

Sprint 54 added the dev-only Bernie review launch affordance.

- Added a dev-only `Dev Bernie Review` toolbar button behind `bernie_dev_review=true`.
- Default diary mode shows no launcher, no Bernie review panel, and makes no supervised-booking or confirm-Bernie calls.
- `?bernie_dev_review=true` shows only the launcher and still makes no endpoint calls until clicked.
- Clicking the launcher preserves existing query parameters and adds `bernie_review=live`, entering the existing dev-gated live review path.
- Confirm-Bernie still requires the approval checkbox before any POST, and the route-intercepted harness proves no confirm call happens before staff approval.
- Bumped diary assets to `diary.css?v=102` and `diary.js?v=109`.
- Antigravity implemented the UI/test slice; Ariadne applied bounded cleanup to the review harness comments and packet statuses.

Residual user review/testing after Sprint 54 closeout: none required. Ariadne verified this with deterministic route-intercepted Playwright checks.


## Previous Closeout - Sprint 53

Sprint 53 added the explicit dev-mode gate for the Bernie live review/confirm path.

- Added an explicit `bernie_dev_review=true` query gate for the Bernie supervised live review/confirm path.
- `bernie_review=live` alone now remains hidden and makes no supervised-booking or confirm-Bernie calls in ordinary mode.
- Smoke live-review tests now also include `bernie_dev_review=true`, keeping the live backend-like path deliberate even in the harness.
- Ordinary dev-mode `?bernie_review=live&bernie_dev_review=true` loads the diary/review panel and can exercise supervised-booking plus explicit confirm through route-intercepted Playwright tests.
- Confirm-Bernie still requires the approval checkbox before any POST, and the deterministic test proves no confirm POST happens before approval.
- Bumped diary JS cache busting to `diary.js?v=108`.
- Antigravity implemented the UI/test slice; Ariadne required the extra dev-flag safety constraint and applied a bounded cleanup removing nonessential inline comments.

Residual user review/testing after Sprint 53 closeout: none required. Ariadne verified it with deterministic route-intercepted Playwright checks.


## Previous Closeout - Sprint 52

Sprint 52 added a deterministic smoke harness proving the supervised-booking live review through explicit confirm submit flow.

- Added a deterministic Playwright smoke harness proving the Sprint 50 live supervised-booking review adapter and Sprint 51 explicit confirm submit adapter work together.
- The success path route-intercepts `/appointments/proposals/bernie/supervised-booking`, renders the returned `staff_review`, proves no confirm-Bernie POST happens before checkbox approval, then route-intercepts confirm-Bernie and asserts the exact `confirmed: true` payload shape.
- The blocked and candidate-selection live-review paths are covered and prove no confirm controls or confirm-Bernie write attempts appear.
- The supervised-booking HTTP-error path is covered and proves the UI falls back to a blocked review state without a confirm write.
- Added a normal-mode exposure check proving `bernie_review=live&bernie_confirm_adapter=true` does nothing unless `smoke=true` is also present.
- No production diary HTML/CSS/JS, backend, schema, or live runtime behaviour changed.
- Antigravity submitted an acceptable plan but repeatedly produced no implementation after release and nudge, so Ariadne completed the approved test-only harness directly to avoid stalling the sprint.

Residual user review/testing after Sprint 52 closeout: none required. Ariadne verified it as a deterministic review-harness-only sprint with route-intercepted endpoint behaviour.


## Previous Closeout - Sprint 51

Sprint 51 added the smoke/feature-gated explicit staff approval submit adapter for Bernie review confirmation payloads.

- Added a smoke/feature-gated Bernie confirmation submit adapter behind `smoke=true&bernie_confirm_adapter=true`.
- In the gated mode only, the confirmation-ready Bernie review panel posts the existing `staff_review.confirm_payload` to `staff_review.confirm_endpoint` after the staff approval checkbox is ticked and the confirm button is clicked.
- The submitted payload is cloned with `confirmed: true`; the source payload remains a review payload until explicit staff action.
- Preserved the existing simulated approval behaviour for ordinary smoke review modes that do not opt into the confirm adapter.
- Added success and error display handling, including retry after a route-intercepted failure.
- Added deterministic Playwright checks for successful submit payload shape, no submit before approval, error/retry behaviour, blocked/candidate states, and existing non-write review paths.
- Bumped diary assets to `diary.css?v=101` and `diary.js?v=107`.
- Antigravity implemented the UI adapter on `antigravity/current`; Ariadne applied a bounded whitespace cleanup after Antigravity left the implementation dirty and unsubmitted.

Residual user review/testing after Sprint 51 closeout: none required. Ariadne verified it as a smoke/feature-gated UI adapter with route-intercepted deterministic Playwright tests.

## Previous Closeout - Sprint 50

Sprint 50 added the smoke-gated diary Bernie review live adapter.

- Extended the smoke-gated diary Bernie review panel with `bernie_review=live` adapter mode.
- In smoke/live-adapter mode, the diary client posts deterministic dev input to `/api/v1/appointments/proposals/bernie/supervised-booking` and renders the returned `staff_review` payload.
- Preserved all Sprint 49 fixture modes for `blocked`, `candidate_selection_required`, and `confirmation_ready`.
- Kept real confirmation out of scope: the confirm button still simulated local approval only and did not post to confirm-Bernie.
- Added route-intercepted Playwright checks for live-adapter blocked, candidate-selection, and confirmation-ready responses.
- Added a deterministic guard that fails if the UI tries to call `/api/v1/appointments/proposals/create/confirm-bernie` during Sprint 50.
- Bumped diary JS to `diary.js?v=106`; diary CSS remained `v=100`.
- Antigravity implemented the live adapter on `antigravity/current`.

Residual user review/testing after Sprint 50 closeout: none required. Ariadne verified it as a smoke/feature-gated UI adapter with route-intercepted deterministic Playwright tests.

## Previous Closeout - Sprint 49

Sprint 49 added a smoke-gated diary Bernie Booking Review panel and deterministic Playwright checks.

- Added the review panel markup, styling, and fixture rendering for Sprint 48-style `staff_review` payloads.
- Covered `blocked`, `candidate_selection_required`, and `confirmation_ready` review states.
- Confirmation-ready smoke rendering required explicit simulated approval before enabling the confirm button.
- The smoke confirmation path stayed local to the browser fixture and called no live API write path.
- Added stable `data-testid` selectors and default hidden-panel checks.
- Bumped diary assets to `diary.css?v=100` and `diary.js?v=105`.
- Antigravity implemented the UI harness on `antigravity/current`.

Residual user review/testing after Sprint 49 closeout: none required. Ariadne verified it as a smoke-only UI review harness with deterministic Playwright tests.

## Previous Closeout - Sprint 48

Sprint 48 added the additive deterministic `staff_review` payload to the supervised Bernie wrapper response.

- Added `BernieStaffReviewPayload` and `BernieStaffReviewSlotSummary` response schemas.
- Added stable review fields for headline/status, staff action required, confirmation readiness, selected slot summary, candidate slot summaries, warning/block summaries, confirm endpoint, confirm payload, and bounded confirm evidence.
- Preserved existing wrapper `result` discriminators: `blocked`, `candidate_selection_required`, and `confirmation_ready`.
- Kept `staff_review.confirm_payload.confirmed` intentionally false so later UI must require explicit staff approval before posting it.
- Cicero/Boole implemented the backend contract sprint on `codex/bernie-supervised-review-payload`.

Residual user review/testing after Sprint 48 closeout: none required. Ariadne verified it as a backend-only additive API contract with focused and adjacent pytest coverage.

## Previous Closeout - Sprint 47

Sprint 47 added the deterministic backend harness proving the supervised Bernie wrapper's `confirmation_ready` evidence can be explicitly confirmed through the existing confirm-Bernie endpoint, while blocked, stale, candidate-only, and `confirmed=false` paths remain non-mutating.

- Added `tests/test_bernie_wrapper_confirmation_review_harness.py`.
- The success path requires `confirmed=true` and writes exactly one appointment plus exactly one bounded audit evidence trail.
- The negative paths write no appointment rows and no appointment audit rows.
- The harness blocks Gemini/LLM/provider access during the flow.
- Cicero/Feynman implemented the test-only sprint on `codex/bernie-wrapper-confirmation-review-harness`.

Residual user review/testing after Sprint 47 closeout: none required. Ariadne verified it as a backend-only deterministic review harness with focused and adjacent pytest coverage.

## Previous Closeout - Sprint 46

Sprint 46 added the backend-only supervised wrapper for deterministic Bernie booking intake: normalize -> slot search -> slot selection/create-proposal evidence, without writing appointments, writing audit rows, calling confirmation, or invoking Gemini/LLM providers.

- Added authenticated `POST /api/v1/appointments/proposals/bernie/supervised-booking`.
- Added `BernieSupervisedBookingIn` and `BernieSupervisedBookingOut` schemas.
- The wrapper accepts typed deterministic Bernie booking command input plus optional supervised selected-slot context.
- It returns a stable `result` discriminator with `blocked`, `candidate_selection_required`, or `confirmation_ready`.
- It composes existing deterministic command normalization, slot-search proposal, slot-selection, and create-proposal evidence paths.
- Added `tests/test_bernie_supervised_booking_wrapper.py` covering auth, practice scoping, blocked normalization, candidate-selection response, selected-slot confirmation-ready evidence, conflict revalidation, non-mutation row counts, and no-LLM/no-write source proof.
- Cicero/Archimedes implemented the backend-only sprint on `codex/bernie-supervised-booking-wrapper`.

Residual user review/testing after Sprint 46 closeout: none required. Ariadne verified it as a backend-only API contract with focused and adjacent pytest coverage.

## Previous Closeout - Sprint 45

Sprint 45 added the deterministic backend harness proving the full supervised Bernie normalize -> normalized search -> slot selection -> explicit confirmation chain remains no-write/no-LLM until explicit confirmation, then writes exactly one appointment and bounded audit evidence on success.

- Added `tests/test_bernie_confirmed_flow_review_harness.py`.
- The harness exercises the full supervised Bernie backend chain: deterministic command normalization, normalized slot search, supervised slot selection/create-proposal evidence, and explicit confirm-write.
- It proves normalize/search/select steps write no appointment rows and no appointment audit rows.
- It proves `confirmed=false` and stale-conflict confirmation paths write no appointment/audit rows.
- It proves successful explicit confirmation writes exactly one appointment and exactly one bounded audit evidence trail.
- It guards the flow against Gemini/LLM/provider calls and autonomous natural-language execution.
- Cicero/Euclid implemented the test-only sprint on `codex/bernie-confirmed-flow-review-harness`.
- No production code, diary UI, taskpane, Command Centre, live Bernie runtime, Gemini parsing, autonomous booking behavior, billing, SMS, resource admin, or migration changed.

Residual user review/testing after Sprint 45 closeout: none required. Ariadne verified it as a deterministic backend review-harness sprint with no visible UI, deployed asset, Office/Word surface, diary interaction, or live clinical workflow for Yuri to manually review.


## Previous Closeout - Sprint 44

Sprint 44 added the backend-only supervised Bernie confirmation route that writes exactly one appointment only after explicit staff confirmation.

- Added authenticated `POST /api/v1/appointments/proposals/create/confirm-bernie`.
- The route accepts supervised Sprint 42/43 slot-selection/create-proposal evidence plus explicit `confirmed=true`.
- It blocks without appointment or audit writes when confirmation is false, source evidence is unsafe, selected slot and create command mismatch, or revalidation finds a stale conflict.
- On success it revalidates existing appointment safety, creates exactly one appointment through the existing create path, and records bounded Bernie/source evidence in the appointment audit log.
- Added `BernieCreateProposalConfirmationIn` and `AppointmentConfirmCreateProposalOut` schemas.
- Refactored appointment creation into `_create_appointment_from_body(...)` so direct create and confirmed Bernie create share validation, conflict checks, output hydration, break-overlap reporting, and audit writing.
- Added `tests/test_bernie_confirm_create_proposal.py` covering auth, explicit confirmation, no-write blocked paths, stale-conflict revalidation, source mismatch blocking, exactly-one-write success, bounded audit evidence, and no-LLM/no-provider proof.
- Cicero/Franklin implemented the backend-only sprint on `codex/bernie-confirm-create-proposal`.
- No diary UI, taskpane, Command Centre, Gemini/LLM parsing, autonomous Bernie runtime, SMS, billing, resource admin, migration, or visible workflow changed.


## Previous Closeout - Sprint 43

Sprint 43 added the deterministic backend harness proving the Bernie normalize -> normalized search -> slot selection chain remains no-write/no-LLM before final booking confirmation work.

- Added `tests/test_bernie_slot_flow_review_harness.py`.
- The harness exercises the backend-only Bernie chain across command normalization, normalized slot search, and supervised slot selection proposal.
- It proves a successful normalize -> search -> select path can prepare create-proposal evidence without writing appointment rows or appointment audit rows.
- It covers no-match selection blocking and conflict selection blocking without new writes.
- It adds runtime and source-level guards that fail if the flow instantiates/calls the AI provider surface or performs final booking/audit writes inside the three Bernie proposal routes.
- Cicero/Plato implemented the sprint on `codex/bernie-slot-flow-review-harness`.
- No production route, schema, model, migration, diary UI, taskpane, Command Centre, Gemini parsing, autonomous Bernie runtime, final booking write bridge, audit mutation, billing, SMS, resource admin, or visible workflow changed.


## Previous Closeout - Sprint 42

Sprint 42 added the non-mutating `POST /api/v1/appointments/proposals/slot-search/selection` endpoint that converts one supervised slot-search candidate selection into create-proposal evidence.

- Added authenticated `POST /api/v1/appointments/proposals/slot-search/selection`.
- The endpoint accepts supervised slot-selection evidence, either from a normalized slot-search execution payload plus selected index/candidate or an explicit selected candidate plus required booking context.
- Selected candidates are validated against the search result when evidence is supplied, including index/candidate mismatch and not-in-results blocking.
- The route reuses the existing non-mutating create-proposal path through `_build_create_appointment_proposal(...)`, preserving conflict, break, provisional-patient, practice-scope, and confirmation semantics.
- Added `SlotSelectionProposalIn` and `SlotSelectionProposalOut` schemas for the supervised select-slot-for-create-proposal response.
- Added focused tests for auth, happy-path index selection, no appointment/audit writes, selected-candidate mismatch blocking, create-proposal conflict semantics, and source-level no-LLM/no-mutation proof.
- Cicero/Hegel implemented the backend-only fallback on `codex/bernie-slot-selection-proposal`.
- No diary UI, taskpane, Command Centre, booking write, audit mutation, billing, SMS, migrations, patient demographics, resource admin, or live Bernie autonomous runtime was added.

## Recommended User Review

Residual user review/testing after closeout: none required before continuing.
Ariadne verified this as a backend-only API contract with focused pytest and compile checks. There is no visible UI, deployed asset, appointment mutation, LLM call, or manual clinical workflow to review.

## Not Required Before Moving On

- No manual live API test is required; focused tests cover the route contract, selected-candidate validation, create-proposal reuse, conflict semantics, and non-mutation proof.
- No manual live UI review is required; no frontend files or deployed assets changed.
- No database migration or data repair is required.
- No Word taskpane, Command Centre, GCP/Gemini, Office dialog, diary grid, resource admin, billing, SMS, or security-console action is required.

## Known Follow-Up

- Future Bernie work can now chain command normalization, safe slot search, supervised candidate selection, and create-proposal evidence without writing appointments.
- The endpoint accepts client-supplied normalized search evidence and validates candidate consistency, but the evidence is not server-persisted. Future UI/runtime should still treat it as supervised review evidence and require create-proposal confirmation before any write.
- The next useful slice is either a supervised confirmation bridge that makes the final write semantics explicit or a lightweight deterministic review harness around the Bernie flow.
- A later sprint can decide where DB-backed name-to-UUID resolution belongs; this sprint intentionally treats identifier normalization as UUID/format parsing only.
- Natural language date phrases beyond deterministic `today`/`tomorrow` remain the upstream parser/LLM's responsibility.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert remains outside Sprint 39.

## Verification

- `python scripts\agent_worktrees.py audit --fetch` -> Sprint 42 Codex worker branch submitted and integration worktree clean.
- Worker plan accepted after metadata correction and implementation released to Cicero/Hegel.
- Ariadne reran backend compile check with the project venv: `python -m py_compile app\schemas\appointments.py app\routers\appointments.py tests\test_slot_selection_proposal.py` -> passed.
- Ariadne reran focused slot-selection tests: `python -m pytest tests\test_slot_selection_proposal.py -q --tb=short -p no:randomly` -> 5 passed.
- Ariadne reran adjacent regression tests: `python -m pytest tests\test_slot_search_normalized_execution.py tests\test_slot_search_proposal.py tests\test_slot_search_normalize_endpoint.py tests\test_appointment_proposals.py -q --tb=short -p no:randomly` -> 41 passed.
- Diff hygiene: `git diff --check origin/master..origin/codex/bernie-slot-selection-proposal` -> passed.

## Recommended Next Direction

Sprint 43 should either add the final supervised confirmation bridge from create-proposal evidence to the existing appointment write path, with explicit audit/write semantics, or add a small deterministic review harness for the Bernie command-normalize-search-select chain before moving to UI/runtime surfaces.


## Previous Closeout - Sprint 41

Sprint 41 added the non-mutating `POST /api/v1/appointments/proposals/slot-search/normalized` endpoint that normalizes a Bernie slot-search command and, only when safe, returns candidate slots. It remains the normalize-and-search foundation used by Sprint 42 selection.


## Previous Closeout - Sprint 40

Sprint 40 added the deterministic, non-mutating `POST /api/v1/appointments/proposals/slot-search/normalize` endpoint. It remains the normalize-only foundation used by the Sprint 41 combined normalize-and-search contract.


## Previous Closeout - Sprint 39

Sprint 39 added the pure deterministic Bernie slot-search command normalizer and its unit tests. It remains the foundation used by the Sprint 40 endpoint.


## Previous Closeout - Sprint 38

| Item | Value |
|---|---|
| Batch | Sprint 38: Bernie-Safe Slot Search Proposal Foundation |
| Integrated through | Sprint 38 backend non-mutating slot-search proposal contract and smoke-only diary preview harness |
| Status | Integrated, pushed, mirrored, audited, and closed |
| Last updated | 2026-06-26 |

## What Changed

- Added a read-only `POST /api/v1/appointments/proposals/slot-search` endpoint that accepts typed slot-search constraints and returns ranked candidate slots, warnings, blocks, and a human-readable summary.
- Added `SlotSearchProposalIn`, `SlotCandidate`, and `SlotSearchProposalOut` schemas for future Bernie/reception scheduling workflows.
- Extracted `_resolve_day_schedule(...)` from existing slot-generation code so `/slots/{practitioner_id}` and slot-search proposal logic share the same day schedule/override resolution.
- Kept the new backend endpoint role-gated, practice-scoped, practitioner-scoped, optional patient/location constrained, and explicitly non-mutating: no appointment rows and no appointment audit rows are written.
- Added focused backend tests for auth, practice scoping, candidate ordering/duration/timezone fields, duration derivation, date-range validation, conflict filtering, non-blocking terminal statuses, break warnings, location-specific conflict handling, no-schedule days, limit caps, and non-mutation proof.
- Added a deterministic smoke-only diary slot-search preview harness behind `?smoke=true&slot_preview=true`; live diary rendering remains inert unless that explicit smoke/review flag is present.
- Added dashed, read-only slot-preview candidate styling and deterministic Playwright checks proving preview count, labels, and no booking-modal opening on preview click.
- Bumped diary assets to `diary.css?v=99` and `diary.js?v=104`.
- No live Bernie runtime, LLM/Gemini parsing, taskpane, Command Centre, real appointment mutation, waiting-room flow, billing, SMS, resource administration, or live diary slot-search UI was added.

## Recommended User Review

Residual user review/testing after closeout: none required before continuing.
Ariadne verified the backend contract, non-mutation behaviour, frontend syntax/assets, and deterministic diary smoke checks. The visible diary preview is smoke/review-harness gated and is not a live user-facing workflow.

Optional confidence check only, if Yuri happens to be in the live diary after deployment:

1. Setup: hard refresh the live diary and confirm `diary.js?v=104` and `diary.css?v=99` are loaded.
2. Exact UI path: open the normal live diary without `smoke=true&slot_preview=true`.
3. Expected result: no dashed slot-search preview candidates should appear anywhere in the live diary.
4. Expected safety: normal appointment cards, booking modal open/edit flows, click-to-create/edit behaviour, waiting-room panel, audit history, status controls, and drag/resize affordances should behave as before.
5. Suspicious signs: dashed preview cards visible in the live diary, clicking empty diary space no longer opens the expected booking workflow, slot previews create/edit appointments, console errors, or asset versions failing to update.
6. Skippable parts: do not manually retest backend slot-search API, taskpane, Command Centre, resource admin, billing, SMS, AI provider facade, security workflows, or cancelled appointment review for Sprint 38.
7. Evidence to report: only report a screenshot/console error if smoke preview artifacts leak into the live diary or booking click behaviour regresses.

## Not Required Before Moving On

- No manual live API test is required; focused pytest covers the slot-search proposal contract and non-mutation proof.
- No manual live UI review is required; deterministic smoke verifies the slot-preview harness and live/default absence condition.
- No database migration or data repair is required.
- No Word taskpane, Command Centre, GCP/Gemini, Office dialog, resource admin, billing, SMS, or security-console action is required.

## Known Follow-Up

- Future Bernie work can feed LLM-parsed constraints into the typed slot-search endpoint, then present candidates for human confirmation through a separate create-proposal path.
- Future UI work can replace the smoke fixture with real API-backed preview data, but only after an explicit live UI task and confirmation workflow are planned.
- Consider making slot-search warnings code-only plus friendly-label mapping if/when they become user-facing outside the smoke harness.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert remains outside Sprint 38.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found both Sprint 38 plan packets and implementation review packets.
- Backend compile check: `python -m py_compile app\routers\appointments.py app\schemas\appointments.py tests\test_slot_search_proposal.py` -> passed.
- Focused backend slot-search tests: `python -m pytest tests\test_slot_search_proposal.py -q --tb=short -p no:randomly` -> 20 passed.
- Frontend static check: `node --check docs\diary\diary.js` -> passed.
- Deterministic diary review: `python -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 19 passed.
- Frontend asset version check: `python scripts\check_frontend_versions.py` -> passed; diary CSS moved to `v=99` and diary JS moved to `v=104` while deployed pages still served previous versions before push.
- Diff hygiene: `git diff --check` -> passed.

## Recommended Next Direction

Sprint 39 was dispatched as the next narrow Bernie slice: deterministic slot-search command parsing/normalization into the existing `SlotSearchProposalIn` constraint shape, without executing searches or creating appointments.


## Previous Closeout - Sprint 36

| Item | Value |
|---|---|
| Batch | Sprint 36: Diary Audit History Keyboard Accessibility |
| Integrated through | Sprint 36 audit-history toggle keyboard and ARIA semantics |
| Status | Integrated, pushed, mirrored, audited, and closed |
| Last updated | 2026-06-26 |

## What Changed

- Added `role="button"`, `tabindex="0"`, `aria-controls="booking-audit-content"`, and `aria-expanded="false"` to the booking audit-history header.
- Updated the audit-history click handler to keep `aria-expanded` synchronized with the collapsed/expanded state.
- Added keyboard support for Enter and Space on the audit-history header, with Space default scrolling prevented.
- Reset `aria-expanded` to `false` whenever the booking edit modal opens.
- Added deterministic diary smoke assertions for role, tabindex, `aria-controls`, `aria-expanded`, Enter toggle, Space toggle, click toggle, and reset-on-reopen behaviour.
- Bumped the diary JS cache-bust to `diary.js?v=102` in `docs/diary/diary.html`.
- No backend code, appointment mutation/proposal flow, taskpane, Command Centre, billing, SMS, AI provider, resource administration, cancelled appointment review, or non-audit-history controls were changed.

## Recommended User Review

Residual user review/testing after closeout: none required before continuing.
Ariadne verified the keyboard behaviour through deterministic Playwright smoke tests and did not need visual/Computer Use review.

Optional confidence check only, if Yuri happens to be in the live diary after deployment:

1. Setup: hard refresh the live diary and confirm `diary.js?v=102` and `diary.css?v=98` are loaded.
2. Exact UI path: open an existing appointment for editing and tab to the `Audit History` header.
3. Expected keyboard behaviour: pressing Enter expands the section, pressing Space collapses it, and clicking still works normally.
4. Expected accessibility state: the section starts collapsed and `aria-expanded` tracks the visible state, though this is mainly for assistive technology and automated checks.
5. Expected safety: no appointment status, waiting-area state, cancellation state, booking details, or proposal confirmation changes occur from toggling audit history.
6. Suspicious signs: focus cannot reach the audit header, Enter/Space do nothing, the page scrolls unexpectedly on Space, visible layout changes, audit rows disappear, console errors appear, or mutation controls appear in audit history.
7. Skippable parts: do not retest backend audit actor fields, test hooks, taskpane, Command Centre, patient files, resource administration, drag/resize, recurrence, SMS, billing, AI provider facade, security workflows, or cancelled-appointment review for Sprint 36.
8. Evidence to report: only report a screenshot/console error if keyboard toggling or visible layout regressed.

## Not Required Before Moving On

- No manual live UI review is required; the deterministic diary smoke passed keyboard and ARIA assertions.
- No database migration, data repair, Word taskpane, Command Centre, GCP/Gemini, Office dialog, resource admin, billing, SMS, or security-console action is required.

## Known Follow-Up

- Continue adding keyboard/ARIA assertions opportunistically when a visible control is touched.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert still appears on GitHub pushes and remains outside Sprint 36.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found the Sprint 36 Antigravity plan and review packets.
- Frontend static check: `node --check docs\diary\diary.js` -> passed.
- Deterministic diary review: `.\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 17 passed.
- Frontend asset version check: `.\.venv\Scripts\python.exe scripts\check_frontend_versions.py` -> passed; `diary.js` moved to `v=102` while live deployed HTML still served `v=101` before push.
- Diff hygiene: `git diff --check` -> passed.

## Recommended Next Direction

Pause Antigravity-only polishing unless Yuri wants more; prefer waiting for Claude's headless limit to recover before backend-heavy audit/proposal work.




## Previous Closeout - Sprint 35

| Item | Value |
|---|---|
| Batch | Sprint 35: Diary Audit History Test-Hook Hardening |
| Integrated through | Sprint 35 stable diary audit-history test hooks and deterministic smoke assertions |
| Status | Integrated, pushed, mirrored, audited, and closed |
| Last updated | 2026-06-26 |

## What Changed

- Added stable `data-testid` hooks to the diary booking audit-history section, header, title, content, list, fallback rows, audit items, metadata, timestamps, and details.
- Updated rendered audit-history list items in `docs/diary/diary.js` to set test hooks without changing visual copy or runtime behaviour.
- Updated `review/test_diary_smoke.py` to use the stable audit-history test hooks instead of brittle CSS class selectors.
- Updated `review/checks_diary.json` to assert the audit header/title through `data-testid` selectors.
- Bumped the diary JS cache-bust to `diary.js?v=101` in `docs/diary/diary.html`.
- No backend code, mutation/proposal flow, taskpane, Command Centre, billing, SMS, AI provider, resource administration, cancelled-appointment review, or broad booking modal redesign was included.

## Recommended User Review

Residual user review/testing after closeout: none required before continuing.
Ariadne verified the deterministic diary smoke harness and asset-version checks. This sprint intentionally adds non-functional test hooks and stronger automated assertions only.

Optional confidence check only, if Yuri happens to be in the live diary after deployment:

1. Setup: hard refresh the live diary and confirm `diary.js?v=101` and `diary.css?v=98` are loaded.
2. Exact UI path: open an existing appointment for editing, then expand `Audit History`.
3. Expected result: the visible audit-history copy should look unchanged from Sprint 34, but automated tests now target stable hooks under the hood.
4. Expected safety: no new buttons, edits, status changes, waiting-area changes, cancellation changes, or proposal confirmations should appear from the audit section.
5. Suspicious signs: audit history no longer expands, visible text changes unexpectedly, console errors appear, or booking save/cancel/status flows change.
6. Skippable parts: do not retest backend audit actor fields, taskpane, Command Centre, patient files, resource administration, drag/resize, recurrence, SMS, billing, AI provider facade, security workflows, or cancelled-appointment review for Sprint 35.
7. Evidence to report: only report a screenshot/console error if the audit section visually regressed or created a new mutation affordance.

## Not Required Before Moving On

- No manual live UI review is required; the deterministic diary smoke passed using the new hooks.
- No database migration, data repair, Word taskpane, Command Centre, GCP/Gemini, Office dialog, resource admin, billing, SMS, or security-console action is required.

## Known Follow-Up

- Keep moving stable UI review checks from visual/class selectors to `data-testid` hooks when touching a surface.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert still appears on GitHub pushes and remains outside Sprint 35.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found the Sprint 35 Antigravity plan and review packets.
- Frontend static check: `node --check docs\diary\diary.js` -> passed.
- Deterministic diary review: `.\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 17 passed.
- Frontend asset version check: `.\.venv\Scripts\python.exe scripts\check_frontend_versions.py` -> passed; `diary.js` moved to `v=101` while live deployed HTML still served `v=100` before push.
- Diff hygiene: `git diff --check` -> passed.

## Recommended Next Direction

Sprint 36 has been dispatched as another small Programme 2D slice while Claude's headless limit recovers: keyboard/ARIA semantics for the read-only audit-history toggle.

## Previous Closeout - Sprint 34

| Item | Value |
|---|---|
| Batch | Sprint 34: Appointment Audit History Readability |
| Integrated through | Sprint 34 backend audit actor-display contract and diary readable audit-history UI |
| Status | Integrated, pushed, mirrored, audited, and closed |
| Last updated | 2026-06-26 |

## What Changed

- Added read-time `confirmed_by_display` and `confirmed_by_role` fields to `AppointmentAuditLogOut`.
- Updated `GET /api/v1/appointments/{appointment_id}/audit` to batch-load confirming users with practitioners, preserve practice scoping, and derive a safe staff display label without adding a migration.
- Actor display falls back from practitioner first/last name to email local-part to `Unknown`; `confirmed_by_user_id` remains in the response for stable machine identity.
- Added audit contract tests proving receptionist fallback (`rec`), clinician practitioner display (`Alex Shera`), actor roles, auth, cross-practice denial, ordering, and empty history.
- Claude's accepted backend plan was recovered by Ariadne because Claude hit a session-limit/429 after committing the plan packet; no production code came from Claude after the plan gate.
- Diary audit history now renders friendly action labels (`Created`, `Updated`, `Status Changed`, `Cancelled`) and friendly status text such as `In Consult` and `Did Not Attend (DNA)`.
- Diary audit actor rendering now uses backend display names when present and restrained UUID fallback text such as `Staff (11111111)` when only a raw UUID is available.
- Diary audit transition copy now reads as `Changed from X to Y` and avoids duplicated `by` wording.
- Deterministic diary smoke checks now assert readable audit names, status transitions, and UUID fallback copy.
- No appointment mutation, proposal safety, taskpane, Command Centre, Gemini/AI provider, billing, SMS, restore/reactivation, or supervisor-dashboard work was included.

## Recommended User Review

Residual user review/testing after closeout: none required before continuing.
Ariadne verified the backend audit actor contract, frontend syntax/assets, and deterministic diary Playwright smoke for the readable audit-history section. The change is read-only and does not add a new mutation workflow.

Optional confidence check only, if Yuri happens to be in the live diary after deployment:

1. Setup: hard refresh the live diary and confirm `diary.js?v=100` and `diary.css?v=98` are loaded.
2. Exact UI path: sign in as a dev Admin or normal dev user, open the Diary, and open an existing appointment for editing.
3. Expected collapsed state: the booking modal shows `Audit History`, collapsed by default, below the booking form fields.
4. Expected expansion: click `Audit History`; rows should use readable action/status text and staff labels, or show a clear empty/unavailable/error fallback.
5. Expected actor copy: if backend actor metadata exists, staff names/roles should display instead of raw UUIDs; if only a UUID is available, it should be shortened as `Staff (<first 8 chars>)`.
6. Expected create behaviour: opening an empty slot for a new booking hides `Audit History`.
7. Expected safety: expanding audit history must not change appointment status, waiting-area state, cancellation state, booking details, or proposal confirmation state.
8. Suspicious signs: raw `undefined`, full raw UUIDs in normal rows, confusing action labels, duplicated `by by`, audit history visible on create, edit modal crashes, new mutation controls in audit history, existing save/cancel/delete flow changes, or console errors.
9. Skippable parts: do not retest taskpane, Command Centre, patient file generation, resource administration, drag/resize, recurrence, SMS, billing, AI provider facade, security workflows, or cancelled-appointment review for Sprint 34.
10. Evidence to report: screenshot or short note showing the expanded audit section, readable row text/fallback, loaded asset versions, and any console error or unexpected mutation.

## Not Required Before Moving On

- No manual live UI review is required; the deterministic diary smoke opens the edit modal, expands audit history, and checks readable audit items.
- No database migration or data repair is required; actor display is derived at read time.
- No Word taskpane, Command Centre, GCP/Gemini, Office dialog, resource admin, recurrence, billing, SMS, or security-console action is required for this sprint.

## Known Follow-Up

- Add warning-code or warning-summary persistence later if supervisor review needs proof of warnings confirmed by staff.
- Consider actor display on future proposal-context previews if those become user-facing.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert still appears on GitHub pushes and remains outside Sprint 34.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found both Sprint 34 plan packets and Antigravity's implementation review packet.
- Backend compile check: `.\.venv\Scripts\python.exe -m py_compile app\schemas\appointments.py app\routers\appointments.py tests\test_appointment_audit.py` -> passed.
- Focused audit contract: `.\.venv\Scripts\python.exe -m pytest tests\test_appointment_audit.py -q --tb=short -p no:randomly` -> 15 passed.
- Frontend static check: `node --check docs\diary\diary.js` -> passed.
- Deterministic diary review: `.\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 17 passed.
- Frontend asset version check: `.\.venv\Scripts\python.exe scripts\check_frontend_versions.py` -> passed.
- Diff hygiene: `git diff --check` -> passed.

## Recommended Next Direction

Sprint 35 has been dispatched as a small deterministic-review-friendly slice while Claude's headless session limit recovers: add stable audit-history test hooks and smoke assertions without changing runtime behaviour.

## Previous Closeout - Sprint 33

| Item | Value |
|---|---|
| Batch | Sprint 33: Appointment Proposal Audit/History Foundation |
| Integrated through | Sprint 33 backend confirmed-mutation audit contract and diary read-only audit-history review UI |
| Status | Integrated, pushed, mirrored, audited, and closed |
| Last updated | 2026-06-26 |

## What Changed

- Added an `appointment_audit_log` table and SQLAlchemy model for confirmed appointment mutation history.
- Added `AppointmentAuditAction` plus `AppointmentAuditLogOut` so audit rows are returned through a typed API response.
- Added `GET /api/v1/appointments/{appointment_id}/audit`, practice-scoped and authenticated, returning the confirmed mutation history for one appointment.
- Confirmed appointment create, update, status-change, and soft-cancel/delete paths now write audit rows in the same transaction as the mutation.
- Proposal endpoints remain non-mutating and do not write audit rows; blocked or aborted proposals leave no audit residue.
- Cancellation audit rows preserve `cancellation_reason`; status audit rows preserve before/after status.
- Added `tests/test_appointment_audit.py` with focused coverage for non-mutating proposals, confirmed writes, empty audit history, auth, cross-practice denial, and ordering.
- Added a read-only collapsed `Audit History` section to the diary booking edit modal; it is hidden for new bookings and visible only when editing an existing appointment.
- The diary calls `/appointments/{id}/audit` in live mode, shows loading/empty/unsupported/error states, and simulates backend-shaped audit events in `?smoke=true`.
- Ariadne applied a bounded integration hotfix so the diary UI renders the backend's actual `status_after`, `status_before`, `confirmed_by_user_id`, and lower-case action enum shape; diary assets moved to `diary.css?v=98` and `diary.js?v=100`.
- No taskpane, Command Centre, Gemini/AI provider, billing, SMS, restore/reactivation, broad supervisor dashboard, or direct Bernie execution work was included.

## Recommended User Review

Residual user review/testing after closeout: none required before continuing.
Ariadne verified the backend audit contract, adjacent appointment proposal/status
regression suites, frontend syntax/assets, and deterministic diary Playwright
smoke for the new audit-history affordance. This is mostly infrastructure and a
read-only review surface, with no new direct mutation affordance.

Optional confidence check only, if Yuri happens to be in the live diary after deployment:

1. Setup: hard refresh the live diary and confirm `diary.js?v=100` and `diary.css?v=98` are loaded.
2. Exact UI path: sign in as a dev Admin or normal dev user, open the Diary, and open an existing appointment for editing.
3. Expected collapsed state: the booking modal shows an `Audit History` row, collapsed by default, below the booking form fields.
4. Expected expansion: click `Audit History`; audit rows, `No audit history found`, or an unavailable/error fallback should appear without enabling any write control.
5. Expected create behaviour: open an empty slot to create a new booking; the `Audit History` section should be hidden.
6. Expected safety: expanding audit history must not change appointment status, waiting-area state, cancellation state, booking details, or proposal confirmation state.
7. Suspicious signs: audit history appears on create, edit modal crashes, audit rows show raw `undefined`, the section enables mutation controls, existing save/cancel/delete flow changes, or browser console errors appear.
8. Skippable parts: do not retest taskpane, Command Centre, patient file generation, resource administration, drag/resize, recurrence, SMS, billing, AI provider facade, or security workflows for Sprint 33.
9. Evidence to report: screenshot or short note showing the edit modal audit section, expanded contents/fallback, loaded diary asset versions, and any console error or unexpected mutation.

## Not Required Before Moving On

- No manual live UI review is required; the deterministic diary smoke opens the edit modal, expands audit history, and checks rendered audit items.
- No manual database repair is required; the migration is additive and the audit table is empty until confirmed mutations occur.
- No Word taskpane, Command Centre, GCP/Gemini, Office dialog, resource admin, recurrence, billing, SMS, or security-console action is required for this sprint.

## Known Follow-Up

- Warning-code or warning-summary persistence was intentionally not completed in Sprint 33 because current confirmed mutation endpoints do not receive the prior proposal warning payload. A later richer audit sprint can add explicit `warning_codes`/`confirmed_with_warnings` capture if supervisor review needs it.
- The diary currently displays `confirmed_by_user_id` when no friendly user name is available; a future user-directory join or backend display field can improve readability.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert still appears on GitHub pushes and remains outside Sprint 33.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found both Sprint 33 implementation review packets.
- Backend compile check: `python -m py_compile app\models\appointments.py app\schemas\appointments.py app\routers\appointments.py tests\test_appointment_audit.py` -> passed.
- Focused audit contract: `.\.venv\Scripts\python.exe -m pytest tests\test_appointment_audit.py -q --tb=short -p no:randomly` -> 14 passed.
- Adjacent appointment regressions: `.\.venv\Scripts\python.exe -m pytest tests\test_appointment_status_mutations.py tests\test_appointment_update_proposal.py tests\test_appointment_proposals.py -q --tb=short -p no:randomly` -> 71 passed when rerun serially. A prior parallel pytest launch hit the known Postgres enum creation race and was disregarded.
- Frontend static check: `node --check docs\diary\diary.js` -> passed.
- Deterministic diary review: `.\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 17 passed.
- Frontend asset version check: `.\.venv\Scripts\python.exe scripts\check_frontend_versions.py` -> passed for modified assets.
- Diff hygiene: `git diff --check` -> passed.

## Recommended Next Direction

Sprint 34 has been dispatched as the next Programme 2D readiness slice: appointment audit history readability, focused on safe backend actor-display metadata and diary read-only audit copy. Workers are plan-gated.

## Previous Closeout - Sprint 32

| Item | Value |
|---|---|
| Batch | Sprint 32: No-show/DNA Attendance Outcome Semantics |
| Integrated through | Sprint 32 backend NoShow/DNA status proposal proof suite; diary frontend stood down after existing semantics were verified |
| Status | Integrated, pushed, mirrored, audited, and closed |
| Last updated | 2026-06-26 |

## What Changed

- Added `tests/test_noshow_dna_status_contract.py`, a focused 14-test backend proof suite for NoShow and DNA attendance outcomes.
- Proved `POST /appointments/proposals/status/{id}` for both `NoShow` and `DNA` is non-mutating, safe, confirmation-required, and uses the terminal `proposal` autonomy tier.
- Proved same-status NoShow/DNA proposals block with `already_in_status`.
- Proved re-transitioning away from terminal NoShow/DNA warns with `already_terminal` while leaving the row unchanged.
- Proved NoShow/DNA proposals from a waiting area surface `clears_waiting_area` plus a `waiting_area_cleared` warning without mutating before confirmation.
- Proved confirmed `PATCH /appointments/{id}/status` to NoShow/DNA clears `waiting_area_id` in the database.
- Proved NoShow/DNA appointments do not block the public `/slots` availability API.
- Proved cross-practice NoShow/DNA status proposals return 404.
- No production backend code changed; the existing contract was correct and is now pinned explicitly.
- Antigravity frontend workstream was superseded: its corrected plan was accepted, but the CLI timed out in print mode before submitting implementation. Ariadne verified the current diary already handles NoShow/DNA labels, status options, waiting-area clearing proposals, active-grid exclusion, and Finished-section classification, so no frontend code delta was integrated.
- Added protocol guidance that Antigravity CLI prompts need an explicit `--print-timeout 15m` and that silent returns should be diagnosed with process, worktree, and CLI-log checks before being treated as crashes.

## Recommended User Review

Residual user review/testing after closeout: none required.
Ariadne verified the backend contract, frontend syntax, deterministic diary smoke
harness, and existing NoShow/DNA diary semantics using cheap tool-enabled checks.
Sprint 32 is primarily a contract-proof sprint and intentionally does not add a
new visible user workflow.

Optional confidence check only, if Yuri happens to be in the live diary:

1. Setup: hard refresh the live diary and sign in as a dev Admin or normal dev user.
2. Exact UI path: open an existing appointment, use the status selector, and choose `No Show` or `DNA`.
3. Expected proposal guard: a confirmation/proposal dialog appears before the appointment is mutated.
4. Expected terminal result: after confirming, the appointment should leave the active diary grid and should not remain in Waiting Room or In Consult.
5. Expected review location: the appointment can appear in the Finished section with a clear `No Show` or `DNA` label, depending on the current selected waiting-area tab/filter.
6. Suspicious signs: the appointment mutates before confirmation, remains in active Waiting Room/In Consult, blocks its old slot, shows as an active grid card, or has unclear status text.
7. Skippable parts: do not retest cancellation reasons, cancelled appointment review, resource administration, drag/resize, recurrence, taskpane, Command Centre, billing, SMS, or patient search for Sprint 32.
8. Evidence to report: a screenshot or short note showing the selected status, proposal dialog, final section/filter, and any unexpected active waiting-room/grid residue.

## Not Required Before Moving On

- No manual live UI test is required; the backend proof suite and existing deterministic diary checks cover Sprint 32's intended safety boundary.
- No database migration, data repair, Word taskpane, Command Centre, GCP, Gemini, Office dialog, security-console, or GitHub Pages manual action is required.
- No Antigravity implementation retry is required for Sprint 32; if future user review finds unclear NoShow/DNA copy or missing assertions, dispatch a fresh frontend-only follow-up.

## Known Follow-Up

- Use `--print-timeout 15m` for future Antigravity CLI plan/implementation prompts, and prefer running from the Antigravity worktree/project context.
- Consider a future lightweight frontend assertion specifically for NoShow/DNA terminal labels in the Finished section if those states become more visible in the review surface.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert still appears on GitHub pushes and remains outside Sprint 32.

## Verification

- `python scriptsgent_worktrees.py poll --fetch` -> found Claude's Sprint 32 implementation review packet and Antigravity's corrected plan packet.
- Antigravity CLI diagnosis: `tasklist /FI "IMAGENAME eq agy.exe"` showed no running CLI process; `git status --short --branch` in `EMR4-worktreesntigravity` was clean; latest Antigravity CLI log ended with `Print mode: timed out`, not a crash.
- Backend verification: `python -m pytest tests	est_noshow_dna_status_contract.py -q --tb=short -p no:randomly` -> 14 passed.
- Backend compile check: `python -m py_compile app
outersppointments.py app\schemasppointments.py` -> passed.
- Frontend static check: `node --check docs\diary\diary.js` -> passed.
- Deterministic diary review: `python -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 14 passed.
- Diff hygiene: `git diff --check` -> passed, with only existing CRLF normalization warnings.

## Recommended Next Direction

Yuri resumed sprint automation after Sprint 32. Sprint 33 has been dispatched as
the next Programme 2D readiness slice: appointment proposal audit/history
foundation.

## Previous Closeout - Sprint 30

| Item | Value |
|---|---|
| Batch | Sprint 30: Cancelled Appointment Review Surface |
| Integrated through | Sprint 30 backend cancelled-appointment review tests and diary cancelled-appointments review UI |
| Status | Integrated locally, verified, and pending push/audit/deploy observation |
| Last updated | 2026-06-25 |

## What Changed

- Backend contract coverage now proves `GET /appointments?status=Cancelled` is authenticated, practice-scoped, excludes active appointments, and returns `cancellation_reason` as either the captured note or `null`.
- Diary patient-flow panel now includes a read-only `Cancelled` section with a count badge.
- Cancelled cards show the appointment reason plus `Reason: <cancellation_reason>` when present.
- Cancelled cards are visually distinct with muted/struck styling and a `CXL` badge.
- Cancelled cards intentionally omit edit buttons, link buttons, status/action buttons, links, and selects, so the review surface cannot mutate appointments.
- Smoke mode includes a cancelled fixture with a cancellation reason for tool-enabled browser review.
- Ariadne applied one bounded integration hotfix after browser smoke: cancelled-card details no longer render `undefined undefined` when a practitioner object lacks first/last names, falling back to AHPRA/Room instead.
- Diary cache bust moved to `diary.css?v=97` and `diary.js?v=98`.
- No restore/reactivation, cancellation editing, audit-history table, taskpane, Command Centre, Resource Administration, drag/resize, recurrence, SMS, or billing work was included.

## Recommended User Review

Residual user review/testing after closeout: none required before pausing.
Ariadne verified the backend contract, frontend syntax/assets, and local browser
smoke path covering cancelled-section visibility, reason display, read-only card
controls, asset versions, and console cleanliness.

Optional confidence check only, if Yuri happens to be in the live diary after deployment:

1. Setup: hard refresh the live diary and confirm `diary.js?v=98` and `diary.css?v=97` are loaded.
2. Exact UI path: sign in as a dev Admin or normal dev user, open the Diary, cancel an appointment with a reason if no cancelled appointment already exists, then open the Waiting Room/patient-flow pane.
3. Expected review surface: a `Cancelled` section appears in the right pane with a count matching the currently selected waiting-area tab.
4. Expected card content: the cancelled appointment shows patient name, time/practitioner or AHPRA fallback, appointment reason, `Reason: <your cancellation reason>`, and a `CXL` badge.
5. Expected read-only behaviour: the cancelled card has no edit pencil, no link button, no check-in/start/complete action, no waiting-area select, and clicking it must not open mutation controls.
6. Suspicious signs: missing `Cancelled` section, missing cancellation reason, `undefined undefined` text, any mutation control on a cancelled card, cancelled rows showing in active diary grid slots, or browser console errors.
7. Skippable parts: do not retest taskpane, Command Centre, Resource Administration, booking create/edit, drag/resize, recurrence, SMS, billing, or patient search for Sprint 30.
8. Evidence to report: screenshot or short note showing the cancelled card, selected waiting-area tab, cancellation reason, and any unexpected control or console error.

## Not Required Before Moving On

- No manual database repair or migration is required; Sprint 30 added tests/UI only.
- No Word taskpane, Command Centre, patient-file, Resource Administration, recurrence, duplicate-audit, billing, or clinical workflow review is required.
- No additional Yuri-only test is required because Ariadne's browser smoke verified the read-only cancelled review surface.
- Per Yuri's instruction, sprint automation should pause after Sprint 30 rather than dispatch Sprint 31 automatically.

## Known Follow-Up

- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- GitHub Pages deployment should be observed after push until live diary assets serve `diary.js?v=98` and `diary.css?v=97`.
- Future cancellation review work may add restore/reactivation or supervisor audit history, but Sprint 30 intentionally stayed read-only.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found both Sprint 30 review packets.
- Claude worker verification rerun by Ariadne: `pytest tests\test_cancelled_appointment_review.py tests\test_appointment_status_mutations.py -q --tb=short -p no:randomly` -> 39 passed, with the existing pytest-asyncio deprecation warning.
- Antigravity worker verification rerun by Ariadne: `node --check docs\diary\diary.js`; `python scripts\check_frontend_versions.py`; `git diff --check` -> passed after Ariadne's cache-bust hotfix.
- Browser smoke: local diary served at `http://127.0.0.1:8765/diary/diary.html?smoke=true`; page loaded `diary.css?v=97` and `diary.js?v=98`, opened Waiting Room/patient-flow pane, showed `Cancelled 1`, rendered `Reason: Patient had transport issues`, rendered no buttons/selects/links inside the cancelled card, and logged no browser console errors.

## Recommended Next Direction

Pause after Sprint 30 as requested. When Yuri resumes, choose the next Programme 2B slice deliberately rather than continuing on heartbeat autopilot.

## Previous Closeout - Sprint 29

| Item | Value |
|---|---|
| Batch | Sprint 29: Appointment Cancellation Reason/Note Capture |
| Integrated through | Sprint 29 backend cancellation reason contract and diary cancellation reason capture flow |
| Status | Integrated, pushed, mirrored, audited, and deployed v96 observed |
| Last updated | 2026-06-25 |

## What Changed

- Backend appointments now persist optional `cancellation_reason` on soft-cancelled appointments through a new nullable migration.
- `DELETE /appointments/{id}` accepts an optional JSON body with `cancellation_reason` capped at 500 characters.
- `POST /appointments/proposals/delete/{appointment_id}` accepts the same body and echoes the reason in the non-mutating delete command payload.
- Appointment output/command schemas include `cancellation_reason`, preserving proposal-first safety while retaining receptionist notes for audit/review surfaces.
- Backend regression coverage now exercises persisted reason, null/no-body reason, proposal echo, and too-long reason validation.
- Diary cancel flow now reveals an optional `CANCELLATION REASON` field after the first `Cancel Appointment` click, focuses it, and keeps the first-click whole-appointment warning.
- The reason is included in both the proposal preflight request and final delete request when live mode is active; smoke mode mirrors the same interaction path.
- Abort/cancel paths hide and clear the reason field, reset the button, and leave the appointment intact.
- Diary frontend asset cache-bust moved to `diary.js?v=96` / `diary.css?v=96`.
- No taskpane, Command Centre, patient workflow, Resource Administration, recurrence, drag/resize, or cancellation-review history surface was included.

## Recommended User Review

Residual user review/testing after closeout: none required before the next sprint.
Ariadne verified the backend contract, frontend syntax/assets, and local
browser smoke paths covering first-click warning, reason reveal/focus, entered
reason, proposal dialog, abort/reset, confirm/save, and appointment removal.
The live GitHub Pages deployment is serving v96 assets; no Yuri-only product
test is required before the next sprint.

Optional confidence check only, if Yuri happens to be in the live diary:

1. Setup: after GitHub Pages deploys, hard refresh the live diary and confirm
   `diary.js?v=96` and `diary.css?v=96` are loaded.
2. Exact UI path: sign in as a dev Admin or normal dev user, open the Diary,
   and choose a cancellable appointment.
3. First-click guard: open the appointment editor, click `Cancel Appointment`,
   and confirm the button changes to `Confirm Cancel`, the inline warning says
   the whole appointment will be cancelled, and a `Cancellation reason
   (optional)` field appears with focus.
4. Reason entry: type a short reason such as `Patient rang to cancel`.
5. Proposal guard: click `Confirm Cancel` and confirm a proposal dialog appears
   before any mutation; for waiting-room appointments it should warn that the
   patient will be removed from the waiting area.
6. Abort result: click `Cancel` in the proposal dialog; the appointment should
   remain present, the modal should stay usable, and the cancel button/reason
   field should reset rather than leaving a stuck confirmation state.
7. Confirm result: repeat the cancel path with a reason and click
   `Confirm & Save`; the modal should close, the appointment should be
   cancelled/removed from active diary display, and the Waiting Room pane should
   not retain a stranded patient.
8. Suspicious signs: appointment disappears before the proposal dialog, reason
   field does not appear/focus, abort leaves stale reason text, `Cancel` still
   mutates data, the confirm button stays stuck after abort, or the console
   shows errors.
9. Skippable parts: do not retest taskpane, Command Centre, Resource
   Administration, room/waiting-area admin, drag/resize, recurrence, or patient
   search for Sprint 29.
10. Evidence to report: screenshot or short note with the appointment, status,
    cancellation reason text, action attempted, and any unexpected dialog or
    console error.

## Not Required Before Moving On

- No manual database repair is required; the Sprint 29 migration is additive and nullable.
- No Word taskpane, Command Centre, patient-file, Resource Administration,
  room/waiting-area admin, recurrence, duplicate-audit, or clinical workflow
  review is required for this sprint.
- No additional Yuri-only test is required because Ariadne's Chrome/CDP smoke
  covered the warning, reason reveal/focus, abort/reset, proposal, confirm, and
  removal path.

## Known Follow-Up

- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- GitHub Pages is serving v96; no deployment propagation follow-up remains for Sprint 29.
- A later cancellation-polish sprint may add a proposal/review history surface
  that displays stored cancellation reasons to supervisors or audit users.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found both Sprint 29 review packets.
- Claude worker verification, rerun by Ariadne with the integration venv: `alembic upgrade head`; `py_compile app\models\appointments.py app\schemas\appointments.py app\routers\appointments.py`; `pytest tests\test_appointment_status_mutations.py -q --tb=short -p no:randomly`; `git diff --check` -> 34 passed.
- Antigravity worker verification, rerun by Ariadne: `node --check docs\diary\diary.js`; `git diff --check` -> passed.
- Integrated-tree backend verification: `alembic upgrade head`, `py_compile app\models\appointments.py app\schemas\appointments.py app\routers\appointments.py`, and `pytest tests\test_appointment_status_mutations.py -q --tb=short -p no:randomly` -> 34 passed, with the existing pytest-asyncio deprecation warning.
- Integrated-tree frontend verification: `node --check docs\diary\diary.js`, `python scripts\check_frontend_versions.py`, and `git diff --check` -> passed; local/head diary v96 and deployed v95 before push.
- Browser smoke: local diary served at `http://127.0.0.1:8765/diary/diary.html?smoke=true`; page identity `EMR - Diary`, 4 smoke appointments, booking modal opened from a visible appointment.
- Browser cancellation-reason smoke: first click revealed the reason field, focused it, changed the button to `Confirm Cancel`, and showed the whole-appointment warning.
- Browser confirm smoke: entering `Patient rang to cancel`, then confirming through the proposal dialog, closed the modal and removed the appointment from the active smoke diary.
- Browser abort smoke: entering a reason, opening the proposal dialog, then clicking dialog `Cancel` left the appointment intact, reset `Cancel Appointment`, hid the reason field, and cleared the stale reason text.

## Recommended Next Direction

1. Continue Programme 2B with the next receptionist-visible appointment mutation slice if no Yuri-only checks remain.
2. Keep using browser/CDP smoke before leaving any UI review to Yuri; Sprint 29 confirms cancellation reason capture can be verified tool-first.

## Previous Closeout - Sprint 28

| Item | Value |
|---|---|
| Batch | Sprint 28: Cancellation/Delete Proposal Safety |
| Integrated through | Sprint 28 backend cancel/delete proposal contract and diary cancel proposal preflight flow |
| Status | Integrated, pushed, mirrored, audited, and deployed v95 observed |
| Last updated | 2026-06-25 |

## Previous Closeout - Sprint 27

| Item | Value |
|---|---|
| Batch | Sprint 27: Visible Diary Mouse Drag/Resize Affordances |
| Integrated through | Sprint 27 backend mouse-equivalent update conflict tests and diary mouse drag/resize proposal flow |
| Status | Integrated, pushed, mirrored, audited, and closed |
| Last updated | 2026-06-25 |

## What Changed

- Backend conflict coverage now proves confirmed `PUT /appointments/{id}` rejects mouse-equivalent drag move, resize into a next booking, and cross-practitioner conflict writes while allowing adjacent moves.
- Diary appointment cards now expose visible mouse affordances: grab cursor on cards, top/bottom resize handles, dashed ghost preview, 15-minute snapping, cross-column drag target detection, and proposal-gated drop handling.
- Mouse move/resize reuses the same non-mutating update-proposal preflight path as keyboard move/resize: blocked proposals stop writes, warning proposals require `Confirm & Save`, and confirmed changes then use the normal appointment update path.
- Ariadne applied two bounded integration hotfixes from tool-enabled review: delayed ghost creation until the pointer moves beyond a 3px threshold, and restored the Resource Administration access-denied paragraph font size accidentally dropped in the worker CSS diff.
- Diary frontend asset cache-bust moved to `diary.js?v=94` / `diary.css?v=94`.
- No schema migration, taskpane, Command Centre, patient workflow, Waiting Room, Resource Administration behaviour, recurrence, or direct-write bypass was included.

## Recommended User Review

Residual user review/testing after closeout: none required before the next sprint.
Ariadne verified the mouse interaction paths locally with browser/CDP against the
smoke diary fixture, including real browser mouse events for drag preview,
warning proposal, confirm-save, resize preview, and confirm-save. Backend conflict
coverage provides the blocked-conflict safety check for the confirmed write path.

Optional confidence check only, if Yuri happens to be in the live diary:

1. Setup: after GitHub Pages deploys, hard refresh the live diary and confirm
   `diary.js?v=94` and `diary.css?v=94` are loaded.
2. Exact UI path: sign in as a dev Admin or normal dev user, open the Diary,
   and hover over an appointment card body/name area.
3. Expected drag affordance: the cursor should read as draggable/grabbable, a
   dashed preview should appear while dragging more than a tiny click movement,
   and releasing on a warning-only move should show the existing proposal
   warning before any save.
4. Expected resize affordance: drag the bottom edge of a card; a dashed preview
   should resize in 15-minute increments and the proposal warning/confirm path
   should appear before the duration changes.
5. Suspicious signs: card moves without a proposal check, a click opens a drag
   preview without meaningful movement, resize shrinks below 15 minutes, the
   status dropdown changes when dragging the card body, or the browser console
   shows errors.
6. Skippable parts: do not retest taskpane, Command Centre, Resource
   Administration, Waiting Room, recurrence, or patient search for Sprint 27.
7. Evidence to report: screenshot or short note with the appointment, action
   attempted, expected time/duration, and any unexpected dialog or console error.

## Not Required Before Moving On

- No database migration or manual data repair is required.
- No Word taskpane, Command Centre, patient-file, Resource Administration,
  Waiting Room, recurrence, duplicate-audit, or clinical workflow review is
  required for this sprint.
- No additional Yuri-only test is required because browser/CDP covered the
  real mouse-input paths that were previously hard for Ariadne to synthesize.

## Known Follow-Up

- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The live GitHub Pages deployment must still be observed after push to confirm
  Pages serves v94; this is a deployment observation, not a manual product test.
- Future UX polish may add a short in-product hint for mouse/keyboard move and
  resize controls once staff workflow feedback accumulates.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found both Sprint 27 review packets.
- Claude worker verification: `pytest tests/test_appointment_conflicts.py -q --tb=short -p no:randomly` on `claude/current` -> 12 passed.
- Antigravity worker verification: `node --check docs\diary\diary.js`, `git diff --check origin/master...HEAD`, and `npm run validate-all` -> passed.
- Integrated-tree backend verification: `.\.venv\Scripts\python.exe -m pytest tests\test_appointment_conflicts.py tests\test_appointment_update_proposal.py -q --tb=short -p no:randomly` -> 43 passed, with the existing pytest-asyncio deprecation warning.
- Integrated-tree frontend verification: `node --check docs\diary\diary.js`, `git diff --check`, and `npm run validate-all` -> passed; manifest valid, production npm audit clean, and asset check accepted v94.
- Browser smoke: local diary served at `http://127.0.0.1:8765/diary/diary.html?smoke=true`; page identity `EMR4 - Diary`, grid rendered 4 smoke appointments, no console warnings/errors.
- Browser/CDP drag smoke: real mouse events on a visible appointment created one dashed ghost preview, snapped the preview down by one slot, opened the proposal warning dialog, and `Confirm & Save` moved the card from `top: 331px` to `top: 361px`.
- Browser/CDP resize smoke: real mouse events on the bottom resize handle created one dashed ghost preview with increased height, opened the proposal warning dialog, and `Confirm & Save` persisted the card height to `88px`.
- Browser smoke confirmed status controls were ignored as drag targets and that ghost previews were removed after drop.

## Recommended Next Direction

1. Push Sprint 27, observe GitHub Pages serving v94, realign mirrors, and audit.
2. Continue Programme 2B with the next receptionist-visible appointment mutation slice: likely cancellation/reschedule reason capture or an appointment proposal/review history surface.
3. Keep running browser/CDP smoke before leaving any UI review to Yuri; this sprint proved the tool path can cover real mouse-input affordances.

## Previous Closeout - Sprint 26

| Item | Value |
|---|---|
| Batch | Sprint 26: Move/Resize Proposal Flow |
| Integrated through | Sprint 26 backend move/resize proposal tests and diary keyboard move/resize proposal flow |
| Status | Integrated, pushed, mirrored, audited, deployed v92 observed, and Yuri physical-keyboard smoke passed |
| Last updated | 2026-06-25 |

## What Changed

- Backend proposal coverage now includes four diary move/resize scenarios for `POST /appointments/proposals/update/{appointment_id}`: resize into next booking blocked, move across practitioner columns into a conflict blocked, adjacent slots safe, and resize-shrink safe.
- The backend proposal route itself was unchanged; the sprint hardens tests around the existing non-mutating contract.
- Diary appointment cards now support proposal-gated keyboard move/resize intent: `Alt+ArrowUp/Down` shifts start time by 15 minutes and `Alt+ArrowLeft/Right` adjusts duration by 15 minutes with a 15-minute floor.
- Move/resize proposal handling uses the existing blocked/warning dialog path before any write, then applies safe/confirmed updates through the normal appointment update path.
- Ariadne hotfixed smoke/runtime gaps found during tool-enabled review: practitioner ID fallback for visible resource columns, diary-date fallback for smoke appointments without `appointment_date`, smoke-cache persistence before reload, existing active-card restoration helper reuse, and capture/nested status-control key routing.
- Diary frontend asset cache-bust moved to `diary.js?v=92` / `diary.css?v=92`.
- No schema migration, taskpane, Command Centre, patient demographics, Resource Administration, Waiting Room layout, recurrence, or visual drag-handle work was included.

## Recommended User Review

Residual user review/testing after push/deploy: complete. Yuri confirmed the
live physical-keyboard shortcut smoke passed after Pages served v92. Ariadne
verified the backend contract, frontend syntax/assets, and local smoke rendering;
the remaining real OS/browser `Alt+Arrow` path was confirmed manually.

Completed Yuri-only check:

1. Setup: open the live diary after deployment and hard refresh. Confirm the
   live page serves `diary.js?v=92` and `diary.css?v=92`.
2. Exact UI path: sign in as a normal dev user or admin, open the Diary, click
   once on an appointment card body/name area rather than the status dropdown.
3. Expected move result: press `Alt+ArrowDown`; if the target slot is safe or
   warning-only, the existing proposal dialog should appear before mutation.
   Cancel should leave the card unchanged; Confirm should move it down by 15
   minutes and keep the card selected/highlighted after reload.
4. Expected block result: choose or create an appointment where a 15-minute move
   or duration increase would overlap another booking, then press the relevant
   shortcut. The dialog should say `Action Blocked`; closing it should leave the
   appointment unchanged.
5. Expected resize result: press `Alt+ArrowRight` on a safe appointment to
   increase duration by 15 minutes, and `Alt+ArrowLeft` to shrink duration. It
   should never shrink below 15 minutes.
6. Suspicious signs: the browser navigates back/forward, the inline status
   dropdown changes instead of move/resize, no proposal dialog appears before a
   risky write, the card moves without confirmation when warnings/blocks exist,
   or the active highlight is lost after reload.
7. Skippable parts: do not test Resource Administration, taskpane, Command
   Centre, patient-file generation, recurrence, or drag-handle UX for Sprint 26.
8. Evidence to report: screenshot of any unexpected dialog/state plus the exact
   card, shortcut pressed, and before/after time/duration.

## Not Required Before Moving On

- No database migration or manual data repair is required.
- No Word taskpane, Command Centre, patient-file, Resource Administration,
  recurrence, duplicate-audit, or clinical workflow review is required for this
  sprint.
- No security or dependency remediation is required; production
  `npm audit --omit=dev` remains clean and Bandit medium+/high checks passed.

## Known Follow-Up

- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The existing GitHub Dependabot moderate alert remains visible on push; it is
  the already-known security queue item and not a Sprint 26 blocker.
- A future UX sprint should consider visible move/resize affordances or a help
  hint for keyboard shortcuts; Sprint 26 intentionally kept the UI slice small.

## Verification

- `.\scripts\check_backend.ps1` -> passed; compileall, Bandit medium+/high scan, and whitespace check all green.
- `.\.venv\Scripts\python.exe -m py_compile app\routers\appointments.py app\schemas\appointments.py` -> passed.
- `.\.venv\Scripts\python.exe -m pytest tests/test_appointment_update_proposal.py -q --tb=short -p no:randomly` -> passed; 31 passed, 1 existing pytest-asyncio deprecation warning.
- `node --check docs\diary\diary.js` -> passed.
- `npm run validate-all` before Ariadne hotfixes -> passed; manifest valid, production npm audit clean, frontend asset/version check passed. Worker-local diary assets were v87 and deployed Pages was still v86 before push.
- `npm run validate-all` after Ariadne hotfixes -> passed; local diary assets are v92, HEAD before closeout was v87, deployed Pages before push was still v86.
- `npm run check-assets` after push/mirror realignment -> passed; deployed GitHub Pages diary assets now report `diary.js?v=92` and `diary.css?v=92`.
- `git diff --check` -> passed.
- Local browser smoke page loaded via `http://127.0.0.1:8787/diary/diary.html?smoke=true` and confirmed `diary.js?v=92` is requested.
- Browser smoke found and Ariadne fixed two move/resize smoke data issues and one nested status-control key-routing issue before final verification.
- Browser automation could not conclusively synthesize a physical `Alt+Arrow`
  chord; the residual Yuri-only test above covers that specific real-keyboard path.

## Recommended Next Direction

1. Complete the short v92 physical-keyboard live diary smoke above.
2. If it passes, continue Programme 2B with the next appointment mutation affordance slice: a clearer visible move/resize UX or a proposal review/history surface, depending on which feels most useful after the keyboard smoke.
3. Keep using browser/Chrome smoke checks before leaving any UI review to Yuri.

## Previous Closeout - Sprint 25

## Previous Closeout - Sprint 23

| Item | Value |
|---|---|
| Batch | Sprint 23: Room Default Waiting-Area Invariant |
| Integrated through | Sprint 23 waiting-area invariant integration |
| Status | Integrated, pushed, mirrored, audited, and awaiting optional live Admin smoke |
| Last updated | 2026-06-24 |

## What Changed

- Backend resource-admin room writes now enforce the active-room default waiting-area invariant where possible: room creation auto-selects the lowest-order compatible active waiting area, explicit null on active rooms resolves to a fallback, and reactivating a room fills a fallback.
- Archiving a waiting area now reassigns active rooms that used it to the next compatible active fallback, or clears the default only when no compatible active waiting area remains.
- Resource Administration room cards now show explicit/fallback default waiting-area labels, room forms preselect active defaults/fallbacks, and smoke-mode waiting-area archive behavior mirrors reassignment.
- Diary frontend asset cache-bust moved to `diary.js?v=84` / `diary.css?v=84`.
- No schema migration, taskpane, Command Centre, patient, appointment booking, or clinical-document changes were made.

## Recommended User Review

Residual user review/testing after push/deploy: one short live diary smoke is
useful because this sprint changes the Resource Administration UI and the real
Office dialog/GitHub Pages surface can reveal deployment or browser-state issues
that static checks cannot. Confirm `diary.js?v=84` is loaded, open Admin ->
Resource Administration, and check that room default waiting areas are visible,
preselected in the room form, and remain coherent after archiving a waiting area.

Detailed steps for Yuri-only review:

1. Hard refresh the live diary/Office-dialog surface and confirm `diary.js?v=84`
   and `diary.css?v=84` are loaded.
2. Sign in as an Admin or PracticeOwner-capable user.
3. Open `Admin` -> `Resource Administration` -> `Rooms`.
4. Confirm every active room card displays an explicit or fallback default
   waiting area when active waiting areas exist.
5. Edit one room, confirm the default waiting-area dropdown is preselected, then
   cancel and confirm no state changed.
6. Edit the same room again, change the default waiting area, save, close and
   reopen Resource Administration, and confirm the saved default persists.
7. Open `Waiting Areas`, archive a non-critical active waiting area, and confirm
   affected rooms now show another compatible active fallback or no default only
   when no active fallback exists.
8. Reopen the right-side Waiting Room pane and confirm its tabs match active
   waiting areas and exclude archived areas.
9. Skip non-admin denial if the taskpane cannot be resized or logged out safely;
   report that as an accessibility blocker rather than spending time fighting
   the UI.
10. Report whether v84 loaded, whether defaults displayed/preselected correctly,
   whether archive reassignment looked coherent, and screenshots for anything
   suspicious.

## Not Required Before Moving On

- No database migration or manual data repair is required for dev data; existing null active-room defaults are repaired on create/update/archive paths where compatible active areas exist.
- No Word taskpane, Command Centre, patient-file, appointment create/edit, status, duplicate-audit, or clinical workflow review is required for this sprint.
- No security or dependency remediation is required; production `npm audit --omit=dev` remains clean and Bandit medium+/high checks passed.

## Known Follow-Up

- The frontend fallback helper operates over the waiting areas currently loaded for the active location. The backend invariant is authoritative and includes compatible practice-wide areas; consider a later UI/API refinement if practice-wide waiting areas become a real configuration path.
- The broad `python -m pytest tests/` run timed out during Ariadne verification without a failure report. Sprint-targeted resource-admin/waiting-room tests passed; investigate broad-suite runtime/hanging separately rather than blocking this narrow integration.
- Taskpane logout is currently hard to reach when the pane cannot be widened:
  Yuri could not test non-admin Resource Administration denial because the
  logout button sits at the extreme right and the resize affordance was blocked
  by an hourglass cursor. Add a future UI/accessibility task to make logout and
  role-switching reachable without relying on taskpane width.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.

## Verification

- `.\scripts\check_backend.ps1` -> passed; compileall, Bandit medium+/high scan, and whitespace check all green.
- `.venv\Scripts\python.exe -m pytest tests\test_diary_resource_admin.py tests\test_waiting_room.py -q --tb=short -p no:randomly` -> passed; 61 passed, 1 existing pytest-asyncio deprecation warning.
- `node --check docs\diary\diary.js` -> passed.
- `npm run validate-all` in `EMR4 Sidebar` -> passed; manifest valid, production npm audit clean, frontend asset/version check passed. Local/HEAD diary assets are v84; deployed Pages was still v83 before push.
- `git diff --check` -> passed.
- Worker-reported full backend suite on Claude branch passed before integration; Ariadne's post-merge broad full-suite attempt timed out without a failure report and is recorded as a follow-up rather than a blocker.

## Recommended Next Direction

1. After Pages serves v84, run the short live Admin smoke above; if clean, proceed to the next product-growth sprint.
2. Plan the next architecture/dev-tooling optimisation sprint around automating the browser smoke checks Ariadne has been doing manually.
3. Keep the room/waiting-area model steady: every active room should have an active default area where possible, with display-order-zero as the natural fallback.

## Sprint 15 Review Harness - Waiting Room Check-In Operations

Use this section after the Sprint 15 backend and diary UI worker branches are
reviewed and integrated. It is a user-review harness, not evidence that the
implementation has already landed.

### Design Guardrails

- A **Waiting Area** is a named physical place where arrived patients wait.
- A **Room** is a physical consult/procedure room. It may have a default waiting
  area, but it is not itself a waiting area.
- A **Practitioner** is the bookable clinician/resource for the appointment.
- **Attendance status** is same-day workflow: Booked, Arrived/Waiting,
  InConsult, Completed, Cancelled, NoShow, or DNA.
- **Booking confirmation** is the patient's intention/response to attend and is
  separate from attendance status.
- **Patient identity** should be described as **Verified** or **Unverified**.
  Do not use "Confirmed" for identity; reserve it for booking attendance intent
  or legacy appointment status only when clearly qualified.
- Bernie may execute deterministic, low-risk operational actions with audit and
  reporting, such as an unambiguous check-in/status correction. Slot selection,
  booking choice, rescheduling, externally consequential actions, clinical
  actions, and ambiguous identity cases still require staff confirmation.
- Any future request for "stacking" must specify the surface:
  **Waiting Room cards** inside the side panel, or **diary appointment blocks**
  on the room/time grid. These are different layout problems and should not be
  changed together by default.

### Manual User Review Checklist

1. Pull latest, restart the backend, rerun `python seed.py`, and hard refresh
   the deployed/local diary surface. Confirm the diary loads `diary.js?v=68`.
2. Open today's diary and the Waiting Room panel. Confirm Expected Today cards
   are compact, chronological by appointment time, and readable without looking
   like the main diary grid's overlapping appointment blocks.
3. Confirm ordinary diary appointment blocks on the room/time grid still use
   their existing time geometry. The Sprint 15 Waiting Room work must not
   introduce appointment-block stacking/cascade changes in the main diary grid.
4. Check in an appointment from Expected Today without manually selecting a
   waiting area when the appointment's room has a default. Confirm the patient
   appears in the correct/default Waiting Area section and the appointment
   detail shows that area consistently.
5. Check in an appointment while explicitly selecting a non-default waiting
   area. Confirm the explicit choice wins over the room default and survives a
   refresh.
6. If the UI supports changing the waiting area after arrival, move an arrived
   patient to another waiting area. Confirm the patient moves sections without
   changing practitioner, room, appointment time, or patient identity state.
7. Move a checked-in patient through Waiting/Arrived -> InConsult -> Completed.
   Confirm Waiting Room sections update immediately and after refresh:
   Waiting/Arrived patients are active in their area, InConsult patients appear
   only in the in-consult section, and Completed patients appear only in the
   finished/terminal section if that section is displayed.
8. Set terminal statuses Cancelled, NoShow, and DNA on appointments that had a
   waiting area. Confirm they do not remain incorrectly visible in active
   Waiting Area sections. If the backend preserves `waiting_area_id` for
   history, the active UI must still filter terminal statuses out of active
   waiting lists.
9. Test a practice/day with exactly one active waiting area. Confirm the UI does
   not show a clipped, fake, or confusing tab strip; the single area should read
   as the natural context rather than a broken multi-tab control.
10. Test an Unverified/provisional appointment if available. Check-in may be
    allowed, but the UI should not imply that arrival verified the patient
    identity. The displayed language should keep identity verification separate
    from attendance.

### Backend / API Spot Checks

Use these only after getting a staff JWT and real IDs from the dev database or
browser network panel. Route names may need the `/api/v1` prefix depending on
the caller base URL.

```powershell
$base = "http://localhost:8001/api/v1"
$headers = @{ Authorization = "Bearer <JWT>" }
$appointmentId = "<appointment-uuid>"
$waitingAreaId = "<waiting-area-uuid>"

# Explicit check-in to a waiting area.
Invoke-RestMethod -Method Patch `
  -Uri "$base/appointments/$appointmentId/status" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ status = "Arrived"; waiting_area_id = $waitingAreaId } | ConvertTo-Json)

# Default/no explicit waiting area path. Verify this follows the integrated
# backend contract: either room default assignment or existing assignment
# preservation, as specified by the Sprint 15 backend worker.
Invoke-RestMethod -Method Patch `
  -Uri "$base/appointments/$appointmentId/status" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ status = "Arrived" } | ConvertTo-Json)

# Terminal status should not leave the patient visible in active waiting areas.
Invoke-RestMethod -Method Patch `
  -Uri "$base/appointments/$appointmentId/status" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ status = "Completed"; waiting_area_id = $null } | ConvertTo-Json)
```

API review expectations:

- Cross-practice or inactive `waiting_area_id` values are rejected.
- Explicit `waiting_area_id = null` clears the appointment's waiting area when
  the contract allows clearing.
- Moving to InConsult, Completed, Cancelled, NoShow, or DNA does not strand the
  patient in active waiting-area feeds.
- Status transitions do not link a provisional patient to a real patient record,
  do not change booking confirmation state, and do not alter practitioner/room
  assignment unless a separate explicit endpoint says so.

### Sprint 15 Review Questions For Codex/Orchestrator

- Did Claude's backend branch make terminal-status clearing explicit, or does it
  preserve `waiting_area_id` for history while filtering in the waiting-room
  endpoint/UI?
- Did Antigravity keep Expected Today compacting scoped to Waiting Room cards
  only, with no diary-grid appointment geometry changes?
- Does the single-waiting-area state read naturally, or should the next UI slice
  replace tabs with a simple heading/count when only one active area exists?
- Are there audit hooks yet for Bernie-style direct check-in/status execution?
  If not, keep Bernie write tools at proposal/report level or limit execution to
  the already validated route behaviour.

---

## Sprint 16 Review Harness - Location-Aware Diary Foundations

Use `orchestration/location_diary_view_review.md` after the Sprint 16 backend
and diary UI worker branches are reviewed and integrated. This closeout pointer
is intentionally brief; the harness file owns the vocabulary table, backend
integration review, diary UI review, Bernie tool vocabulary, manual user review,
API spot checks, and merge gate.

Codex/orchestrator should specifically report whether:

- Backend location scoping keeps practice tenancy separate from physical
  location scoping.
- Rooms, waiting areas, diary templates, rosters, and appointments are
  associated with a physical location or have a deliberate safe fallback.
- The diary UI exposes the active physical location when there is more than one
  site, while the one-location case stays uncluttered.
- Diary page/view groups are treated as screen layout inside a location, not as
  extra locations.
- Waiting Room panels/cards, main diary appointment blocks, booking slots, and
  status controls remain separate review surfaces.
- Bernie tool language requires explicit location/resource context before any
  future write proposal.

---

## Sprint 17 Review Harness - Command/Proposal Workflow Retrofit

Use `orchestration/command_proposal_review.md` after the Sprint 17 backend and
diary UI worker branches are reviewed and integrated. This closeout pointer is
intentionally brief; the harness file owns the command/proposal vocabulary,
integration checklist, expected response classes, and PowerShell snippets.

Codex/orchestrator should specifically report whether:

- Proposal endpoints are non-mutating and return typed commands for staff
  confirmation.
- Safe create proposals still require staff confirmation before the diary is
  written.
- Conflict proposals return `safe=false`, `autonomy_tier=blocked`, and a stable
  `appointment_conflict` block without creating an appointment.
- Break overlaps and provisional patients return warnings, not blocks, and stay
  confirmable by staff.
- The diary UI treats blocked proposals as hard stops and warning proposals as
  explicit confirmation paths.
- Booking slots, diary grid cells, Waiting Room cards, appointment status, and
  patient identity are described as separate surfaces.
- No Sprint 17 work starts a Bernie runtime, bypasses normal appointment route
  validation, or creates a privileged agent-only write path.

### Sprint 17 Integrated Outcome

Integrated submissions:

- Claude: existing-appointment update/status proposal contracts.
- Antigravity: diary new-booking modal create-proposal preflight.
- Codex/Banach: command proposal review harness and API snippets.

Verification run after integration:

```powershell
.venv\Scripts\python.exe -m py_compile app\routers\appointments.py app\schemas\appointments.py tests\test_appointment_update_proposal.py tests\test_appointment_proposals.py
node --check docs\diary\diary.js
.venv\Scripts\python.exe -m pytest tests\test_appointment_update_proposal.py tests\test_appointment_proposals.py tests\test_appointment_status_mutations.py tests\test_booking_create_edit.py tests\test_break_overlap_contract.py -q --tb=short -p no:randomly
git diff --check
```

Result: `75 passed`; JS syntax and whitespace checks clean.

Manual user review:

- Confirm diary assets load at `diary.js?v=72`.
- Create a normal non-conflicting booking and confirm it saves.
- Try an overlapping booking and confirm the modal blocks the save before writing.
- Create a booking that crosses a break and confirm the warning appears, then `Confirm & Save` writes it.
- Create a provisional-patient booking and confirm the warning appears, then `Confirm & Save` writes it.
- Confirm the proposal warning/error copy is readable in the booking modal and does not disturb the main diary grid or Waiting Room panel.

User review result: positive after hotfix `d081834`; break-crossing warning now appears for the visible break path.
