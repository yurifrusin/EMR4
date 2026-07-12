# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Closeout Completeness Rule

A sprint or sprint batch is not closed until the integrated work is committed,
pushed to `origin/master`, and the integration worktree is clean. If publication
is intentionally deferred, the status must say `local-only`, `pending commit`,
or `pending push`, and the closeout must name the blocker or Yuri instruction
that caused the deferral.

Every closeout entry should record:

- verification commands and results;
- the integration commit SHA once committed;
- push result or explicit push blocker;
- final `git status --short --branch`;
- whether the sprint engine is continuing or paused, and why.

## Current Closeout

| Item | Value |
|---|---|
| Batch | S8 Receptionist Workflow Implementation |
| Integrated through | Fable conduction, DeepSeek W1/W2 implementation, W3 executable review gates, Antigravity GO verdict, and Sol integration |
| Status | Published to `origin/master` and `origin/handoff/current` |
| Commit | `f8b354cf` |
| Push | `master` and `handoff/current` pushed successfully |
| Final status | `## master...origin/master` after S8 closeout publication |
| Last updated | 2026-07-13 |

## S8 What Changed

- Hardened taskpane Diary launch resolution, error guidance, and bounded retry.
- Added inline terminal-reason guidance, webview date fallback, same-day search,
  and read-only reason/notes preview to the diary.
- Passed both DeepSeek candidates through W3 and the executable acceptance gate.
- Integrated Antigravity's corrected GO consumer verdict.
- Enabled local DeepCode candidate commits without push/integration authority.

## S8 Verification

```powershell
.venv\Scripts\python.exe -m pytest review\test_taskpane_diary_launch.py review\test_diary_reason_code_affordance.py review\test_diary_date_picker_fallback.py review\test_diary_day_search.py review\test_diary_note_preview.py -q
.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py review\test_diary_selection_preservation.py -q
.venv\Scripts\python.exe -m pytest review\test_diary_graphql_practitioner_switch.py review\test_diary_deprecation_consumer.py -q
.venv\Scripts\python.exe -m pytest tests\test_ariadne_deepcode_pty.py tests\test_ariadne_deepcode_mailbox_settings.py tests\test_ariadne_deepcode_adapter_settings.py -q
node --check docs\diary\diary.js
.venv\Scripts\python.exe scripts\check_frontend_versions.py
git diff --check
```

Result: product focused `28 passed`; smoke/selection `142 passed`; adjacent
GraphQL/deprecation `15 passed`; DeepCode permission contract `53 passed`;
syntax, versions, executable reviews, and whitespace checks passed.

Sprint engine state: continuing to the next Conductor boundary after publication. No
deployment, production, external-client, provider, memory/RAG, H15/trove,
schema, database, new-write-authority, or product-policy gate is opened.

---

## Previous Closeout - S7 Review Acceptance Contract Audit

S7 added the executable cross-boundary review acceptance gate and was published
through `1ff7dd9a`, with publication-state correction through `559bc0ac`.
Evidence: `docs/ariadne-s7-review-acceptance-closeout.md`.

---

## Previous Closeout - S6 Diary Contract Repair

S6 restored the diary browser suite to 139/139, repaired the AHPRA runtime
`ReferenceError`, updated GraphQL practitioner-directory contracts, and proved
the DeepSeek Pro Conductor fallback. It was published through `b1292c49` to
`origin/master` and `origin/handoff/current`. Full evidence is in
`docs/emr4-s6-diary-contract-repair-closeout.md`.

---

## Previous Closeout - Sprint 290

| Item | Value |
|---|---|
| Batch | Sprint 289 View-Model Contract Cross-Reference |
| Integrated through | Ariadne cross-reference packet with Claude, Antigravity, and DeepSeek reviews |
| Status | Published to `origin/master` and `origin/handoff/current` |
| Commit | `15baca10` |
| Push | `master` and `handoff/current` pushed successfully |
| Final status | `## master...origin/master` before Sprint 290 local edits |
| Last updated | 2026-07-09 |

## Sprint 289 What Changed

- Added
  `docs/bernie-ui-derived-state-view-model-contract-cross-reference.{json,md}`.
- Added
  `tests/test_bernie_ui_view_model_contract_cross_reference.py`.
- Built one reviewer-facing map across D3 inventory, D4 preflight, D5
  completion review, evidence consolidation, and API-spine boundary.
- Recorded reviewer questions for tracing display flags, route-intercepted
  evidence labels, signed REST command authority, and separate approval points.
- Claude and Antigravity both blocked an initial Markdown/JSON goal mismatch;
  the fix was integrated before closeout.
- DeepSeek passed the corrected packet and suggested cosmetic key
  normalization; the key sets were normalized before closeout.
- Kept D5 expansion, route delivery, frontend JavaScript changes,
  provider/live-provider wiring, Access AI, memory/RAG/GraphRAG, H15/H-series,
  historical diary runtime inputs, GraphQL delivery/readiness, external
  clients, confirm payload/write behavior changes, model-to-database writes,
  deployment, and production readiness closed.

## Sprint 289 Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_view_model_contract_cross_reference.py tests\test_bernie_ui_post_d5_next_slice_inventory.py tests\test_sprint287_next_block_reorientation.py tests\test_bernie_ui_dag_d5_first_slice_completion_review.py tests\test_sprint_closeout_protocol.py -q
git diff --check
```

Result: final targeted closeout suite passed before publication; Sprint 289 was
published at `15baca10`.

Sprint engine state after Sprint 289 publication: stopped for Yuri direction. No
deployment, production, readiness, telemetry, external-client, write, provider,
memory, H15/trove, mutation, subscription, D5 expansion, or field-expansion gate
is opened.

---

## Previous Closeout - Sprint 288

| Item | Value |
|---|---|
| Batch | Sprint 288 Post-D5 Next-Slice Inventory |
| Integrated through | Ariadne inventory with Claude, Antigravity, and DeepSeek PASS reviews |
| Status | Published to `origin/master` and `handoff/current`; worktree clean |
| Commit | `4ccea66a15c41b92f7a91a5afc180667ddd04cc4` |
| Push | `master` and `handoff/current` pushed successfully |
| Final status | `## master...origin/master` |
| Last updated | 2026-07-09 |

## Sprint 288 What Changed

- Added
  `docs/bernie-ui-derived-state-post-d5-next-slice-inventory.{json,md}`.
- Added
  `tests/test_bernie_ui_post_d5_next_slice_inventory.py`.
- Recorded Yuri's approval for Sprints 288-289 as a non-runtime Bernie UI
  derived-state post-D5 checkpoint block.
- Inventoried three possible non-D5 next-slice candidates:
  `review_copy_safety_matrix`, `view_model_contract_cross_reference`, and
  `ordinary_prompt_release_gate_mapping`.
- Recommended Sprint 289 as `view_model_contract_cross_reference` because it
  is the lowest-risk docs/tests-only map across D3, D4, D5, and API-spine
  evidence.
- Recorded Claude strategic gate PASS, Antigravity product/workflow PASS, and
  DeepSeek static gate PASS review artifacts.
- Kept D5 expansion, route delivery, frontend JavaScript changes,
  provider/live-provider wiring, Access AI, memory/RAG/GraphRAG, H15/H-series,
  historical diary runtime inputs, GraphQL delivery/readiness, external
  clients, confirm payload/write behavior changes, and model-to-database writes
  closed.

## Sprint 288 Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_post_d5_next_slice_inventory.py tests\test_sprint287_next_block_reorientation.py tests\test_bernie_ui_dag_d5_first_slice_completion_review.py tests\test_sprint_closeout_protocol.py -q
git diff --check
```

Result: post-D5 inventory/related protocol suite `22 passed`; whitespace check
passed with known CRLF notices for touched orchestration Markdown files.

Sprint engine state: continued to Sprint 289. No deployment, production,
readiness, telemetry, external-client, write, provider, memory, H15/trove,
mutation, subscription, D5 expansion, or field-expansion gate was opened.

---

## Previous Closeout - Sprint 287

| Item | Value |
|---|---|
| Batch | Sprint 287 Next Block Reorientation |
| Integrated through | Ariadne non-runtime next-block recommendation packet and guard tests |
| Status | Published to `origin/master` and `handoff/current`; worktree clean |
| Commit | `ed012044` |
| Push | `master` and `handoff/current` pushed successfully |
| Final status | `## master...origin/master` |
| Last updated | 2026-07-09 |

## Sprint 287 What Changed

- Added
  `docs/sprint-287-next-block-reorientation.{json,md}`.
- Added
  `tests/test_sprint287_next_block_reorientation.py`.
- Recommends pausing the practitioner-directory GraphQL default-on track before
  deployment, production, telemetry, or global readiness work.
- Uses the D5 completion review without reopening D5 expansion.
- Recommends Sprints 288-289 only as a documentation/tests-only Bernie UI
  derived-state non-D5 checkpoint block, and only if Yuri agrees.
- Keeps GraphQL readiness/deployment/telemetry, D5 expansion, provider/live
  provider, Access AI, memory/RAG/GraphRAG, H15/H-series, historical diary
  runtime inputs, external clients, confirm payload changes, write behavior
  changes, and model-to-database writes closed.

## Sprint 287 Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_sprint287_next_block_reorientation.py tests\test_bernie_ui_dag_d5_first_slice_completion_review.py tests\test_sprint286_publication_state_correction.py tests\test_sprint_closeout_protocol.py -q
git diff --check
```

Result: next-block/D5/publication-state/protocol suite `18 passed`; whitespace
check passed with known CRLF notices for touched orchestration Markdown files.

Sprint engine state: stopped for Yuri approval before Sprint 288. No deployment,
production, readiness, telemetry, external-client, write, provider, memory,
H15/trove, mutation, subscription, D5 expansion, or field-expansion gate was
opened.

---

## Previous Closeout - Sprint 286

| Item | Value |
|---|---|
| Batch | Sprint 286 Publication State Correction |
| Integrated through | Ariadne stale Sprint 285 publication wording correction and guard test |
| Status | Published to `origin/master` and `handoff/current`; worktree clean |
| Commit | `7e2dd6e7` |
| Push | `master` and `handoff/current` pushed successfully |
| Final status | `## master...origin/master` |
| Last updated | 2026-07-09 |

## Sprint 286 What Changed

- Corrected `AGENTS.md`, `orchestration/sprint_closeout.md`, and
  `orchestration/integration_log.md` so Sprint 285 no longer appeared pending
  after it had already been pushed.
- Added `tests/test_sprint286_publication_state_correction.py` to guard the
  current Sprint 285 closeout section against stale pending commit/push wording.

## Sprint 286 Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_sprint286_publication_state_correction.py tests\test_sprint_closeout_protocol.py -q
git diff --check
```

Result: publication-state/protocol suite `8 passed`; whitespace check passed
with known CRLF notices for touched orchestration Markdown files.

Sprint engine state: continued to Sprint 287 next-block reorientation. No
deployment, production, readiness, telemetry, external-client, write, provider,
memory, H15/trove, mutation, subscription, or field-expansion gate was opened.

---

## Previous Closeout - Sprint 285

| Item | Value |
|---|---|
| Batch | Sprint 285 Default-On Monitoring Boundary |
| Integrated through | Ariadne monitoring/readiness-boundary packet and guard tests |
| Status | Published to `origin/master` and `handoff/current`; worktree clean |
| Commit | `2c6cd5146b1c8c9538873f4a3f2e3a2970191077` |
| Push | `master` and `handoff/current` pushed successfully |
| Final status | `## master...origin/master` |
| Last updated | 2026-07-09 |

## Sprint 285 What Changed

- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-default-on-monitoring-boundary.{json,md}`.
- Added
  `tests/test_practitioner_directory_office_addin_graphql_default_on_monitoring_boundary.py`.
- Defined observable-without-new-instrumentation evidence for the default-on
  Office add-in practitioner selector path.
- Recorded operator watchpoints for selector-empty reports, GraphQL-specific
  logout loops, fallback warnings, leakage reports, and rollback use.
- Kept production observability, deployment validation, external-client policy,
  global GraphQL readiness, broader security review, and telemetry privacy
  review as blockers before any readiness claim.
- Added no telemetry endpoint, metrics system, runtime override, server config,
  or readiness flag.

## Sprint 285 Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_office_addin_graphql_default_on_monitoring_boundary.py tests\test_practitioner_directory_office_addin_graphql_default_on_rollback_packet.py tests\test_sprint_closeout_protocol.py -q
node --check docs\diary\diary.js
git diff --check
```

Result: monitoring/rollback/protocol suite `19 passed`; `node --check` and
whitespace checks passed.

Sprint engine state: paused before any deployment or production readiness claim.
No deployment, production, readiness, telemetry, external-client, write,
provider, memory, H15/trove, mutation, subscription, or field-expansion gate was
opened.

---

## Previous Closeout - Sprint 284

| Item | Value |
|---|---|
| Batch | Sprint 284 Default-On Rollback Packet |
| Integrated through | Ariadne rollback packet and guard tests |
| Status | Published to `origin/master` and `handoff/current`; worktree clean |
| Commit | `16eed7ed5fbf47d978712f752be164610335d8b2` |
| Push | `master` and `handoff/current` pushed successfully |
| Final status | `## master...origin/master` |
| Last updated | 2026-07-09 |

## Sprint 284 What Changed

- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-default-on-rollback-packet.{json,md}`.
- Added
  `tests/test_practitioner_directory_office_addin_graphql_default_on_rollback_packet.py`.
- Defined the exact bounded rollback action if needed:
  change only `docs/diary/diary.js` from
  `const ENABLE_GRAPHQL_PRACTITIONERS = true;` to
  `const ENABLE_GRAPHQL_PRACTITIONERS = false;`.
- Recorded rollback triggers and post-rollback validation commands.
- Explicitly forbade destructive rollback expansion such as deleting the
  GraphQL dependency, unmounting `/api/v1/graphql`, removing the resolver,
  changing backend auth/error handling, removing the REST route, or claiming
  broader readiness.
- Did not roll back the runtime now; the current default-on path remains
  active for the one approved Office add-in diary practitioner selector.
- DeepSeek blocked the first packet because post-rollback validation listed
  current default-on baseline tests; the fix replaced those commands with
  rollback-specific validation and added a static one-line rollback simulator.

## Sprint 284 Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_office_addin_graphql_default_on_rollback_packet.py tests\test_practitioner_directory_office_addin_graphql_switch_runtime.py tests\test_practitioner_directory_office_addin_graphql_default_on_local_backend_smoke.py tests\test_sprint_closeout_protocol.py -q
node --check docs\diary\diary.js
git diff --check
```

Result: rollback/support/protocol suite `22 passed`; `node --check` and
whitespace checks passed.

Sprint engine state: continued to Sprint 285 monitoring/readiness-boundary
packet. No deployment, production, readiness, telemetry, external-client, write,
provider, memory, H15/trove, mutation, subscription, or field-expansion gate was
opened.

---

## Previous Closeout - Sprint 283

| Item | Value |
|---|---|
| Batch | Sprint 283 Default-On Local Backend Smoke |
| Integrated through | Ariadne local backend fake-data smoke and bounded evidence |
| Status | Published to `origin/master` and `handoff/current`; worktree clean |
| Commit | `7fe7565e6c33c17d17dc5547c0f372ac00fdb4c0` |
| Push | `master` and `handoff/current` pushed successfully |
| Final status | `## master...origin/master` |
| Last updated | 2026-07-09 |

## Sprint 283 What Changed

- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-default-on-local-backend-smoke.{json,md}`.
- Added
  `tests/test_practitioner_directory_office_addin_graphql_default_on_local_backend_smoke.py`.
- Extracted the committed Office add-in GraphQL query from
  `docs/diary/diary.js` and posted it through the local FastAPI `TestClient`
  `/api/v1/graphql` route with authenticated fake staff context.
- Proved fake-data practice scoping, active-only filtering, default-location
  projection, sensitive canary absence, and no appointment audit writes without
  browser route interception.
- Kept the default-on scope as exactly one Office add-in diary practitioner
  selector consumer with REST fallback retained.
- DeepSeek returned PASS for the local backend smoke review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint283-default-on-local-backend-smoke.md`.

## Sprint 283 Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_office_addin_graphql_default_on_local_backend_smoke.py tests\test_practitioner_directory_graphql_resolver.py tests\test_practitioner_directory_office_addin_graphql_switch_runtime.py tests\test_sprint_closeout_protocol.py -q
node --check docs\diary\diary.js
git diff --check
```

Result: local backend smoke/support/protocol suite `36 passed`; `node --check`
and whitespace checks passed.

Sprint engine state: continued to Sprint 284 rollback packet. No deployment,
production, readiness, telemetry, external-client, write, provider, memory,
H15/trove, mutation, subscription, or field-expansion gate was opened.

---

## Previous Closeout - Sprint 282

| Item | Value |
|---|---|
| Batch | Sprint 282 Default-On Publication Status |
| Integrated through | Ariadne publication status snapshot and guard tests |
| Status | Published to `origin/master` and `handoff/current`; worktree clean |
| Commit | `514970f656eb55991c3c0def62bfd6d522ea3f74` |
| Push | `master` and `handoff/current` pushed successfully |
| Final status | `## master...origin/master` |
| Last updated | 2026-07-09 |

## Sprint 282 What Changed

- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-default-on-publication-status.{json,md}`.
- Added
  `tests/test_practitioner_directory_office_addin_graphql_default_on_publication_status.py`.
- Corrected Sprint 281 closeout publication metadata inside the previous
  closeout entry, proving `master` and `handoff/current` were pushed at
  `d3dda16e657a4eb51b845a509c5cff071f530c43`.
- Preserved the default-on scope as exactly one Office add-in diary practitioner
  selector consumer with REST fallback retained.
- DeepSeek returned PASS for publication-boundary review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint282-default-on-publication-status.md`.

## Sprint 282 Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_office_addin_graphql_default_on_publication_status.py tests\test_sprint_closeout_protocol.py -q
git diff --check
```

Result: publication/status suite `11 passed`; whitespace check passed with the
known CRLF notices for touched orchestration Markdown files.

Sprint engine state: continued to Sprint 283, a narrow non-intercepted local
backend fake-data check. No deployment, production, readiness, telemetry,
external-client, write, provider, memory, H15/trove, mutation, subscription, or
field-expansion gate was opened.

---

## Previous Closeout - Sprint 281

| Item | Value |
|---|---|
| Batch | Sprint 281 Practitioner Directory Office Add-in GraphQL Default-On Runtime |
| Integrated through | Ariadne default-on runtime flip with route-intercepted evidence and DeepSeek PASS review |
| Status | Published to `origin/master` and `handoff/current`; worktree clean |
| Commit | `d3dda16e657a4eb51b845a509c5cff071f530c43` |
| Push | `master` and `handoff/current` pushed successfully |
| Final status | `## master...origin/master` |
| Last updated | 2026-07-09 |

## Sprint 281 What Changed

- Recorded Yuri's default-on approval in
  `docs/api-spine/practitioner-directory-office-addin-graphql-default-on-approval-packet.{json,md}`.
- Flipped only `docs/diary/diary.js`:
  `ENABLE_GRAPHQL_PRACTITIONERS = true`.
- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-default-on-runtime.{json,md}`.
- Expanded `review/test_diary_graphql_practitioner_switch.py` to prove the
  committed default-on GraphQL success path, approved query variables,
  one-shot REST fallback, GraphQL HTTP 401 logout/no-REST-fallback behavior,
  `practice=null`, `defaultLocation=null`, and sensitive-canary non-rendering.
- Updated static guards for the approved default-on posture.
- Recorded DeepSeek PASS review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint281-office-addin-graphql-default-on-runtime.md`.
- Antigravity was invoked but timed out. Claude was stood down because no API
  contract, resolver, backend route, schema, or auth model changed.

## Sprint 281 Verification

```powershell
.venv\Scripts\python.exe -m pytest review\test_diary_graphql_practitioner_switch.py -q
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_office_addin_graphql_default_on_approval_packet.py tests\test_practitioner_directory_office_addin_graphql_switch_route_intercepted.py tests\test_practitioner_directory_office_addin_graphql_switch_runtime.py tests\test_practitioner_directory_office_addin_graphql_mock_contract.py tests\test_practitioner_directory_graphql_release_boundary.py tests\test_sprint_closeout_protocol.py -q
node --check docs\diary\diary.js
git diff --check
```

Result: route-intercepted browser evidence `14 passed`; runtime/support/protocol
suite `46 passed`; `node --check` and whitespace checks passed.

Sprint engine state: continuing, but only into post-default-on safety evidence
or rollback/monitoring packets. No deployment, production, readiness,
telemetry, external-client, write, provider, memory, H15/trove, mutation,
subscription, or field-expansion gate is opened.

---

## Previous Closeout - Sprint 280

## Sprint 280 What Changed

- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-default-on-approval-packet.{json,md}`.
- Added
  `tests/test_practitioner_directory_office_addin_graphql_default_on_approval_packet.py`.
- The packet decision is
  `pending_yuri_approval_for_office_addin_graphql_practitioner_selector_default_on`.
- No runtime code was changed; `docs/diary/diary.js` remains
  `ENABLE_GRAPHQL_PRACTITIONERS = false`.
- The packet defines the exact approval template, single-consumer default-on
  scope, REST fallback requirements, required post-approval runtime tests, and
  must-remain-false gates.
- Claude and Antigravity were stood down for Sprint 280 because this is a
  docs/tests-only approval packet with no API contract, resolver, backend route,
  schema, auth model, or runtime UX change. DeepSeek final review is recorded in
  `orchestration/agent_inbox/codex/review-deepseek-sprint280-office-addin-graphql-default-on-packet.md`.

## Sprint 280 Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_office_addin_graphql_default_on_approval_packet.py tests\test_practitioner_directory_office_addin_graphql_switch_route_intercepted.py tests\test_practitioner_directory_office_addin_graphql_switch_runtime.py tests\test_sprint_closeout_protocol.py -q
git diff --check
```

Result: packet/support/protocol suite `25 passed`; whitespace check passed.

Sprint engine state: paused for Yuri approval before any default-on runtime
change or Office add-in GraphQL traffic by default. Yuri approved the packet on
2026-07-09, enabling Sprint 281's single-consumer runtime flip.

---

## Previous Closeout - Sprint 279

## Sprint 279 What Changed

- Added `review/test_diary_graphql_practitioner_switch.py` with
  route-intercepted Playwright evidence for the Office add-in diary practitioner
  selector GraphQL switch.
- Proved the committed default-off runtime sends zero GraphQL requests and uses
  `GET /api/v1/practice/practitioners?activeOnly=true&limit=200`.
- Proved the enabled path only through a test-harness-served copy of `diary.js`,
  covering `FORBIDDEN`, `BAD_USER_INPUT`, transport failure, `practice: null`,
  and `defaultLocation: null`.
- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-switch-route-intercepted-evidence.{json,md}`
  plus static guard tests.
- Recorded DeepSeek PASS review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint279-office-addin-graphql-switch-route-intercepted.md`.
- Antigravity was invoked for Office add-in UX review but timed out. Claude was
  stood down because no API contract, backend route, schema, resolver, or auth
  model changed.

## Sprint 279 Verification

```powershell
.venv\Scripts\python.exe -m pytest review\test_diary_graphql_practitioner_switch.py -q
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_office_addin_graphql_switch_route_intercepted.py tests\test_practitioner_directory_office_addin_graphql_switch_runtime.py tests\test_practitioner_directory_office_addin_graphql_consumer_switch_approval_packet.py tests\test_practitioner_directory_office_addin_graphql_mock_contract.py tests\test_practitioner_directory_graphql_release_boundary.py tests\test_sprint_closeout_protocol.py -q
node --check docs\diary\diary.js
git diff --check
```

Result: route-intercepted browser evidence `6 passed`; runtime/support/protocol
suite `48 passed`; `node --check` and whitespace checks passed.

Sprint engine state: continuing, but default-on Office add-in GraphQL traffic
requires a separate approval packet before runtime enablement. Next recommended
work is Sprint 280, a docs/tests-only default-on decision packet or explicit
pause for Yuri approval.

---

## Previous Closeout - Sprint 278

## Sprint 278 What Changed

- Recorded Yuri's switch approval in
  `docs/api-spine/practitioner-directory-office-addin-graphql-consumer-switch-approval-packet.{json,md}`.
- Updated `docs/diary/diary.js` with `ENABLE_GRAPHQL_PRACTITIONERS = false`,
  the exact approved `Query.practice.practitioners` query, a GraphQL practitioner
  directory loader, and REST fallback through the existing route.
- Preserved `roleLabel` and `active` in normalized practitioner rows while the
  selector still renders the existing display name/location shape.
- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-switch-runtime.{json,md}`.
- Added
  `tests/test_practitioner_directory_office_addin_graphql_switch_runtime.py`.
- Added Antigravity UX PASS review artifact at
  `orchestration/agent_inbox/antigravity/antigravity-sprint278-office-addin-graphql-switch-runtime.md`.
- Added DeepSeek static/security PASS review artifact at
  `orchestration/agent_inbox/codex/review-deepseek-sprint278-office-addin-graphql-switch-runtime.md`.
- Updated `orchestration/bernie_release_gates.md` to name `docs/diary/diary.js`
  as the actual Office add-in diary selector surface.

Boundary:

- GraphQL switch is implemented but default-off; no GraphQL traffic is sent by
  default.
- No backend route/schema change, server config endpoint, telemetry endpoint,
  readiness flag change, write/audit write, provider/memory/H15/trove path,
  mutation, subscription, deployment, production, external-client exposure,
  default-on switch, or field expansion.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_office_addin_graphql_switch_runtime.py tests\test_practitioner_directory_office_addin_graphql_consumer_switch_approval_packet.py tests\test_practitioner_directory_office_addin_graphql_mock_contract.py tests\test_practitioner_directory_graphql_release_boundary.py tests\test_sprint_closeout_protocol.py -q
node --check docs\diary\diary.js
```

Result: Sprint 278 runtime/support/protocol suite `43 passed`; `node --check`
passed.

Implementation commit: integrating commit for Sprint 278.

Sprint engine state: continuing only to route-intercepted evidence for
default-off REST behavior and enabled-path GraphQL fallback; no default-on,
telemetry, deployment, production, or readiness claim.

---

## Previous Closeout - Sprint 277

| Item | Value |
|---|---|
| Batch | Sprint 277 Practitioner Directory Office Add-in GraphQL Consumer Switch Approval Packet |
| Integrated through | Ariadne approval packet/tests with Antigravity and DeepSeek PASS reviews |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

## Sprint 277 What Changed

- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-consumer-switch-approval-packet.json`.
- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-consumer-switch-approval-packet.md`.
- Added
  `tests/test_practitioner_directory_office_addin_graphql_consumer_switch_approval_packet.py`.
- Added Antigravity consumer/UX PASS review artifact at
  `orchestration/agent_inbox/antigravity/antigravity-sprint277-office-addin-graphql-consumer-switch-approval.md`.
- Added DeepSeek static/release PASS review artifact at
  `orchestration/agent_inbox/codex/review-deepseek-sprint277-office-addin-graphql-consumer-switch-approval.md`.
- Updated `orchestration/bernie_release_gates.md` with the Office add-in GraphQL
  switch gate.

Boundary:

- Decision remains `pending_yuri_switch_approval`.
- No `taskpane.js` edit, live GraphQL traffic, feature gate, backend route/schema
  change, server config endpoint, telemetry endpoint, readiness flag change,
  write/audit write, provider/memory/H15/trove path, mutation, subscription,
  deployment, production, external-client exposure, or field expansion.
- If later approved, the approval expires on `2026-08-06` and authorizes only a
  default-off internal staff practitioner-selector switch.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_office_addin_graphql_consumer_switch_approval_packet.py tests\test_practitioner_directory_office_addin_graphql_mock_contract.py tests\test_practitioner_directory_office_addin_graphql_fetch_wrapper_test_plan.py tests\test_practitioner_directory_graphql_release_boundary.py tests\test_sprint_closeout_protocol.py -q
```

Result: Sprint 277 approval-packet/support/protocol suite `43 passed`.

Implementation commit: integrating commit for Sprint 277.

Sprint engine state: stopped for Yuri switch approval before any Office add-in
taskpane runtime implementation or live GraphQL traffic.

---

## Previous Closeout - Sprint 276

| Item | Value |
|---|---|
| Batch | Sprint 276 Practitioner Directory Office Add-in GraphQL Mock Contract Scaffold |
| Integrated through | Ariadne scaffold/tests with Antigravity and DeepSeek PASS reviews |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

## Sprint 276 What Changed

- Added `tests/practitioner_directory_office_addin_graphql_mock_contract.py`.
- Added
  `tests/test_practitioner_directory_office_addin_graphql_mock_contract.py`.
- Added
  `tests/practitioner_directory_office_addin_graphql_mock_contract/DRIFT.md`.
- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-mock-contract-scaffold.json`.
- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-mock-contract-scaffold.md`.
- Updated the Sprint 275 test plan to set
  `projection_drift_behavior=discard`.
- Added Antigravity UX/test PASS review artifact at
  `orchestration/agent_inbox/antigravity/antigravity-sprint276-office-addin-graphql-mock-contract-scaffold.md`.
- Added DeepSeek static/gate PASS review artifact at
  `orchestration/agent_inbox/codex/review-deepseek-sprint276-office-addin-graphql-mock-contract-scaffold.md`.

Boundary:

- Python tests-only scaffold under `tests/`.
- No `taskpane.js` edit, app import, live GraphQL fetch, hidden feature flag,
  runtime shadow fetch, telemetry endpoint, backend route/schema change,
  readiness flag change, write/audit write, provider/memory/H15/trove path,
  mutation, subscription, deployment, production, external-client exposure, or
  field expansion.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_office_addin_graphql_mock_contract.py tests\test_practitioner_directory_office_addin_graphql_fetch_wrapper_test_plan.py tests\test_practitioner_directory_office_addin_graphql_consumer_proposal.py tests\test_practitioner_directory_graphql_release_boundary.py tests\test_sprint_closeout_protocol.py -q
```

Result: Sprint 276 scaffold/plan/proposal/release/protocol suite `43 passed`.

Implementation commit: integrating commit for Sprint 276.

Sprint engine state: paused for separate consumer switch approval before any
Office add-in taskpane runtime implementation or live GraphQL traffic.

---

## Previous Closeout - Sprint 275

| Item | Value |
|---|---|
| Batch | Sprint 275 Practitioner Directory Office Add-in GraphQL Fetch-wrapper Test Plan |
| Integrated through | Ariadne plan/tests with Antigravity and DeepSeek PASS reviews |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

## Sprint 275 What Changed

- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-fetch-wrapper-test-plan.json`.
- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-fetch-wrapper-test-plan.md`.
- Added
  `tests/test_practitioner_directory_office_addin_graphql_fetch_wrapper_test_plan.py`.
- Added Antigravity UX/test PASS review artifact at
  `orchestration/agent_inbox/antigravity/antigravity-sprint275-office-addin-graphql-fetch-wrapper-test-plan.md`.
- Added DeepSeek static/gate PASS review artifact at
  `orchestration/agent_inbox/codex/review-deepseek-sprint275-office-addin-graphql-fetch-wrapper-test-plan.md`.
- Defined mocked test cases for success, empty list, HTTP `401`, GraphQL
  `FORBIDDEN`, GraphQL `BAD_USER_INPUT`, `practice = null`,
  `defaultLocation = null`, projection drift, expired/disabled gate, and future
  REST fallback.

Boundary:

- No `taskpane.js` edit, hidden feature flag, runtime shadow fetch, telemetry
  endpoint, backend route/schema change, readiness flag change, write/audit
  write, provider/memory/H15/trove path, mutation, subscription, deployment,
  production, external-client exposure, or field expansion.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_office_addin_graphql_fetch_wrapper_test_plan.py tests\test_practitioner_directory_office_addin_graphql_consumer_proposal.py tests\test_practitioner_directory_graphql_internal_consumer_harness.py tests\test_practitioner_directory_graphql_release_boundary.py tests\test_sprint_closeout_protocol.py -q
```

Result: Sprint 275 plan/proposal/harness/release/protocol suite `55 passed`.

Implementation commit: integrating commit for Sprint 275.

Sprint engine state: pause before runtime taskpane implementation unless Yuri
approves a separate consumer switch gate; non-runtime mocked client-contract
scaffolding remains possible.

---

## Previous Closeout - Sprint 274

| Item | Value |
|---|---|
| Batch | Sprint 274 Practitioner Directory Office Add-in GraphQL Consumer Proposal |
| Integrated through | Ariadne proposal/tests with Antigravity and DeepSeek PASS reviews |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

## Sprint 274 What Changed

- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-consumer-proposal.json`.
- Added
  `docs/api-spine/practitioner-directory-office-addin-graphql-consumer-proposal.md`.
- Added
  `tests/test_practitioner_directory_office_addin_graphql_consumer_proposal.py`.
- Added Antigravity consumer/UX PASS review artifact at
  `orchestration/agent_inbox/antigravity/antigravity-sprint274-office-addin-graphql-consumer-proposal.md`.
- Added DeepSeek API/static PASS review artifact at
  `orchestration/agent_inbox/codex/review-deepseek-sprint274-office-addin-graphql-consumer-proposal.md`.
- Proved the proposal stays proposal-only: no `taskpane.js` GraphQL query,
  hidden feature flag, runtime shadow fetch, taskpane code change, route change,
  schema change, readiness flag change, deployment/production claim,
  external-client exposure, provider/memory/H15/trove path, write/audit write,
  mutation, subscription, telemetry endpoint, or field expansion.

Worker mix:

- Antigravity via `agy.exe`: PASS; reviewed the Office add-in consumer/UX
  surface, error copy, comparison posture, fallback behavior, privacy, and future
  feature-flag posture.
- DeepSeek via direct Codex `deepseek-worker`: PASS; reviewed API/static
  boundaries, especially HTTP `401` versus GraphQL `extensions.code`, no hidden
  switch, exact projection, and no latency/readiness claims.
- Claude: intentionally stood down because Sprint 274 did not change the API
  contract, resolver shape, or runtime auth/error model.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_office_addin_graphql_consumer_proposal.py tests\test_practitioner_directory_graphql_internal_consumer_harness.py tests\test_practitioner_directory_graphql_release_boundary.py tests\test_sprint_closeout_protocol.py -q
```

Result: Sprint 274 proposal/harness/release/protocol suite `48 passed`.

Implementation commit: integrating commit for Sprint 274.

Sprint engine state: continuing to Sprint 275 only as a blocked-by-default
Office add-in GraphQL fetch-wrapper test plan; no runtime traffic without a
separate consumer switch approval.

---

## Previous Closeout - Sprint 273

| Item | Value |
|---|---|
| Batch | Sprint 273 Practitioner Directory GraphQL Internal Consumer Harness |
| Integrated through | Ariadne harness with Claude and DeepSeek PASS reviews |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

## Sprint 273 What Changed

- Added `tests/graphql_practitioner_consumer_harness.py`.
- Added `tests/test_practitioner_directory_graphql_internal_consumer_harness.py`.
- Added
  `docs/api-spine/practitioner-directory-graphql-internal-consumer-harness.json`.
- Added
  `docs/api-spine/practitioner-directory-graphql-internal-consumer-harness.md`.
- Added Claude API/contract review artifact at
  `orchestration/agent_inbox/claude/claude-sprint273-graphql-internal-consumer-harness-review.md`.
- Added DeepSeek security/static review artifact at
  `orchestration/agent_inbox/codex/review-deepseek-sprint273-graphql-internal-consumer-harness.md`.
- Proved the test-only internal consumer harness handles approved success,
  HTTP 401, GraphQL `BAD_USER_INPUT`, GraphQL `FORBIDDEN`,
  `practice(id:) = null`, sensitive-field rejection, no idempotency-key
  requirement or behavior change, default/max/offset pagination, role/default
  active scope, practice scoping, inactive/cross-practice location nulls, no
  audit writes, and forbidden runtime-path imports.

Worker mix:

- Claude via `scripts\drive_agent_headless.py` and the Claude CLI: PASS;
  reviewed the API/contract boundary and pushed the harness toward reusable
  consumer-contract helpers instead of duplicated resolver tests.
- DeepSeek via direct Codex `deepseek-worker`: PASS; reviewed security/static
  boundaries and added pitfalls for GraphQL error-code shape, null-variable
  serialization, no UI/schema changes, and forbidden runtime paths.
- Antigravity via `agy.exe`: not used in Sprint 273 because this sprint was a
  backend/test-only harness. Antigravity is reserved for Sprint 274's Office
  add-in consumer/UX proposal where it has a distinct artifact or veto surface.

Boundary:

- Test-only harness under `tests/`.
- No Office add-in runtime switch, production UI wiring, runtime schema change,
  global readiness snapshot change, provider/Access AI invocation,
  memory/RAG/GraphRAG wiring, H15/H-series runtime import, historical
  diary/local_data import, external patient-client exposure, write authority,
  audit write, mutation, subscription, deployment claim, or production
  readiness claim.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_graphql_internal_consumer_harness.py tests\test_practitioner_directory_graphql_release_boundary.py tests\test_sprint_closeout_protocol.py -q
```

Result: Sprint 273 harness/release/protocol suite `40 passed`.

Implementation commit: integrating commit for Sprint 273.

Sprint engine state: continuing to Sprint 274 Office add-in GraphQL consumer
proposal with Antigravity consumer/UX review.

---

## Previous Closeout - Sprint 272 Approval

| Item | Value |
|---|---|
| Batch | Sprint 272 Practitioner Directory GraphQL Release-Boundary Approval |
| Integrated through | Ariadne approval-slip update after Yuri go/no-go |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

## Sprint 272 Approval Update

- Yuri approved the Sprint 272 GraphQL release-boundary packet with expiry
  `2026-08-06`.
- Updated
  `docs/api-spine/practitioner-directory-graphql-release-boundary.json` with
  `decision=release_boundary_approved_for_internal_staff_consumer_development`,
  `approved_contract_commit=d4ed14d3`, `go_no_go_acknowledged=true`, and
  `approval_expires_on=2026-08-06`.
- Set only `internal_consumer_development=true`; all global readiness,
  deployment, production, external-client, write, provider, memory, H15/trove,
  mutation, subscription, and field-expansion gates remain closed.
- Updated `docs/api-spine/practitioner-directory-graphql-release-boundary.md`,
  `tests/test_practitioner_directory_graphql_release_boundary.py`,
  `orchestration/bernie_release_gates.md`, `AGENTS.md`, and the integration log.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_graphql_release_boundary.py tests\test_practitioner_directory_graphql_contract_hardening.py tests\test_sprint_closeout_protocol.py -q
```

Implementation commit: integrating commit for Sprint 272 approval update.

Sprint engine state: continuing only into bounded internal staff consumer
development, or pause for a new approval packet before any expansion.

---

## Previous Closeout - Sprint 272 Packet

| Item | Value |
|---|---|
| Batch | Sprint 272 Practitioner Directory GraphQL Release-Boundary Packet |
| Integrated through | Ariadne approval-packet drafting with DeepSeek PASS review |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

## Sprint 272 What Changed

- Added
  `docs/api-spine/practitioner-directory-graphql-release-boundary.json`.
- Added
  `docs/api-spine/practitioner-directory-graphql-release-boundary.md`.
- Added `tests/test_practitioner_directory_graphql_release_boundary.py`.
- Added the practitioner-directory GraphQL release-boundary gate section to
  `orchestration/bernie_release_gates.md`.
- Integrated DeepSeek Sprint 272 PASS review.
- Converted the release decision into a proposed approval surface before the
  subsequent Yuri approval update.

Worker mix:

- DeepSeek via direct Codex `deepseek-worker`: PASS; confirmed the Sprints
  268-271 evidence chain supports a scoped internal-staff consumer proposal, but
  required an explicit Yuri approval slip before treating it as ready. The
  packet now records that pause.

Boundary:

- No runtime code changed in Sprint 272.
- No internal consumer development is authorized yet.
- No GraphQL mutations, subscriptions, global readiness snapshot change,
  provider/Access AI invocation, memory/RAG/GraphRAG wiring, H15/H-series
  runtime import, historical diary/local_data import, external patient-client
  exposure, write authority, audit write, deployment claim, or production
  readiness claim.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_graphql_release_boundary.py tests\test_practitioner_directory_graphql_contract_hardening.py tests\test_sprint_closeout_protocol.py -q
```

Result: Sprint 272 release-boundary/protocol suite `23 passed`.

Implementation commit: integrating commit for Sprint 272.

Sprint engine state: paused for Yuri go/no-go on the Sprint 272 release-boundary
packet.

---

## Previous Closeout - Sprint 271

| Item | Value |
|---|---|
| Batch | Sprint 271 Practitioner Directory GraphQL Contract Hardening |
| Integrated through | Ariadne hardening with DeepSeek PASS review |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

## Sprint 271 What Changed

- Added
  `docs/api-spine/practitioner-directory-graphql-contract-hardening.json`.
- Added
  `docs/api-spine/practitioner-directory-graphql-contract-hardening.md`.
- Added `tests/test_practitioner_directory_graphql_contract_hardening.py`.
- Added runtime SDL parity checks for the approved practitioner GraphQL slice.
- Added token-budget negative tests for both `graphqlHealth` and the
  `practice.practitioners` resolver path.
- Recorded that the current 500-token budget preempts 501-alias attempts before
  the alias limiter is reached; the alias limiter remains configured.
- Recorded that the current shallow practitioner graph cannot structurally
  exceed depth six, and that any future deeper field must add a true depth
  negative test before sprint closeout.
- Broadened blocked-readiness snapshot checks.
- Added cross-document `must_remain_false` consistency checks across shell,
  resolver, and hardening evidence.
- Updated DeepSeek Sprint 271 review artifact from pending to PASS with
  integrated recommendations.

Worker mix:

- DeepSeek via direct Codex `deepseek-worker`: PASS; recommended documenting the
  depth-test limitation, resolving alias/token ambiguity honestly, testing the
  practitioner resolver path under token pressure, broadening readiness checks,
  and closing the pending worker-review marker. Those recommendations were
  integrated.

Boundary:

- No new runtime field beyond `graphqlHealth`, `Query.practice(id)`, and
  `Practice.practitioners(activeOnly, limit, offset)`.
- No GraphQL mutations, subscriptions, global readiness snapshot change,
  provider/Access AI invocation, memory/RAG/GraphRAG wiring, H15/H-series
  runtime import, historical diary/local_data import, external patient-client
  exposure, write authority, audit write, deployment claim, or production
  readiness claim.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_graphql_contract_hardening.py tests\test_practitioner_directory_graphql_resolver.py tests\test_practitioner_directory_graphql_runtime_shell.py tests\test_sprint_closeout_protocol.py tests\test_api_spine_practitioner_directory_graphql_resolver_ownership_plan.py tests\test_api_spine_practitioner_directory_rest_graphql_drift_contract.py tests\test_api_spine_practitioner_directory_sdl_resolution_proposal.py -q
```

Result: Sprint 271 hardening/API-spine suite `81 passed`.

Implementation commit: integrating commit for Sprint 271.

Sprint engine state: continuing to Sprint 272 practitioner GraphQL
release-boundary packet.

---

## Previous Closeout - Sprint 270

| Item | Value |
|---|---|
| Batch | Sprint 270 Practitioner Directory GraphQL Resolver |
| Integrated through | Ariadne resolver implementation with DeepSeek PASS review |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

## Sprint 270 What Changed

- Added `Query.practice(id: ID)` to the Strawberry schema; it returns the
  viewer practice context by default and returns `null` for a mismatched
  practice ID without querying or leaking the other practice.
- Added the single approved
  `Practice.practitioners(activeOnly: Boolean = true, limit: Int = 50, offset: Int = 0)`
  field.
- The resolver calls only
  `app/services/practice/practitioner_directory_read.py::list_practitioner_directory`.
- GraphQL projection matches the REST slice:
  `id`, `displayName`, `roleLabel`, `active`, and
  `defaultLocation { id, name }`.
- Added explicit GraphQL bounds checks for `limit` and `offset`.
- Mapped inactive-directory authorization failures to GraphQL `FORBIDDEN` and
  unexpected resolver failures to `INTERNAL_ERROR`.
- Added
  `docs/api-spine/practitioner-directory-graphql-resolver-runtime.json`.
- Added
  `docs/api-spine/practitioner-directory-graphql-resolver-runtime.md`.
- Added `tests/test_practitioner_directory_graphql_resolver.py`.
- Updated older plan-era static tests so they now assert the approved live
  resolver boundary rather than the pre-approval absence of GraphQL runtime code.
- Added DeepSeek Sprint 270 resolver-boundary review artifact.

Worker mix:

- DeepSeek via direct Codex `deepseek-worker`: PASS; flagged the HTTPException
  mapping, GraphQL-side input validation, UUID-to-ID conversion, and no-leak
  `practice(id:)` behavior. Those cautions were integrated.

Boundary:

- Only `Query.practice.practitioners` is opened.
- No GraphQL mutations, subscriptions, global readiness snapshot change,
  provider/Access AI invocation, memory/RAG/GraphRAG wiring, H15/H-series
  runtime import, historical diary/local_data import, external patient-client
  exposure, write authority, audit write, deployment claim, or production
  readiness claim.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_graphql_resolver.py tests\test_practitioner_directory_graphql_runtime_shell.py tests\test_practitioner_directory_graphql_dependency_preflight.py tests\test_practitioner_directory_graphql_runtime_gate.py tests\test_api_spine_practitioner_directory_graphql_resolver_ownership_plan.py tests\test_practitioner_directory_graphql_sdl_alignment_evidence.py tests\test_api_spine_practitioner_directory_rest_graphql_drift_contract.py tests\test_api_spine_practitioner_directory_sdl_resolution_proposal.py -q
```

Result: Sprint 270 resolver/API-spine suite `82 passed`.

Implementation commit: integrating commit for Sprint 270.

Sprint engine state: continuing to Sprint 271 GraphQL practitioner contract
hardening and release-boundary evidence.

---

## Previous Closeout - Sprint 269

| Item | Value |
|---|---|
| Batch | Sprint 269 Practitioner Directory GraphQL Runtime Shell |
| Integrated through | Ariadne runtime shell with DeepSeek PASS review |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

## Sprint 269 What Changed

- Added `app/graphql/context.py`, reusing the existing `get_current_user` and
  `get_db` dependency path for GraphQL context.
- Added `app/graphql/schema.py`, a query-only Strawberry schema with only the
  authenticated `graphqlHealth` placeholder field.
- Added `app/graphql/router.py` and mounted it from `app/main.py` at
  `/api/v1/graphql`.
- Configured `QueryDepthLimiter(max_depth=6)`,
  `MaxAliasesLimiter(max_alias_count=500)`, and
  `MaxTokensLimiter(max_token_count=500)`.
- Added
  `docs/api-spine/practitioner-directory-graphql-runtime-shell.json`.
- Added
  `docs/api-spine/practitioner-directory-graphql-runtime-shell.md`.
- Added `tests/test_practitioner_directory_graphql_runtime_shell.py`.
- Updated Sprint 267/268 guard tests so the mounted shell is allowed while
  `Query.practice.practitioners` remains absent.
- Added DeepSeek Sprint 269 runtime-shell review artifact.

Worker mix:

- DeepSeek via direct Codex `deepseek-worker`: PASS; called out the need to
  supersede old no-endpoint assertions and to record Strawberry 0.320.3's
  lack of a native field-cost estimator. Sprint 269 uses depth, alias, and
  token guards and defers any custom cost estimator until richer fields need it.

Boundary:

- GraphQL dependency, endpoint mount, authenticated context, and placeholder
  health query only.
- No `Query.practice.practitioners` resolver, no GraphQL `Practice` type, no
  GraphQL mutation/subscription surface, no readiness flag change, no
  provider/Access AI invocation, no memory/RAG/GraphRAG wiring, no H15/H-series
  runtime import, no historical diary/local_data import, no external
  patient-client exposure, no write authority, no audit write, no deployment
  claim, and no production-readiness claim.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_graphql_runtime_shell.py tests\test_practitioner_directory_graphql_dependency_preflight.py tests\test_practitioner_directory_graphql_runtime_gate.py -q
```

Result: Sprint 269 shell/gate suite `21 passed`.

Implementation commit: integrating commit for Sprint 269.

Sprint engine state: continuing to Sprint 270 single approved
`Query.practice.practitioners` resolver against the shared read service.

---

## Previous Closeout - Sprint 268

| Item | Value |
|---|---|
| Batch | Sprint 268 Practitioner Directory GraphQL Dependency Preflight |
| Integrated through | Ariadne dependency pin/evidence with DeepSeek PASS review |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

## Sprint 268 What Changed

- Pinned `strawberry-graphql[fastapi]==0.320.3` in `requirements.txt`.
- Added
  `docs/api-spine/practitioner-directory-graphql-dependency-preflight.json`.
- Added
  `docs/api-spine/practitioner-directory-graphql-dependency-preflight.md`.
- Added `tests/test_practitioner_directory_graphql_dependency_preflight.py`.
- Updated `tests/test_practitioner_directory_graphql_runtime_gate.py` so the
  Sprint 267 gate now recognizes the approved Sprint 268 dependency while still
  forbidding endpoint/resolver runtime code.
- Added DeepSeek Sprint 268 dependency/security review artifact.
- Verified `GraphQLRouter`, `QueryDepthLimiter`, `MaxAliasesLimiter`, and
  `DisableIntrospection` imports.

Worker mix:

- DeepSeek via direct Codex `deepseek-worker`: PASS; confirmed the Strawberry
  pin is viable, noted `graphql-core==3.2.11` and `cross-web==0.7.0`
  transitives, and found no new vulnerability introduced by the dependency.

Boundary:

- Dependency pin and local install/import evidence only.
- No `/api/v1/graphql` endpoint/server, no GraphQL schema runtime code, no
  resolver, no global readiness snapshot change, no external-readiness DAG
  readiness change, no provider/Access AI invocation, no memory/RAG/GraphRAG
  wiring, no H15/H-series runtime import, no historical diary/local_data import,
  no external patient-client exposure, no write authority, no deployment claim,
  and no production-readiness claim.

Verification:

```powershell
.venv\Scripts\python.exe -m pip install "strawberry-graphql[fastapi]==0.320.3"
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_graphql_dependency_preflight.py tests\test_practitioner_directory_graphql_runtime_gate.py -q
```

Result: dependency installed; `pip check` reported no broken requirements;
Sprint 268 dependency/gate suite `12 passed`.

Implementation commit: integrating commit for Sprint 268.

Sprint engine state: continuing to Sprint 269 minimal GraphQL runtime shell
without practitioner resolver.

---

## Previous Closeout - Sprint 267

| Item | Value |
|---|---|
| Batch | Sprint 267 Practitioner Directory GraphQL Runtime Gate |
| Integrated through | Ariadne gate packet with DeepSeek PASS review |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

Sprint 267 added the Yuri-approved gate packet for
`Query.practice.practitioners`, selected Strawberry as preferred future runtime,
and kept dependency/server/resolver readiness closed. Commit: `a76dd371`.

---

## Previous Closeout - Sprint 266

| Item | Value |
|---|---|
| Batch | Sprint 266 Practitioner Directory GraphQL SDL Alignment |
| Integrated through | Ariadne SDL/test alignment with DeepSeek PASS review |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

Sprint 266 aligned the non-runtime GraphQL SDL to the REST practitioner-directory
projection, resolved the two former SDL drift points, and kept runtime/resolver
readiness false. Commit: `eb349d87`.

---

## Previous Closeout - Sprint 265

| Item | Value |
|---|---|
| Batch | Sprint 265 Practitioner Directory Runtime Consumer Evidence |
| Integrated through | Ariadne browser/backend evidence with DeepSeek PASS review |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

Sprint 265 added route-intercepted Playwright and backend evidence for the
approved Diary booking practitioner selector/list REST consumer, proving
bearer-token route use, route 401 fail-closed behavior, smoke/legacy fallback,
200 returned-row rendering, and no adjacent gate openings. Commit: `63201c65`.

---

## Previous Closeout - Sprint 264

| Item | Value |
|---|---|
| Batch | Sprint 264 Practitioner Directory Internal Runtime Consumer Wiring |
| Integrated through | Ariadne implementation with DeepSeek PASS review |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

Sprint 264 wired the approved Office add-in Diary booking practitioner
selector/list to `GET /api/v1/practice/practitioners?activeOnly=true&limit=200`
through existing `apiFetch`, normalized display-safe route fields, preserved
legacy AHPRA fallback, corrected the approval packet to the actual REST field
names, and kept adjacent gates closed. Commit: `3c48ab59`.

---

## Previous Closeout - Sprint 263

| Item | Value |
|---|---|
| Batch | Sprint 263 Practitioner Directory Internal Runtime Consumer Approval |
| Integrated through | Ariadne approval packet with Claude PASS, DeepSeek API-boundary PASS, and substitute DeepSeek UI/consumer PASS after Antigravity timeout |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

Sprint 263 approved exactly one route-data runtime consumer,
`office_addin_diary_booking_practitioner_selector`, using
`http_through_existing_route`, while preserving the Sprint 261 readiness-status
boundary, the Sprint 262 static release check, and all adjacent gates. Commit:
`f19a17a6`.

---

## Previous Closeout - Sprint 262

| Item | Value |
|---|---|
| Batch | Sprint 262 Practitioner Directory Static Release Check |
| Integrated through | Ariadne implementation with DeepSeek static-boundary PASS, Claude complete-diff PASS, and Antigravity consumer/deployment PASS |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

## Sprint 262 What Changed

- Added `scripts/practitioner_directory_route_readiness_release_check.py`.
- Added `tests/test_practitioner_directory_route_readiness_release_check.py`.
- Hardened `scripts/practitioner_directory_route_readiness_status.py` so
  readiness artifact drift raises `ValueError` rather than relying on bare
  Python `assert`.
- Updated `orchestration/bernie_release_gates.md` so the preferred practitioner
  directory static gate is the release-check wrapper, with the raw status helper
  still available as supporting evidence.
- Added DeepSeek, Claude, and Antigravity review artifacts for Sprint 262.
- Preserved the Sprint 261 consumer boundary: the new helper may be used only by
  static CI/pytest release gates or developer-facing release summaries.

Worker mix:

- DeepSeek via direct Codex `deepseek-worker` spawn: PASS; recommended verifying
  the adjacent-gate count and replacing bare `assert` with fail-closed runtime
  checks.
- Claude via `scripts\drive_agent_headless.py`: initially BLOCKED because its
  worker branch was stale and then because the first pasted diff omitted the new
  untracked helper; after complete-diff review it returned PASS and Ariadne
  integrated its exact-membership and runtime-isolation suggestions.
- Antigravity via `agy.exe`: PASS for static-only consumer/deployment boundary;
  its worker CLI unexpectedly merged `origin/master` in the Antigravity worktree,
  so Ariadne did not rely on any worker-tree changes and integrated only the
  review content.

Boundary:

- Static script, tests, release-gate text, and worker review packets only.
- No route/schema/service behavior change, no global readiness snapshot change,
  no external-readiness DAG change, no SDL or GraphQL resolver, no provider/
  Access AI invocation, no memory/RAG/GraphRAG wiring, no H15/H-series runtime
  import, no historical diary/local_data import, no external patient-client
  exposure, no write authority, no deployment claim, and no production-readiness
  claim.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile scripts\practitioner_directory_route_readiness_status.py scripts\practitioner_directory_route_readiness_release_check.py tests\test_practitioner_directory_route_readiness_release_check.py
.venv\Scripts\python.exe scripts\practitioner_directory_route_readiness_release_check.py
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_route_readiness_release_check.py tests\test_practitioner_directory_route_readiness_status.py tests\test_practitioner_directory_route_readiness_consumer_boundary.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
.venv\Scripts\python.exe -m pytest tests\test_external_read_model_readiness_status.py tests\test_sprint_closeout_protocol.py -q
git diff --check
```

Result: focused release/status/consumer-boundary suite `18 passed`; API-spine
artifact suite `31 passed`; external-readiness/protocol suite `16 passed`;
`py_compile`, CLI sample, and whitespace check passed. A deliberately parallel
broader run hit the known disposable Postgres enum race and passed after schema
reset and serial rerun.

Implementation commit: `061f9cd0`.

Sprint engine state: continuing only to static release-summary/report
integration if useful, or pausing for Yuri direction before runtime consumption.

---

## Previous Closeout - Sprint 261

| Item | Value |
|---|---|
| Batch | Sprint 261 Practitioner Directory Route Readiness Consumer Boundary |
| Integrated through | Ariadne implementation with DeepSeek consumer-boundary preflight, Claude API-spine/security PASS, and Antigravity consumer/release/deployment PASS |
| Status | Integrated, verified, and pushed |
| Last updated | 2026-07-09 |

## Sprint 261 What Changed

- Added
  `docs/api-spine/practitioner-directory-route-readiness-consumer-boundary.json`.
- Added
  `docs/api-spine/practitioner-directory-route-readiness-consumer-boundary.md`.
- Added
  `tests/test_practitioner_directory_route_readiness_consumer_boundary.py`.
- Added a Practitioner Directory Route Readiness Gate to
  `orchestration/bernie_release_gates.md`.
- Added DeepSeek, Claude, and Antigravity review artifacts for the consumer
  boundary.
- Allowed only static docs, orchestration, CI/pytest release checks, and
  developer-facing release summaries to consume the route-scoped readiness
  status.
- Forbid runtime `app/` consumers, global external-readiness DAG/snapshot
  mutation, provider/Access AI/memory/RAG/GraphRAG, Office add-in runtime UI,
  deployment/production configuration, external patient-client enablement,
  GraphQL resolver work, and write authority.
- Added a runtime isolation guard proving `app/` Python code does not import the
  route readiness helper or read its fixture.

Worker mix:

- DeepSeek via direct Codex `deepseek-worker` spawn: used for consumer-boundary
  preflight; recommended a release-gate citation and static-only consumers.
- Claude via `scripts\drive_agent_headless.py`: used for API-spine/security and
  runtime-import veto; returned PASS.
- Antigravity via `agy.exe`: used for consumer/release/deployment/UI boundary
  review; returned PASS.

Boundary:

- Docs, release-gate text, worker review packets, and tests only.
- No route/schema/service behavior change, no global readiness snapshot change,
  no external-readiness DAG change, no SDL or GraphQL resolver, no provider/
  Access AI invocation, no memory/RAG/GraphRAG wiring, no H15/H-series runtime
  import, no historical diary/local_data import, no external patient-client
  exposure, no write authority, no deployment claim, and no production-readiness
  claim.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_route_readiness_consumer_boundary.py -q
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_route_readiness_consumer_boundary.py tests\test_practitioner_directory_route_readiness_status.py tests\test_practitioner_directory_rest_route_readiness_approval.py -q
.venv\Scripts\python.exe -m pytest tests\test_external_read_model_readiness_status.py tests\test_sprint_closeout_protocol.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
git diff --check -- AGENTS.md orchestration\integration_log.md orchestration\sprint_closeout.md orchestration\bernie_release_gates.md docs\api-spine\practitioner-directory-route-readiness-consumer-boundary.json docs\api-spine\practitioner-directory-route-readiness-consumer-boundary.md tests\test_practitioner_directory_route_readiness_consumer_boundary.py orchestration\agent_inbox\codex\review-deepseek-sprint261-route-readiness-consumer-boundary.md orchestration\agent_inbox\codex\review-claude-sprint261-route-readiness-consumer-boundary.md orchestration\agent_inbox\codex\review-antigravity-sprint261-route-readiness-consumer-boundary.md
```

Result: focused consumer-boundary suite `5 passed`; route-readiness chain
`18 passed`; external-readiness/protocol suite `16 passed`; API-spine artifact
suite `31 passed`; whitespace check clean apart from the known CRLF notice on
`orchestration/integration_log.md`. An overlapping DB-backed pytest attempt hit
the known disposable Postgres enum creation race and passed after resetting the
test schema and rerunning serially.

Implementation commit: `05007bc8`.

Sprint engine state: continuing only to static release-check/report integration
if useful. Do not wire runtime behavior or widen adjacent readiness gates.

---

## Previous Closeout - Sprint 260

| Item | Value |
|---|---|
| Batch | Sprint 260 Practitioner Directory Route-Scoped Readiness Status |
| Integrated through | Ariadne implementation with DeepSeek mechanical status-model review |
| Status | Integrated and pushed |
| Last updated | 2026-07-09 |

## Sprint 260 What Changed

- Added `scripts/practitioner_directory_route_readiness_status.py`.
- Added
  `tests/fixtures/api_spine_external_readiness/practitioner_directory_route_readiness_status.json`.
- Added `tests/test_practitioner_directory_route_readiness_status.py`.
- Added
  `orchestration/agent_inbox/codex/review-deepseek-sprint260-route-readiness-status.md`.
- Accepted DeepSeek's recommendation to expose a route-scoped readiness
  fixture/report instead of flipping the global `blocked_readiness_status.json`
  or external-readiness DAG semantics.
- The route-scoped status reports `rest_route_ready=true` for
  `GET /api/v1/practice/practitioners` only, with approval expiry and residual
  risk posture.
- The helper asserts the global external-readiness snapshot remains all-false
  and fails closed if the global snapshot is silently flipped.
- The helper rejects wrong routes, adjacent gate drift, and expired approval.

Worker mix:

- DeepSeek via direct Codex `deepseek-worker` spawn: used for status-model
  path selection; recommended the route-scoped fixture/report path and warned
  against global readiness flag migration in this sprint.
- Claude and Antigravity were not re-invoked because Sprint 260 was a narrow
  mechanical status-model follow-up to the already reviewed Sprint 259 approval
  payload; DeepSeek had the distinct artifact/veto surface.

Boundary:

- Script, fixture, worker review packet, and tests only.
- No route/schema/service behavior change, no global readiness snapshot change,
  no external-readiness DAG change, no SDL or GraphQL resolver, no provider/
  Access AI invocation, no memory/RAG/GraphRAG wiring, no H15/H-series runtime
  import, no historical diary/local_data import, no external patient-client
  exposure, no write authority, no deployment claim, and no production-readiness
  claim.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_route_readiness_status.py -q
```

Result: route-scoped readiness status suite `7 passed`.

Implementation commit: `0ff0e10a`.

Sprint engine state: continuing to Sprint 261 consumer-boundary/readiness-use
preflight. The next block should decide where this route-scoped readiness status
is allowed to be consumed without wiring runtime behavior or widening adjacent
gates.

---

## Previous Closeout - Sprint 259

| Item | Value |
|---|---|
| Batch | Sprint 259 Practitioner Directory REST Route Readiness Approval |
| Integrated through | Ariadne orchestration/integration with Claude API-spine/security PASS, Antigravity consumer/deployment-boundary PASS, and DeepSeek mechanical approval-scope PASS |
| Status | Integrated and pushed |
| Last updated | 2026-07-09 |

## Sprint 259 What Changed

- Added
  `docs/api-spine/practitioner-directory-rest-route-readiness-approval.json`.
- Added
  `docs/api-spine/practitioner-directory-rest-route-readiness-approval.md`.
- Added `tests/test_practitioner_directory_rest_route_readiness_approval.py`.
- Recorded Yuri's explicit authorization for a separate
  `rest_route_ready=true` approval payload for
  `GET /api/v1/practice/practitioners` only.
- Added route-scoped approval fields: reviewer, acknowledgement, expiry,
  approved contract commit, route-only scope, and non-REST adjacent gates.
- Integrated Claude and Antigravity PASS reviews, plus DeepSeek's PASS for
  approval-payload creation.
- Preserved the global external-readiness snapshot in this sprint. The payload
  records approval; it does not silently flip the broader status checker or DAG.
- Preserved all GraphQL/provider/memory/H15/trove/external-client/write/
  deployment/production gates as false.

Worker mix:

- Claude via `scripts\drive_agent_headless.py`: used for route-scope and
  API-spine/security veto; returned PASS.
- Antigravity via `agy.exe`: used for consumer, deployment, production, and
  external-client boundary review; returned PASS.
- DeepSeek via direct Codex `deepseek-worker` spawn: used for mechanical
  approval/fixture-change analysis; returned PASS for approval creation and
  identified global fixture flipping as a separate readiness-model migration.

Boundary:

- Approval payload, decision markdown, worker review packets, and tests only.
- No route/schema/service behavior change, no global readiness snapshot change,
  no SDL or GraphQL resolver, no provider/Access AI invocation, no
  memory/RAG/GraphRAG wiring, no H15/H-series runtime import, no historical
  diary/local_data import, no external patient-client exposure, no write
  authority, no deployment claim, and no production-readiness claim.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_rest_route_readiness_approval.py tests\test_practitioner_directory_readiness_criteria.py tests\test_practitioner_directory_sprint258_blocker_closure.py -q
.venv\Scripts\python.exe -m pytest tests\test_external_read_model_readiness_status.py -q
git diff --check -- docs\api-spine\practitioner-directory-rest-route-readiness-approval.json docs\api-spine\practitioner-directory-rest-route-readiness-approval.md tests\test_practitioner_directory_rest_route_readiness_approval.py orchestration\agent_inbox\codex\review-claude-sprint259-practitioner-readiness-approval.md orchestration\agent_inbox\codex\review-antigravity-sprint259-practitioner-readiness-approval.md orchestration\agent_inbox\codex\review-deepseek-sprint259-practitioner-readiness-approval.md
```

Result: approval/criteria/Sprint 258 closure set `16 passed`; external
readiness status suite `9 passed`; whitespace check passed. An accidental
parallel DB-backed run hit the known transient Postgres enum creation collision;
the local `gp_pms_test` public schema was reset and the DB-backed suite passed
when rerun serially.

Implementation commit: `69297a02`.

Sprint engine state: continuing to Sprint 260 route-readiness status
migration/preflight. The next block must not claim deployment, production,
external patient-client, GraphQL, provider, memory/RAG/GraphRAG, H15/H-series,
historical diary, or write readiness.

---

## Previous Closeout - Sprint 258

| Item | Value |
|---|---|
| Batch | Sprint 258 Practitioner Directory Blocker Closure |
| Integrated through | Ariadne orchestration/integration with Claude security/gap wording review, Antigravity deployment/external-client boundary review, and DeepSeek mechanical completeness sweep |
| Status | Integrated and pushed |
| Last updated | 2026-07-09 |

## Sprint 258 What Changed

- Added
  `docs/api-spine/practitioner-directory-sprint258-blocker-closure.json`.
- Added `docs/api-spine/practitioner-directory-sprint258-blocker-closure.md`.
- Added `tests/test_practitioner_directory_sprint258_blocker_closure.py`.
- Integrated Claude's Sprint 258 security/gap wording review.
- Integrated Antigravity's Sprint 258 deployment/external-client boundary
  review.
- Ran a DeepSeek `deepseek-worker` mechanical completeness sweep; result:
  PASS.
- Closed all Sprint 257 blocker-evidence items except the intentionally
  withheld separate Yuri approval payload.
- Recorded isolated runtime route and API-spine artifact test pass evidence.
- Recorded deferred internal-route rate-limit posture, including accepted risk
  for a compromised authenticated staff credential and current soft controls.
- Named the current development/internal deployment surface while keeping
  deployment and production readiness false.
- Recorded the RLS gap as not equivalent to PostgreSQL RLS and the
  field-encryption residual risk for regulated practitioner identifiers.
- Recorded explicit internal-staff-only external-client scope.
- Preserved `rest_route_ready=false` and all GraphQL/provider/memory/H15/trove/
  external-client/write/deployment/production readiness gates as false.

Worker mix:

- Claude via `scripts\drive_agent_headless.py`: used for security/gap wording
  review; tightened rate-limit, deployment, RLS, field-encryption, and
  external-client residual-risk language.
- Antigravity via `agy.exe`: used for deployment/external-client and consumer
  boundary review; reported PASS/VERIFY.
- DeepSeek via direct Codex `deepseek-worker` spawn: used for mechanical
  completeness; reported all Sprint 257 blockers closed except the separate
  Yuri approval payload, which remains intentionally absent.

Boundary:

- Docs, worker review packets, and tests only.
- No route/schema/service behavior change, no readiness flag change, no SDL or
  GraphQL resolver, no provider/Access AI invocation, no memory/RAG/GraphRAG
  wiring, no H15/H-series runtime import, no historical diary/local_data import,
  no external patient-client exposure, no write authority, no deployment claim,
  no production-readiness claim, and no Yuri approval payload.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_sprint258_blocker_closure.py tests\test_practitioner_directory_sprint257_go_no_go.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_route.py -q
git diff --check -- docs\api-spine\practitioner-directory-sprint258-blocker-closure.json docs\api-spine\practitioner-directory-sprint258-blocker-closure.md tests\test_practitioner_directory_sprint258_blocker_closure.py orchestration\agent_inbox\codex\review-antigravity-sprint258-practitioner-blocker-closure.md
```

Result: Sprint 258/Sprint 257 blocker-governance set `10 passed`;
API-spine artifact suite `31 passed`; practitioner-directory route matrix
`31 passed`; whitespace check passed. An accidental parallel run of
DB-bootstrapping suites hit the known transient Postgres enum creation
collision; the local `gp_pms_test` public schema was reset and the suites passed
when rerun serially.

Implementation commits: Claude review commit `bf2c0412`; Sprint 258 synthesis
commit `f24d7a34`.

Sprint engine state: paused for Yuri decision. The next move is not another
autonomous implementation sprint; Yuri must explicitly decide whether to
authorize a separate `rest_route_ready=true` approval payload for
`GET /api/v1/practice/practitioners` only.

---

## Previous Closeout - Sprint 257

| Item | Value |
|---|---|
| Batch | Sprint 257 Practitioner Directory Multi-Worker Go/No-Go |
| Integrated through | Ariadne orchestration/integration with Claude readiness/safety veto, Antigravity consumer/API-boundary review, and DeepSeek mechanical static sweep |
| Status | Integrated and pushed |
| Last updated | 2026-07-09 |

## Sprint 257 What Changed

- Integrated Claude plan/review packets for
  `claude-sprint257-practitioner-readiness-veto`.
- Integrated Antigravity plan/review packets for
  `antigravity-sprint257-practitioner-consumer-boundary`.
- Ran a DeepSeek `deepseek-worker` mechanical static sweep; result:
  no mechanical blockers.
- Added
  `docs/api-spine/practitioner-directory-sprint257-go-no-go.json`.
- Added `docs/api-spine/practitioner-directory-sprint257-go-no-go.md`.
- Added `tests/test_practitioner_directory_sprint257_go_no_go.py`.
- Decision:
  `no_go_blocker_closure_required_before_readiness_approval_request`.
- Preserved `rest_route_ready=false` and all GraphQL/provider/memory/H15/trove/
  external-client/write/deployment/production readiness gates as false.

Worker mix:

- Claude via `scripts\drive_agent_headless.py`: used for independent
  readiness/safety veto; submitted a no-go because several Sprint 255 criteria
  remain undocumented and a separate Yuri readiness approval payload is absent.
- Antigravity via `agy.exe`: used for consumer/API ergonomics and
  external-client boundary review; submitted a pass for the internal consumer
  contract.
- DeepSeek via direct Codex `deepseek-worker` spawn: used for mechanical
  static sweep; reported no readiness flag, detail-route, sensitive-field,
  adjacent-import, write-side-effect, or OpenAPI/test mismatch blocker.

Boundary:

- Docs, worker review packets, and tests only.
- No route/schema/service behavior change, no readiness flag change, no SDL or
  GraphQL resolver, no provider/Access AI invocation, no memory/RAG/GraphRAG
  wiring, no H15/H-series runtime import, no historical diary/local_data import,
  no external patient-client exposure, no write authority, no deployment claim,
  and no production-readiness claim.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_sprint257_go_no_go.py tests\test_practitioner_directory_readiness_criteria.py -q
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_consumer_contract_report.py -q
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_route.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
git diff --check -- docs\api-spine\practitioner-directory-sprint257-go-no-go.json docs\api-spine\practitioner-directory-sprint257-go-no-go.md tests\test_practitioner_directory_sprint257_go_no_go.py
```

Result: Sprint 257 go/no-go and readiness criteria set `10 passed`;
consumer-contract report set `5 passed`; practitioner-directory route matrix
`31 passed`; API-spine artifact suite `31 passed`; whitespace check passed. An
accidental parallel run of DB-bootstrapping suites hit the known transient
Postgres enum creation collision, then passed when rerun serially.

Implementation commits: worker/prep commits `1644c978`, `ce7d358f`,
`c8bdbbf9`, `954f4eac`, `d7132d25`; Ariadne synthesis commit `3a1d7c0a`;
closeout metadata commit `b2e6f839`.

Sprint engine state: continuing to Sprint 258 blocker-closure block. Do not
create a Yuri approval payload or flip `rest_route_ready` without explicit Yuri
approval.

---

## Previous Closeout - Sprints 254-256

| Item | Value |
|---|---|
| Batch | Sprints 254-256 Practitioner Directory Evidence, Readiness Criteria, and Consumer Contract |
| Integrated through | Ariadne direct implementation; Claude/Antigravity were available but not invoked, and DeepSeek lane count stayed zero because the block was bounded API-spine evidence/contract work over an implemented read route |
| Status | Integrated and pushed |
| Last updated | 2026-07-09 |

## Sprints 254-256 What Changed

Sprint 254:

- Added `docs/api-spine/practitioner-directory-runtime-evidence-refresh.json`.
- Added `docs/api-spine/practitioner-directory-runtime-evidence-refresh.md`.
- Added `tests/test_practitioner_directory_runtime_evidence_refresh.py`.
- Refreshed runtime evidence for `GET /api/v1/practice/practitioners` while
  keeping readiness blocked.

Sprint 255:

- Added `docs/api-spine/practitioner-directory-readiness-criteria.json`.
- Added `docs/api-spine/practitioner-directory-readiness-criteria.md`.
- Added `tests/test_practitioner_directory_readiness_criteria.py`.
- Defined criteria required before any future `rest_route_ready=true` decision.

Sprint 256:

- Added `scripts/practitioner_directory_consumer_contract_report.py`.
- Added
  `tests/fixtures/api_spine_practitioner_directory/consumer_contract_report.json`.
- Added `docs/api-spine/practitioner-directory-consumer-contract-check.md`.
- Added `tests/test_practitioner_directory_consumer_contract_report.py`.
- Locked the FastAPI/OpenAPI consumer contract: GET-only route, security
  declared, `activeOnly`/`limit`/`offset` query defaults and bounds,
  `PractitionerOut` response fields, sensitive-field absence, and no detail
  route.

Worker mix:

- Claude worktree available; Claude was not invoked because this was bounded
  evidence/criteria/contract work over committed route code.
- Antigravity worktree available; Antigravity was not invoked for the same
  reason.
- DeepSeek was not invoked; DeepSeek lane count stayed zero.
- Integration worktree was clean at block start.

Boundary:

- Docs, fixture, script, and tests only.
- No route/schema/service behavior change, no readiness flag change, no SDL or
  GraphQL resolver, no provider/Access AI invocation, no memory/RAG/GraphRAG
  wiring, no H15/H-series runtime import, no historical diary/local_data import,
  no external patient-client exposure, no write authority, no deployment claim,
  and no production-readiness claim.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_runtime_evidence_refresh.py tests\test_practitioner_directory_post_implementation_readiness_review.py tests\test_practitioner_directory_approval_gate_static.py -q
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_route.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_readiness_criteria.py tests\test_practitioner_directory_runtime_evidence_refresh.py tests\test_external_read_model_readiness_status.py -q
.venv\Scripts\python.exe scripts\practitioner_directory_consumer_contract_report.py
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_consumer_contract_report.py tests\test_practitioner_directory_readiness_criteria.py tests\test_practitioner_directory_runtime_evidence_refresh.py -q
git diff --check -- docs\api-spine\practitioner-directory-runtime-evidence-refresh.json docs\api-spine\practitioner-directory-runtime-evidence-refresh.md tests\test_practitioner_directory_runtime_evidence_refresh.py
git diff --check -- docs\api-spine\practitioner-directory-readiness-criteria.json docs\api-spine\practitioner-directory-readiness-criteria.md tests\test_practitioner_directory_readiness_criteria.py
git diff --check -- scripts\practitioner_directory_consumer_contract_report.py tests\fixtures\api_spine_practitioner_directory\consumer_contract_report.json docs\api-spine\practitioner-directory-consumer-contract-check.md tests\test_practitioner_directory_consumer_contract_report.py
```

Result: Sprint 254 guard/review set `20 passed`; practitioner-directory route
matrix `31 passed` after isolated rerun; API-spine artifact suite `31 passed`;
Sprint 255 criteria/status set `19 passed`; Sprint 256 consumer-contract set
`15 passed`; OpenAPI report emitted the expected safe aggregate snapshot;
whitespace checks passed. An accidental parallel run of the DB-heavy route suite
hit the known transient Postgres enum creation collision, then passed when
rerun alone.

Implementation commits: `4615a51e`, `923b74e4`, `43dabd60`.

Sprint engine state: pause before any `rest_route_ready=true` change; next safe
step is a Sprint 257 go/no-go decision draft requiring explicit Yuri approval
before readiness flips.

---

## Previous Closeout - Sprint 253

| Item | Value |
|---|---|
| Batch | Sprint 253 Bernie UI D5 First-Slice Completion Review |
| Integrated through | Ariadne direct implementation; Claude/Antigravity were available but not invoked, and DeepSeek lane count stayed zero because this was a bounded review/decision packet |
| Status | Integrated and pushed |
| Last updated | 2026-07-09 |

## Sprint 253 What Changed

- Added
  `docs/bernie-ui-derived-state-dag-d5-first-slice-completion-review.json`.
- Added
  `docs/bernie-ui-derived-state-dag-d5-first-slice-completion-review.md`.
- Added `tests/test_bernie_ui_dag_d5_first_slice_completion_review.py`.
- Recorded decision `d5_first_slice_complete_pause_expansion`.
- Classified D5 as a read/display response contract, not a GraphQL mutation,
  REST command mutation, or write-authority surface.
- Recommended pausing D5 expansion and moving next to either a human review
  checkpoint or a separate bounded non-D5 sprint with gates closed.

Worker mix:

- Claude worktree available; Claude was not invoked because this was a bounded
  decision packet over already committed evidence.
- Antigravity worktree available; Antigravity was not invoked for the same
  reason.
- DeepSeek was not invoked; DeepSeek lane count stayed zero.
- Integration worktree was clean at sprint start.

Boundary:

- Review JSON/MD and deterministic guard tests only.
- No production JavaScript change, no backend route/schema/service change, no
  provider call, no Access AI invocation, no memory/RAG/GraphRAG wiring, no
  H15/H-series runtime import, no historical diary/local_data import, no GraphQL
  resolver, no external patient-client exposure, no confirm payload change, and
  no appointment write behavior change.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_dag_d5_first_slice_completion_review.py tests\test_bernie_ui_dag_d5_frontend_consumption_evidence.py tests\test_bernie_ui_dag_d5_response_shape_report.py tests\test_bernie_ui_dag_d5_post_implementation_review.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
git diff --check -- docs\bernie-ui-derived-state-dag-d5-first-slice-completion-review.json docs\bernie-ui-derived-state-dag-d5-first-slice-completion-review.md tests\test_bernie_ui_dag_d5_first_slice_completion_review.py
```

Result: D5 packet/evidence suite `18 passed` on sequential rerun; API-spine
artifact suite `31 passed`; existing Starlette and Google GenAI deprecation
warnings only; whitespace check passed. An earlier parallel validation attempt
hit a transient Postgres enum create collision in `tests/conftest.py`, then
passed when rerun sequentially.

Implementation commit: `80ef373d`.

Sprint engine state: pause D5 expansion; select a separate bounded non-D5
sprint or human review checkpoint unless Yuri explicitly approves more D5 scope.

---

## Previous Closeout - Sprint 252

| Item | Value |
|---|---|
| Batch | Sprint 252 Bernie UI D5 Frontend Consumption Evidence |
| Integrated through | Ariadne direct implementation; Claude/Antigravity were available but not invoked, and DeepSeek lane count stayed zero because this was a bounded route-intercepted frontend evidence slice |
| Status | Integrated and pushed |
| Last updated | 2026-07-09 |

## Sprint 252 What Changed

- Added
  `docs/bernie-ui-derived-state-dag-d5-frontend-consumption-evidence.json`.
- Added
  `docs/bernie-ui-derived-state-dag-d5-frontend-consumption-evidence.md`.
- Added `tests/test_bernie_ui_dag_d5_frontend_consumption_evidence.py`.
- Added
  `review/test_diary_smoke.py::test_bernie_ui_view_model_consumes_backend_staff_review_field_without_js_expansion`.
- Proved, with a route-intercepted Playwright response, that the existing
  Diary JavaScript consumes the post-D5 backend response shape at
  `staff_review.ui_view_model` without requiring a top-level `ui_view_model`
  field or any JavaScript expansion.
- Confirmed the rendered staff-review panel uses the backend-shaped view model
  and that the signed confirm payload still excludes view-model fields.

Worker mix:

- Claude worktree available; Claude was not invoked because this was a bounded
  route-intercepted Playwright/evidence slice over existing code.
- Antigravity worktree available; Antigravity was not invoked for the same
  reason.
- DeepSeek was not invoked; DeepSeek lane count stayed zero.
- Integration worktree was clean at sprint start.

Boundary:

- One route-intercepted browser-smoke test plus docs/tests.
- No production JavaScript change, no backend route/schema/service change beyond
  Sprint 249, no provider call, no Access AI invocation, no memory/RAG/GraphRAG
  wiring, no H15/H-series runtime import, no historical diary/local_data import,
  no GraphQL resolver, no external patient-client exposure, no confirm payload
  change, and no appointment write behavior change.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_dag_d5_frontend_consumption_evidence.py tests\test_bernie_ui_dag_d5_response_shape_report.py -q
.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q -k "consumes_backend_staff_review_field"
git diff --check -- review\test_diary_smoke.py docs\bernie-ui-derived-state-dag-d5-frontend-consumption-evidence.json docs\bernie-ui-derived-state-dag-d5-frontend-consumption-evidence.md tests\test_bernie_ui_dag_d5_frontend_consumption_evidence.py
```

Result: `9 passed` for the static/evidence checks, the focused Playwright smoke
case passed, existing Starlette and Google GenAI deprecation warnings only, and
the whitespace check passed.

Implementation commit: `fac533de`.

Sprint engine state: pause before D5 expansion; the first slice now has backend
delivery, post-implementation review, response-shape evidence, and
route-intercepted frontend consumption evidence.

---

## Previous Closeout - Sprint 251

| Item | Value |
|---|---|
| Batch | Sprint 251 Bernie UI D5 Response-Shape Report |
| Integrated through | Ariadne direct implementation; Claude/Antigravity were available but not invoked, and DeepSeek lane count stayed zero because this was a bounded safe aggregate report/checker |
| Status | Integrated and pushed |
| Last updated | 2026-07-09 |

## Sprint 251 What Changed

- Added `scripts/bernie_ui_dag_d5_response_shape_report.py`.
- Added `tests/fixtures/bernie_ui_dag_d5/response_shape_report.json`.
- Added `tests/test_bernie_ui_dag_d5_response_shape_report.py`.
- Reported the delivered D5 backend response-shape contract as safe aggregate
  evidence without route paths, payload IDs, raw diary material, or provider
  claims.
- Preserved one backend response assembly point, present/null field behavior,
  unchanged command payload and appointment write behavior, unchanged frontend
  JavaScript, and false values for additional routes, GraphQL, providers/live
  providers, memory/RAG, external clients, and write authority.

Worker mix:

- Claude worktree available; Claude was not invoked because this was a bounded
  safe aggregate report and checker.
- Antigravity worktree available; Antigravity was not invoked for the same
  reason.
- DeepSeek was not invoked; DeepSeek lane count stayed zero.
- Integration worktree was clean at sprint start.

Boundary:

- Script, fixture, and tests only.
- No backend response expansion beyond Sprint 249, no new route/schema/service
  behavior, no provider call, no Access AI invocation, no memory/RAG/GraphRAG
  wiring, no H15/H-series runtime import, no historical diary/local_data import,
  no GraphQL resolver, no frontend JavaScript change, no external patient-client
  exposure, and no new write authority.

Verification:

```powershell
.venv\Scripts\python.exe scripts\bernie_ui_dag_d5_response_shape_report.py
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_dag_d5_response_shape_report.py tests\test_bernie_ui_dag_d5_post_implementation_review.py tests\test_bernie_route_outcome_events.py -q
git diff --check -- scripts\bernie_ui_dag_d5_response_shape_report.py tests\fixtures\bernie_ui_dag_d5\response_shape_report.json tests\test_bernie_ui_dag_d5_response_shape_report.py
```

Result: report emitted the expected safe aggregate snapshot; `14 passed`;
existing Starlette and Google GenAI deprecation warnings only; whitespace check
passed.

Implementation commit: `c029f27e`.

Sprint engine state: continuing only through evidence/reporting work; D5 scope
expansion remains blocked pending separate review.

---

## Previous Closeout - Sprint 250

| Item | Value |
|---|---|
| Batch | Sprint 250 Bernie UI D5 Post-Implementation Review |
| Integrated through | Ariadne direct implementation; Claude/Antigravity were available but not invoked, and DeepSeek lane count stayed zero because this was a bounded review artifact with mechanical guards |
| Status | Integrated and pushed |
| Last updated | 2026-07-09 |

## Sprint 250 What Changed

- Added `docs/bernie-ui-derived-state-dag-d5-post-implementation-review.json`.
- Added `docs/bernie-ui-derived-state-dag-d5-post-implementation-review.md`.
- Added `tests/test_bernie_ui_dag_d5_post_implementation_review.py`.
- Recorded Sprint 249 as `implemented_first_slice_reviewed_scope_blocked`.
- Cited the backend delivery, no-server-session compatibility, router import
  guard, D5 readiness snapshot, D5 gate/approval, and API-spine evidence.
- Preserved separate-review requirements for any additional response assembly
  point, GraphQL, providers, Access AI, memory/RAG/GraphRAG, H15/H-series,
  historical diary runtime input, confirm payload/write behavior change,
  external patient clients, frontend JavaScript expansion, or model-to-database
  writes.

Worker mix:

- Claude worktree available; Claude was not invoked because this was a bounded
  static review artifact.
- Antigravity worktree available; Antigravity was not invoked for the same
  reason.
- DeepSeek was not invoked; DeepSeek lane count stayed zero.
- Integration worktree was clean at sprint start.

Boundary:

- Static docs/tests only.
- No backend response expansion, no route/schema/service change, no provider
  call, no Access AI invocation, no memory/RAG/GraphRAG wiring, no H15/H-series
  runtime import, no historical diary/local_data import, no GraphQL resolver, no
  frontend runtime change, no external patient-client exposure, and no new write
  authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_dag_d5_post_implementation_review.py tests\test_bernie_ui_dag_d5_readiness_snapshot.py tests\test_bernie_route_outcome_events.py tests\test_bernie_ui_view_model_d5_response_delivery_gate.py -q
.venv\Scripts\python.exe scripts\bernie_ui_dag_d5_readiness_snapshot.py
git diff --check -- docs\bernie-ui-derived-state-dag-d5-post-implementation-review.json docs\bernie-ui-derived-state-dag-d5-post-implementation-review.md tests\test_bernie_ui_dag_d5_post_implementation_review.py
```

Result: `23 passed`; D5 readiness snapshot emitted the approved first-slice and
closed-gates status; existing Starlette and Google GenAI deprecation warnings
only; whitespace check passed.

Implementation commit: `d2a0151b`.

Sprint engine state: continuing only through evidence/reporting work; D5 scope
expansion remains blocked pending separate review.

---

## Previous Closeout - Sprint 249

| Item | Value |
|---|---|
| Batch | Sprint 249 Bernie UI D5 Response Delivery First Slice |
| Integrated through | Ariadne direct implementation after Yuri explicitly approved Codex's recommended narrow D5 go; Claude/Antigravity were available but not invoked, and DeepSeek lane count stayed zero because the approved slice was already bounded by the committed D5 plan/checker |
| Status | Integrated and pushed |
| Last updated | 2026-07-09 |

## Sprint 249 What Changed

- Updated the D5 gate and approval-decision artifacts to
  `approved_for_backend_response_delivery_first_slice`, reviewer `yuri`,
  approved contract commit `b0e255c8`, and expiry `2026-07-23`.
- Added optional `ui_view_model` to `BernieStaffReviewPayload`.
- Wired `app/routers/appointments.py` to attach
  `build_bernie_ui_view_model(server_session)` only at the existing
  supervised-booking response assembly point and only when a server session
  snapshot exists.
- Responses without a server session keep `staff_review.ui_view_model` null.
- Confirm payloads remain free of UI view-model fields, and supervised booking
  still performs zero appointment/audit writes without a confirm command.
- Updated D5 readiness snapshot/checker to report the first slice ready while
  provider, memory/RAG/GraphRAG, raw-trove, live-provider, provider-call, write,
  external-client, GraphQL, H15/H-series, and model-to-database gates remain
  closed.

Worker mix:

- Claude worktree available; Claude was not invoked because the first-slice
  implementation was narrow and already covered by committed D5 contracts.
- Antigravity worktree available; Antigravity was not invoked for the same
  reason.
- DeepSeek was not invoked; DeepSeek lane count stayed zero.
- Integration worktree was clean at sprint start.

Boundary:

- One backend response field at one existing Bernie supervised-booking assembly
  point.
- No confirm payload change, no appointment/audit write change, no provider
  call, no Access AI invocation, no memory/RAG/GraphRAG wiring, no H15/H-series
  runtime import, no historical diary/local_data import, no GraphQL resolver, no
  frontend runtime change, no external patient-client exposure, and no
  model-to-database-write gate.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_route_outcome_events.py tests\test_bernie_supervised_booking_wrapper.py tests\test_bernie_ui_view_model.py tests\test_bernie_ui_view_model_d5_response_delivery_gate.py tests\test_bernie_ui_view_model_d5_approval_decision_draft.py tests\test_bernie_ui_view_model_d5_backend_delivery_test_plan.py tests\test_bernie_ui_dag_d5_readiness_snapshot.py tests\test_api_spine_artifacts.py -q
.venv\Scripts\python.exe scripts\bernie_ui_dag_d5_readiness_snapshot.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe -m py_compile scripts\bernie_ui_dag_d5_readiness_snapshot.py tests\test_bernie_route_outcome_events.py tests\test_bernie_ui_dag_d5_readiness_snapshot.py
git diff --check
```

Result: focused/API-spine suite `93 passed`; D5 readiness snapshot emitted the
approved first-slice/closed-provider-write-gates status; interpretation
readiness and provider-boundary reports remained blocked/disabled; py_compile
passed; whitespace check passed apart from the known CRLF notice on
`app/schemas/appointments.py`.

Implementation commit: `098b92a7`.

Sprint engine state: paused for separate review before any D5 expansion beyond
the single supervised-booking response field.

---

## Previous Closeout - Sprint 248

| Item | Value |
|---|---|
| Batch | Sprint 248 Bernie UI D5 Readiness Snapshot |
| Integrated through | Ariadne direct implementation; Claude/Antigravity worktrees available but not invoked, and DeepSeek lane count stayed zero because this was a bounded safe aggregate checker/snapshot |
| Status | Integrated and ready to push |
| Last updated | 2026-07-09 |

## Sprint 248 What Changed

- Added `scripts/bernie_ui_dag_d5_readiness_snapshot.py`.
- Added
  `tests/fixtures/bernie_ui_dag_d5/blocked_readiness_snapshot.json`.
- Added `tests/test_bernie_ui_dag_d5_readiness_snapshot.py`.
- The checker derives a safe aggregate status from the committed D5 gate,
  approval-decision draft, and backend delivery test plan.
- The emitted snapshot says `ui_consumer_ready=true`, while backend response
  delivery ready/approved, implementation authorization, runtime/provider
  readiness, raw-trove access, live-provider enablement, provider calls, write
  authority, and external-client readiness remain false or blocked.
- The snapshot intentionally omits route fragments, payload field names, local
  data paths, and identifier field names.

Worker mix:

- Claude worktree available and previously checked clean; Claude was not invoked
  because this was a small safe aggregate checker/snapshot sprint.
- Antigravity worktree available and previously checked clean; Antigravity was
  not invoked for the same reason.
- DeepSeek was not invoked; DeepSeek lane count stayed zero.
- Integration worktree was clean at sprint start.

Boundary:

- Safe aggregate script, fixture, and tests only.
- No backend response delivery, no route/schema/service change, no provider
  call, no Access AI invocation, no memory/RAG/GraphRAG wiring, no H15/H-series
  runtime import, no historical diary/local_data import, no GraphQL resolver, no
  frontend runtime change, no external patient-client exposure, and no new write
  authority.

Verification:

```powershell
.venv\Scripts\python.exe scripts\bernie_ui_dag_d5_readiness_snapshot.py
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_dag_d5_readiness_snapshot.py tests\test_bernie_ui_view_model_d5_backend_delivery_test_plan.py tests\test_bernie_ui_view_model_d5_approval_decision_draft.py tests\test_bernie_ui_view_model_d5_response_delivery_gate.py -q
.venv\Scripts\python.exe -m py_compile scripts\bernie_ui_dag_d5_readiness_snapshot.py tests\test_bernie_ui_dag_d5_readiness_snapshot.py
git diff --check -- scripts\bernie_ui_dag_d5_readiness_snapshot.py tests\fixtures\bernie_ui_dag_d5\blocked_readiness_snapshot.json tests\test_bernie_ui_dag_d5_readiness_snapshot.py
```

Result: checker CLI emitted the committed safe aggregate snapshot; `26 passed`;
py_compile passed; existing Starlette and Google GenAI deprecation warnings
only; whitespace check passed.

Implementation commit: `7b86ab9f`.

Sprint engine state: paused for Yuri's explicit D5 go/no-go before any backend
response delivery. If approved, the next implementation must stay inside the
single first-slice boundary and keep provider, memory, GraphQL, H15/H-series,
historical diary, external-client, and write gates closed.

---

## Previous Closeout - Sprint 247

| Item | Value |
|---|---|
| Batch | Sprint 247 Bernie UI D5 Backend Delivery Test Plan |
| Integrated through | Ariadne direct implementation; Claude/Antigravity worktrees available but not invoked, and DeepSeek lane count stayed zero because this was a bounded static test-plan artifact |
| Status | Integrated and ready to push |
| Last updated | 2026-07-09 |

## Sprint 247 What Changed

- Added `docs/bernie-ui-derived-state-dag-d5-backend-delivery-test-plan.json`.
- Added `docs/bernie-ui-derived-state-dag-d5-backend-delivery-test-plan.md`.
- Added `tests/test_bernie_ui_view_model_d5_backend_delivery_test_plan.py`.
- Defined the future approval prerequisite:
  `approved_for_backend_response_delivery_first_slice`.
- Named one candidate attachment point:
  `POST /api/v1/appointments/proposals/bernie/supervised-booking` with optional
  `staff_review.bernie.ui_view_model` response delivery.
- Captured required future tests for preflight, optional response attachment,
  backend-confirmed-only success, pressed/awaiting/stale/failed state behavior,
  confirm-payload purity, zero supervised-booking writes, import isolation, and
  non-live-provider evidence labels.

Worker mix:

- Claude worktree available and previously checked clean; Claude was not invoked
  because this was a small static test-plan sprint.
- Antigravity worktree available and previously checked clean; Antigravity was
  not invoked for the same reason.
- DeepSeek was not invoked; DeepSeek lane count stayed zero.
- Integration worktree was clean at sprint start.

Boundary:

- Static docs/tests only.
- No backend response delivery, no route/schema/service change, no provider
  call, no Access AI invocation, no memory/RAG/GraphRAG wiring, no H15/H-series
  runtime import, no historical diary/local_data import, no GraphQL resolver, no
  frontend runtime change, no external patient-client exposure, and no new write
  authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_view_model_d5_backend_delivery_test_plan.py tests\test_bernie_ui_view_model_d5_approval_decision_draft.py tests\test_bernie_ui_view_model_d5_response_delivery_gate.py -q
.venv\Scripts\python.exe -m py_compile tests\test_bernie_ui_view_model_d5_backend_delivery_test_plan.py
git diff --check -- docs\bernie-ui-derived-state-dag-d5-backend-delivery-test-plan.json docs\bernie-ui-derived-state-dag-d5-backend-delivery-test-plan.md tests\test_bernie_ui_view_model_d5_backend_delivery_test_plan.py
```

Result: `20 passed`; py_compile passed; existing Starlette and Google GenAI
deprecation warnings only; whitespace check passed.

Implementation commit: `abd50492`.

Sprint engine state: continuing through the user-approved Sprint 248
review-only readiness snapshot/report. Backend response delivery remains
blocked until explicit D5 approval exists.

---

## Previous Closeout - Sprint 246

| Item | Value |
|---|---|
| Batch | Sprint 246 Bernie UI D5 Approval Decision Draft |
| Integrated through | Ariadne direct implementation; Claude/Antigravity worktrees available but not invoked, and DeepSeek lane count stayed zero because this was a bounded blocked-decision artifact |
| Status | Integrated and ready to push |
| Last updated | 2026-07-09 |

## Sprint 246 What Changed

- Added `docs/bernie-ui-derived-state-dag-d5-approval-decision-draft.json`.
- Added `docs/bernie-ui-derived-state-dag-d5-approval-decision-draft.md`.
- Added `tests/test_bernie_ui_view_model_d5_approval_decision_draft.py`.
- Recorded the only proposed future approval decision name:
  `approved_for_backend_response_delivery_first_slice`.
- Kept `decision: blocked`, reviewer blank, approved contract commit blank,
  expiry blank, acknowledgement false, and every approval-scope field false.
- Restated the forbidden scope that remains closed even if a future first slice
  is approved: GraphQL, providers, Access AI, memory/RAG/GraphRAG,
  H15/H-series, historical diary material, confirm payload changes, writes,
  external patient clients, and frontend JavaScript expansion.

Worker mix:

- Claude worktree available and previously checked clean; Claude was not invoked
  because this was a small blocked-decision draft.
- Antigravity worktree available and previously checked clean; Antigravity was
  not invoked for the same reason.
- DeepSeek was not invoked; DeepSeek lane count stayed zero.
- Integration worktree was clean at sprint start.

Boundary:

- Static docs/tests only.
- No backend response delivery, no route/schema/service change, no provider
  call, no Access AI invocation, no memory/RAG/GraphRAG wiring, no H15/H-series
  runtime import, no historical diary/local_data import, no GraphQL resolver, no
  frontend runtime change, no external patient-client exposure, and no new write
  authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_view_model_d5_approval_decision_draft.py tests\test_bernie_ui_view_model_d5_response_delivery_gate.py tests\test_bernie_ui_view_model_evidence_consolidation.py -q
.venv\Scripts\python.exe -m py_compile tests\test_bernie_ui_view_model_d5_approval_decision_draft.py
git diff --check -- docs\bernie-ui-derived-state-dag-d5-approval-decision-draft.json docs\bernie-ui-derived-state-dag-d5-approval-decision-draft.md tests\test_bernie_ui_view_model_d5_approval_decision_draft.py
```

Result: `20 passed`; py_compile passed; existing Starlette and Google GenAI
deprecation warnings only; whitespace check passed.

Implementation commit: `a4573a6b`.

Sprint engine state: continuing through the user-approved Sprint 247-248
review-only block. Backend response delivery remains blocked until explicit D5
approval exists.

---

## Previous Closeout - Sprint 245

| Item | Value |
|---|---|
| Batch | Sprint 245 Bernie UI D4/D5 Evidence Consolidation |
| Integrated through | Ariadne review-only implementation with DeepSeek sidecar review; Claude/Antigravity worktrees checked clean but not invoked because this sprint only consolidated already-committed evidence |
| Status | Integrated and ready to push |
| Last updated | 2026-07-09 |

## Sprint 245 What Changed

- Added `docs/bernie-ui-derived-state-dag-evidence-consolidation.md`.
- Added `tests/test_bernie_ui_view_model_evidence_consolidation.py`.
- Consolidated D1-D5 evidence into a single review packet covering pure selector
  evidence, route-intercepted UI evidence, evidence-label limits, payload/write
  authority boundaries, and still-blocked D5 delivery surfaces.
- Restated that `BernieUiViewModel` is display-only state and carries no write
  authority.
- Recorded the next review-only sequence: Sprint 246 approval-decision draft,
  Sprint 247 backend delivery test plan, and Sprint 248 readiness snapshot.

Worker mix:

- Claude worktree checked clean; Claude was not invoked because the sprint was
  a bounded evidence-consolidation artifact.
- Antigravity worktree checked clean; Antigravity was not invoked for the same
  reason.
- DeepSeek direct-spawn sidecar reviewed the consolidation packet shape;
  Ariadne incorporated its section recommendations, then closed the lane.
  DeepSeek lane count returned to zero.
- Integration worktree was clean at sprint start.

Boundary:

- Static docs/tests only.
- No backend response delivery, no route/schema/service change, no provider
  call, no Access AI invocation, no memory/RAG/GraphRAG wiring, no H15/H-series
  runtime import, no historical diary/local_data import, no GraphQL resolver, no
  frontend runtime change, no external patient-client exposure, and no new write
  authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_view_model_evidence_consolidation.py tests\test_bernie_ui_view_model.py tests\test_bernie_ui_view_model_d5_response_delivery_gate.py -q
git diff --check -- docs\bernie-ui-derived-state-dag-evidence-consolidation.md tests\test_bernie_ui_view_model_evidence_consolidation.py
```

Result: `31 passed`; existing Starlette and Google GenAI deprecation warnings
only; whitespace check passed.

Implementation commit: `77c01756`.

Sprint engine state: continuing through the user-approved Sprint 246-248
review-only block. Backend response delivery remains blocked until explicit D5
approval exists.

---

## Previous Closeout - Sprint 244

| Item | Value |
|---|---|
| Batch | Sprint 244 Bernie UI Clarification/Identity Route-Intercepted Evidence |
| Integrated through | Ariadne test implementation with DeepSeek sidecar review; Claude/Antigravity worktrees checked clean but not invoked because this stayed inside the existing Playwright harness |
| Status | Integrated and ready to push |
| Last updated | 2026-07-09 |

## Sprint 244 What Changed

- Added `test_bernie_ui_view_model_clarification_blocks_legacy_confirmable_payload`
  to `review/test_diary_smoke.py`.
- Added `test_bernie_ui_view_model_identity_ambiguous_blocks_confirm_and_shows_choices`
  to `review/test_diary_smoke.py`.
- Proved route-intercepted `bernie.ui_view_model.v1` clarification state can
  override a legacy confirmable payload, hide selected-slot/confirm/success UI,
  and avoid confirm POSTs.
- Proved ambiguous identity state shows the identity evidence card, recognition
  prompt, and patient candidate choices while blocking proposal/confirm UI and
  avoiding write-authority copy.
- Folded in DeepSeek's sidecar recommendations for absent identity markers in
  plain clarification, absent block/candidate lists, and identity copy safety.

Worker mix:

- Claude worktree checked clean; Claude was not invoked because this was a
  bounded route-intercepted test sprint.
- Antigravity worktree checked clean; Antigravity was not invoked for the same
  reason.
- DeepSeek direct-spawn sidecar reviewed clarification/identity DOM and
  copy-safety gaps; Ariadne integrated its recommendations, then closed the
  lane. DeepSeek lane count returned to zero.
- Integration worktree was clean at sprint start.

Boundary:

- `review/test_diary_smoke.py` only.
- No frontend runtime code change, no asset bump, no backend response delivery,
  no route/schema/service change, no provider call, no Access AI invocation, no
  memory/RAG/GraphRAG wiring, no H15/H-series runtime import, no historical
  diary/local_data import, no GraphQL resolver, and no new write authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q -k "ui_view_model"
.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q -k "ui_view_model or clarification or identity"
git diff --check
```

Result: focused `ui_view_model` route-intercepted cluster `8 passed`; broader
clarification/identity route-intercepted cluster `12 passed`; whitespace check
passed.

Implementation commit: `3da57321`.

Sprint engine state: pausing before any D5 gate change or backend response
delivery; only bounded review-only work remains without explicit approval.

---

## Previous Closeout - Sprint 243

| Item | Value |
|---|---|
| Batch | Sprint 243 Bernie UI D5 Router Import Guard Plan |
| Integrated through | Ariadne direct implementation; no Claude/Antigravity/DeepSeek lanes opened because this was a bounded static guard-plan sprint |
| Status | Integrated and pushed |
| Last updated | 2026-07-09 |

## Sprint 243 What Changed

- Added `docs/bernie-ui-derived-state-dag-d5-router-import-guard-plan.md`.
- Documented that the current broad production-router selector import ban
  remains in force while the D5 response-delivery gate is blocked.
- Documented the future fine-grained guard shape if D5 is explicitly approved:
  only the reviewed Bernie response-delivery attachment point may import the
  selector, while non-Bernie routers remain blocked.
- Added guard coverage to
  `tests/test_bernie_ui_view_model_d5_response_delivery_gate.py`.

Worker mix:

- Claude worktree checked clean; Claude was not invoked because this was a
  small static guard-plan sprint.
- Antigravity worktree checked clean; Antigravity was not invoked for the same
  reason.
- DeepSeek was not invoked; DeepSeek lane count stayed zero.
- Integration worktree was clean at sprint start.

Boundary:

- Static docs/tests only.
- No backend response delivery, no route/schema/service change, no provider
  call, no Access AI invocation, no memory/RAG/GraphRAG wiring, no H15/H-series
  runtime import, no historical diary/local_data import, no GraphQL resolver, no
  frontend runtime change, and no new write authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_view_model_d5_response_delivery_gate.py tests\test_bernie_ui_view_model.py -q
git diff --check -- docs\bernie-ui-derived-state-dag-d5-router-import-guard-plan.md tests\test_bernie_ui_view_model_d5_response_delivery_gate.py
```

Result: D5 gate/import-plan + selector suite `25 passed`; whitespace check
passed.

Implementation commit: `a1d4b2df`.

Sprint engine state: pausing before any D5 gate change or backend response
delivery; only bounded review-only work remains without explicit approval.

---

## Previous Closeout - Sprint 242

| Item | Value |
|---|---|
| Batch | Sprint 242 Bernie UI D5 Implementation Checklist |
| Integrated through | Ariadne direct implementation using the already-integrated DeepSeek D5 recommendations; no Claude/Antigravity/DeepSeek lanes opened because this was a bounded checklist and gate-hygiene sprint |
| Status | Integrated and pushed |
| Last updated | 2026-07-09 |

## Sprint 242 What Changed

- Removed a duplicate `reviewer` key from
  `docs/bernie-ui-derived-state-dag-d5-response-delivery-gate.json`.
- Added a duplicate-key guard to
  `tests/test_bernie_ui_view_model_d5_response_delivery_gate.py`.
- Added `docs/bernie-ui-derived-state-dag-d5-implementation-checklist.md`, a
  static implementation checklist/test matrix for any future explicitly
  approved D5 backend-delivery slice.
- Guarded the checklist so it remains static, gate-bound, and non-authorizing.

Worker mix:

- Claude worktree checked clean; Claude was not invoked because this was a
  small checklist/gate-hygiene sprint.
- Antigravity worktree checked clean; Antigravity was not invoked for the same
  reason.
- DeepSeek was not invoked; Sprint 242 reused the just-integrated Sprint 241
  DeepSeek recommendations. DeepSeek lane count stayed zero.
- Integration worktree was clean at sprint start.

Boundary:

- Static docs/tests only.
- No backend response delivery, no route/schema/service change, no provider
  call, no Access AI invocation, no memory/RAG/GraphRAG wiring, no H15/H-series
  runtime import, no historical diary/local_data import, no GraphQL resolver, no
  frontend runtime change, and no new write authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_view_model_d5_response_delivery_gate.py tests\test_bernie_ui_view_model.py tests\test_bernie_ui_view_model_d4_preflight.py -q
git diff --check -- docs\bernie-ui-derived-state-dag-d5-response-delivery-gate.json docs\bernie-ui-derived-state-dag-d5-response-delivery-gate.md docs\bernie-ui-derived-state-dag-d5-implementation-checklist.md tests\test_bernie_ui_view_model_d5_response_delivery_gate.py
```

Result: D5 checklist/gate + selector + D4 preflight suite `30 passed`;
whitespace check passed.

Implementation commit: `3a3319d8`.

Sprint engine state: continuing only with bounded plan/review work unless Yuri
explicitly approves changing the D5 gate; all backend/provider/GraphQL/write/
memory/H15 gates remain closed.

---

## Previous Closeout - Sprint 241

| Item | Value |
|---|---|
| Batch | Sprint 241 Bernie UI Derived-State DAG D5 Response Delivery Gate |
| Integrated through | Ariadne implementation with DeepSeek sidecar review; Claude/Antigravity worktrees checked clean but not invoked because this was a bounded static gate sprint |
| Status | Integrated and pushed |
| Last updated | 2026-07-09 |

## Sprint 241 What Changed

- Added `docs/bernie-ui-derived-state-dag-d5-response-delivery-gate.json` as a
  blocked-by-default source-of-truth gate for any future backend delivery of
  `BernieUiViewModel`.
- Added `docs/bernie-ui-derived-state-dag-d5-response-delivery-gate.md` to
  explain the post-D4 posture and required readiness commands.
- Added `tests/test_bernie_ui_view_model_d5_response_delivery_gate.py`.
- Incorporated DeepSeek's recommendations for pre-D5 readiness commands,
  expected blocked/disabled values, allowed future D5 scope, forbidden runtime
  scope, pause triggers, backward-compatibility checks, and non-Bernie router
  import guards.

Worker mix:

- Claude worktree checked clean; Claude was not invoked because the sprint was a
  bounded static gate.
- Antigravity worktree checked clean; Antigravity was not invoked for the same
  bounded-gate reason.
- DeepSeek direct-spawn sidecar reviewed the D5 backend-response-delivery gate
  shape; Ariadne integrated its readiness-command, forbidden-scope, pause, and
  test-matrix recommendations, then closed the lane. DeepSeek lane count
  returned to zero.
- Integration worktree was clean at sprint start.

Boundary:

- Static gate docs/tests only.
- No backend response delivery, no route/schema/service change, no provider
  call, no Access AI invocation, no memory/RAG/GraphRAG wiring, no H15/H-series
  runtime import, no historical diary/local_data import, no GraphQL resolver,
  no frontend runtime change, and no new write authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_view_model_d5_response_delivery_gate.py tests\test_bernie_ui_view_model.py tests\test_bernie_ui_view_model_d4_preflight.py -q
git diff --check -- docs\bernie-ui-derived-state-dag-d5-response-delivery-gate.json docs\bernie-ui-derived-state-dag-d5-response-delivery-gate.md tests\test_bernie_ui_view_model_d5_response_delivery_gate.py
```

Result: D5 gate + selector + D4 preflight suite `28 passed`; whitespace check
passed.

Implementation commit: `c10f2d9a`.

Sprint engine state: continuing only with bounded plan/review work unless Yuri
explicitly approves changing the D5 gate; all backend/provider/GraphQL/write/
memory/H15 gates remain closed.

---

## Previous Closeout - Sprint 240

| Item | Value |
|---|---|
| Batch | Sprint 240 Bernie UI Derived-State DAG D4 Consumer |
| Integrated through | Ariadne implementation with DeepSeek sidecar review; Claude/Antigravity worktrees checked clean but not invoked because the slice stayed bounded to one UI file and one existing Playwright harness |
| Status | Integrated and pushed |
| Last updated | 2026-07-09 |

## Sprint 240 What Changed

- Added optional `bernie.ui_view_model.v1` consumption to the primary
  `renderBernieReview` panel in `docs/diary/diary.js`.
- Added a small response adapter that carries route-intercepted/root
  `ui_view_model` data onto the existing `staff_review` display payload without
  changing backend route schemas.
- Let the view model drive display-only transitions for candidate slots,
  proposal-ready, pressed/awaiting backend, stale, failed, and success states.
- Preserved existing signed confirm authority: `isBernieConfirmReady`,
  `confirm_endpoint`, `confirm_payload`, freshness IDs, evidence, and REST
  submit logic remain the command surface.
- Added stale warning, retry, edit, and success-copy DOM markers for D4 state
  assertions.
- Bumped `docs/diary/diary.html` from `diary.js?v=179` to `diary.js?v=180`.
- Added route-intercepted Playwright coverage proving view-model precedence,
  pending/stale/failed no-confirm behavior, recovery actions, and confirm
  payload purity.

Worker mix:

- Claude worktree checked clean; Claude was not invoked because the
  implementation remained bounded after local inspection.
- Antigravity worktree checked clean; Antigravity was not invoked for the same
  bounded-slice reason.
- DeepSeek direct-spawn sidecar `Delta` reviewed the D4 risks and acceptance
  checks; Ariadne integrated the payload-purity, precedence, and recovery-action
  recommendations, then closed the lane. DeepSeek lane count returned to zero.
- Integration worktree was clean at sprint start.

Boundary:

- `docs/diary/diary.js`, `docs/diary/diary.html`, and
  `review/test_diary_smoke.py` only.
- No backend route/schema/service change, no provider call, no Access AI
  invocation, no memory/RAG/GraphRAG wiring, no H15/H-series runtime import, no
  historical diary/local_data import, no GraphQL resolver, and no new write
  authority.

Verification:

```powershell
node --check docs\diary\diary.js
.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q -k "ui_view_model or confirm_flow_harness"
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_view_model.py tests\test_bernie_ui_view_model_d4_preflight.py -q
.venv\Scripts\python.exe scripts\check_frontend_versions.py
.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q
git diff --check -- docs\diary\diary.js docs\diary\diary.html review\test_diary_smoke.py
rg -n "ui_view_model|bernie_ui_view_model|copy_mode|confirmation_state|freshness_state|show_confirm_button|show_success_copy" docs\diary\diary.js review\test_diary_smoke.py
```

Result: JS syntax passed; focused route-intercepted D4/confirm-flow smoke
cluster `11 passed`; Python selector + D4 preflight guards `23 passed`; frontend
asset version check passed; full Diary route-intercepted Playwright harness
passed and wrote `review/diary-review.xml`; whitespace check passed; static grep
confirmed view-model field references are confined to the display adapter and
payload-purity tests.

Implementation commit: `845e6d2c`.

Sprint engine state: continuing only to a bounded post-D4 review or backend
response-delivery gate decision; all backend/provider/GraphQL/write/memory/H15
gates remain closed.

---

## Previous Closeout - Sprint 239

| Item | Value |
|---|---|
| Batch | Sprint 239 Diary/Bernie Playwright Evidence Protocol |
| Integrated through | Ariadne direct implementation; no Claude/Antigravity/DeepSeek lanes used because this was a tiny protocol/test clarification requested before D4 UI wiring |
| Status | Integrated and pushed |
| Last updated | 2026-07-09 |

## Sprint 239 What Changed

- Updated the EMR4 handover protocol to make existing Playwright/pytest review
  harnesses, especially `review/test_diary_smoke.py`, the default committed
  evidence for Diary/Bernie UI sprints.
- Clarified that Browser plugin use is supplemental for visual inspection,
  screenshots, console/debug exploration, and ambiguous rendering failures, not
  a replacement for committed route-intercepted Playwright regression evidence.
- Added a protocol guard test preserving that evidence priority.

Worker mix:

- Claude was not invoked; the sprint was a narrow protocol/test edit.
- Antigravity was not invoked.
- DeepSeek was not invoked; DeepSeek lane count stayed zero.
- Integration worktree was clean at sprint start; no worker artifacts were
  created.

Boundary:

- Protocol/docs/tests only.
- No frontend runtime code, no backend route/schema/service change, no provider
  call, no Access AI invocation, no memory/RAG/GraphRAG wiring, no H15/H-series
  runtime import, no historical diary/local_data import, no GraphQL resolver, no
  write authority, and no appointment confirmation behavior change.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_sprint_closeout_protocol.py -q
git diff --check -- AGENTS.md orchestration\protocol_alerts.md tests\test_sprint_closeout_protocol.py orchestration\sprint_closeout.md orchestration\integration_log.md
```

Result: protocol closeout suite `4 passed`; whitespace check passed with only
Git's existing CRLF normalization warning for `orchestration/integration_log.md`.

Implementation commit: `7669fa57`.

Sprint engine state: continuing after push to the narrow D4 route-intercepted
UI consumer slice if no user redirect arrives; all provider/backend/GraphQL/write
gates remain closed.

---

## Previous Closeout - Sprint 238

| Item | Value |
|---|---|
| Batch | Sprint 238 Bernie UI Derived-State DAG D4 Preflight |
| Integrated through | Ariadne direct implementation following Fable's prior verdict; no Claude/Antigravity/DeepSeek lanes used because this was a bounded preflight/review sprint |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 238 What Changed

- Added `docs/bernie-ui-derived-state-dag-d4-preflight.md`.
- Added `tests/test_bernie_ui_view_model_d4_preflight.py`.
- Defined the narrow D4 route-intercepted UI consumer slice for the primary
  `renderBernieReview` booking panel only.
- Required fixture coverage for candidate slots, proposal ready, pressed or
  awaiting backend, backend-confirmed success, stale proposal, backend rejected,
  and ambiguous identity states.
- Preserved command-payload boundaries: existing signed proposal/freshness/
  evidence fields remain the command authority, and `BernieUiViewModel` fields
  must not appear in command payloads.

Worker mix:

- Claude/Fable was not invoked; the sprint followed the existing Fable review
  artifact directly.
- Antigravity was not invoked.
- DeepSeek was not invoked; DeepSeek lane count stayed zero.
- Integration worktree was clean at sprint start; no worker artifacts were
  created.

Boundary:

- Preflight/review artifact and tests only.
- No edits to `docs/diary/diary.js`, no UI wiring, no backend response wiring,
  no route/schema change, no provider call, no Access AI invocation, no
  memory/RAG/GraphRAG wiring, no H15/H-series runtime import, no historical
  diary/local_data import, no GraphQL resolver, no write authority, and no
  appointment confirmation behavior change.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_view_model_d4_preflight.py tests\test_bernie_ui_view_model_d3_inventory.py tests\test_bernie_ui_view_model.py -q
.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_guard.py docs\bernie-ui-derived-state-dag-d4-preflight.md
git diff --check -- docs\bernie-ui-derived-state-dag-d4-preflight.md tests\test_bernie_ui_view_model_d4_preflight.py
```

Result: D4 preflight + D3 inventory + selector suite `28 passed`; proposal
guard and whitespace check passed.

Implementation commit: `ee3991a9`.

Sprint engine state: continuing to the narrow D4 route-intercepted UI consumer
slice if no user redirect arrives; all provider/backend/GraphQL/write gates
remain closed.

---

## Previous Closeout - Sprint 237

| Item | Value |
|---|---|
| Batch | Sprint 237 Bernie UI Derived-State DAG D3 Inventory |
| Integrated through | Ariadne direct implementation following Fable's prior verdict; no Claude/Antigravity/DeepSeek lanes used because this was a bounded inventory/review sprint |
| Status | Integrated and ready to push |
| Last updated | 2026-07-08 |

## Sprint 237 What Changed

- Added `docs/bernie-ui-derived-state-dag-d3-inventory.md`.
- Added `tests/test_bernie_ui_view_model_d3_inventory.py`.
- Mapped current `docs/diary/diary.js` switch points to future
  `BernieUiViewModel` fields, including `BERNIE_STATUS_COPY`,
  `BERNIE_HEADLINE_COPY`, `scrubBernieStaffCopy`, `bernieReviewTransition`,
  status/headline/action copy helpers, `createBernieServerSessionBanner`,
  `bernieComposerPlaceholder`, `renderBernieReview`,
  `handleBernieConfirmShortcut`, and the `bernie-review-confirm-button` branch.
- Preserved the command boundary: confirm command payloads must continue using
  existing signed proposal/freshness/evidence fields and must not consume
  display view-model fields.

Worker mix:

- Claude/Fable was not invoked; the sprint followed the existing Fable review
  artifact directly.
- Antigravity was not invoked.
- DeepSeek was not invoked; DeepSeek lane count stayed zero.
- Integration worktree was clean at sprint start; no worker artifacts were
  created.

Boundary:

- Inventory/review artifact and tests only.
- No edits to `docs/diary/diary.js`, no UI wiring, no route/response wiring for
  `BernieUiViewModel`, no provider call, no Access AI invocation, no
  memory/RAG/GraphRAG wiring, no H15/H-series runtime import, no historical
  diary/local_data import, no GraphQL resolver, no write authority, and no
  appointment confirmation behavior change.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_view_model_d3_inventory.py tests\test_bernie_ui_view_model.py -q
.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_guard.py docs\bernie-ui-derived-state-dag-d3-inventory.md
git diff --check -- docs\bernie-ui-derived-state-dag-d3-inventory.md tests\test_bernie_ui_view_model_d3_inventory.py
```

Result: inventory + selector suite `22 passed`; proposal guard and whitespace
check passed.

Implementation commit: `900ee253`.

Sprint engine state: continuing to a D4 preflight/review packet before any UI
consumer wiring.

---

## Previous Closeout - Sprint 236

| Item | Value |
|---|---|
| Batch | Sprint 236 Bernie UI Derived-State DAG D1/D2 Selector |
| Integrated through | Ariadne direct implementation following Fable's prior verdict; no Claude/Antigravity/DeepSeek lanes used because this was a bounded pure selector/test sprint |
| Status | Integrated and ready to push |
| Last updated | 2026-07-08 |

## Sprint 236 What Changed

- Amended `docs/bernie-ui-derived-state-dag-plan.md` with Fable's required D2
  constraints: bind `session_phase` to `BernieSessionState`, anchor input to
  `BernieSessionSnapshotOut`, source-tag node values, keep `copy_mode` derived,
  fail closed on unknown enums, keep success backend-confirmed only, and emit no
  write-echo fields.
- Added `app/services/bernie/ui_view_model.py`, a pure display selector that
  maps a Bernie session snapshot plus explicit client-transient confirmation
  request state to a `BernieUiViewModel`.
- Added authored synthetic fixtures in
  `tests/fixtures/bernie_ui_view_model/cases.json`.
- Added `tests/test_bernie_ui_view_model.py` covering fixture projections,
  confirmation-state conditioning across unrelated UI flags, backend-confirmed
  only success copy, negative pre-confirm copy, fail-closed unknown enums,
  no write-echo schema fields, no provider/route/DB/memory/H15/trove imports,
  and no production route imports yet.

Worker mix:

- Claude/Fable was not invoked; the sprint followed the existing Fable review
  artifact directly.
- Antigravity was not invoked.
- DeepSeek was not invoked; DeepSeek lane count stayed zero.
- Integration worktree was clean at sprint start; no worker artifacts were
  created.

Boundary:

- Pure backend contract selector, synthetic fixtures, plan amendment, and tests
  only.
- No route mount or response wiring, UI consumer wiring, provider call, Access
  AI invocation, memory/RAG/GraphRAG wiring, H15/H-series runtime import,
  historical diary/local_data import, GraphQL resolver, write authority, or
  appointment confirmation behavior change.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_ui_view_model.py -q
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_guard.py docs\bernie-ui-derived-state-dag-plan.md
.venv\Scripts\python.exe -m py_compile app\services\bernie\ui_view_model.py tests\test_bernie_ui_view_model.py
git diff --check -- app\services\bernie\ui_view_model.py tests\test_bernie_ui_view_model.py tests\fixtures\bernie_ui_view_model\cases.json docs\bernie-ui-derived-state-dag-plan.md
```

Result: selector suite `17 passed`; readiness check stayed
`runtime_or_provider_wiring_ready=false`, `raw_trove_access_ready=false`,
`runtime_gate_decision=blocked`; provider-boundary report stayed
`default_provider=disabled`, `live_provider_enabled=false`,
`provider_calls_performed=false`, `route_behavior_changed=false`,
`database_access_performed=false`, `memory_or_rag_access_performed=false`, and
`historical_diary_material_access_performed=false`; proposal guard, py_compile,
and whitespace checks passed.

Implementation commit: `3ff5838a`.

Sprint engine state: continuing to D3 inventory/review only; D4 UI wiring waits
for a separate reviewed route-intercepted UI consumer sprint.

---

## Previous Closeout - Sprint 235

| Item | Value |
|---|---|
| Batch | Sprint 235 API Spine Practitioner Directory Post-Implementation Readiness Review |
| Integrated through | Ariadne direct implementation; no Claude/Antigravity/DeepSeek lanes used because this was a bounded artifact/test review sprint |
| Status | Integrated and ready to push |
| Last updated | 2026-07-08 |

## Sprint 235 What Changed

- Added
  `docs/api-spine/practitioner-directory-post-implementation-readiness-review.json`
  and `.md`.
- Recorded that the bounded practitioner-directory REST first slice at
  implementation commit `5b3b9102` is implemented and runtime-tested.
- Preserved blocked posture for `rest_route_ready`, `graphql_resolver_ready`,
  `external_read_model_runtime_ready`, `runtime_or_memory_ready`,
  `provider_or_directory_runtime_ready`, `write_authority_ready`, deployment
  readiness, and production readiness.
- Added
  `tests/test_practitioner_directory_post_implementation_readiness_review.py`
  to guard the decision, runtime evidence checklist, unchanged blocked
  readiness snapshot, and forbidden scope expansions.

Worker mix:

- Claude/Fable was not invoked; prior Fable verdict remains binding.
- Antigravity was not invoked.
- DeepSeek was not invoked; DeepSeek lane count stayed zero.
- Integration worktree was clean at sprint start; no worker artifacts were
  created.

Boundary:

- Review artifact and static/runtime guard tests only.
- No readiness snapshot flag change, SDL edit, GraphQL resolver, provider call,
  Access AI invocation, memory/RAG/GraphRAG wiring, H15/H-series runtime import,
  historical diary/local_data import, write authority, audit write, deployment
  claim, production claim, or external patient-client exposure.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_post_implementation_readiness_review.py tests\test_practitioner_directory_route.py tests\test_api_spine_external_read_model_readiness_dag.py tests\test_external_read_model_readiness_status.py -q
git diff --check -- docs\api-spine\practitioner-directory-post-implementation-readiness-review.json docs\api-spine\practitioner-directory-post-implementation-readiness-review.md tests\test_practitioner_directory_post_implementation_readiness_review.py
```

Result: focused review/route/readiness suite `52 passed`; whitespace check
clean.

Implementation commit: `de81111e`.

Sprint engine state: continuing to Fable-approved Bernie UI derived-state DAG
D1/D2 only; no practitioner-directory readiness expansion without separate
review.

---

## Previous Closeout - Sprint 234

| Item | Value |
|---|---|
| Batch | Sprint 234 API Spine Practitioner Directory Approval Gate DAG Wiring |
| Integrated through | Ariadne implementation with Antigravity CLI, DeepSeek direct-spawn sidecar review, and extra DeepSeek substitution for Claude session limit |
| Status | Integrated and ready to push |
| Last updated | 2026-07-08 |

## Sprint 234 What Changed

- Added
  `practitioner_directory_approval_gate` to
  `docs/api-spine/external-read-model-readiness-dag.json` as a static
  `approval_gate` node between `combined_readiness_review` and
  `rest_route_wiring`.
- Updated `scripts/external_read_model_readiness_status.py` and
  `tests/fixtures/api_spine_external_readiness/blocked_readiness_status.json`
  with safe aggregate approval-gate fields:
  `approval_gate_node_count: 1`, `approval_gate_decision: blocked`,
  `approval_gate_artifact_present: true`, and
  `approval_gate_runtime_authority: false`.
- Updated `tests/test_api_spine_external_read_model_readiness_dag.py` and
  `tests/test_external_read_model_readiness_status.py` to guard the new node,
  rerouted edges, sprint metadata, closed-gate additions, and blocked aggregate
  posture.
- Runtime state remains blocked: no approved gate, no REST route, no SDL change,
  no GraphQL dependency/resolver, no runtime schema, no shared read service, no
  database query or migration, no audit write, no provider, no
  memory/RAG/GraphRAG, no H15/H-series runtime import, no external client, no
  GraphQL mutation, no readiness flag change, and no write authority.

Worker mix:

- Claude was called through `scripts\drive_agent_headless.py` / the Claude CLI.
  It remained session-limited, so Ariadne recorded the unavailability and
  spawned an extra DeepSeek lane to cover the missing review work.
- Antigravity was called through the `agy.exe` CLI and produced a tangible
  review artifact. Ariadne incorporated its recommendation to add a static
  approval-gate node while preserving blocked runtime posture.
- DeepSeek was called through direct Codex `deepseek-worker` spawning and
  recommended routing the DAG through `practitioner_directory_approval_gate`
  before `rest_route_wiring`. A second DeepSeek lane was spawned as Claude
  substitution and supplied an alternate pre-combined topology; Ariadne kept the
  post-combined approval gate path because it reflects the gate between planning
  readiness and runtime wiring.
- Worker cleanliness was checked during the sprint. Integration was clean at
  start; Claude and Antigravity were clean at sprint start; Claude and
  Antigravity worker artifacts were cleaned after integration; DeepSeek has zero
  open lanes after closeout cleanup/realignment.

Boundary:

- Static DAG/readiness-status documentation, snapshot, script, and tests only.
- No approved gate, REST route, SDL edit, GraphQL runtime dependency, GraphQL
  resolver, GraphQL mutation, runtime schema, database query/join/migration,
  shared read service, audit write/migration, rate-limiter, field encryption,
  RLS policy, provider call, provider dry-run, Access AI invocation,
  RAG/GraphRAG/memory wiring, H15/H-series runtime import, broad historical diary
  trove mining, external patient client, runtime FGA client, write authority,
  model-to-database write authority, readiness flag change, or raw compatibility
  deprecation mode change.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_external_read_model_readiness_dag.py tests\test_external_read_model_readiness_status.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_external_read_model_readiness_dag.py tests\test_external_read_model_readiness_status.py tests\test_practitioner_directory_approval_gate_static.py tests\test_api_spine_practitioner_directory_route_breakdown_readiness_decision.py tests\test_api_spine_practitioner_directory_sdl_resolution_proposal.py tests\test_api_spine_practitioner_directory_security_audit_preflight.py tests\test_api_spine_practitioner_directory_rest_graphql_drift_contract.py tests\test_api_spine_practitioner_directory_graphql_resolver_ownership_plan.py tests\test_api_spine_practitioner_directory_implementation_proposal.py tests\test_api_spine_external_read_model_ownership_consolidation.py tests\test_api_spine_patient_messages_ownership_candidate.py tests\test_api_spine_patient_reminders_ownership_candidate.py tests\test_api_spine_practitioner_directory_ownership_candidate.py tests\test_api_spine_external_read_model_implementation_planning_review.py tests\test_api_spine_external_read_model_combined_readiness_review.py tests\test_api_spine_directory_read_shape_design.py tests\test_api_spine_directory_source_licensing_review.py tests\test_api_spine_patient_messages_read_shape_design.py tests\test_api_spine_patient_reminders_read_shape_design.py tests\test_api_spine_practitioner_directory_read_shape_design.py tests\test_api_spine_external_read_model_gap_inventory.py tests\test_external_read_model_gap_status.py tests\test_api_spine_external_router_read_root_inventory.py -q
git diff --check -- docs\api-spine\external-read-model-readiness-dag.json scripts\external_read_model_readiness_status.py tests\fixtures\api_spine_external_readiness\blocked_readiness_status.json tests\test_api_spine_external_read_model_readiness_dag.py tests\test_external_read_model_readiness_status.py
```

Result: focused DAG/status suite `16 passed`; broader external/practitioner
static suite `197 passed`; whitespace check clean.

Implementation commit: `ad6c762e`.

Sprint engine state: pausing after push for Yuri's runtime implementation
review, per Yuri's request.

---

## Previous Closeout - Sprint 233

| Item | Value |
|---|---|
| Batch | Sprint 233 API Spine Practitioner Directory REST Route Approval-Decision Draft |
| Integrated through | Ariadne implementation with Antigravity CLI, DeepSeek direct-spawn sidecar review, and extra DeepSeek substitution for Claude session limit |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 233 What Changed

- Added
  `docs/api-spine/practitioner-directory-approval-payload-draft.json`, a
  blocked-by-default approval payload draft for the future
  `GET /api/v1/practice/practitioners` go/no-go.
- Added `docs/api-spine/practitioner-directory-approval-decision.md`.
- Added `tests/test_practitioner_directory_approval_gate_static.py`.
- Verification: focused approval-gate static suite `10 passed`; broader
  external read-model static suite `196 passed`; whitespace check clean.
- Implementation commit: `3ac7eee2`; closeout commit `a011c8fd`.

---

## Previous Closeout - Sprint 232

| Item | Value |
|---|---|
| Batch | Sprint 232 API Spine Practitioner Directory Route Implementation Breakdown Readiness Decision |
| Integrated through | Ariadne implementation with Claude CLI, Antigravity CLI, and DeepSeek direct-spawn sidecar review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 232 What Changed

- Added
  `docs/api-spine/practitioner-directory-route-implementation-breakdown-readiness-decision.md`,
  a static implementation breakdown/readiness decision packet for the future
  `GET /api/v1/practice/practitioners` route.
- Added
  `tests/test_api_spine_practitioner_directory_route_breakdown_readiness_decision.py`.
- Verification: focused route-breakdown readiness suite `11 passed`; broader
  external read-model static suite `186 passed`; whitespace check clean.
- Implementation commit: `c817067e`; closeout commit `0598c468`.

---

## Previous Closeout - Sprint 231

| Item | Value |
|---|---|
| Batch | Sprint 231 API Spine Practitioner Directory SDL Pagination/DefaultLocation Resolution Proposal |
| Integrated through | Ariadne implementation with Claude CLI, Antigravity CLI, and DeepSeek direct-spawn sidecar review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 231 What Changed

- Added
  `docs/api-spine/practitioner-directory-sdl-pagination-default-location-resolution-proposal.md`,
  a static SDL-resolution proposal for the two Sprint 229
  `known_and_blocked_drift` items.
- Added `tests/test_api_spine_practitioner_directory_sdl_resolution_proposal.py`.
- Verification: focused SDL-resolution proposal suite `13 passed`; broader
  external read-model static suite `175 passed`; whitespace check clean.
- Implementation commit: `ad2d9c42`; closeout commit `c18c31d4`.

---

## Previous Closeout - Sprint 230

| Item | Value |
|---|---|
| Batch | Sprint 230 API Spine Practitioner Directory Security/Audit Test Harness Preflight |
| Integrated through | Ariadne implementation with Claude CLI, Antigravity CLI, and DeepSeek direct-spawn sidecar review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 230 What Changed

- Added
  `docs/api-spine/practitioner-directory-security-audit-test-harness-preflight.md`,
  a static security/audit preflight for the future first REST practitioner
  directory route.
- Added
  `tests/test_api_spine_practitioner_directory_security_audit_preflight.py`.
- Verification: focused security/audit preflight suite `14 passed`; broader
  external read-model static suite `162 passed`; whitespace check clean.
- Implementation commit: `aa48ccfc`; closeout commit `3cf81f0b`.

---

## Previous Closeout - Sprint 229

| Item | Value |
|---|---|
| Batch | Sprint 229 API Spine Practitioner Directory REST/GraphQL Drift Contract |
| Integrated through | Ariadne implementation with Claude CLI, Antigravity CLI, and DeepSeek direct-spawn sidecar review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 229 What Changed

- Added
  `docs/api-spine/practitioner-directory-rest-graphql-drift-contract.md`, a
  static parity contract between the future REST `PractitionerOut` and future
  GraphQL `Practitioner` projection.
- Added
  `tests/test_api_spine_practitioner_directory_rest_graphql_drift_contract.py`.
- Verification: focused drift contract suite `12 passed`; broader external
  read-model static suite `148 passed`; whitespace check clean.
- Implementation commit: `ad58563a`; closeout commit `b08e89a1`.

---

## Previous Closeout - Sprint 228

| Item | Value |
|---|---|
| Batch | Sprint 228 API Spine Practitioner Directory GraphQL Resolver Ownership Plan |
| Integrated through | Ariadne implementation with Claude CLI, Antigravity CLI, and DeepSeek direct-spawn sidecar review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 228 What Changed

- Added
  `docs/api-spine/practitioner-directory-graphql-resolver-ownership-plan.md`,
  a static GraphQL ownership/authorization plan for future
  `Query.practice.practitioners`.
- Added
  `tests/test_api_spine_practitioner_directory_graphql_resolver_ownership_plan.py`.
- Verification: focused GraphQL plan suite `12 passed`; broader external
  read-model static suite `136 passed`; whitespace check clean.
- Implementation commit: `c9dc54bb`; closeout commit `998481ff`.

---

## Previous Closeout - Sprint 227

| Item | Value |
|---|---|
| Batch | Sprint 227 API Spine Practitioner Directory First-Runtime Proposal Gate |
| Integrated through | Ariadne implementation with Claude CLI, Antigravity CLI, and DeepSeek direct-spawn sidecar review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 227 What Changed

- Added
  `docs/api-spine/practitioner-directory-first-runtime-implementation-proposal.md`,
  a static implementation-proposal gate for the first candidate runtime read
  route, `GET /api/v1/practice/practitioners`.
- Added
  `tests/test_api_spine_practitioner_directory_implementation_proposal.py`.
- Verification: focused proposal suite `9 passed`; broader external read-model
  static suite `124 passed`; whitespace check clean.
- Implementation commit: `ad5b8e5d`; closeout commit `7231d42c`.

---

## Previous Closeout - Sprint 226

| Item | Value |
|---|---|
| Batch | Sprint 226 API Spine External Read-Model Ownership Consolidation Preflight |
| Integrated through | Ariadne implementation with Claude CLI, Antigravity CLI, and DeepSeek direct-spawn sidecar review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 226 What Changed

- Added
  `docs/api-spine/external-read-model-ownership-consolidation-preflight.md`,
  a static consolidation/go/no-go preflight across the three ownership
  candidates from Sprints 223-225.
- Added
  `tests/test_api_spine_external_read_model_ownership_consolidation.py`.
- Verification: focused consolidation suite `7 passed`; broader external
  read-model static suite `115 passed`; whitespace check clean.
- Implementation commit: `8abf5531`; closeout commit `da60751c`.

---

## Previous Closeout - Sprint 225

| Item | Value |
|---|---|
| Batch | Sprint 225 API Spine Patient Messages Ownership Candidate |
| Integrated through | Ariadne implementation with Claude CLI, Antigravity CLI, and DeepSeek direct-spawn sidecar review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 225 What Changed

- Added
  `docs/api-spine/patient-messages-route-schema-ownership-candidate.md`,
  a static route/schema ownership candidate packet for
  `Query.patient.messages`.
- Added `tests/test_api_spine_patient_messages_ownership_candidate.py`.
- Verification: focused messages/read-shape suite `15 passed`; broader external
  read-model static suite `108 passed`; whitespace check clean.
- Implementation commit: `77567098`; closeout commit `aae92286`.

---

## Previous Closeout - Sprint 224

| Item | Value |
|---|---|
| Batch | Sprint 224 API Spine Patient Reminders Ownership Candidate + Sprint Ritual Protocol Repair |
| Integrated through | Ariadne implementation with Claude CLI, Antigravity CLI, and DeepSeek direct-spawn sidecar review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 224 What Changed

- Added
  `docs/api-spine/patient-reminders-route-schema-ownership-candidate.md`,
  a static route/schema ownership candidate packet for
  `Query.patient.reminders`.
- Updated `AGENTS.md` and `orchestration/protocol_alerts.md` so every
  sprint-start ritual must announce each worker's invocation mode and worker
  cleanliness state.
- Added `tests/test_api_spine_patient_reminders_ownership_candidate.py` and
  `docs/sprint-204-223-summary.html`.
- Verification: focused ownership candidate suite `7 passed`; broader external
  read-model static suite `101 passed`; whitespace check clean.
- Implementation/protocol commit: `92470dbf`; closeout commit `8bb50686`.

---

## Previous Closeout - Sprint 223

| Item | Value |
|---|---|
| Batch | Sprint 223 API Spine Practitioner Directory Ownership Candidate |
| Integrated through | Ariadne implementation with DeepSeek sidecar review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 223 What Changed

- Added
  `docs/api-spine/practitioner-directory-route-schema-ownership-candidate.md`,
  a static route/schema ownership candidate packet for
  `Query.practice.practitioners`.
- The candidate proposes, without approving, `GET /api/v1/practice/practitioners`,
  new `app/routers/practice.py`, new `app/schemas/practice.py::PractitionerOut`,
  authenticated practice scoping, candidate pagination values, deterministic
  ordering, empty-result behavior, inactive-inclusion review, and sensitive
  field exclusions.
- Added `tests/test_api_spine_practitioner_directory_ownership_candidate.py`,
  guarding the candidate-only posture, absence of current route/schema code,
  model evidence boundaries, auth/scoping/pagination/test prerequisites, closed
  gates, and blocked readiness snapshot posture.
- Verification: focused ownership/planning/status suite `22 passed`; broader
  external read-model static suite `94 passed`; whitespace check clean.
- Implementation commit: `30e91b8d`.

---

## Previous Closeout - Sprint 222

| Item | Value |
|---|---|
| Batch | Sprint 222 API Spine External Read-Model Implementation Planning Review |
| Integrated through | Ariadne implementation with DeepSeek sidecar review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 222 What Changed

- Added
  `docs/api-spine/external-read-model-implementation-planning-review.md`, a
  static planning review before any external read-model REST/GraphQL work.
- Defined route/schema/resolver ownership prerequisites,
  authorization/scoping/pagination/error requirements, candidate sequence, and
  test gates.
- Verification: focused planning/status suite `15 passed`; broader external
  read-model static suite `87 passed`; whitespace check clean.
- Implementation commit: `3ae88570`.

---

## Previous Closeout - Sprint 216

| Item | Value |
|---|---|
| Batch | Sprint 216 API Spine External Read-Model Readiness DAG |
| Integrated through | Ariadne implementation with DeepSeek/Shen sidecar review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 216 What Changed

- Added `docs/api-spine/external-read-model-readiness-dag.json`, a static
  Directed Acyclic Graph snapshot for external read-model readiness.
- The DAG connects the external gap inventory, safe aggregate gap checker,
  completed practitioner/reminder design packets, pending patient messages
  design, pending RACGP/Cochrane source review, combined readiness review, and
  still-blocked runtime gates for REST route wiring, GraphQL resolver wiring,
  and provider/memory/external-client use.
- Added `tests/test_api_spine_external_read_model_readiness_dag.py`, proving the
  graph has the expected nodes/edges, is acyclic, keeps every readiness flag
  false, gives no node runtime authority, requires future nodes to stay blocked,
  and preserves closed gates including no runtime graph execution and no
  GraphRAG runtime wiring.
- Extended the sprint protocol in `AGENTS.md` and
  `orchestration/protocol_alerts.md`: every sprint start must explicitly name
  Claude, Antigravity, and DeepSeek use/non-use; state why any lane is not used;
  announce any extra DeepSeek substitution for usage-limited Claude/Antigravity;
  state the current DeepSeek lane count; close completed/idle lanes; and reuse
  a coherent open DeepSeek lane for related follow-on work when appropriate.
- Extended `tests/test_bernie_interpretation_protocol_alert.py` so the new
  worker-mix and DeepSeek lane-count/reuse ritual is guarded.

Worker mix:

- Claude was not used because this was a narrow static readiness/DAG packet,
  not a budget-heavy architecture or implementation lane.
- Antigravity was not used because the sprint had no UI/workflow artifact or
  frontend/product interaction surface.
- DeepSeek/Shen was used as the independent sidecar and recommended a more
  elaborate script-plus-snapshot readiness graph; Ariadne integrated a smaller
  JSON-first DAG now and left the script/snapshot promotion as a possible next
  sprint.
- Existing completed DeepSeek/Delta sidecars from Sprints 213-216 were closed
  after their outputs were captured. The next sprint-start announcement must
  state the current DeepSeek lane count and reuse/cleanup plan before spawning
  more workers.

Boundary:

- Static JSON DAG, protocol documentation, and tests only.
- No runtime graph engine, no GraphRAG, no GraphQL resolver, no GraphQL
  mutation, no REST route, no database query, no provider call, no provider
  dry-run wiring, no runtime FGA client, no external patient client, no
  H15/H-series runtime import, no memory/RAG runtime wiring, no broad historical
  diary trove mining, no Access AI invocation, no write authority, no
  model-to-database write authority, and no raw compatibility deprecation mode
  change.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_external_read_model_readiness_dag.py tests\test_bernie_interpretation_protocol_alert.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_external_read_model_readiness_dag.py tests\test_api_spine_patient_reminders_read_shape_design.py tests\test_api_spine_practitioner_directory_read_shape_design.py tests\test_api_spine_external_read_model_gap_inventory.py tests\test_external_read_model_gap_status.py tests\test_bernie_interpretation_protocol_alert.py -q
git diff --check -- docs\api-spine\external-read-model-readiness-dag.json tests\test_api_spine_external_read_model_readiness_dag.py AGENTS.md orchestration\protocol_alerts.md tests\test_bernie_interpretation_protocol_alert.py
```

Result: DAG/protocol suite `11 passed`; broader external read-model static
suite plus protocol alerts `42 passed`; whitespace check clean.

Implementation commit: `6125d6e2`.

Sprint engine state: continuing after push. No user intervention is required;
next recommended direction is a non-runtime `Query.patient.messages`
read-shape design packet or script-plus-snapshot external readiness checker.

---

## Previous Closeout - Sprint 215

| Item | Value |
|---|---|
| Batch | Sprint 215 API Spine Patient Reminders Read-Shape Design |
| Integrated through | Ariadne implementation with DeepSeek/Delta sidecar review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 215 What Changed

- Added `docs/api-spine/patient-reminders-read-shape-design.md`, a static
  design packet for the `Query.patient.reminders` route-and-shape gap.
- Mapped the SDL `PatientReminder` shape to current `Reminder` model facts:
  `id` direct, `dueAt` from date-only `due_date` with an explicit
  date-to-DateTime gap, `summary` as a derived/truncated display-safe projection
  from raw `message`/`reminder_type`, and `status` from `is_dismissed` with an
  incomplete enum gap because `COMPLETED` has no current model state.
- Documented current backing evidence: `Reminder` has practice and patient
  indexes, while current patient/clinical routers expose no reminder read route
  and current schemas expose no patient reminder summary shape.
- Captured future route requirements for any later implementation sprint:
  authenticated patient-scoped GET, `current_user.practice_id` and patient
  ownership checks, summary-only display fields, documented date conversion,
  fail-closed or unreachable `COMPLETED` handling, deterministic ordering,
  bounded result policy, no raw message exposure, and no dismissal/create/
  complete/escalate mutation authority.
- Added `tests/test_api_spine_patient_reminders_read_shape_design.py`,
  validating the packet against the SDL, `Reminder` model fields, patient and
  clinical router source, patient schemas, existing gap inventory, and closed
  gates.

Worker mix:

- DeepSeek/Delta completed a bounded sidecar review and sharpened the design
  around `derive_truncate` summary semantics, incomplete `COMPLETED` status,
  raw-message PHI risk, and date/timezone conversion risk. Ariadne kept Sprint
  215 design-only because current gates do not authorize route/schema/runtime
  work.
- Claude was not used because this sprint was a narrow static design packet and
  the independent reminder-shape review was already covered by the DeepSeek lane.
- Antigravity was not used because this sprint had no UI/product interaction
  surface and no separate frontend or workflow artifact to review.
- No extra DeepSeek substitution was needed because neither unused lane was
  skipped due to a usage-limit or quota failure; the sprint scope was deliberately
  small enough for Ariadne plus one DeepSeek/Delta sidecar.

Boundary:

- Static design packet and parser/source tests only.
- No Pydantic runtime schema, no REST patient reminder route, no GraphQL
  resolver, no GraphQL mutation, no database query, no provider call, no
  provider dry-run wiring, no runtime FGA client, no external patient client,
  no H15/H-series runtime import, no memory/RAG/GraphRAG, no broad historical
  diary trove mining, no Access AI invocation, no reminder create/update/
  dismiss/complete/escalate command, no result-triage or recall-policy write
  authority, no model-to-database write authority, and no raw compatibility
  deprecation mode change.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_patient_reminders_read_shape_design.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_patient_reminders_read_shape_design.py tests\test_api_spine_practitioner_directory_read_shape_design.py tests\test_api_spine_external_read_model_gap_inventory.py tests\test_external_read_model_gap_status.py -q
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_protocol_alert.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_patient_reminders_read_shape_design.py tests\test_api_spine_practitioner_directory_read_shape_design.py tests\test_api_spine_external_read_model_gap_inventory.py tests\test_external_read_model_gap_status.py tests\test_bernie_interpretation_protocol_alert.py -q
git diff --check -- docs\api-spine\patient-reminders-read-shape-design.md tests\test_api_spine_patient_reminders_read_shape_design.py
```

Result: focused patient reminders design test `8 passed`; combined reminders/
practitioner/gap inventory/gap status suite `31 passed`; protocol alert guard
`4 passed`; combined design/gap/protocol suite `35 passed` when rerun serially.
One earlier parallel combined run failed during shared Postgres enum setup with
duplicate `userrole`, consistent with the known test process concurrency race
rather than Sprint 215 behavior. Whitespace check clean.

Implementation commit: `a8a8ed50`.

Sprint engine state: continuing after push. No user intervention is required;
next recommended direction is either a combined external read-model readiness
snapshot or a non-runtime design packet for `Query.patient.messages`.

---

## Previous Closeout - Sprint 214

| Item | Value |
|---|---|
| Batch | Sprint 214 API Spine Practitioner Directory Read-Shape Design |
| Integrated through | Ariadne implementation with DeepSeek sidecar review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 214 What Changed

- Added `docs/api-spine/practitioner-directory-read-shape-design.md`, a static
  design packet for the `Query.practice.practitioners` route gap.
- Mapped the SDL `Practitioner` shape to current model facts:
  `id` direct, `displayName` derived from first/last name, `roleLabel` as an
  optional `specialty` mapping with a documented mismatch, `active` from
  `is_active`, and `defaultLocation` as a linked read gap through
  `default_location_id`.
- Documented current supporting context reads from diary template and roster,
  while making clear they are not practitioner-directory coverage.
- Captured future route requirements for any later implementation sprint:
  authenticated practice-scoped GET, `current_user.practice_id` filtering,
  default active-only behavior, display-safe fields only, same-practice
  default-location projection, deterministic ordering, bounded result policy,
  and no provider/RAG/Access AI/external-client authority.
- Added `tests/test_api_spine_practitioner_directory_read_shape_design.py`,
  validating the packet against the SDL, tenancy model fields, diary/auth
  router source, diary schemas, existing gap inventory, and closed gates.

Worker mix:

- DeepSeek completed a bounded sidecar review and recommended the same
  SDL/model mapping plus future route properties. It also suggested adding a
  schema next; Ariadne kept Sprint 214 design-only because current gates do not
  authorize route/schema/runtime work.

Boundary:

- Static design packet and parser/source tests only.
- No Pydantic runtime schema, no REST practitioner directory route, no GraphQL
  resolver, no GraphQL mutation, no database query, no provider call, no
  provider dry-run wiring, no runtime FGA client, no external patient client,
  no H15/H-series runtime import, no memory/RAG/GraphRAG, no broad historical
  diary trove mining, no Access AI invocation, no practitioner create/update
  command, no appointment/roster/schedule/diary write authority, no
  model-to-database write authority, and no raw compatibility deprecation mode
  change.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_practitioner_directory_read_shape_design.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_practitioner_directory_read_shape_design.py tests\test_api_spine_external_read_model_gap_inventory.py tests\test_external_read_model_gap_status.py -q
git diff --check -- docs\api-spine\practitioner-directory-read-shape-design.md tests\test_api_spine_practitioner_directory_read_shape_design.py
```

Result: focused practitioner design test `7 passed`; combined practitioner
design/gap inventory/gap status suite `23 passed`; whitespace check clean.

Implementation commit: `db98e742`.

Sprint engine state: continuing after push. No user intervention is required;
next recommended direction is either a combined external read-model readiness
snapshot or a non-runtime design packet for `Query.patient.reminders`.

---

## Previous Closeout - Sprint 213

| Item | Value |
|---|---|
| Batch | Sprint 213 API Spine External Read-Model Gap Status Checker |
| Integrated through | Ariadne implementation with DeepSeek sidecar review; Claude/Antigravity not escalated beyond non-blocking availability because the checker was narrow |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 213 What Changed

- Added `scripts/external_read_model_gap_status.py`, an importable CLI checker
  for `docs/api-spine/external-router-read-model-gap-inventory.md`.
- The checker validates the five Sprint 212 gap rows directly from markdown:
  expected surface set, all route sources still `none`, coverage counts
  (`model_only=3`, `none=2`), gap-posture counts (`route_gap=1`,
  `route_and_shape_gap=2`, `source_and_licensing_gap=2`), and all closed-gate
  phrases.
- The CLI emits only safe aggregate status fields: counts, schema labels,
  `sprint_engine_state: continuing`, `pause_required: false`, and false
  readiness flags for GraphQL resolvers, REST routes, provider/directory
  runtime, memory/runtime, write authority, and raw-compat mode changes.
- Added `tests/test_external_read_model_gap_status.py`, including exact
  safe-output assertions and negative drift tests for added surfaces, route
  source claims, coverage drift, gap-posture drift, and removed closed gates.
- Updated the gap inventory doc to reference the new safe aggregate checker.

Worker mix:

- DeepSeek completed a bounded sidecar review and recommended a heavier JSON
  gate. Ariadne kept this sprint lean by validating the markdown source
  directly, avoiding a second source of truth while preserving fail-closed
  aggregate output.

Boundary:

- Static checker/report and tests only.
- No GraphQL resolvers, no new REST routes, no provider calls, no provider
  dry-run wiring, no runtime FGA clients, no external patient clients, no
  H15/H-series runtime imports, no memory/RAG/GraphRAG, no broad historical
  diary trove mining, no Access AI invocation wiring, no practitioner/reminder/
  message/SMS/directory write authority, no model-to-database write authority,
  and no raw compatibility deprecation mode change.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_external_read_model_gap_status.py -q
.venv\Scripts\python.exe scripts\external_read_model_gap_status.py
.venv\Scripts\python.exe -m pytest tests\test_external_read_model_gap_status.py tests\test_api_spine_external_read_model_gap_inventory.py -q
.venv\Scripts\python.exe -m pytest tests\test_external_read_model_gap_status.py tests\test_api_spine_external_read_model_gap_inventory.py tests\test_api_spine_external_router_read_root_inventory.py tests\test_api_spine_artifacts.py -q
git diff --check -- scripts\external_read_model_gap_status.py tests\test_external_read_model_gap_status.py docs\api-spine\external-router-read-model-gap-inventory.md
```

Result: focused checker test `7 passed`; CLI emitted aggregate status; paired
gap inventory/checker suite `16 passed`; broader external-router/API Spine suite
`56 passed` when rerun serially. One earlier parallel wider run failed during
shared Postgres enum setup with duplicate `userrole`, consistent with test
process concurrency rather than Sprint 213 behavior. Whitespace check clean.

Implementation commit: `9b7c19b2`.

Sprint engine state: continuing after push. No user intervention is required;
next recommended direction is a non-runtime design packet for one external
read-model gap, likely practitioner directory read shape first because it is
the pure `route_gap`.

---

## Previous Closeout - Sprint 212

| Item | Value |
|---|---|
| Batch | Sprint 212 API Spine External Read-Model Gap Inventory |
| Integrated through | Ariadne implementation with DeepSeek review; Claude budget-blocked and Antigravity timed out without artifact |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 212 What Changed

- Added `docs/api-spine/external-router-read-model-gap-inventory.md`, expanding
  the five external-router read-model gaps left by the earlier external-root
  inventory:
  `Query.practice.practitioners`, `Query.patient.reminders`,
  `Query.patient.messages`, `Query.directorySearch.RACGP_GUIDELINES`, and
  `Query.directorySearch.COCHRANE_LIBRARY`.
- Mapped each gap to current backing models or source absence:
  `Practitioner`, `Reminder`, `InternalMessage`, `SmsLog`, and the absence of
  RACGP/Cochrane local/cited source models.
- Captured shape mismatches: practitioner display-name derivation, reminder
  `Date` versus SDL `DateTime`, missing reminder `COMPLETED` representation,
  message two-table union, absent EMAIL model, raw body avoidance, and
  RACGP/Cochrane source/licensing prerequisites.
- Added `tests/test_api_spine_external_read_model_gap_inventory.py`, which
  parses the markdown table, AST-checks selected model fields, verifies the SDL
  reserved surfaces, confirms the missing routes remain missing, and preserves
  closed gates.

Worker mix:

- DeepSeek completed a bounded review lane and recommended the detailed
  model/schema/source gap shape and exact invariants.
- Claude was invoked through `scripts/drive_agent_headless.py` but exceeded the
  sprint review budget before producing a usable final recommendation.
- Antigravity was invoked through `agy.exe` but timed out without producing a
  review artifact.

Boundary:

- Static inventory and parser/source tests only.
- No GraphQL resolvers, no new REST routes, no provider calls, no provider
  dry-run wiring, no runtime FGA clients, no external patient clients, no
  H15/H-series runtime imports, no memory/RAG/GraphRAG, no broad historical
  diary trove mining, no Access AI invocation wiring, no practitioner/reminder/
  message/SMS/directory write authority, no model-to-database write authority,
  and no raw compatibility deprecation mode change.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_external_read_model_gap_inventory.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_external_read_model_gap_inventory.py tests\test_api_spine_external_router_read_root_inventory.py tests\test_api_spine_artifacts.py -q
git diff --check -- docs\api-spine\external-router-read-model-gap-inventory.md tests\test_api_spine_external_read_model_gap_inventory.py
```

Result: focused gap inventory test `9 passed`; broader external-router/API
Spine suite `49 passed`; whitespace check clean.

Implementation commit: `eacdb5bc`.

Sprint engine state: continuing after push. No user intervention is required;
next recommended direction is a safe aggregate external read-model gap status
checker/report for the five practitioner/reminder/message/directory gaps.

---

## Previous Closeout - Sprint 211

| Item | Value |
|---|---|
| Batch | Sprint 211 API Spine Raw Compat Header Rollout Gate Status Checker |
| Integrated through | Ariadne implementation with DeepSeek review; Claude budget-blocked |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 211 What Changed

- Added `scripts/raw_compat_header_rollout_gate_check.py`, a CLI/importable
  checker for `docs/api-spine/raw-compat-header-rollout-gate.json`.
- The checker asserts the gate remains `blocked`, has zero environments allowed
  to default `appointment_raw_compat_mode` to `header`, keeps all unblocking
  observability signals false, and preserves required/allowed/forbidden/pause
  trigger lists.
- The checker emits only safe aggregate status fields: counts, booleans,
  schema/decision, `sprint_engine_state: continuing`, and
  `pause_required: false`.
- Added `tests/test_raw_compat_header_rollout_gate_check.py`, including exact
  safe-output assertions and negative drift tests for unblocked decision,
  non-empty environment list, changed required/forbidden lists, true
  unblocking signals, and missing pause triggers.
- Updated the raw-compat readiness doc and rollout-gate test to reference the
  checker.

Worker mix:

- DeepSeek completed a bounded review lane and recommended the safe aggregate
  status shape, payload-free output fragments, and negative mutation tests.
- Claude was invoked through `scripts/drive_agent_headless.py` but exceeded the
  sprint review budget before producing a usable final recommendation.
- Antigravity was not re-run for this small checker sprint after repeated
  timeout behavior in the prior raw-compat header sprints.

Boundary:

- Safe aggregate checker/report and tests only.
- No `appointment_raw_compat_mode` change, no environment default to `header`,
  no backend route behavior change, no frontend production code change, no
  user-facing deprecation UI, no route removal, no idempotency expansion, no
  provider calls or dry-runs, no memory/RAG/GraphRAG, no H15/H-series runtime
  imports, no historical diary material access, no GraphQL mutations, no
  external patient clients, no runtime FGA clients, and no model-to-database
  write authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_raw_compat_header_rollout_gate_check.py -q
.venv\Scripts\python.exe scripts\raw_compat_header_rollout_gate_check.py
.venv\Scripts\python.exe -m pytest tests\test_raw_compat_header_rollout_gate_check.py tests\test_api_spine_raw_compat_header_rollout_gate.py tests\test_api_spine_raw_compat_consumer_signal_readiness.py review\test_diary_deprecation_consumer.py tests\test_api_spine_legacy_compatibility_write_deprecation_map.py tests\test_appointment_raw_compat.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py tests\test_raw_compat_header_rollout_gate_check.py tests\test_api_spine_raw_compat_header_rollout_gate.py tests\test_api_spine_raw_compat_consumer_signal_readiness.py tests\test_api_spine_legacy_compatibility_write_deprecation_map.py -q
git diff --check -- scripts\raw_compat_header_rollout_gate_check.py tests\test_raw_compat_header_rollout_gate_check.py docs\api-spine\raw-compat-consumer-signal-readiness.md tests\test_api_spine_raw_compat_header_rollout_gate.py
```

Result: focused checker test `9 passed`; checker CLI emitted blocked aggregate
status with `environment_count: 0`, `observability_ready: false`,
`rollout_ready: false`, and `pause_required: false`; integrated raw-compat
suite `46 passed`; API Spine static suite with checker `63 passed`; whitespace
check clean.

Implementation commit: `3231a381`.

Sprint engine state: continuing after push. No user intervention is required;
next recommended direction is a small read-model gap inventory for
practitioner/reminder/message/directory gaps.

---

## Previous Closeout - Sprint 210

| Item | Value |
|---|---|
| Batch | Sprint 210 API Spine Raw Compat Header Rollout Gate |
| Integrated through | Ariadne implementation with DeepSeek review; Claude budget-blocked and Antigravity timed out without artifact |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 210 What Changed

- Added `docs/api-spine/raw-compat-header-rollout-gate.json`, a structured
  blocked-by-default gate for any future raw compatibility header-mode rollout.
- The gate records decision `blocked`, empty
  `environments_can_default_header`, the four raw compatibility route families,
  the sole backend signal site, the known frontend console consumer, and no
  user-facing UI consumers.
- The gate separates already-proven readiness signals from still-false
  observability requirements, including per-environment observability, rollback
  planning, signal-volume metrics, staff impact assessment, external consumer
  impact audit, and proposal/confirm parity review.
- Added `tests/test_api_spine_raw_compat_header_rollout_gate.py`, validating
  the blocked decision, route inventory, false unblocking requirements,
  forbidden uses, and mutation-driven sprint-engine pause triggers.
- Cross-linked the rollout gate from
  `docs/api-spine/raw-compat-consumer-signal-readiness.md` and its parser test.

Worker mix:

- DeepSeek completed a bounded review lane and recommended the JSON gate shape,
  invariant set, and pause-trigger pattern.
- Claude was invoked through `scripts/drive_agent_headless.py` but exceeded the
  sprint review budget before producing a usable final recommendation.
- Antigravity was invoked through `agy.exe` but timed out without producing a
  review artifact.

Boundary:

- Static gate JSON, documentation, and parser tests only.
- No `appointment_raw_compat_mode` change, no environment default to `header`,
  no backend route behavior change, no frontend production code change, no
  user-facing deprecation UI, no route removal, no idempotency expansion, no
  provider calls or dry-runs, no memory/RAG/GraphRAG, no H15/H-series runtime
  imports, no historical diary material access, no GraphQL mutations, no
  external patient clients, no runtime FGA clients, and no model-to-database
  write authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_raw_compat_header_rollout_gate.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_raw_compat_header_rollout_gate.py tests\test_api_spine_raw_compat_consumer_signal_readiness.py review\test_diary_deprecation_consumer.py tests\test_api_spine_legacy_compatibility_write_deprecation_map.py tests\test_appointment_raw_compat.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py tests\test_api_spine_raw_compat_header_rollout_gate.py tests\test_api_spine_raw_compat_consumer_signal_readiness.py tests\test_api_spine_legacy_compatibility_write_deprecation_map.py -q
git diff --check -- docs\api-spine\raw-compat-header-rollout-gate.json tests\test_api_spine_raw_compat_header_rollout_gate.py docs\api-spine\raw-compat-consumer-signal-readiness.md tests\test_api_spine_raw_compat_consumer_signal_readiness.py
```

Result: focused rollout-gate test `6 passed`; integrated raw-compat/readiness
suite `37 passed`; API Spine static suite with rollout gate `54 passed`;
whitespace check clean.

Implementation commit: `386aed6f`.

Sprint engine state: continuing after push. No user intervention is required;
next recommended direction is a safe aggregate raw compatibility header rollout
gate status checker/report so workers can inspect the blocked posture without
hand-reading JSON.

---

## Previous Closeout - Sprint 209

| Item | Value |
|---|---|
| Batch | Sprint 209 API Spine Diary Deprecation Header Browser Harness |
| Integrated through | Ariadne implementation with DeepSeek review; Claude budget-blocked twice and Antigravity timed out without artifact |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 209 What Changed

- Added `review/test_diary_deprecation_consumer.py`, a dedicated Playwright
  review test that serves the Diary page, stubs Office, routes two synthetic
  appointment API responses, captures browser console warnings, and calls the
  real `apiFetch()` in page context.
- Proved the positive path: when a routed response includes `Deprecation` and
  `Access-Control-Expose-Headers: Deprecation`, browser-executed `apiFetch()`
  emits the expected `[EMR4 Deprecation Warning]` developer warning.
- Proved the negative path: a routed response without `Deprecation` emits no
  deprecation warning.
- Updated `docs/api-spine/raw-compat-consumer-signal-readiness.md` and
  `tests/test_api_spine_raw_compat_consumer_signal_readiness.py` to record
  `console_warn_proven` and
  `consumer_cors_backend_and_browser_harness_checked_keep_audit_mode`.

Worker mix:

- DeepSeek completed a bounded review lane and recommended the exact
  route-intercepted Playwright proof shape with positive and negative controls.
- Claude was invoked twice through `scripts/drive_agent_headless.py`, once with
  Sonnet and once with Haiku, but both runs exceeded their sprint review budget
  before producing a usable final recommendation.
- Antigravity was invoked through `agy.exe` but timed out without producing a
  review artifact.

Browser path note:

- The in-app Browser plugin was bootstrapped and its documentation read, but
  the exposed Browser Playwright subset does not include network route
  interception. Sprint 209 therefore used the repo's regular Playwright review
  harness for the necessary routed-response proof.

Boundary:

- Route-intercepted browser execution proof only.
- No `appointment_raw_compat_mode` change, no backend route behavior change, no
  frontend production code change, no user-facing UI change, no route removal,
  no idempotency expansion, no provider calls or dry-runs, no
  memory/RAG/GraphRAG, no H15/H-series runtime imports, no historical diary
  material access, no GraphQL mutations, no external patient clients, no
  runtime FGA clients, and no model-to-database write authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest review\test_diary_deprecation_consumer.py -q
.venv\Scripts\python.exe -m pytest review\test_diary_deprecation_consumer.py tests\test_api_spine_raw_compat_consumer_signal_readiness.py -q
.venv\Scripts\python.exe -m pytest review\test_diary_deprecation_consumer.py tests\test_api_spine_raw_compat_consumer_signal_readiness.py tests\test_api_spine_legacy_compatibility_write_deprecation_map.py tests\test_appointment_raw_compat.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py tests\test_api_spine_raw_compat_consumer_signal_readiness.py tests\test_api_spine_legacy_compatibility_write_deprecation_map.py -q
git diff --check -- review\test_diary_deprecation_consumer.py docs\api-spine\raw-compat-consumer-signal-readiness.md tests\test_api_spine_raw_compat_consumer_signal_readiness.py
```

Result: dedicated Playwright review test `1 passed`; focused browser/readiness
suite `11 passed`; adjacent raw-compat/deprecation-map suite `31 passed`; API
Spine static suite with new/legacy guards `48 passed`; whitespace check clean.

Implementation commit: `84deb920`.

Sprint engine state: continuing after push. No user intervention is required;
next recommended direction is a blocked-by-default raw compatibility header-mode
rollout/observability gate that records the operational purpose, rollout
surface, metrics/audit signals, and explicit review requirements before any
environment emits `Deprecation` by default.

---

## Previous Closeout - Sprint 208

| Item | Value |
|---|---|
| Batch | Sprint 208 API Spine Raw Compat CORS Exposed-Header Readiness |
| Integrated through | Ariadne implementation with Claude and DeepSeek review; Antigravity invoked twice but timed out without artifact |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 208 What Changed

- Added `expose_headers=["Deprecation"]` to the FastAPI `CORSMiddleware`
  configuration in `app/main.py`, making the raw compatibility deprecation
  signal readable by cross-origin browser JavaScript when a reviewed
  environment emits it.
- Tightened `tests/test_appointment_raw_compat.py` so a header-mode raw
  appointment create response with an allowed `Origin` now proves both
  `Deprecation` and `Access-Control-Expose-Headers: Deprecation`.
- Extended `tests/test_api_spine_raw_compat_consumer_signal_readiness.py` with
  a static and TestClient CORS exposure guard, while continuing to assert the
  raw compatibility default remains `audit`.
- Updated `docs/api-spine/raw-compat-consumer-signal-readiness.md` to record the
  new posture:
  `consumer_cors_and_backend_header_checked_keep_audit_mode`.

Worker mix:

- Claude completed a Sonnet review lane and identified missing
  `expose_headers` as the critical CORS gap, while recommending no mode change.
- DeepSeek completed a bounded review lane and confirmed the exact invariant:
  `expose_headers=["Deprecation"]`, with `appointment_raw_compat_mode` staying
  `audit`.
- Antigravity was invoked twice through `agy.exe`; both runs timed out without
  producing a review artifact, so no Antigravity recommendations were
  integrated for this sprint.

Boundary:

- CORS response-header exposure and tests only.
- No `appointment_raw_compat_mode` change, no route behavior change, no route
  removal, no idempotency expansion, no user-facing UI change, no provider
  calls or dry-runs, no memory/RAG/GraphRAG, no H15/H-series runtime imports,
  no historical diary material access, no GraphQL mutations, no external
  patient clients, no runtime FGA clients, and no model-to-database write
  authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_raw_compat_consumer_signal_readiness.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_raw_compat_consumer_signal_readiness.py tests\test_appointment_raw_compat.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_raw_compat_consumer_signal_readiness.py tests\test_api_spine_legacy_compatibility_write_deprecation_map.py tests\test_appointment_raw_compat.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py tests\test_api_spine_raw_compat_consumer_signal_readiness.py tests\test_api_spine_legacy_compatibility_write_deprecation_map.py -q
git diff --check -- app\main.py docs\api-spine\raw-compat-consumer-signal-readiness.md tests\test_api_spine_raw_compat_consumer_signal_readiness.py tests\test_appointment_raw_compat.py
```

Result: focused readiness test `9 passed`; raw-compat plus readiness suite
`22 passed`; adjacent deprecation-map/raw-compat suite `29 passed`; API Spine
static suite with new/legacy guards `47 passed`; whitespace check clean.

Implementation commit: `7d9b0e85`.

Sprint engine state: continuing after push. No user intervention is required;
next recommended direction is a browser or equivalent frontend execution check
proving `apiFetch()` can read a raw compatibility `Deprecation` header after
CORS filtering, or a small read-model gap inventory for
practitioner/reminder/message/directory gaps.

---

## Previous Closeout - Sprint 207

| Item | Value |
|---|---|
| Batch | Sprint 207 API Spine Frontend Deprecation Header Consumer |
| Integrated through | Ariadne implementation with Claude, Antigravity, and DeepSeek review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 207 What Changed

- Added a shared `Deprecation` response-header consumer to
  `docs/diary/diary.js` inside `apiFetch()`. When the header is present, the
  taskpane now emits a developer-facing `console.warn()` identifying the route.
- Updated `docs/api-spine/raw-compat-consumer-signal-readiness.md` so all four
  raw compatibility writes now record `Header consumed` as `console_warn` and
  `Readiness posture` as `consumer_wired_keep_audit_mode`.
- Updated `tests/test_api_spine_raw_compat_consumer_signal_readiness.py` so the
  frontend guard proves the only current deprecation-header consumer is the
  shared `apiFetch()` boundary and that it runs after the 401 branch.
- Preserved the `keep_audit_mode` decision. This sprint does not flip
  `appointment_raw_compat_mode` to `header` or `off`.

Worker mix:

- Claude completed a Sonnet review lane and recommended the shared `apiFetch()`
  insertion with no backend or route changes.
- Antigravity completed a CLI review lane and produced a tangible review note
  in its worker worktree, recommending the same minimal console warning
  posture and static assertion.
- DeepSeek completed a bounded review lane and confirmed this should remain a
  static/frontend precondition rather than a browser/live-backend mode flip.

Boundary:

- Frontend console-warning consumer only.
- No user-facing UI banner, no backend route behavior change, no config change,
  no `appointment_raw_compat_mode` change, no route removal, no idempotency
  expansion, no provider calls or dry-runs, no memory/RAG/GraphRAG, no
  H15/H-series runtime imports, no historical diary material access, no
  GraphQL mutations, no external patient clients, no runtime FGA clients, and
  no model-to-database write authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_raw_compat_consumer_signal_readiness.py -q
node --check docs\diary\diary.js
.venv\Scripts\python.exe -m pytest tests\test_api_spine_raw_compat_consumer_signal_readiness.py tests\test_api_spine_legacy_compatibility_write_deprecation_map.py tests\test_appointment_raw_compat.py -q
git diff --check -- docs\diary\diary.js docs\api-spine\raw-compat-consumer-signal-readiness.md tests\test_api_spine_raw_compat_consumer_signal_readiness.py
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py tests\test_api_spine_raw_compat_consumer_signal_readiness.py tests\test_api_spine_legacy_compatibility_write_deprecation_map.py -q
```

Result: focused readiness test `8 passed`; JS syntax check clean; adjacent
raw-compat suite `28 passed`; whitespace check clean; API Spine static suite
with new/legacy guards `46 passed`.

Implementation commit: `0884bca9`.

Sprint engine state: continuing after push. No user intervention is required;
next recommended direction is a live/non-intercepted raw-compat header consumer
verification and CORS exposed-header preflight before any
`appointment_raw_compat_mode` change, or a small read-model gap inventory for
practitioner/reminder/message/directory gaps.

---

## Previous Closeout - Sprint 206

| Item | Value |
|---|---|
| Batch | Sprint 206 API Spine Raw Compatibility Consumer Signal Readiness |
| Integrated through | Ariadne implementation with Claude, Antigravity, and DeepSeek review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 206 What Changed

- Added `docs/api-spine/raw-compat-consumer-signal-readiness.md`, a static
  preflight before any future `appointment_raw_compat_mode` move from `audit`
  to `header`.
- Mapped all four raw compatibility writes to their backend
  `_raw_compat_evidence_and_headers()` signal calls, current Diary frontend
  fallback call-site IDs, header-consumption status, and readiness posture.
- Recorded the current decision as `keep_audit_mode`: backend header mode
  exists, but no committed frontend JavaScript/HTML surface consumes or logs
  the `Deprecation` response header.
- Added `tests/test_api_spine_raw_compat_consumer_signal_readiness.py`, a
  parser/static-source guard over the preflight doc, appointment router,
  config, Diary JS fallback call sites, frontend header-consumption baseline,
  raw compatibility backend tests, and the existing deprecation map.

Worker mix:

- DeepSeek completed a bounded review lane and recommended the consumer
  inventory, frontend non-consumption assertion, and handler consistency guard.
- Antigravity completed a CLI review lane and produced a tangible review note
  in its worker worktree; the integrated artifact folded in its call-site and
  mock-drift recommendations.
- Claude initially hit budget stops twice; a cheap Sonnet retry succeeded and
  confirmed no hard blockers, with recommendations to pin route completeness,
  explicit header non-consumption, and the `keep_audit_mode` decision.

Boundary:

- Static source/markdown parsing only.
- No config change, no `appointment_raw_compat_mode` change, no frontend
  behavior change, no backend route behavior change, no route removal, no
  idempotency expansion, no provider calls or dry-runs, no memory/RAG/GraphRAG,
  no H15/H-series runtime imports, no historical diary material access, no
  GraphQL mutations, no external patient clients, no runtime FGA clients, and
  no model-to-database write authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_raw_compat_consumer_signal_readiness.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_raw_compat_consumer_signal_readiness.py tests\test_api_spine_legacy_compatibility_write_deprecation_map.py tests\test_appointment_raw_compat.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py tests\test_api_spine_raw_compat_consumer_signal_readiness.py tests\test_api_spine_legacy_compatibility_write_deprecation_map.py -q
git diff --check -- docs\api-spine\raw-compat-consumer-signal-readiness.md tests\test_api_spine_raw_compat_consumer_signal_readiness.py
```

Result: focused readiness test `8 passed`; adjacent raw-compat suite
`28 passed`; API Spine static suite with new/legacy guards `46 passed`;
whitespace check clean.

Implementation commit: `8244f36c`.

Sprint engine state: continuing after push. No user intervention is required;
next recommended direction is a deliberate frontend deprecation-header consumer
design/test preflight before any `appointment_raw_compat_mode` change, or a
small read-model gap inventory for practitioner/reminder/message/directory
gaps.

---

## Previous Closeout - Sprint 205

| Item | Value |
|---|---|
| Batch | Sprint 205 API Spine External Router Read-Root Inventory |
| Integrated through | Ariadne implementation with DeepSeek review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 205 What Changed

- Added `docs/api-spine/external-router-read-root-inventory.md`, a static
  inventory for the four GraphQL roots that Sprint 202 marked external to the
  appointment-router slice: `viewer`, `practice`, `patient`, and
  `directorySearch`.
- Mapped current GET/read sources across auth, diary, patients, clinical,
  search, and appointment type surfaces without creating GraphQL resolvers or
  changing runtime behavior.
- Recorded explicit read-model gaps for viewer environment/feature/capability
  hints, practice practitioner directory, patient reminders/messages, and
  RACGP/Cochrane directory lookup.
- Added `tests/test_api_spine_external_router_read_root_inventory.py`, which
  AST-parses selected router/service sources and parses the markdown table
  without importing FastAPI routers or executing handlers.
- Integrated DeepSeek's review recommendation to keep missing/gap rows
  explicit, avoid reusing the old `external` coverage label, resolve router
  prefixes mechanically, and preserve closed-gate wording.

Worker mix:

- DeepSeek completed a bounded review lane and its recommendations were
  incorporated.
- Claude and Antigravity were not launched for this small continuation slice
  because Sprint 205 stayed within one static documentation/test surface and
  did not touch runtime code. Next larger general sprint work should return to
  the Ariadne plus Claude, Antigravity, and DeepSeek default.

Boundary:

- Static source/markdown parsing only.
- No FastAPI router import, HTTP requests, database writes, route behavior
  changes, raw compatibility deprecation mode changes, provider calls,
  provider dry-runs, memory/RAG/GraphRAG access, H15/H-series runtime imports,
  historical diary material access, GraphQL mutations, external patient
  clients, runtime FGA clients, Access AI invocation wiring, or
  model-to-database write authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_external_router_read_root_inventory.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_external_router_read_root_inventory.py tests\test_api_spine_appointment_read_model_route_inventory.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
git diff --check -- docs\api-spine\external-router-read-root-inventory.md tests\test_api_spine_external_router_read_root_inventory.py
```

Result: focused external-router inventory `9 passed`; adjacent read-model
inventory run `17 passed`; API Spine artifacts `31 passed`; whitespace check
clean. An initial parallel adjacent pytest run hit the known PostgreSQL enum
creation race; serial reruns passed.

Implementation commit: `547ddd18`.

Sprint engine state: continuing after push. No user intervention is required;
next recommended direction is a raw-compat consumer/signal readiness preflight
before any deprecation-header mode change, or a small read-model gap inventory
for the newly explicit practitioner/reminder/message/directory gaps.

---

## Previous Closeout - Sprint 204

| Item | Value |
|---|---|
| Batch | Sprint 204 API Spine Legacy Compatibility Write Deprecation Map |
| Integrated through | Ariadne implementation with DeepSeek review |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 204 What Changed

- Added `docs/api-spine/legacy-compatibility-write-deprecation-map.md`, a
  static map from the four raw appointment compatibility writes to their
  proposal/confirm replacement families and read-model witness routes.
- Added `tests/test_api_spine_legacy_compatibility_write_deprecation_map.py`,
  which parses the markdown map and existing static source artifacts without
  importing the FastAPI router.
- The map records raw compatibility tags (`raw_compat_create`,
  `raw_compat_update`, `raw_compat_status`, `raw_compat_delete`) and the current
  `appointment_raw_compat_mode` posture: default `audit`, optional `header`,
  and explicit `off`.
- The current decision remains `map_only`: no raw route is removed, renamed,
  blocked, deprecated in code, or changed by this sprint.
- Integrated DeepSeek's review recommendation to include the raw compatibility
  signal modes and preserve the risk that `off` suppresses evidence/header
  signals.

Worker mix:

- DeepSeek completed a bounded review lane and its recommendations were
  incorporated.
- Claude and Antigravity were not launched for this small continuation slice
  because Sprint 204 stayed within one static documentation/test surface and did
  not touch runtime code. Next larger general sprint work should return to the
  Ariadne plus Claude, Antigravity, and DeepSeek default.

Boundary:

- Static source/markdown parsing only.
- No FastAPI router import, HTTP requests, database writes, route behavior
  changes, raw compatibility deprecation mode changes, provider calls,
  provider dry-runs, memory/RAG/GraphRAG access, H15/H-series runtime imports,
  historical diary material access, GraphQL mutations, external patient
  clients, runtime FGA clients, or model-to-database write authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_legacy_compatibility_write_deprecation_map.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_legacy_compatibility_write_deprecation_map.py tests\test_api_spine_appointment_read_model_route_inventory.py tests\test_api_spine_appointment_openapi_drift_guard.py -q
git diff --check -- docs\api-spine\legacy-compatibility-write-deprecation-map.md tests\test_api_spine_legacy_compatibility_write_deprecation_map.py
```

Result: focused map test `7 passed`; adjacent API Spine continuity run
`20 passed`; whitespace check clean.

Implementation commit: `28d5f617`.

Sprint engine state: continuing after push. No user intervention is
required; next recommended direction is a static external-router inventory for
viewer/practice/patient/directory GraphQL roots, or a raw-compat consumer/signal
readiness preflight before any deprecation-header mode change.

---

## Previous Closeout - Sprint 203

| Item | Value |
|---|---|
| Batch | Sprint 203 API Spine Blueprint First Boundary Capture |
| Integrated through | Ariadne documentation/test capture from Yuri paper review discussion |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 203 What Changed

- Reviewed local paper `2508.02721v2.pdf`, `Blueprint First, Model Second: A
  Framework for Deterministic LLM Workflow`, and captured the useful EMR4
  mapping in `docs/api-spine/blueprint-first-model-second-boundary.md`.
- Recorded the architectural vocabulary: Bernie interprets; the backend
  blueprint decides; signed command routes mutate.
- Framed Bernie training as practice-management training, analogous to a
  novice receptionist learning allowed diary lanes, rather than probabilistic
  fine-tuning or raw retrieval.
- Added `tests/test_api_spine_blueprint_first_boundary.py` to keep the note
  anchored to API Spine rules and closed gates.

Worker mix:

- Ariadne-only by scope: this was a narrow documentation preservation step from
  a just-finished user discussion and local paper review, with no runtime,
  product, provider, route, database, or UI change.
- Next general sprint work should return to the Ariadne plus Claude,
  Antigravity, and DeepSeek pattern, with extra DeepSeek substitutions for any
  unavailable external lane.

Boundary:

- Documentation and parser-style markdown assertions only.
- No FastAPI route imports, HTTP requests, database writes, provider calls,
  provider dry-runs, memory/RAG/GraphRAG access, H15/H-series runtime imports,
  historical diary material access, GraphQL mutations, external patient clients,
  runtime FGA clients, or model-to-database write authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_blueprint_first_boundary.py tests\test_api_spine_artifacts.py -q
git diff --check -- docs\api-spine\blueprint-first-model-second-boundary.md tests\test_api_spine_blueprint_first_boundary.py
```

Result: combined serial pytest `36 passed`; whitespace check clean. Earlier
parallel pytest attempts hit the known PostgreSQL enum creation race; the same
tests passed serially.

Implementation commit: `e3a6b41f`.

Sprint engine state: continuing after push. No user intervention is
required; next recommended direction remains a command/read-model deprecation
map for legacy compatibility writes or a static external-router inventory for
viewer/practice/patient/directory GraphQL roots, with runtime/provider gates
still blocked.

---

## Previous Closeout - Sprint 202

| Item | Value |
|---|---|
| Batch | Sprint 202 API Spine Appointment Read-Model Route Inventory |
| Integrated through | Ariadne implementation with Antigravity `agy.exe` review/draft and DeepSeek review; Claude attempted but unavailable |
| Status | Integrated and pushed |
| Last updated | 2026-07-08 |

## Sprint 202 What Changed

- Added `docs/api-spine/appointment-read-model-route-inventory.md`, a static
  bridge from GraphQL appointment/diary/audit/Bernie read surfaces to current
  appointment-router GET/read routes.
- Added `tests/test_api_spine_appointment_read_model_route_inventory.py`, which
  parses only the markdown inventory, GraphQL SDL, appointment router source,
  and existing OpenAPI drift guard route inventory.
- The inventory covers every GraphQL `Query` root and every current
  appointment-router GET/read route, marking coverage as `full`, `partial`,
  `external`, or `unmapped`.
- It records the four legacy compatibility writes as `outside_read_graph` and
  keeps proposal commands, confirm commands, command-style POST reads, and
  Bernie session POST commands outside the GraphQL read-route bridge.
- Integrated Sprint 202 review records under `orchestration/agent_inbox/codex/`.

Worker mix:

- Antigravity was reached through the documented `agy.exe` CLI and produced a
  useful review packet plus a draft implementation. Ariadne did not copy the
  draft wholesale; the integrated version tightened GET coverage, unmapped-route
  accounting, and mutating-route exclusion tests.
- DeepSeek completed before integration and independently recommended the same
  static route inventory, with warnings about partial GraphQL coverage and
  command-style POST read exclusion.
- Claude was invoked through `scripts\drive_agent_headless.py` with
  `--mint-session`, but stopped at the configured budget limit before producing
  a durable review packet. No Claude recommendations were integrated.

Boundary:

- Static source/markdown parsing only.
- No FastAPI router import in the new inventory test, no route handler
  execution, HTTP requests, database session, provider calls, memory/RAG/GraphRAG
  access, H15/H-series runtime imports, historical diary material access,
  GraphQL mutation work, or writes.
- The change does not prove runtime resolver implementation, schema conversion
  correctness, authorization policy, performance, database access behavior,
  provider readiness, or deployment readiness.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_appointment_read_model_route_inventory.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_appointment_openapi_drift_guard.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_idempotency_continuity_index.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_audit_correlation_continuity_index.py -q
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
git diff --check
```

Result: appointment read-model route inventory `8 passed`; OpenAPI drift guard
`5 passed`; idempotency continuity index `5 passed`; audit/correlation
continuity index `7 passed`; readiness/provider reports stayed blocked/false;
leakage lint safe; whitespace check clean. An initial parallel continuity run
hit the known PostgreSQL enum creation race; serial reruns passed.

Implementation commit: `3564f9d0`.

Sprint engine state: continuing after push. No user intervention is required;
next recommended direction is a command/read-model deprecation map for legacy
compatibility writes or a static external-router inventory for
viewer/practice/patient/directory GraphQL roots, with runtime/provider gates
still blocked.

---

## Sprint 201 What Changed

- Added `docs/api-spine/audit-correlation-continuity-index.md`, a static bridge
  between GraphQL audit/read-model declarations and OpenAPI appointment command
  audit/correlation metadata.
- Added `tests/test_api_spine_audit_correlation_continuity_index.py`, which
  parses only the GraphQL SDL, OpenAPI YAML, and markdown index.
- The index pins action continuity labels across GraphQL
  `AppointmentAuditAction` and OpenAPI `AuditIntent.audit_action`: shared
  values are `bridged`, `DIRECT_COMPATIBILITY_WRITE` and `READ` are
  `read_model_only`, and slot-search audit intents are `command_plane_only`.
- It also pins correlation surfaces (`AuditEvent.correlationId`,
  `AppointmentAuditEvent.correlationId`, `AuditFilter.correlationId`,
  `X-Correlation-Id`, `CommandMeta.correlation_id`, and
  `ConfirmationAuditEvent.correlation_id`) plus target-kind asymmetries.
- Integrated Sprint 201 review records under `orchestration/agent_inbox/codex/`.

Worker mix:

- Claude was invoked through `scripts\drive_agent_headless.py` with
  `--mint-session`; the CLI returned a budget-stop result after producing a
  durable review packet, so Ariadne trusted the artifact rather than the result
  JSON. Claude also hit denied internal `handin` command attempts, which did not
  block review-packet creation.
- Antigravity was reached through the documented `agy.exe` CLI and produced a
  durable review packet in the Antigravity worktree.
- DeepSeek completed before integration and independently recommended the same
  parser-only audit/read-model continuity artifact, with warnings about
  intentional enum asymmetry and command-plane field leakage.

Boundary:

- Static SDL/YAML/markdown parsing only.
- No FastAPI router import in the new continuity test, no route handler
  execution, HTTP requests, database session, provider calls, memory/RAG/GraphRAG
  access, H15/H-series runtime imports, historical diary material access,
  GraphQL mutation work, or writes.
- The change does not prove runtime correlation-id propagation, audit-log
  append-only semantics, database durability, resolver implementation, route
  handler correctness, or deployment readiness.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_audit_correlation_continuity_index.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_idempotency_continuity_index.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_idempotency_audit_metadata.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
git diff --check
```

Result: audit/correlation continuity index `7 passed`; idempotency continuity
index `5 passed`; idempotency/audit metadata `7 passed`; API spine artifacts
`31 passed`; readiness/provider reports stayed blocked/false; leakage lint
safe; whitespace check clean. An initial parallel adjacent pytest run hit the
known PostgreSQL enum creation race; serial reruns passed.

Implementation commit: `1aa8fb48`.

Sprint engine state: continuing after push. No user intervention is required;
next recommended direction is a narrow appointment read-model route inventory
or command/read-model deprecation map for legacy compatibility writes, with
runtime/provider gates still blocked.

---

## Sprint 200 What Changed

- Added `docs/api-spine/idempotency-continuity-index.md`, a static continuity
  table over the eleven canonical OpenAPI appointment command paths.
- Added `tests/test_api_spine_idempotency_continuity_index.py`, which parses
  only the OpenAPI YAML and the markdown index, then checks exact path coverage,
  status counts, source-test citations, table shape, and closed-gate wording.
- The accepted count is four canonical OpenAPI confirm paths as
  `ledger_wired`, four proposal-only paths as `documented_gap`, and three
  slot-search command-style reads as `read_no_idempotency`. The fifth wired
  backend family in the runtime checkpoint is the Bernie create-confirm backend
  variant, not a canonical OpenAPI `paths` entry.
- The index records that legacy compatibility writes and Bernie backend variants
  remain outside the OpenAPI continuity table unless they become canonical
  OpenAPI paths.
- Integrated Sprint 200 review records under `orchestration/agent_inbox/codex/`.

Worker mix:

- Antigravity was reached through the documented `agy.exe` CLI and produced a
  durable review artifact. Its broader runtime header-enforcement suggestions
  were intentionally kept out of scope for this static index sprint.
- DeepSeek recommended the index/test shape and warned against overclaiming
  runtime replay behavior.
- Replacement DeepSeek completed before integration and caught the 5/3/3 versus
  4/4/3 count mismatch; Ariadne accepted the correction and folded in its
  source-file-existence and out-of-scope-note suggestions.
- Claude was attempted through the headless driver but not with the preferred
  routine protocol shape: the attempt lacked the `--mint-session` handin/submit
  packet pattern and produced no durable artifact before the budget limit.
  Sprint 200 therefore records Claude as unavailable/replaced, not as a
  successful Claude lane. Future Claude sprint lanes should use
  `scripts\drive_agent_headless.py --cwd C:\Users\sarashera\EMR4-worktrees\claude --phase plan --mint-session --prompt "handin, write the implementation plan, submit the plan packet, then stop"`
  or the equivalent implementation-phase prompt.

Boundary:

- Static OpenAPI YAML and markdown parsing only.
- No FastAPI router import in the new continuity test, no route handler
  execution, HTTP requests, database session, provider calls, memory/RAG/GraphRAG
  access, H15/H-series runtime imports, historical diary material access,
  GraphQL mutation work, or writes.
- The change does not prove runtime concurrency behavior, network-loss replay
  behavior, backend handler correctness, transaction durability, audit-log
  append-only semantics, or deployment readiness.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_idempotency_continuity_index.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_idempotency_audit_metadata.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_appointment_idempotency_gap.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_confirmation_family_idempotency_checkpoint.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
git diff --check
```

Result: continuity index `5 passed`; idempotency/audit metadata `7 passed`;
appointment idempotency gap `5 passed`; confirmation-family checkpoint
`7 passed`; API spine artifacts `31 passed`; readiness/provider reports stayed
blocked/false; leakage lint safe; whitespace check clean.

Implementation commit: `496e0cee`.

Sprint engine state: continuing after push. No user intervention is required;
next recommended direction is a narrow audit-event/read-model inventory or
correlation/audit continuity pass, with runtime/provider gates still blocked.

---

## Sprint 199 What Changed

- Added `tests/test_api_spine_idempotency_audit_metadata.py`, an import-free
  YAML structural preflight over `docs/api-spine/openapi/appointment-commands.yaml`.
- The preflight guards that appointment proposal/confirmation command paths
  carry `Idempotency-Key` and `X-Correlation-Id`, while slot-search
  command-style reads carry `X-Correlation-Id` but not `Idempotency-Key`.
- It pins core OpenAPI metadata shapes for `AuditIntent`, `FreshnessRef`,
  `SignedConfirmationEvidence`, confirmation commands, and
  `ConfirmationAuditEvent` idempotency/correlation linkage.
- Added `docs/api-spine/idempotency-audit-metadata-preflight.md` to document the
  guard and state clearly that runtime idempotency storage and durable audit
  writes remain separate closed gates.
- Integrated Claude and DeepSeek review artifacts under
  `orchestration/agent_inbox/codex/`; Antigravity timed out via `agy.exe`, so a
  second DeepSeek review substituted for that lane.

Worker mix:

- Claude recommended a pure YAML structural guard and warned not to require
  idempotency on non-mutating slot-search reads.
- DeepSeek identified OpenAPI schema gaps and recommended a focused
  idempotency/audit preflight.
- Replacement DeepSeek confirmed the guard adds coverage beyond older
  idempotency gap tests while remaining a schema-invariant check, not runtime
  enforcement evidence.
- Antigravity was dispatched through `agy.exe` but produced no artifact before
  timeout; no Antigravity changes were integrated.

Boundary:

- Static OpenAPI YAML parsing only.
- No FastAPI router import in the new preflight, no route handler execution,
  HTTP requests, database session, provider calls, memory/RAG/GraphRAG access,
  H15/H-series runtime imports, historical diary material access, GraphQL
  mutation work, or writes.
- The change does not prove idempotency-store enforcement, replay semantics, or
  durable audit writes.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_idempotency_audit_metadata.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_appointment_idempotency_gap.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_appointment_openapi_drift_guard.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_confirmation_family_idempotency_checkpoint.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_post_sprint118_checkpoint.py -q
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_contract.py -q
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_endpoint_coverage.py -q
.venv\Scripts\python.exe scripts\bernie_scenario_evidence_snapshot.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
git diff --check
```

Result: new preflight `7 passed`; API spine artifacts `31 passed`; idempotency
gap `5 passed`; OpenAPI drift guard `5 passed`; confirmation-family checkpoint
`7 passed`; post-Sprint-118 checkpoint `4 passed`; route contract `12 passed`;
endpoint coverage `12 passed`; readiness/provider reports stayed blocked/false;
leakage lint safe; whitespace check clean. Initial parallel DB-backed pytest
commands hit the known PostgreSQL enum/drop race; serial reruns passed.

Implementation commit: `49718e21`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is a narrow bridge from static idempotency/audit metadata
to existing runtime idempotency checkpoints, or a small audit-event/read-model
inventory, with runtime/provider gates still blocked.

---

## Sprint 198 What Changed

- Added `docs/appointment-support-routes-infrastructure-boundary.md` to define
  the current out-of-contract appointment POST sub-families as infrastructure,
  not Diary grammar dispatch authority.
- Updated `docs/appointment-route-inventory-preflight.md` to cite the Sprint 198
  boundary and the current aggregate split: `proposal_support_post=7`,
  `state_tracking_post=2`, and `ambiguous_post=0`.
- Strengthened `tests/test_appointment_route_inventory_preflight.py` so
  ambiguous out-of-contract appointment POST rows must remain zero.
- Integrated Claude and Antigravity Sprint 198 review artifacts under
  `orchestration/agent_inbox/codex/`.

Worker mix:

- Claude recommended staying in the aggregate preflight boundary rather than
  adding support routes to `DIARY_ACTION_ROUTE_CONTRACTS`.
- Antigravity ran through `agy.exe` and recommended explicit support-route drift
  guards while keeping the infrastructure/grammar distinction clear.
- DeepSeek recommended the zero-ambiguous guard and a dedicated boundary doc.

Boundary:

- Static route-table and documentation guard only.
- No route handler execution, HTTP requests, database session, provider calls,
  memory/RAG/GraphRAG access, H15/H-series runtime imports, historical diary
  material access, GraphQL access, or writes.
- The change does not add support routes to the Diary action contract, promote
  planned verbs, authorize runtime/provider wiring, or expand grammar authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_appointment_route_inventory_preflight.py -q
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_endpoint_coverage.py -q
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_contract.py -q
.venv\Scripts\python.exe scripts\appointment_route_inventory_preflight.py
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q
.venv\Scripts\python.exe scripts\bernie_scenario_evidence_snapshot.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
git diff --check
```

Result: inventory preflight tests `24 passed` after serial rerun; endpoint
coverage `12 passed`; route contract `12 passed` after serial rerun; inventory
script emitted safe aggregate counts with `proposal_support_post=7` and
`state_tracking_post=2`; API spine artifacts `31 passed`; scenario integrity
`8 passed, 1 skipped`; readiness/provider reports stayed blocked/false;
leakage lint safe; whitespace check clean. An initial parallel pytest invocation
hit the known PostgreSQL enum DDL race (`userrole` duplicate type); serial
reruns passed.

Implementation commit: `457d6614`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is a bounded idempotency/audit metadata preflight for
documented appointment command surfaces while provider/runtime gates remain
blocked.

---

## Sprint 197 What Changed

- Extended `tests/test_diary_action_route_endpoint_coverage.py` with static
  auth-gating metadata checks for documented Diary write contract routes.
- Added helper inspection over FastAPI's flattened `APIRoute.dependant`
  metadata.
- Proposal routes, confirm routes, and raw mutation write-method rows must now
  resolve through both `get_current_user` and the `require_role` checker.
- Updated `docs/diary-action-route-contract.md` to document the auth/role
  metadata verification layer.
- Integrated Claude and Antigravity Sprint 197 review artifacts under
  `orchestration/agent_inbox/codex/`.

Worker mix:

- Claude recommended flattened-dependant identity checks against
  `get_current_user`, with write-row iteration to avoid shared-path blind spots.
- Antigravity ran through `agy.exe` and recommended static dependency-tree
  inspection for proposal, confirm, and raw mutation routes.
- DeepSeek reviewed the same boundary and confirmed the current write surfaces
  are covered by `require_role`, while warning against path-only checks.

Boundary:

- Static FastAPI dependency metadata inspection only.
- No `TestClient`, HTTP requests, route handler execution, database session,
  provider calls, memory/RAG/GraphRAG access, H15/H-series runtime imports,
  historical diary material access, GraphQL access, or writes.
- The checks do not add routes to the Diary action contract, promote planned
  verbs, or convert support routes into grammar authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_endpoint_coverage.py -q
.venv\Scripts\python.exe -m pytest tests\test_appointment_route_inventory_preflight.py -q
.venv\Scripts\python.exe scripts\appointment_route_inventory_preflight.py
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_contract.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q
.venv\Scripts\python.exe scripts\bernie_scenario_evidence_snapshot.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
git diff --check
```

Result: endpoint coverage `12 passed`; inventory preflight tests `23 passed`;
inventory script emitted the same safe aggregate counts; route contract
`12 passed`; API spine artifacts `31 passed`; scenario integrity
`8 passed, 1 skipped`; readiness/provider reports stayed blocked/false;
leakage lint safe; whitespace check clean.

Implementation commit: `cd8983a7`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded backend-readiness via narrow non-grammar
documentation for out-of-contract support routes or a small idempotency/audit
metadata preflight.

---

## Sprint 196 What Changed

- Extended `tests/test_diary_action_route_endpoint_coverage.py` with two static
  route-contract behavior checks.
- Added a disjointness invariant proving read routes do not overlap proposal,
  confirm, or raw mutation surfaces, and signed-confirm confirm routes stay
  distinct from adjacent raw mutation routes.
- Added a route-table/preflight cross-check proving mounted out-of-contract
  appointment POST support rows exactly match the preflight sub-family counts:
  `proposal_support_post=7`, `state_tracking_post=2`, and `ambiguous_post=0`.
- Updated `docs/diary-action-route-contract.md` to document the new verification
  layer.
- Integrated Claude and Antigravity Sprint 196 review artifacts under
  `orchestration/agent_inbox/codex/`.

Worker mix:

- Claude recommended static behavior checks for signed-confirm/raw separation
  and auth-gating metadata; Ariadne accepted the lower-coupling disjointness
  portion for this sprint and deferred auth-gating metadata review.
- Antigravity ran through `agy.exe`, submitted a tangible review artifact, and
  its worker worktree was cleaned after integration.
- DeepSeek identified the strongest low-risk invariant: cross-check route table
  gaps against the safe preflight's POST support counts.

Boundary:

- Static FastAPI `APIRoute` path/method metadata and route-contract tuples only.
- No HTTP requests, route handler execution, database session, provider calls,
  memory/RAG/GraphRAG access, H15/H-series runtime imports, historical diary
  material access, GraphQL access, or writes.
- The new checks do not add routes to the Diary action contract, promote planned
  verbs, or convert out-of-contract support routes into grammar authority.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_endpoint_coverage.py -q
.venv\Scripts\python.exe -m pytest tests\test_appointment_route_inventory_preflight.py -q
.venv\Scripts\python.exe scripts\appointment_route_inventory_preflight.py
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_contract.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q
.venv\Scripts\python.exe scripts\bernie_scenario_evidence_snapshot.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
git diff --check
```

Result: endpoint coverage `11 passed`; inventory preflight tests `23 passed`;
inventory script emitted the same safe aggregate counts; route contract
`12 passed`; API spine artifacts `31 passed`; scenario integrity
`8 passed, 1 skipped`; readiness/provider reports stayed blocked/false;
leakage lint safe; whitespace check clean. Parallel pytest attempts again hit
the known PostgreSQL enum DDL setup race (`userrole` duplicate type); affected
pytest commands passed when rerun serially.

Implementation commit: `9aad8bf7`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded backend-readiness via auth-gating metadata
review for documented write surfaces or narrow non-grammar documentation for
out-of-contract support routes.

---

## Sprint 195 What Changed

- Extended `scripts/appointment_route_inventory_preflight.py` with a separate
  POST sub-family axis for out-of-contract appointment route method rows.
- Kept the existing method-family compatibility anchor:
  `out_of_contract_by_method_family["query_or_command_post"] == 9`.
- Added `out_of_contract_post_route_method_count=9`.
- Added `out_of_contract_post_by_sub_family` with current safe aggregate counts:
  - `proposal_support_post=7`;
  - `state_tracking_post=2`.
- Added `out_of_contract_post_rows_are_grammar_dispatch_authority=false` and
  `post_sub_family_classifier=fixed_static_path_patterns`.
- Strengthened `tests/test_appointment_route_inventory_preflight.py` with POST
  count anchoring, sub-family sum invariants, unknown-label rejection, authority
  flag rejection, and leakage checks for route/path fragments.
- Updated `docs/appointment-route-inventory-preflight.md`.
- Integrated Claude and Antigravity Sprint 195 review artifacts under
  `orchestration/agent_inbox/codex/`.

Worker mix:

- Claude submitted a usable review artifact and recommended retaining the
  legacy POST method-family anchor while adding a separate false-authority POST
  axis.
- Antigravity ran through the corrected `agy.exe` protocol and submitted a
  tangible review artifact; its worker worktree was cleaned after integration.
- DeepSeek reviewed the same narrow scope and recommended neutral naming,
  count-sum invariants, and explicit non-authority posture.

Boundary:

- Static FastAPI `APIRoute` metadata inspection only.
- Count-only/path-free output; no route paths, handler names, request bodies,
  IDs, patient/practitioner data, local material paths, or external-provider
  content.
- No HTTP requests, route handler execution, database session, provider calls,
  memory/RAG/GraphRAG access, H15/H-series runtime imports, historical diary
  material access, GraphQL access, or writes.
- POST sub-family labels are planning signals only and do not add proposal,
  confirm, raw mutation, or Diary grammar dispatch authority.

Verification:

```powershell
.venv\Scripts\python.exe scripts\appointment_route_inventory_preflight.py
.venv\Scripts\python.exe -m pytest tests\test_appointment_route_inventory_preflight.py -q
.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_endpoint_coverage.py -q
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_contract.py -q
.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q
.venv\Scripts\python.exe scripts\bernie_scenario_evidence_snapshot.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
git diff --check
```

Result: inventory script emitted safe aggregate counts with 9 out-of-contract
POST method rows split into 7 proposal-support and 2 state-tracking rows;
inventory tests `23 passed`; API spine artifacts `31 passed`; endpoint coverage
`9 passed` on serial rerun; route contract `12 passed`; scenario integrity
`8 passed, 1 skipped`; readiness/provider reports stayed blocked/false;
leakage lint safe; whitespace check clean. A parallel pytest batch hit the
known PostgreSQL enum DDL setup race (`userrole` duplicate type); affected
commands passed when rerun serially.

Implementation commit: `69ff1e9f`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded backend-readiness via route contract behavior
checks or narrow non-grammar documentation review for out-of-contract support
surfaces.

---

## Sprint 194 What Changed

- Extended `scripts/appointment_route_inventory_preflight.py` with a
  documented-path versus wholly undocumented split for out-of-contract
  appointment route method rows.
- The safe aggregate report now keeps the total 17 out-of-contract method rows
  but splits them into:
  - 2 documented-path out-of-contract method rows;
  - 15 wholly undocumented out-of-contract method rows.
- Added `documented_path_out_of_contract_rows_are_grammar_authority=false` so
  documented-path tunnel accounting cannot be mistaken for Diary grammar
  authority.
- Strengthened `tests/test_appointment_route_inventory_preflight.py` with
  partition invariants for documented and undocumented method/path counts.
- Updated `docs/appointment-route-inventory-preflight.md` to explain that
  documented-path out-of-contract rows remain out-of-contract and are planning
  signals only.
- Added the Antigravity Sprint 194 review artifact at
  `orchestration/agent_inbox/codex/review-antigravity-sprint194-contract-tunnel-accounting.md`.

Worker mix:

- Claude submitted a usable backend-readiness review.
- Antigravity was corrected after Yuri's protocol reminder and run via
  `C:\Users\sarashera\AppData\Local\agy\bin\agy.exe --add-dir C:\Users\sarashera\EMR4-worktrees\antigravity --print ...`.
  Future sprints must not infer Antigravity unavailability from a missing bare
  `antigravity` shell command.
- DeepSeek review lanes agreed on neutral documented/undocumented accounting,
  partition invariants, and preserving POST classification as a separate
  follow-up.

Boundary:

- Static FastAPI `APIRoute` metadata inspection only.
- Count-only/path-free output; no route paths, handler names, request bodies,
  IDs, patient/practitioner data, local material paths, or external-provider
  content.
- No HTTP requests, route handler execution, database session, provider calls,
  memory/RAG/GraphRAG access, H15/H-series runtime imports, historical diary
  material access, GraphQL access, or writes.
- Documented-path out-of-contract rows are not grammar dispatch authority and
  do not expand the Diary route contract.

Verification:

```powershell
.venv\Scripts\python.exe scripts\appointment_route_inventory_preflight.py
.venv\Scripts\python.exe scripts\bernie_scenario_evidence_snapshot.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe -m pytest tests\test_appointment_route_inventory_preflight.py -q
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_endpoint_coverage.py -q
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_contract.py -q
.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
git diff --check
```

Result: inventory script emitted safe aggregate counts with 2 documented-path
and 15 wholly undocumented out-of-contract method rows; inventory tests
`19 passed`; endpoint coverage `9 passed`; route contract `12 passed`; scenario
integrity `8 passed, 1 skipped`; readiness/provider reports stayed
blocked/false; leakage lint safe; whitespace check clean.

Implementation commit: `ba694ceb`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded backend-readiness via out-of-contract POST
route classification or route contract behavior checks, using Ariadne plus
Claude, Antigravity via `agy.exe`, and DeepSeek by default.

---

## Sprint 193 What Changed

- Added `scripts/appointment_route_inventory_preflight.py`, a source-derived
  aggregate report over mounted FastAPI appointment `APIRoute` metadata.
- Added `tests/test_appointment_route_inventory_preflight.py`.
- Added `docs/appointment-route-inventory-preflight.md`.
- The report separates method rows rather than path-only matches:
  - 35 mounted appointment route/method rows;
  - 18 contract-covered method rows;
  - 14 grammar-authority method rows;
  - 4 raw-adjacent write method rows;
  - 17 out-of-contract method rows.
- The report keeps raw mutation paths as adjacent awareness only with
  `raw_adjacent_routes_are_grammar_dispatch_authority=false`.
- The report is count-only and path-free; it does not emit route paths, handler
  names, request bodies, IDs, patient/practitioner data, or local material paths.

Worker mix:

- Claude was attempted but hit the configured budget before producing a usable
  review, so Ariadne replaced that lane with DeepSeek.
- Antigravity still had no callable CLI in this environment, so Ariadne replaced
  that lane with DeepSeek.
- The three DeepSeek review lanes shaped the sprint toward aggregate counts,
  method-specific raw-adjacent separation, and explicit non-catalogue boundary
  wording.

Boundary:

- Static FastAPI `APIRoute` metadata inspection only.
- No HTTP requests, route handler execution, database session, provider calls,
  memory/RAG/GraphRAG access, H15/H-series runtime imports, historical diary
  material access, GraphQL access, or writes.
- `DIARY_ACTION_ROUTE_CONTRACTS` remains a Diary grammar authority contract,
  not a complete appointment-router catalogue.
- Out-of-contract route counts are planning signals, not automatic bugs and not
  a reason to add non-grammar infrastructure routes to the Diary action
  contract.
- Runtime/provider wiring remains blocked; live-provider and provider-quality
  evidence remain false.

Verification:

```powershell
.venv\Scripts\python.exe scripts\appointment_route_inventory_preflight.py
.venv\Scripts\python.exe scripts\bernie_scenario_evidence_snapshot.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe -m pytest tests\test_appointment_route_inventory_preflight.py -q
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_endpoint_coverage.py -q
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_contract.py -q
.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
git diff --check
```

Result: inventory script emitted safe aggregate counts; inventory tests
`17 passed`; endpoint coverage `9 passed`; route contract `12 passed`; scenario
integrity `8 passed, 1 skipped`; readiness/provider reports stayed
blocked/false; leakage lint safe; whitespace check clean.

Implementation commit: `95da886b`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded backend-readiness via method-specific contract
tunnel review, out-of-contract POST route classification, or route contract
behavior checks.

---

## Sprint 192 What Changed

- Hardened `tests/test_diary_action_route_endpoint_coverage.py` beyond simple
  route membership checks.
- Added static guards for duplicate documented `(path, method)` mounts.
- Added a segment-by-segment declaration-order guard so literal documented
  contract paths are not captured by earlier parametric routes with overlapping
  methods.
- Tightened proposal and confirm route method posture to POST-only, ignoring
  framework-level HEAD/OPTIONS metadata.
- Added a read-route guard allowing GET or query-style POST while rejecting
  PUT/PATCH/DELETE.
- Added a planned-action guard so planned proposal routes do not overlap
  implemented confirm or raw mutation targets.
- Updated `docs/diary-action-route-endpoint-coverage.md` to document the Sprint
  192 hardening and explicitly defer the broader appointment-router inventory
  question.

Worker mix:

- Claude completed a read-only review and recommended duplicate mount,
  parametric shadow, POST-only, and read-route mutation-creep checks.
- DeepSeek identified a broader appointment-router inventory/classification
  follow-up; Ariadne deferred it to avoid changing the Diary grammar contract
  scope inside this sprint.
- Antigravity had no callable CLI in this environment, so Ariadne substituted a
  second DeepSeek lane. The substituted lane validated the implemented shadow
  checks and the segment-by-segment matching approach.

Boundary:

- Static FastAPI `APIRoute` registry scan only.
- No HTTP requests, route handler execution, database session, provider calls,
  memory/RAG/GraphRAG access, H15/H-series runtime imports, historical diary
  material access, GraphQL mutation, or writes.
- These checks prove route-table shape for documented Diary action contract
  paths only. They do not prove runtime dispatch, authorization, tenancy,
  permission enforcement, idempotency, confirmation evidence, provider quality,
  availability quality, or handler behavior.
- `DIARY_ACTION_ROUTE_CONTRACTS` remains a Diary grammar authority contract,
  not a complete appointment-router catalogue.
- Runtime/provider wiring remains blocked; live-provider and provider-quality
  evidence remain false.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_endpoint_coverage.py -q
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_contract.py -q
.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q
.venv\Scripts\python.exe scripts\bernie_scenario_evidence_snapshot.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
git diff --check
```

Result: endpoint coverage `9 passed`; route contract `12 passed`; scenario
integrity `8 passed, 1 skipped`; readiness/provider reports stayed
blocked/false; leakage lint safe; whitespace check clean. Parallel pytest
attempts again hit the known Postgres enum DDL `userrole` duplicate-type race
and passed when rerun serially.

Implementation commit: `11d76bfb`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded backend-readiness via a deliberate appointment
route inventory/classification preflight or route contract behavior checks.

---

## Sprint 191 What Changed

- Added `tests/test_diary_action_route_endpoint_coverage.py`, a static FastAPI
  route-table scan proving every route documented in
  `DIARY_ACTION_ROUTE_CONTRACTS` is mounted on `app.main:app`.
- Corrected the static `slot_search` read-route contract from stale
  `/api/v1/appointments/bernie/interpret` to mounted
  `/api/v1/appointments/proposals/bernie/interpret-booking-instruction`.
- Added `docs/diary-action-route-endpoint-coverage.md` documenting the static
  route-registry boundary and anti-overclaim posture.

Worker mix:

- Claude, Antigravity, and DeepSeek all recommended moving from micro-fixtures
  to a route table reconciliation / endpoint coverage scan.
- Ariadne implemented the integrated slice.
- No worker-lane substitution was needed for Sprint 191.

Boundary:

- Static FastAPI `APIRoute` registry scan only.
- No HTTP requests, route handler execution, database session, provider calls,
  memory/RAG/GraphRAG access, H15/H-series runtime imports, historical diary
  material access, GraphQL mutation, or writes.
- Endpoint existence does not prove route behavior, authorization,
  idempotency, confirmation evidence, provider quality, or availability
  quality.
- Runtime/provider wiring remains blocked; live-provider and provider-quality
  evidence remain false.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_endpoint_coverage.py -q
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_contract.py -q
.venv\Scripts\python.exe scripts\bernie_scenario_evidence_snapshot.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q
.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q
git diff --check
```

Result: endpoint coverage `4 passed`; route contract `12 passed`; scenario
integrity `8 passed, 1 skipped`; scenario replay `.x................................`;
readiness/provider reports stayed blocked/false; leakage lint safe; whitespace
check clean. Parallel pytest attempts hit the known Postgres enum DDL
`userrole` duplicate-type race and passed when rerun serially.

Implementation commit: `48e2f8ba`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded backend-readiness with route-method/path shadow
checks, route contract behavior checks, or another genuinely uncovered
route-level prompt-thread fixture.

---

## Sprint 190 What Changed

- Added `scripts/bernie_scenario_evidence_snapshot.py`, a path/text-free
  aggregate evidence snapshot over `tests/fixtures/bernie_scenarios/*.yaml`.
- Added
  `tests/fixtures/bernie_scenario_evidence/blocked_fake_provider_snapshot.json`
  as the committed golden snapshot.
- Added `tests/test_bernie_scenario_evidence_snapshot.py`.
- Refreshed `docs/bernie-prompt-thread-fake-provider-backend-pass.md` to cite
  the new executable snapshot and current replay result.
- The snapshot records only aggregate counts and closed evidence posture:
  50 scenario YAML fixtures, 31 interpret fixtures, 2 harness demo fixtures,
  17 non-interpret fixtures, 6 fixtures since the last backend pass,
  `fake_provider_evidence=true`, `route_level_backend_evidence=true`,
  `live_provider_evidence=false`, `provider_quality_evidence=false`, provider
  calls false, runtime/provider wiring false, default provider disabled, raw
  trove access false, and runtime gate decision blocked.

Sprint 190 is a Fable-aligned Programme 2D / Programme 2G backend-readiness
evidence consolidation sprint. It does not add runtime behavior and does not
open live provider, provider dry-run, runtime memory, RAG, GraphRAG,
H15/H-series runtime imports, historical diary material access, GraphQL
mutations, or model-to-database writes.

Worker mix:

- Antigravity recommended refreshing the fake-provider backend-pass evidence
  now that Sprints 184-189 added six fixtures.
- DeepSeek recommended making the refresh executable rather than prose-only by
  adding a safe aggregate snapshot and tests.
- Claude hit a session limit resetting at 11:30pm Australia/Brisbane, so Ariadne
  substituted a second DeepSeek lane under the Ariadne-plus-three protocol.
- The replacement DeepSeek lane independently supported the snapshot-script
  approach, with filename-only counting and anti-overclaim labels.
- Ariadne implemented the snapshot, tests, and doc refresh.

## Sprint 190 Verification

- `.venv\Scripts\python.exe scripts\bernie_scenario_evidence_snapshot.py`
  passed and matched the committed golden snapshot.
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_evidence_snapshot.py -q`
  passed (`9 passed`; existing warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_fake_provider_evidence_labels.py -q`
  passed serially (`2 passed`; existing warnings only).
- `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`
  returned blocked/false values with `sprint_engine_state=continuing`.
- `.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py`
  returned `default_provider=disabled`, live provider disabled, provider calls
  false, route behavior unchanged, DB false, memory/RAG false, and historical
  diary material false.
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  passed (`historical diary leakage lint safe`).
- `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_guard.py docs\bernie-prompt-thread-fake-provider-backend-pass.md`
  passed.
- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q`
  passed serially (`.x................................`; one pre-existing xfail,
  existing warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q`
  passed (`8 passed, 1 skipped`; existing warnings only).
- `git diff --check` passed.
- Note: an earlier parallel run of evidence-label pytest work hit the known
  transient Postgres enum DDL race (`userrole` duplicate type); rerunning
  serially passed.
- Integration commit: `2877ce50`.
- Push result: `git push origin master` succeeded.
- Sprint engine state: continuing unless Yuri pauses.

## Sprint 189 What Changed

- Added
  `tests/fixtures/bernie_scenarios/interpret_date_change_same_time_distractor.yaml`.
- The fixture proves a date-change follow-up containing "at the same time"
  preserves the threaded prior time through route-level merge.
- The fixture deliberately frames "same time" as inert distractor text in the
  deterministic fake interpreter, not as true anaphora support.
- The first turn requests `2026-07-14` at `11:00`; the follow-up changes to
  `2026-07-15` while preserving `11:00`, patient, practitioner, and duration.
- Updated `tests/fixtures/bernie_scenarios/README.md` to record same-time
  distractor coverage.

Sprint 189 is a Fable-aligned Programme 2D / Programme 2G backend-readiness
fixture increment. It continues the native Bernie prompt-thread route-level
track and does not open live provider, provider dry-run, runtime memory, RAG,
GraphRAG, H15/H-series runtime imports, historical diary material access,
GraphQL mutations, or model-to-database writes.

Worker mix:

- Claude confirmed "same time" is inert in the fake interpreter and recommended
  adding it only as distractor robustness, not anaphora support.
- Antigravity confirmed the same route-merge behavior and recommended using
  `next Wednesday` instead of bare `Wednesday` to avoid a separate
  bare-weekday ambiguity.
- DeepSeek identified the distractor/date-change matrix gap and recommended
  asserting `clarification_merge` so the fixture does not over-claim explicit
  time parsing.
- Ariadne implemented the fixture with those boundaries.

## Sprint 189 Verification

- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q`
  passed serially (`.x................................`; one pre-existing xfail,
  existing warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q`
  passed (`8 passed, 1 skipped`; existing warnings only).
- `git diff --check` passed.
- Integration commit: `cb38cf82`.
- Push result: `git push origin master` succeeded.
- Sprint engine state: continuing unless Yuri pauses.

## Sprint 188 What Changed

- Added
  `tests/fixtures/bernie_scenarios/interpret_change_date_and_time_new_reply_wins.yaml`.
- The fixture proves a single follow-up can change both date and time together
  while preserving threaded patient, practitioner, and duration.
- The first turn requests `2026-07-14` at `10:00`; the follow-up changes to
  `2026-07-15` at `11:00` with patient, practitioner, and duration preserved.
- Updated `tests/fixtures/bernie_scenarios/README.md` to record multi-field
  override prompt coverage.

Sprint 188 is a Fable-aligned Programme 2D / Programme 2G backend-readiness
fixture increment. It continues the native Bernie prompt-thread route-level
track and does not open live provider, provider dry-run, runtime memory, RAG,
GraphRAG, H15/H-series runtime imports, historical diary material access,
GraphQL mutations, or model-to-database writes.

Worker mix:

- Claude recommended against landing the same-time anaphora prompt as an
  anaphora fixture because the deterministic fake-provider path currently
  treats "same time" as inert wording and ordinary threading fills the time.
  Claude recommended the integrated simultaneous date-and-time override
  fixture as a real uncovered merge contract.
- Antigravity recommended a passing same-time fixture plus a broader xfail for
  bare-weekday ambiguity, but also confirmed the deterministic fake-provider
  path relies on merge behavior rather than true anaphora resolution.
- DeepSeek recommended the same-time prompt as a useful explicit anaphora edge.
- Ariadne chose the simultaneous date-and-time override fixture for Sprint 188
  because it adds a non-misleading route contract now; same-time anaphora
  remains a candidate only if framed honestly as distractor robustness or after
  true anaphora behavior is specified.

## Sprint 188 Verification

- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q`
  passed serially (`.x...............................`; one pre-existing xfail,
  existing warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q`
  passed (`8 passed, 1 skipped`; existing warnings only).
- `git diff --check` passed.
- Integration commit: `47ff5375`.
- Push result: `git push origin master` succeeded.
- Sprint engine state: continuing unless Yuri pauses.

## Sprint 187 What Changed

- Added
  `tests/fixtures/bernie_scenarios/interpret_time_window_date_change_preserves_upper.yaml`.
- The fixture proves a date-change follow-up preserves the threaded
  time-window upper bound (`normalization.constraint.latest_time`) alongside
  earliest time, patient, practitioner, and duration.
- The first turn parses a bounded time window (`after 14:00 but before 15:30`)
  for `2026-07-14`; the second turn changes only the date to `2026-07-15`
  while preserving the full time window.
- Updated `tests/fixtures/bernie_scenarios/README.md` to record
  time-window threading prompt coverage.

Sprint 187 is a Fable-aligned Programme 2D / Programme 2G backend-readiness
fixture increment. It continues the native Bernie prompt-thread route-level
track and does not open live provider, provider dry-run, runtime memory, RAG,
GraphRAG, H15/H-series runtime imports, historical diary material access,
GraphQL mutations, or model-to-database writes.

Worker mix:

- Claude reviewed the remaining Sprint 186 fixture candidates and recommended
  the time-window upper-bound fixture over same-time anaphora because it closes
  a real `latest_time` threading gap without novel anaphora ambiguity.
- Antigravity independently reviewed the same candidates and also recommended
  the time-window upper-bound fixture, after inspecting parser and route merge
  behavior.
- DeepSeek independently recommended the same time-window fixture and warned
  not to assert `command_candidate.latest_time` because the stable contract is
  currently on `normalization.constraint.latest_time`.
- Ariadne implemented and integrated the fixture after realigning stale
  Claude/current and Antigravity/current mirrors to `handoff/current`.

## Sprint 187 Verification

- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q`
  passed serially (`.x..............................`; one pre-existing xfail,
  existing warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q`
  passed (`8 passed, 1 skipped`; existing warnings only).
- `git diff --check` passed.
- Integration commit: `f2a046ff`.
- Push result: `git push origin master` succeeded.
- Sprint engine state: continuing unless Yuri pauses.

## Sprint 186 What Changed

- Added
  `tests/fixtures/bernie_scenarios/interpret_reference_date_change_no_relative_wording.yaml`.
- The fixture proves a follow-up turn with a changed `reference_date` but no
  date wording keeps the auto-threaded absolute appointment date instead of
  re-resolving it against the current turn date.
- The same follow-up applies the current time change from `09:00` to `10:00`
  while preserving patient, practitioner, date, and duration.
- Updated `tests/fixtures/bernie_scenarios/README.md` to record
  reference-date no-op prompt coverage.

Sprint 186 is a Fable-aligned Programme 2D / Programme 2G backend-readiness
fixture increment. It continues the native Bernie prompt-thread route-level
track and does not open live provider, provider dry-run, runtime memory, RAG,
GraphRAG, H15/H-series runtime imports, historical diary material access,
GraphQL mutations, or model-to-database writes.

Worker mix:

- Ariadne implemented and integrated the narrow fixture.
- One DeepSeek lane recommended a future time-window threading fixture.
- One DeepSeek replacement lane for unavailable Claude recommended a future
  same-time anaphora fixture.
- One DeepSeek replacement lane for unavailable Antigravity recommended the
  integrated no-relative-wording reference-date drift fixture.
- Claude and Antigravity durable mirrors were 30 commits behind and dirty with
  old Sprint 160-era changes, so they were treated as unavailable in this
  sprint window and replaced with extra DeepSeek lanes under the
  Ariadne-plus-three rule.

## Sprint 186 Verification

- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q`
  passed serially (`.x.............................`; one pre-existing xfail,
  existing warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q`
  passed (`8 passed, 1 skipped`; existing warnings only).
- `git diff --check` passed.
- Note: an earlier parallel run of scenario replay and integrity hit the known
  transient Postgres enum DDL race (`userrole` duplicate type); rerunning the
  replay suite serially passed.
- Integration commit: `1db4cd4c`.
- Push result: `git push origin master` succeeded.
- Sprint engine state: continuing unless Yuri pauses.

## Sprint 185 What Changed

- Added
  `tests/fixtures/bernie_scenarios/interpret_reference_date_reload_resolve_conflict.yaml`.
- The fixture proves repeated relative-date wording re-resolves against the
  current turn `reference_date` instead of reusing the previous turn-level
  resolution or the auto-threaded prior requested appointment date.
- The two-turn case first resolves `next Tuesday` from `2026-07-15` to
  `2026-07-21`, then resolves the same phrase from `2026-07-08` to
  `2026-07-14` while preserving threaded patient, practitioner, time, and
  duration.
- Updated `tests/fixtures/bernie_scenarios/README.md` to record
  reference-date reload/reset coverage.
- Documented Yuri's Ariadne-plus-three protocol correction in
  `orchestration/protocol_alerts.md`: general sprint work should use Ariadne
  plus Claude, Antigravity, and DeepSeek by default, with extra DeepSeek lanes
  substituting immediately when Claude or Antigravity is unavailable.

Sprint 185 is a Fable-aligned Programme 2D / Programme 2G backend-readiness
fixture increment. It continues the native Bernie prompt-thread route-level
track and does not open live provider, provider dry-run, runtime memory, RAG,
GraphRAG, H15/H-series runtime imports, historical diary material access,
GraphQL mutations, or model-to-database writes.

Worker mix:

- Ariadne implemented and integrated the narrow fixture directly.
- DeepSeek reviewed the reference-date reload edge and recommended the
  conflict shape: same relative phrase, different current-turn reference date,
  prior requested appointment auto-threaded, and current resolution winning.
- The Ariadne-plus-three correction was applied during this sprint. Future
  general sprints must use Ariadne plus Claude, Antigravity, and DeepSeek, with
  unavailable Claude/Antigravity lanes replaced by extra DeepSeek workers in
  the same sprint window.

## Sprint 185 Verification

- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q`
  passed serially (`.x............................`; one pre-existing xfail,
  existing warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q`
  passed (`8 passed, 1 skipped`; existing warnings only).
- `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_guard.py orchestration\protocol_alerts.md`
  passed.
- `git diff --check` passed.
- Note: an earlier parallel run of scenario replay and integrity hit the known
  transient Postgres enum DDL race (`userrole` duplicate type); rerunning the
  tests serially passed.
- Integration commit: `13d5dbc9`.
- Push result: `git push origin master` succeeded.
- Sprint engine state: continuing unless Yuri pauses.

## Sprint 184 What Changed

- Added
  `tests/fixtures/bernie_scenarios/interpret_default_duration_no_type.yaml`.
- The fixture proves a complete generic receptionist booking instruction with
  patient, practitioner, date, and time, but no duration or appointment type,
  defaults to `duration_minutes=15` at the route boundary.
- The fixture also asserts fake-provider metadata, no live provider, explicit
  default-duration assumption field/value, and no appointment/audit writes.
- Updated `tests/fixtures/bernie_scenarios/README.md` to record
  default-duration prompt coverage.
- Documented Yuri's protocol correction in `orchestration/protocol_alerts.md`:
  product-facing EMR4 development and sprint-direction work should stay in a
  multi-agent stream by default, using Claude and Antigravity when available
  and DeepSeek as an independent worker/reviewer or fallback lane.

Sprint 184 returns the sprint engine to the Fable-aligned Bernie/Diary track:
native prompt-thread and fake-provider route-level behavior first, with provider
and runtime gates still closed. It is a backend-readiness fixture increment, not
orchestration cleanup, and it does not open live provider, provider dry-run,
runtime memory, RAG, GraphRAG, H15/H-series runtime imports, historical diary
material access, GraphQL mutations, or model-to-database writes.

Worker mix:

- Ariadne implemented the narrow fixture directly.
- DeepSeek reviewed fixture scope and brittleness, confirmed Fable alignment,
  and recommended removing the one-off exact `reversible_copy` assertion. That
  change was accepted so the fixture matches the rest of the corpus by asserting
  `assumptions.0.field` and `assumptions.0.assumed_value`.

## Sprint 184 Verification

- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q`
  passed serially (`.x...........................`; one pre-existing xfail,
  existing warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q`
  passed (`8 passed, 1 skipped`; existing warnings only).
- `git diff --check` passed.
- Note: an earlier parallel run of scenario replay and integrity hit the known
  transient Postgres enum DDL race (`userrole` duplicate type); rerunning the
  scenario replay serially passed.
- Integration commit: `cf683833`.
- Push result: `git push origin master` succeeded.
- Sprint engine state: continuing unless Yuri pauses.

## Sprint 183 What Changed

- Updated `orchestration/protocol_alerts.md` so the Bernie Interpretation
  Harness readiness alert also cites
  `scripts\bernie_provider_boundary_readiness_report.py`.
- Added exact compact closed provider-boundary values to the protocol alert:
  `default_provider=disabled`, `live_provider_enabled=false`,
  `provider_calls_performed=false`, `route_behavior_changed=false`,
  `database_access_performed=false`, `memory_or_rag_access_performed=false`,
  and `historical_diary_material_access_performed=false`.
- The current release/protocol slice
  (`orchestration\sprint_closeout.md`,
  `orchestration\bernie_release_gates.md`, and
  `orchestration\protocol_alerts.md`) now passes the proposal-surface guard.

Sprint 183 is a protocol guardrail documentation sprint. It does not change
runtime code, routes, provider configuration, database behavior, memory, RAG,
GraphRAG, H15/H-series imports, historical diary processing, GraphQL mutations,
or model-to-database write authority.

## Sprint 183 Verification

- `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_guard.py orchestration\sprint_closeout.md orchestration\bernie_release_gates.md orchestration\protocol_alerts.md`
  passed.
- `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_report.py docs orchestration`
  returned `missing_readiness_count=446`, `unreadable_markdown_count=0`, and
  `total_fail_closed_findings_count=446`, down from Sprint 182's 447/0/447.
- `git diff --check` passed.
- Integration commit: `8374109e`.
- Push result: `git push origin master` succeeded.
- Sprint engine state: continuing unless Yuri pauses.

## Sprint 182 What Changed

- Converted the two markdown files that the proposal-surface guard reported as
  unreadable into UTF-8-readable markdown:
  `orchestration/agent_inbox/codex/plan-r30-action-grammar-replay-consumer.md`
  and
  `orchestration/agent_inbox/codex/review-deepseek-sprint159-bernie-tool-intent-confirm-header.md`.
- Added exact closed-gate proposal-surface citations to the now-readable R30
  plan packet so it does not move from unreadable to missing-readiness backlog.
- Removed trailing-space hard breaks surfaced by the UTF-16-to-UTF-8 conversion
  in the Sprint 159 review artifact.

Sprint 182 is a documentation/encoding cleanup sprint. It does not change
runtime code, routes, provider configuration, database behavior, memory, RAG,
GraphRAG, H15/H-series imports, historical diary processing, GraphQL mutations,
or model-to-database write authority.

## Sprint 182 Verification

- `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_guard.py orchestration\agent_inbox\codex\plan-r30-action-grammar-replay-consumer.md orchestration\agent_inbox\codex\review-deepseek-sprint159-bernie-tool-intent-confirm-header.md`
  passed.
- `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_report.py docs orchestration`
  returned `missing_readiness_count=447`, `unreadable_markdown_count=0`, and
  `total_fail_closed_findings_count=447`, down from Sprint 181's 447/2/449.
- `git diff --check` passed.
- Integration commit: `76f8cf26`.
- Push result: `git push origin master` succeeded.
- Sprint engine state: continuing unless Yuri pauses.

## Sprint 181 What Changed

- Added exact proposal-surface guard citations to
  `docs/adversarial/h64_interpretation_readiness_independent_review.md`.
- The citations include the required readiness and provider-boundary commands
  plus compact closed values such as `runtime_or_provider_wiring_ready=false`,
  `raw_trove_access_ready=false`, `runtime_gate_decision=blocked`,
  `live_provider_enabled=false`, and no provider/DB/memory/trove activity.
- The H63/H64 review-doc slice now passes the proposal-surface guard directly.

Sprint 181 is a narrow recent-review-doc backlog triage sprint. It does not
change runtime code, routes, provider configuration, database behavior, memory,
RAG, GraphRAG, H15/H-series imports, historical diary processing, GraphQL
mutations, or model-to-database write authority.

Worker mix:

- DeepSeek confirmed the patched H64 pattern passes the guard and asserts
  blocked/false status rather than readiness.

## Sprint 181 Verification

- `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_guard.py docs\adversarial\h63_interpretation_independent_review_brief.md docs\adversarial\h64_interpretation_readiness_independent_review.md`
  passed.
- `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_report.py docs orchestration`
  returned `missing_readiness_count=447`, `unreadable_markdown_count=2`, and
  `total_fail_closed_findings_count=449`, down from Sprint 180's 448/2/450.
- `git diff --check` passed.
- Integration commit: `654e67fc`.
- Push result: `git push origin master` succeeded.
- Sprint engine state: continuing unless Yuri pauses.

## Sprint 180 What Changed

- Added exact proposal-surface guard citation blocks to
  `docs/bernie-prompt-thread-tranche-readiness.md` and
  `docs/bernie-prompt-thread-fake-provider-backend-pass.md`.
- The citations include the required readiness and provider-boundary commands
  plus compact closed values such as `runtime_or_provider_wiring_ready=false`,
  `raw_trove_access_ready=false`, `runtime_gate_decision=blocked`,
  `live_provider_enabled=false`, and no provider/DB/memory/trove activity.
- The two recent prompt-thread evidence docs now pass the proposal-surface
  guard directly without implying live-provider, provider-quality, runtime,
  memory, H15/H-series, historical diary, GraphQL, or model-write readiness.

Sprint 180 is a narrow backlog-slice triage sprint over recent evidence docs. It
does not change runtime code, routes, provider configuration, database behavior,
memory, RAG, GraphRAG, H15/H-series imports, historical diary processing,
GraphQL mutations, or model-to-database write authority.

Worker mix:

- DeepSeek confirmed the patched two-doc slice passes the guard with no missing
  items and no live-provider/runtime-readiness implication.

## Sprint 180 Verification

- `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_guard.py docs\bernie-prompt-thread-tranche-readiness.md docs\bernie-prompt-thread-fake-provider-backend-pass.md`
  passed.
- `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_report.py docs orchestration`
  returned `missing_readiness_count=448`, `unreadable_markdown_count=2`, and
  `total_fail_closed_findings_count=450`, down from Sprint 179's 450/2/452.
- `git diff --check` passed.
- Integration commit: `dbb110ca`.
- Push result: `git push origin master` succeeded.
- Sprint engine state: continuing unless Yuri pauses.

## Sprint 179 What Changed

- Added `scripts/bernie_interpretation_proposal_surface_report.py`, a safe
  aggregate JSON report over the proposal-surface guard.
- The report emits counts and closed boundary posture only: markdown scanned,
  trigger hits, missing-readiness findings, unreadable-markdown findings, total
  fail-closed findings, required command names, prohibited boundary map, and
  omitted-field declarations.
- The report deliberately omits paths, filenames, decode-error text, trigger
  phrase text, and document text.
- Added `tests/test_bernie_interpretation_proposal_surface_report.py` covering
  aggregate counts, CLI JSON output, omitted path/text fields, nonnegative and
  consistent count invariants, and closed runtime/provider boundary posture.

Sprint 179 is a reporting sprint. It does not change runtime code, routes,
provider configuration, database behavior, memory, RAG, GraphRAG, H15/H-series
imports, historical diary processing, GraphQL mutations, or model-to-database
write authority.

Worker mix:

- DeepSeek reviewed the aggregate report shape and recommended trigger-hit
  counts, boundary/omitted-field declarations, and no path/decode-error leakage.

## Sprint 179 Verification

- `.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_proposal_surface_report.py tests\test_bernie_interpretation_proposal_surface_guard.py -q`
  (`22 passed`; existing warnings only).
- `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_report.py docs orchestration`
  returned `scanned_markdown_count=1045`, `trigger_phrase_hit_count=456`,
  `missing_readiness_count=450`, `unreadable_markdown_count=2`, and
  `total_fail_closed_findings_count=452`, with paths/text omitted and boundary
  posture prohibited/false.
- `git diff --check` passed.
- Integration commit: `6460ce50`.
- Push result: `git push origin master` succeeded.
- Sprint engine state: continuing unless Yuri pauses.

## Sprint 178 What Changed

- Changed `scripts/bernie_interpretation_proposal_surface_guard.py` to treat
  non-UTF-8 markdown as an explicit fail-closed finding instead of crashing or
  silently decoding with replacement.
- Added `ProposalSurfaceGuardFindings` and `scan_proposal_surface()` so callers
  can distinguish missing readiness citations from unreadable markdown.
- Kept the compatibility wrapper fail-closed by returning unreadable markdown
  paths together with missing-readiness paths.
- Added regression coverage proving invalid UTF-8 markdown is reported as
  unreadable with a path-specific decode error.

Sprint 178 is a guard robustness sprint. It does not edit historical backlog
documents en masse and does not change runtime code, routes, provider
configuration, database behavior, memory, RAG, GraphRAG, H15/H-series imports,
historical diary processing, GraphQL mutations, or model-to-database write
authority.

Worker mix:

- DeepSeek reviewed the unreadable-markdown options and recommended
  path-specific diagnostics that fail closed.

## Sprint 178 Verification

- `.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_proposal_surface_guard.py -q`
  (`12 passed`; existing warnings only).
- `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_guard.py docs orchestration`
  now fails closed with missing-citation backlog paths plus two explicit
  unreadable markdown diagnostics instead of crashing.
- `git diff --check` passed.
- Integration commit: `06189cb0`.
- Push result: `git push origin master` succeeded.
- Sprint engine state: continuing unless Yuri pauses.

## Sprint 177 What Changed

- Extended `scripts/bernie_interpretation_proposal_surface_guard.py` so
  proposal markdown is checked for more release-gate wording: route/provider
  integration, provider prompt/dry-run integration, live provider enablement,
  Access AI, H15/H-series runtime imports, historical diary/raw-trove/local-data
  access, model selection, and provider-specific aliasing.
- Narrowed the old generic `aliasing` trigger to provider-specific wording so
  unrelated code-aliasing notes do not require provider-boundary citations.
- Added regression coverage in
  `tests/test_bernie_interpretation_proposal_surface_guard.py`.
- Updated `docs/adversarial/h63_interpretation_independent_review_brief.md` to
  include the provider-boundary readiness report command and expected closed
  values before any provider-boundary recommendation.

Sprint 177 is a bounded guardrail sprint. It changes only proposal/review
artifact validation and one existing review brief. It does not change runtime
code, routes, provider configuration, database behavior, memory, RAG, GraphRAG,
H15/H-series imports, historical diary processing, GraphQL mutations, or
model-to-database write authority.

Worker mix:

- DeepSeek reviewed the guard vocabulary and identified additional release-gate
  variants plus the generic-aliasing false-positive risk.

## Sprint 177 Verification

- `.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_proposal_surface_guard.py -q`
  (`11 passed`; existing warnings only).
- `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_guard.py docs\adversarial\h63_interpretation_independent_review_brief.md`
  passed.
- `git diff --check` passed.
- Integration commit: `a6815d8d`.
- Push result: `git push origin master` succeeded.
- Sprint engine state: continuing unless Yuri pauses.

## Sprint 176 What Changed

- Added `tests/test_bernie_fake_provider_evidence_labels.py`, a static guard
  over the prompt-thread readiness and backend-pass evidence packets.
- The guard requires the backend-pass packet to keep its
  fake-provider/route-level evidence label, explicitly deny live-provider and
  provider-quality evidence, and preserve the provider-boundary false values.
- The guard requires the tranche-readiness packet to keep the closed-gate
  labels for fake-provider testing and `live_provider: false`.

Sprint 176 is a small evidence-label integrity sprint. It does not change
runtime code, routes, provider configuration, database behavior, memory, RAG,
GraphRAG, H15/H-series imports, historical diary material access, GraphQL
mutations, or model-to-database write authority.

## Sprint 176 Verification

- `.venv\Scripts\python.exe -m pytest tests\test_bernie_fake_provider_evidence_labels.py -q`
  (`2 passed`; existing warnings only).
- `git diff --check` passed.
- Integration commit: `14facb34`.
- Push result: `git push origin master` succeeded.
- Sprint engine state: continuing unless Yuri pauses.

## Sprint 175 What Changed

- Added `docs/bernie-prompt-thread-fake-provider-backend-pass.md`, recording the
  narrow fake-provider backend pass for the authored Bernie prompt-thread
  corpus.
- The report explicitly labels this evidence as fake-provider, route-level
  backend evidence, not live-provider evidence or provider-quality evidence.
- The pass records the route used by the replay harness:
  `POST /api/v1/appointments/proposals/bernie/interpret-booking-instruction`.
- The pass records the existing guard posture: fake interpreter configured,
  `_get_default_provider` forbidden by monkeypatch, and appointment/audit row
  counts checked.

Sprint 175 is a backend-readiness evidence sprint inside Programme 2D Reception
Copilot Readiness and Programme 2G Bernie API Spine review-readiness. It moves
from fixture-tranche readiness to a documented backend-pass result without
changing runtime code or opening provider gates.

Worker mix:

- Ariadne-only reporting was chosen because Sprint 174 had already integrated
  DeepSeek's readiness review and this sprint only records the required gate
  checks plus existing replay-harness evidence.

Sprint 175 does not open runtime route wiring from the provider-free
interpretation harness, provider prompt/dry-run wiring, live-provider enablement,
memory/RAG/GraphRAG, H15/H-series runtime imports, historical diary material
access, GraphQL mutations, or model-to-database writes.

## Sprint 175 Verification

- `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`
  returned `runtime_or_provider_wiring_ready=false`,
  `raw_trove_access_ready=false`, `runtime_gate_decision=blocked`, and
  `sprint_engine_state=continuing`.
- `.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py`
  returned `default_provider=disabled`, `live_provider_enabled=false`,
  `provider_calls_performed=false`, `route_behavior_changed=false`,
  `database_access_performed=false`, `memory_or_rag_access_performed=false`, and
  `historical_diary_material_access_performed=false`.
- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q`
  (`.x..........................`; one pre-existing xfail, existing warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q`
  (`8 passed, 1 skipped`; existing warnings only).
- `git diff --check` passed.
- Integration commit: `abfaac3d`.
- Push result: `git push origin master` succeeded; GitHub reported the
  repository moved notice and the existing moderate Dependabot alert.

Sprint engine state: continuing. No user intervention is required. Next planned
step is a small evidence-label guard/report or the next bounded
backend-readiness step, still with all provider/runtime/memory/H15/trove/GraphQL
and model-write gates closed.

---

## Sprint 174 What Changed

- Added `docs/bernie-prompt-thread-tranche-readiness.md`, a compact readiness
  packet for the authored Bernie/Diary prompt-thread fixture tranche.
- Integrated DeepSeek's independent readiness review at
  `orchestration/agent_inbox/codex/review-deepseek-sprint174-fixture-tranche-readiness.md`.
- Recorded that the tranche is ready for a narrow non-intercepted fake-provider
  backend pass, with remaining fixture-only gaps non-blocking.

Sprint 174 is a strategy/review integration sprint inside Programme 2D
Reception Copilot Readiness and Programme 2G Bernie API Spine
review-readiness. It closes the fixture tranche as sufficient for the next
bounded evidence step without authorizing live-provider, runtime memory, H15,
historical diary, GraphQL, or model-write gates.

Worker mix:

- Ariadne drafted the readiness packet.
- DeepSeek Flash independently reviewed the fixture tranche and returned
  `READY` for a narrow fake-provider backend pass with three non-blocking gaps.
- Claude/Antigravity were not re-run because their durable mirrors remain
  stale/dirty and this was a bounded review artifact, not a separable
  implementation surface.

Sprint 174 does not open runtime route wiring from the provider-free
interpretation harness, provider prompt/dry-run wiring, live-provider enablement,
memory/RAG/GraphRAG, H15/H-series runtime imports, historical diary material
access, GraphQL mutations, or model-to-database writes.

## Sprint 174 Verification

- `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`
  returned `runtime_or_provider_wiring_ready=false`,
  `raw_trove_access_ready=false`, `runtime_gate_decision=blocked`, and
  `sprint_engine_state=continuing`.
- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q`
  (`.x..........................`; one pre-existing xfail, existing warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q`
  (`8 passed, 1 skipped`; existing warnings only).
- `git diff --check` passed.
- Integration commit: `67b051b3`.
- Push result: `git push origin master` succeeded; GitHub reported the
  repository moved notice and the existing moderate Dependabot alert.

Sprint engine state: continuing. No user intervention is required. Next planned
step is the narrow non-intercepted fake-provider backend pass, provided the same
readiness values remain blocked/false before launch.

---

## Sprint 173 What Changed

- Added `interpret_context_multi_frame_source_reset.yaml`, proving that a request
  derived from multiple diary context frames can still be threaded as a
  requested appointment when a follow-up omits `context_frames`.
- The same fixture then proves explicit `context_frames: []` clears that derived
  requested appointment and asks again instead of carrying forward
  patient/practitioner/date.
- Updated the Bernie scenario corpus README so context-threading coverage
  includes requested appointments originally derived from multiple diary context
  frames.

Sprint 173 is a tiny fixture-only guardrail hardening pass inside the Programme
2D Reception Copilot Readiness / Programme 2G Bernie API Spine
review-readiness track. It consumes the remaining practical Sprint 171 DeepSeek
fixture recommendation and keeps the tranche inside authored synthetic
fake-provider replay.

Worker mix:

- Ariadne-only implementation was chosen because the accepted recommendation
  was one test-only YAML fixture with no route or UI changes.
- No new Claude/Antigravity run was launched while their durable mirrors remain
  stale/dirty.

Sprint 173 does not open runtime route wiring from the provider-free
interpretation harness, provider prompt/dry-run wiring, live-provider enablement,
memory/RAG/GraphRAG, H15/H-series runtime imports, historical diary material
access, GraphQL mutations, or model-to-database writes.

## Sprint 173 Verification

- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -k interpret_context_multi_frame_source_reset -q`
  (`1 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q`
  (`.x..........................`; one pre-existing xfail, existing warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q`
  (`8 passed, 1 skipped`; existing warnings only).
- `git diff --check` passed.
- Integration commit: `62325db2`.
- Push result: `git push origin master` succeeded; GitHub reported the
  repository moved notice and the existing moderate Dependabot alert.

Sprint engine state: continuing. No user intervention is required. Next planned
step is either a narrow non-intercepted fake-provider backend pass or a compact
closeout/readiness artifact for the authored prompt-thread tranche.

---

## Sprint 172 What Changed

- Added `interpret_explicit_requested_appointment_frame.yaml`, proving that a
  caller-supplied `requested_appointment` frame can provide prior appointment
  fields directly in `context_frames`.
- The fixture asserts that current-turn instruction text still wins for the
  updated time: explicit frame payload supplies patient/practitioner/date/
  duration, while the instruction changes `earliest_time` from `09:00` to
  `09:30`.
- Updated the Bernie scenario corpus README to record explicit-frame prompt
  coverage.

Sprint 172 is a tiny fixture-only guardrail hardening pass inside the Programme
2D Reception Copilot Readiness / Programme 2G Bernie API Spine
review-readiness track. It directly consumes a Sprint 171 DeepSeek
recommendation and closes the highest-value remaining context-frame coverage
gap without changing runtime code.

Worker mix:

- Ariadne-only implementation was chosen because the accepted recommendation
  was one test-only YAML fixture with an obvious route helper contract.
- The Sprint 171 DeepSeek adversarial artifact is the source review for this
  follow-on. No new Claude/Antigravity run was launched while their durable
  mirrors remain stale/dirty.

Sprint 172 does not open runtime route wiring from the provider-free
interpretation harness, provider prompt/dry-run wiring, live-provider enablement,
memory/RAG/GraphRAG, H15/H-series runtime imports, historical diary material
access, GraphQL mutations, or model-to-database writes.

## Sprint 172 Verification

- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -k interpret_explicit_requested_appointment_frame -q`
  (`1 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q`
  (`.x.........................`; one pre-existing xfail, existing warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q`
  (`8 passed, 1 skipped`; existing warnings only).
- `git diff --check` passed.
- Integration commit: `f7285175`.
- Push result: `git push origin master` succeeded; GitHub reported the
  repository moved notice and the existing moderate Dependabot alert.

Sprint engine state: continuing. No user intervention is required. Next planned
step is either DeepSeek's remaining multi-frame reset fixture or the narrow
non-intercepted fake-provider backend pass.

---

## Sprint 171 What Changed

- Added `interpret_context_reset_patient_date_no_practitioner.yaml`, proving that
  after a complete prior request, an explicit `context_frames: []` reset with
  restated patient and relative date does not inherit practitioner, time, or
  duration from the prior requested appointment.
- Kept the canonical fixture more assertive than the duplicate DeepSeek
  suggestion by checking raw `date_from: tomorrow`, default
  `duration_minutes: 15`, `normalization.safe: false`, missing practitioner,
  clarifying copy, and no appointment/audit writes.
- Tightened `interpret_no_prior_frame_no_merge.yaml` wording so it describes its
  actual first-turn empty-context scope instead of overclaiming stale-context
  coverage.
- Updated `tests/fixtures/bernie_scenarios/README.md` to record reset/no-merge
  follow-up coverage.
- Integrated DeepSeek's Sprint 171 adversarial review artifact at
  `orchestration/agent_inbox/codex/review-deepseek-sprint171-reset-no-prior-context-matrix.md`.

Sprint 171 is a narrow guardrail hardening sprint inside the Programme 2D
Reception Copilot Readiness / Programme 2G Bernie API Spine review-readiness
track. It advances the larger objective of proving authored Bernie prompt-thread
context semantics before any provider/runtime/memory gate opens. The sprint
stayed fixture-only because the behavior under test is already implemented and
needed deterministic replay coverage, not new route behavior.

Worker mix:

- Claude task packet dispatched:
  `orchestration/agent_inbox/claude/claude-sprint171-reset-no-prior-context-matrix.md`.
- Antigravity task packet dispatched:
  `orchestration/agent_inbox/antigravity/antigravity-sprint171-reset-no-prior-context-review.md`.
- External Claude/Antigravity mirrors were stale/dirty with old Sprint 160 staged
  reversions, so Ariadne did not destructively reset them during this sprint.
- DeepSeek Flash lane 1 produced the adversarial review artifact and identified
  remaining fixture-only recommendations.
- DeepSeek Flash lane 2 independently proposed the same patient+relative-date
  reset fixture; Ariadne kept the stronger local version and removed the
  duplicate.

Sprint 171 does not open runtime route wiring from the provider-free
interpretation harness, provider prompt/dry-run wiring, live-provider enablement,
memory/RAG/GraphRAG, H15/H-series runtime imports, historical diary material
access, GraphQL mutations, or model-to-database writes.

## Sprint 171 Verification

- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -k "interpret_context_temporal_drift_followup or interpret_context_temporal_drift_reset_no_merge or interpret_context_reset_patient_date_no_practitioner or interpret_context_frames_auto_thread_vs_empty or interpret_no_prior_frame_no_merge" -q`
  (`5 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q`
  (`.x........................`; one pre-existing xfail, existing warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q`
  (`8 passed, 1 skipped`; existing warnings only).
- `git diff --check` passed with the known CRLF normalization warning on
  `interpret_no_prior_frame_no_merge.yaml`.
- Integration commit: `f6a3ea50`.
- Push result: `git push origin master` succeeded; GitHub reported the
  repository moved notice and the existing moderate Dependabot alert.

An earlier concurrent integrity/replay run hit the known transient Postgres enum
DDL race (`userrole` duplicate type); rerunning the integrity check serially
passed.

Sprint engine state: continuing unless Yuri asks for a pause. No user
intervention is required for the fixture tranche itself. Next planned step is a
small Sprint 172 fixture-only pass using one of DeepSeek's remaining
recommendations, preferably explicit `requested_appointment` frame input or
multi-frame reset coverage.

---

## Sprint 170 What Changed

- Added `interpret_context_temporal_drift_reset_no_merge.yaml`, an authored
  synthetic fake-provider route-level fixture proving that explicit
  `context_frames: []` clears prior requested-appointment context.
- The fixture stages a complete initial request, then sends a later-turn
  relative `tomorrow` follow-up with Dr Shera restated and empty context. It
  proves `tomorrow` resolves from the current turn `reference_date:
  2026-07-09` to `2026-07-10`, while patient/time/duration are not inherited
  from the prior requested appointment.
- Updated `AGENTS.md` so the baton records Sprint 170 as the current active
  prompt-thread guardrail and recommends continuing only inside reset/no-prior
  context or non-intercepted fake-provider backend edges.

Sprint 170 is a narrow guardrail hardening sprint inside the Programme 2D
Reception Copilot Readiness / Programme 2G Bernie API Spine review-readiness
track. It advances the larger objective of proving Bernie prompt-thread context
semantics before any provider/runtime/memory gate opens. The sprint was small
because it touched only an executable fixture and handover state after Sprint
169 had already established the adjacent threaded-date behavior.

Sprint 170 does not open runtime route wiring from the provider-free
interpretation harness, provider prompt/dry-run wiring, live-provider
enablement, memory/RAG/GraphRAG, H15/H-series runtime imports, historical diary
material access, GraphQL mutations, or model-to-database writes.

## Sprint 170 Verification

- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -k interpret_context_temporal_drift_reset_no_merge -q`
  (`1 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -k "interpret_context_temporal_drift_followup or interpret_context_temporal_drift_reset_no_merge or interpret_context_frames_auto_thread_vs_empty or interpret_no_prior_frame_no_merge" -q`
  (`4 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q`
  (`8 passed, 1 skipped`; existing Starlette/Google GenAI warnings only).
- `git diff --check` passed.
- Integration commit: `92c96c36`.
- Push result: `git push origin master` succeeded; GitHub reported the
  repository moved notice and the existing moderate Dependabot alert.

Initial parallel verification hit the known transient Postgres enum DDL race
(`userrole` duplicate type) when two DB-initializing tests ran at once; rerunning
the replay by itself passed.

Sprint engine state: continuing. No user intervention is required; next planned
step is Sprint 171, a bounded reset/no-prior context matrix using the preferred
Claude, Antigravity, and DeepSeek worker mix where available, with extra
DeepSeek lanes substituting for temporary Claude/Antigravity limits.

---

## Sprint 169 What Changed

- Added `interpret_context_temporal_drift_followup.yaml`, an authored synthetic
  fake-provider route-level fixture proving that an omitted-context follow-up can
  preserve threaded patient/practitioner/time/duration while resolving a new
  relative date against the current turn `reference_date`.
- The fixture intentionally asserts both raw and normalized date contracts:
  `command_candidate.date_from` remains `tomorrow`, while
  `normalization.constraint.date_from` resolves to `2026-07-10` from the
  follow-up turn's `reference_date: 2026-07-09`.
- Updated the Bernie scenario corpus README to record temporal-drift follow-up
  coverage.
- Recorded worker lanes:
  - Claude CLI review in
    `orchestration/agent_inbox/claude/claude-sprint169-temporal-drift-followup.md`.
  - Antigravity CLI product/receptionist review in
    `orchestration/agent_inbox/antigravity/antigravity-sprint169-temporal-drift-followup.md`.
  - DeepSeek review in
    `orchestration/agent_inbox/codex/review-deepseek-sprint169-temporal-drift-followup.md`.

Sprint 169 does not open runtime route wiring from the provider-free
interpretation harness, provider prompt/dry-run wiring, live-provider
enablement, memory/RAG/GraphRAG, H15/H-series runtime imports, historical diary
material access, GraphQL mutations, or model-to-database writes.

## Sprint 169 Verification

- `.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\ -q`
  (`.x......................`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q`
  (`........s`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`
  succeeded with `runtime_or_provider_wiring_ready=false`,
  `raw_trove_access_ready=false`, and `runtime_gate_decision=blocked`.
- `.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py`
  succeeded with `default_provider=disabled`,
  `live_provider_enabled=false`, `provider_calls_performed=false`,
  `route_behavior_changed=false`, `database_access_performed=false`,
  `memory_or_rag_access_performed=false`, and
  `historical_diary_material_access_performed=false`.
- `git diff --check` clean.
- Note: one parallel verification attempt hit the existing Postgres test-schema
  enum creation race (`CREATE TYPE userrole` duplicate) when two pytest
  processes started together. The standalone `tests\bernie_scenarios\` rerun
  passed.

Publication state:

- Implementation commit SHA: `1f3268f6`.
- Closeout metadata commit SHA: `2f8704fe`.
- Push result: `origin/master`, `handoff/current`, `codex/current`,
  `claude/current`, and `antigravity/current` aligned at Sprint 169 final
  closeout head.
- Final `git status --short --branch`: clean after publication push.

Strategic position: Sprint 169 locks a subtle reference-date drift behavior that
automated prompt troubleshooting will need before broader backend or provider
evidence claims. Provider-quality and live-provider gates remain closed.

Sprint engine state: continuing unless Yuri pauses. Next recommended work is a
narrow non-intercepted fake-provider backend pass or an additional no-prior-date
threading edge fixture.

---

## Previous Closeout - Sprint 168

Sprint 168 added `interpret_multi_field_missing_no_context.yaml`, adjusted
clarifying-copy ordering so under-specified patient-only prompts ask for missing
practitioner/date together, and preserved non-UUID practitioner-name
pre-resolution for live-provider-style payloads. It was committed through
`0f19ca6b`, closeout metadata through `ab8ae0a9`, and published through final
closeout head `97f6f52b`.

---

## Previous Closeout - Sprint 167

Sprint 167 added `interpret_context_practitioner_override.yaml` and narrowed
interpretation context merge order so a current-turn practitioner name overrides
prior requested-appointment context while patient/date/time/duration thread
forward. It was committed through `2620bed1`, closeout metadata through
`0fbd5ee8`, and published through final closeout head `79509e99`.

---

## Previous Closeout - Sprint 166

Sprint 166 added `interpret_context_frames_auto_thread_vs_empty.yaml`, proving
omitted `context_frames` auto-threads prior requested appointment context while
explicit `context_frames: []` clears the thread and re-clarifies. It was
committed through `b83e694f`, closeout metadata through `0f474c13`, and
publication status through `e5f65906`.

---

## Previous Closeout - Sprint 165

Sprint 165 added the fake-provider route-level omitted-date/no-context fallback
fixture, proving Bernie asks for the missing date instead of guessing while
preserving no-write/provider-boundary gates. It was committed through
`0ccea30d`, closeout metadata through `0f2ecc3d`, and publication status through
`45d7cb6`.

---

## Previous Closeout - Sprint 164

Sprint 164 added fake-provider route-level fixtures proving selected proposal
date beats selected diary appointment and visible diary page context, and
selected diary appointment date beats visible diary page context. It was
committed through `9eb3a6a5`, closeout metadata through `7a9659a4`, and
publication status through `dfa6d75`.

---

## Previous Closeout - Sprint 163

Sprint 163 added four fake-provider route-level interpret edge fixtures for
empty instruction validation, unknown sentinel patient names without invented
patient ids, visible-diary date context, and per-turn reference-date drift. It
was committed through `d1804cb6`, closeout metadata through `a25b69ea`, and
publication status through `e6e5c1e`.

---

## Previous Closeout - Sprint 162

Sprint 162 added the executable `interpret` action to
`tests/bernie_scenarios`, threaded `requested_appointment` frames, enabled
interpret -> search -> select replay, added deterministic confirm
`Idempotency-Key` headers, and introduced 10 authored synthetic natural
prompt-thread fixtures. It was committed through `a31ebfdf`, closeout metadata
through `b96f5a90`, and publication status through `bd4f598`.

---

## Previous Closeout - Sprint 160

Sprint 160 added `orchestration/bernie_diary_review_readiness_sprint160.md`,
verified blocked readiness/provider values, integrated DeepSeek's adversarial
review, and paused the sprint engine for Yuri's hands-on Diary/Bernie review
without claiming live-provider or live-backend proof. It was committed and
pushed through `0714ed2`, followed by the post-closeout launcher fix `6e8c19b`.

---

## Previous Closeout - Sprint 159

## Sprint 159 What Changed

- Updated `docs/diary/diary.js` so `confirmBernieToolIntentChange()` sends HTTP
  `Idempotency-Key` to the signed update-confirm endpoint.
- Reused the same freshness-derived key strategy as ordinary update-confirm:
  `update-confirm-{update_proposal_freshness_id}` through
  `updateConfirmIdempotencyKey(envelope, confirmPayload)`.
- Bumped `docs/diary/diary.html` to `diary.js?v=179`.
- Updated the Bernie tool-intent route-intercepted smoke test to capture and
  assert `update-confirm-fresh-tool-1`.
- Updated API-spine header inventory/checkpoint tests and living docs so the
  tool-intent confirm gap is now closed.
- Added
  `orchestration/api_spine_appointment_idempotency_bernie_tool_intent_confirm_client_header.md`.
- Integrated worker lanes:
  - DeepSeek confirmed the user-clickable missing-header bug and the small fix.
  - Replacement Claude-lane DeepSeek confirmed freshness-derived keying is
    API-spine correct for the update-confirm route family.
  - Replacement Antigravity-lane DeepSeek confirmed smoke coverage captures the
    header and no UI/provider/backend scope expanded.

## Sprint 159 Verification

- `node --check docs\diary\diary.js`.
- `.venv\Scripts\python.exe scripts\check_frontend_versions.py`
  (`[PASSED] Verification Passed: All modified assets have appropriate version bumps`).
- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_frontend_header_inventory.py tests\test_api_spine_confirm_client_surface_checkpoint.py -q`
  (`13 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py::test_bernie_tool_intent_extension_proposal_renders_and_confirms -q`
  (`1 passed`).
- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_frontend_header_inventory.py tests\test_api_spine_confirm_client_surface_checkpoint.py tests\test_api_spine_artifacts.py -q`
  (`44 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py::test_bernie_tool_intent_extension_proposal_renders_and_confirms review\test_diary_smoke.py::test_human_drag_resize_uses_signed_update_confirm_route review\test_diary_smoke.py::test_edit_modal_uses_signed_update_confirm_before_status_patch -q`
  (`3 passed`).
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean.

Publication state:

- Dispatch commit SHA: `bc31b10`.
- Implementation commit SHA: `710e1b9`.
- Closeout metadata commit SHA: `a7cf880`.
- Push result: pushed to `origin/master`; `handoff/current`, `codex/current`,
  `claude/current`, and `antigravity/current` all aligned and pushed to
  `0f94f1e4`.
- Final `git status --short --branch`: `## master...origin/master`.

Strategic position: Sprint 159 is **Programme 2G / EMR4 API Spine** client
readiness. It closes the last known enforced confirm-client header gap before a
meaningful integrated Bernie/Diary review-readiness packet.

Sprint engine state: continuing. Next recommended slice is Sprint 160: prepare
the Bernie/Diary review-readiness packet, run the required
readiness/provider-boundary checks, and pause for Yuri if checks pass.

---

## Previous Closeout - Sprint 158

## Sprint 158 What Changed

- Added `orchestration/api_spine_confirm_client_surface_checkpoint.md`.
- Added `tests/test_api_spine_confirm_client_surface_checkpoint.py`.
- Recorded that the ordinary Diary confirm-client header surface is now covered:
  create-proposal, staff create-confirm, Bernie create-confirm review adapter,
  ordinary update-confirm, status-confirm, and delete-confirm.
- Kept proposal-only backend binding and strict OpenAPI `minLength: 8`
  enforcement deferred.
- Reclassified `confirmBernieToolIntentChange()` as the next user-clickable
  enforced-route gap rather than a harmless long-term deferral, because it posts
  to the already-enforced update-confirm backend route without an HTTP
  `Idempotency-Key`.
- Recommended Sprint 159: wire Bernie tool-intent update-confirm client headers.
- Recommended Sprint 160: prepare the Bernie/Diary review-readiness packet and
  pause for Yuri if readiness checks pass.

## Sprint 158 Verification

- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_confirm_client_surface_checkpoint.py -q`
  (`5 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_frontend_header_inventory.py tests\test_api_spine_artifacts.py tests\test_api_spine_confirm_client_surface_checkpoint.py -q`
  (`44 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean.

Note: an earlier parallel pytest attempt collided while creating the shared
local Postgres test schema, leaving `gp_pms_test` half-reset. Ariadne reset only
the guarded `gp_pms_test` public schema and reran the suites sequentially.

Publication state:

- Dispatch commit SHA: `9f939dd`.
- Checkpoint implementation commit SHA: `908cf7a`.
- Closeout metadata commit SHA: `cec5746`.
- Push result: pushed to `origin/master`; `handoff/current`, `codex/current`,
  `claude/current`, and `antigravity/current` all aligned and pushed to
  `00146e87`.
- Final `git status --short --branch`: `## master...origin/master`.

Strategic position: Sprint 158 is **Programme 2G / EMR4 API Spine** checkpoint
work. It says the ordinary confirm-client surface is complete enough, but the
Bernie tool-intent update-confirm click should be fixed before asking Yuri for a
meaningful integrated Bernie/Diary review.

Sprint engine state: continuing. Next recommended slice is Sprint 159: wire
`confirmBernieToolIntentChange()` HTTP `Idempotency-Key` headers.

---

## Previous Closeout - Sprint 157

## Sprint 157 What Changed

- Updated `docs/diary/diary.js` so ordinary update-confirm calls send HTTP
  `Idempotency-Key` to `/appointments/proposals/update/confirm`.
- Added `updateConfirmIdempotencyKey(proposal, confirmPayload)`, deriving keys
  from `update_proposal_freshness_id` with the existing proposal-scoped
  generated fallback for absent or oversized freshness values.
- Wired both ordinary Diary update-confirm call sites:
  - `saveBooking()` edit-modal update confirm;
  - `handleMoveResize()` drag/move/resize update confirm.
- Left raw compatibility `PUT /appointments/{id}` fallbacks header-free.
- Left `confirmBernieToolIntentChange`, proposal-only backend binding, backend
  runtime validation, idempotency ledger semantics, providers, GraphQL,
  H15/H-series, memory/RAG/GraphRAG, and strict `minLength: 8` enforcement
  unchanged.
- Bumped `docs/diary/diary.html` to `diary.js?v=178`.
- Updated `tests/test_api_spine_frontend_header_inventory.py` and
  `review/test_diary_smoke.py` to guard modal edit and drag/resize
  update-confirm header emission.
- Refreshed the Sprint 154 diary/API header preflight inventory so it no longer
  lists ordinary update-confirm as missing after Sprint 157.
- Added
  `orchestration/api_spine_appointment_idempotency_update_confirm_client_header.md`.
- Integrated worker lanes:
  - DeepSeek review accepted freshness-derived update-confirm keys and caught
    stale preflight/test inventory language, which Ariadne fixed.
  - Replacement Claude-lane DeepSeek review found the command/idempotency
    boundary clean and recommended a compact confirm-client checkpoint next.
  - Replacement Antigravity-lane DeepSeek review found the frontend/smoke
    coverage ready for closeout, with only non-blocking future ideas.

## Sprint 157 Verification

- `node --check docs\diary\diary.js`.
- `.venv\Scripts\python.exe scripts\check_frontend_versions.py`
  (`[PASSED] Verification Passed: All modified assets have appropriate version bumps`).
- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_frontend_header_inventory.py -q`
  (`8 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py::test_human_drag_resize_uses_signed_update_confirm_route review\test_diary_smoke.py::test_edit_modal_uses_signed_update_confirm_before_status_patch -q`
  (`2 passed`).
- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py tests\test_api_spine_frontend_header_inventory.py -q`
  (`39 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean.

Note: a broader lint command including `orchestration/` encountered an existing
legacy non-UTF-8 artifact before scanning current Sprint 157 content, so the
established safe lint scope `tests docs` was used for closeout.

Publication state:

- Implementation commit SHA: `df3f926`.
- Closeout metadata commit SHA: `3bdce2b`.
- Push result: pushed to `origin/master`; `handoff/current`, `codex/current`,
  `claude/current`, and `antigravity/current` all aligned and pushed to
  `8464a3ee`. Claude/Antigravity durable worktrees had untracked stale review
  artifacts, which were stashed before clean realignment.
- Final `git status --short --branch`: `## master...origin/master`.

Strategic position: Sprint 157 is **Programme 2G / EMR4 API Spine** client
readiness and guardrail hardening. It closes the ordinary update-confirm client
header gap while preserving raw fallback and backend semantics.

Sprint engine state: continuing. Next recommended slice is Sprint 158, a compact
confirm-client surface checkpoint before deciding whether Bernie tool-intent
confirm, proposal-only backend binding, or strict `minLength: 8` enforcement is
the next safe implementation path.

---

## Previous Closeout - Sprint 156

## Sprint 156 What Changed

- Updated `docs/diary/diary.js` so `applySignedStatusProposal()` sends HTTP
  `Idempotency-Key` to `/appointments/proposals/status-confirm`.
- Updated `docs/diary/diary.js` so `applySignedDeleteProposal()` sends HTTP
  `Idempotency-Key` to `/appointments/proposals/delete-confirm`.
- Preferred freshness-derived keys:
  `status-confirm-{status_proposal_freshness_id}` and
  `delete-confirm-{delete_proposal_freshness_id}`, with a proposal-scoped
  generated fallback only for malformed fixtures with missing/oversized
  freshness IDs.
- Left raw compatibility `PATCH /appointments/{id}/status` and
  `DELETE /appointments/{id}` fallbacks header-free.
- Left update-confirm, Bernie tool-intent confirm, proposal-only backend
  binding, backend runtime validation, idempotency ledger semantics, providers,
  GraphQL, H15/H-series, memory/RAG/GraphRAG, and strict `minLength: 8`
  enforcement unchanged.
- Bumped `docs/diary/diary.html` to `diary.js?v=177`.
- Updated `tests/test_api_spine_frontend_header_inventory.py` and
  `review/test_diary_smoke.py` to guard status/delete confirm header emission
  and raw-fallback separation.
- Added
  `orchestration/api_spine_appointment_idempotency_status_delete_confirm_client_header.md`.
- Integrated worker lanes:
  - Claude recommended stable per-proposal status/delete confirm keys and no
    backend changes.
  - Antigravity recommended proposal-object key scoping and focused static/
    smoke coverage.
  - DeepSeek recommended freshness-derived status/delete keys and preserving
    update-confirm/tool-intent/proposal-only boundaries; Ariadne accepted the
    freshness-derived key recommendation.

## Sprint 156 Verification

- `node --check docs\diary\diary.js`.
- `.venv\Scripts\python.exe scripts\check_frontend_versions.py`
  (`[PASSED] Verification Passed: All modified assets have appropriate version bumps`).
- `.venv\Scripts\python.exe -m pytest -k "test_status_control_uses_signed_status_confirm_without_raw_patch or test_cancel_flow_uses_signed_delete_confirm_without_raw_delete" review\test_diary_smoke.py -q`
  (`2 passed`).
- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_frontend_header_inventory.py tests\test_api_spine_create_proposal_header_alignment.py tests\test_api_spine_create_proposal_idempotency_route_contract.py tests\test_api_spine_confirmation_family_idempotency_checkpoint.py tests\test_phase_programmes_current_checkpoint.py tests\test_sprint_closeout_protocol.py -q`
  (`43 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean.

Publication state:

- Integration commit SHA: `475cfef`.
- Closeout metadata commit SHA: `4dc1f23`.
- Push result: pushed to `origin/master`; `handoff/current` was moved locally by
  `.venv\Scripts\python.exe scripts\agent_worktrees.py handoff --message "Sprint 156 closeout: status/delete confirm client headers"`
  and then pushed directly after the helper's internal master push raced the
  already-completed `git push origin master`. GitHub reported the known
  moved-repo notice and 1 moderate Dependabot alert.
- Final `git status --short --branch`: `## master...origin/master`.

Strategic position: Sprint 156 is **Programme 2G / EMR4 API Spine** client
readiness and guardrail hardening. It closes the status/delete confirmed-write
client header gaps while preserving raw fallback and backend semantics.

Sprint engine state: continuing. Next recommended slice is Sprint 157:
update-confirm client header emission across modal update and drag/reschedule
call sites before proposal-only backend binding or strict `minLength: 8`
enforcement.

---

## Previous Closeout - Sprint 155

## Sprint 155 What Changed

- Updated `docs/diary/diary.js` so the staff booking-modal create-confirm POST
  sends HTTP `Idempotency-Key` when the returned confirm endpoint is
  `/appointments/proposals/create/confirm`.
- Kept the create-proposal key and create-confirm key distinct:
  `btn-booking-save.dataset.idempotencyKey` remains proposal-scoped, while
  `btn-booking-save.dataset.confirmIdempotencyKey` is stable for the staged
  confirmation attempt and is cleared by `resetProposalConfirmation()`.
- Updated the Bernie review confirm adapter so create-confirm-Bernie calls send
  `Idempotency-Key` from
  `bernieSession.getServerRouteIdempotencyKey("create-confirm-bernie", ...)`.
- Left Bernie tool-intent confirm, update-confirm, status-confirm,
  delete-confirm, proposal-only backend binding, raw compatibility writes,
  backend runtime validation, idempotency ledger semantics, providers, GraphQL,
  H15/H-series, memory/RAG/GraphRAG, and strict `minLength: 8` enforcement
  unchanged.
- Bumped `docs/diary/diary.html` to `diary.js?v=176`.
- Updated `tests/test_api_spine_frontend_header_inventory.py` and
  `review/test_diary_smoke.py` to guard staff create-confirm and Bernie review
  create-confirm-Bernie header emission while keeping remaining confirm gaps
  explicit.
- Added
  `orchestration/api_spine_appointment_idempotency_create_confirm_client_header.md`.
- Integrated worker lanes:
  - Claude recommended a client-only fix with stable confirm keys and no
    backend changes.
  - Antigravity agreed the create-confirm/Bernie confirm path is the right
    next client slice.
  - DeepSeek recommended a distinct staff confirm key and preserving closed
    boundaries; Ariadne accepted the distinct-key recommendation.

## Sprint 155 Verification

- `node --check docs\diary\diary.js`.
- `.venv\Scripts\python.exe scripts\check_frontend_versions.py`
  (`[PASSED] Verification Passed: All modified assets have appropriate version bumps`).
- `.venv\Scripts\python.exe -m pytest -k "test_create_proposal_idempotency_header" review\test_diary_smoke.py -q`
  (`1 passed`).
- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_frontend_header_inventory.py tests\test_api_spine_create_proposal_header_alignment.py tests\test_api_spine_create_proposal_idempotency_route_contract.py tests\test_api_spine_confirmation_family_idempotency_checkpoint.py -q`
  (`37 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean.

Publication state:

- Integration commit SHA: `25e42bc`.
- Closeout metadata commit SHA: `d172b2c`.
- Push result: pushed to `origin/master`; `handoff/current` was moved locally by
  `.venv\Scripts\python.exe scripts\agent_worktrees.py handoff --message "Sprint 155 closeout: create-confirm client headers"`
  and then pushed directly after the helper's internal master push raced the
  already-completed `git push origin master`. GitHub reported the known
  moved-repo notice and 1 moderate Dependabot alert.
- Final `git status --short --branch`: `## master...origin/master`.

Strategic position: Sprint 155 is **Programme 2G / EMR4 API Spine** client
readiness and guardrail hardening. It closes the first already-enforced
confirmation client gap after create-proposal without changing backend command
semantics.

Sprint engine state: continuing. Next recommended slice is Sprint 156: choose
the next bounded confirm client-header family, likely status-confirm/delete-
confirm or update-confirm, before proposal-only backend binding or strict
`minLength: 8` enforcement.

---

## Previous Closeout - Sprint 154

## Sprint 154 What Changed

- Added
  `orchestration/api_spine_appointment_idempotency_diary_header_gap_preflight.md`.
- Added `tests/test_api_spine_frontend_header_inventory.py`, a source-derived
  frontend inventory guard for current Diary `Idempotency-Key` header emission
  and explicitly missing confirm/proposal headers.
- Strengthened
  `tests/test_api_spine_create_proposal_header_alignment.py` so the
  handler-level proposal binding gap includes `propose_waiting_area_update` as
  the status/waiting-area proposal variant.
- Updated the Sprint 151/152 header-alignment/readiness docs to name the
  waiting-area proposal handler gap.
- Integrated worker lanes:
  - DeepSeek found only one current frontend HTTP `Idempotency-Key` emitter
    and identified five already-enforced confirmation routes with missing
    Diary client headers.
  - Claude recommended a stable per-proposal confirm key so retries use the
    existing confirmation ledger replay path.
  - Antigravity agreed create-confirm/confirm-Bernie is the safest next slice;
    Ariadne recorded its fresh-per-attempt key suggestion as dissent because it
    would weaken replay semantics.
- No runtime route behavior, OpenAPI schema, idempotency ledger semantics,
  provider, GraphQL, H15/H-series, memory/RAG/GraphRAG, or raw compatibility
  write behavior changed.

## Sprint 154 Verification

- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_frontend_header_inventory.py tests\test_api_spine_create_proposal_header_alignment.py -q`
  (`13 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check` clean.

Publication state:

- Integration commit SHA: `ded8791`.
- Closeout metadata commit SHA: `db76171`.
- Push result: pushed to `origin/master` and `origin/handoff/current` by
  `.venv\Scripts\python.exe scripts\agent_worktrees.py handoff --message "Sprint 154 closeout: diary API header gap preflight"`;
  GitHub reported the known moved-repo notice and 1 moderate Dependabot alert.
- Final `git status --short --branch`: `## master...origin/master`.

Strategic position: Sprint 154 is **Programme 2G / EMR4 API Spine** preflight
and guardrail hardening. It clarifies that create-proposal client readiness is
not enough by itself: the next live break is the missing HTTP header on
already-enforced create-confirm and confirm-Bernie routes.

Sprint engine state: continuing. Next recommended slice is Sprint 155:
wire create-confirm and confirm-Bernie client header emission first, using a
stable per-proposal confirm key and preserving backend ledger/runtime behavior.

---

## Previous Closeout - Sprint 153

## Sprint 153 What Changed

- Updated `docs/diary/diary.js` so the real diary create-proposal POST sends an
  `Idempotency-Key` header for new appointment proposals.
- Added `generateClientIdempotencyKey()`, using `crypto.randomUUID()` when
  available and an `evt-...` fallback that satisfies the 8+ character
  readiness precondition.
- Scoped the key to the current booking-modal proposal attempt by storing it on
  the Save button dataset; it remains stable across warning-confirm retries and
  is cleared when `resetProposalConfirmation()` runs after input changes or
  modal reset.
- Left update-proposal behavior unchanged.
- Bumped `docs/diary/diary.html` to `diary.js?v=175`.
- Added `review/test_diary_smoke.py::test_create_proposal_idempotency_header`
  to assert the header is present, 8+ characters, stable across warning-confirm
  retry, and refreshed after input changes.
- Integrated worker lanes:
  - Claude recommended a client-only fix with no backend/OpenAPI/runtime
    `minLength` changes.
  - Antigravity implemented the diary client/header and smoke-test slice.
  - DeepSeek found no blockers and flagged the broader remaining diary header
    gap for confirm and sibling proposal routes.
- No backend route behavior, OpenAPI schema, idempotency ledger semantics,
  provider, GraphQL, H15/H-series, memory/RAG/GraphRAG, or raw compatibility
  write behavior changed.

## Sprint 153 Verification

- `node --check docs\diary\diary.js`.
- `.venv\Scripts\python.exe scripts\check_frontend_versions.py`
  (`[PASSED] Verification Passed: All modified assets have appropriate version bumps`).
- `.venv\Scripts\python.exe -m pytest -k "test_create_proposal_idempotency_header or test_create_modal_uses_signed_create_confirm_before_status_patch" review/test_diary_smoke.py -q`
  (`2 passed`).
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_create_proposal_header_alignment.py tests/test_api_spine_create_proposal_idempotency_route_contract.py -q`
  (`25 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean apart from a CRLF normalization warning on a
  coordination packet.

Publication state:

- Integration commit SHA: `9d7f9bd`.
- Closeout metadata commit SHA: `a60b084`.
- Push result: pushed to `origin/master`; GitHub reported the known moved-repo
  notice and 1 moderate Dependabot alert.
- Final `git status --short --branch`: `## master...origin/master`.

Strategic position: Sprint 153 is **Programme 2G / EMR4 API Spine** client
readiness and guardrail hardening. It was the right-sized follow-up to Sprint
152 because it closed one concrete runtime/client mismatch without broadening
proposal-route enforcement or changing backend idempotency semantics.

Sprint engine state: continuing. Next recommended slice is Sprint 154, a
remaining diary/API header-gap preflight. DeepSeek specifically flagged that
create-confirm, confirm-Bernie, status/delete confirm, and sibling proposal
callers may still lack HTTP `Idempotency-Key` emission; address those in
bounded slices rather than rolling headers onto raw compatibility writes by
default.

---

## Previous Closeout - Sprint 152

## Sprint 152 What Changed

- Added
  `orchestration/api_spine_appointment_idempotency_create_proposal_minlength_readiness.md`.
- Decided **not** to enforce OpenAPI `Idempotency-Key` `minLength: 8` at
  runtime for create-proposal yet.
- Preserved current runtime behavior: missing/blank keys fail closed, while
  short non-blank keys still pass until named client-readiness preconditions
  are met.
- Added tests proving all four canonical OpenAPI proposal operations continue
  to reference the shared `IdempotencyKey` parameter.
- Added tests documenting the current FastAPI proposal-header binding gap:
  `propose_update_appointment`, `propose_status_update`, and
  `propose_delete_appointment` do not yet bind `Idempotency-Key`.
- Added tests requiring concrete preconditions before future runtime
  `minLength: 8` enforcement: real client key emission, 8+ character trimmed
  candidate keys, typed short-key rejection behavior, and a shared review of
  proposal-route header postures.
- Updated the Sprint 151 header-alignment guard and Programme 2G checkpoint to
  point to the Sprint 152 decision and Sprint 153 direction.
- Integrated worker lanes:
  - Claude recommended defer-with-guard and flagged that the diary caller still
    has to prove the non-blank header path.
  - Antigravity recommended enforce-now; Ariadne accepted its future-key
    observation as useful dissent but rejected immediate enforcement.
  - DeepSeek recommended defer-with-guard and flagged the wider 3-of-4 proposal
    binding gap.
- No route behavior changed.

## Sprint 152 Verification

- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_create_proposal_header_alignment.py tests/test_api_spine_create_proposal_idempotency_route_contract.py tests/test_api_spine_appointment_openapi_drift_guard.py tests/test_api_spine_create_proposal_replay_model_decision.py tests/test_phase_programmes_current_checkpoint.py tests/test_sprint_closeout_protocol.py -q`
  (`44 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_create_proposal_header_alignment.py tests\test_phase_programmes_current_checkpoint.py`.
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean apart from a CRLF normalization warning on a
  coordination packet.

Publication state:

- Integration commit SHA: `11913f0`.
- Closeout metadata commit SHA: `eb09470`.
- Push result: pushed to `origin/master`; GitHub reported the known moved-repo
  notice and 1 moderate Dependabot alert.
- Final `git status --short --branch`: `## master...origin/master`.

Strategic position: Sprint 152 is **Programme 2G / EMR4 API Spine** guardrail
hardening and compatibility-decision work. It was intentionally small because
the right outcome was to settle whether to tighten one proposal route without
silently changing runtime behavior across adjacent proposal surfaces. It
advanced the larger objective of making the appointment command plane explicit,
auditable, and mechanically guarded.

Sprint engine state: continuing. Next recommended slice is Sprint 153, a
proposal-header readiness gap preflight: either wire/preflight the real diary
create-proposal caller to send an 8+ character `Idempotency-Key`, or preflight
the next proposal-only route's non-blank header discipline. Keep raw
compatibility writes out of scope.

---

## Previous Closeout - Sprint 151

## Sprint 151 What Changed

- Added
  `orchestration/api_spine_appointment_idempotency_create_proposal_header_alignment.md`.
- Added `tests/test_api_spine_create_proposal_header_alignment.py`.
- Added the operation-level
  `x-emr4-proposal-header-posture` OpenAPI annotation for
  `proposeAppointmentCreate`.
- Guarded that OpenAPI keeps the shared required `Idempotency-Key` header for
  `/appointments/proposals/create` with `minLength: 8` and `maxLength: 128`.
- Guarded that FastAPI binds `Header(None, alias="Idempotency-Key")` on
  `propose_create_appointment` before proposal evidence is minted.
- Recorded and tested that runtime `minLength: 8` enforcement remains deferred:
  Sprint 150 rejects missing/blank keys only until a separate client-readiness
  decision changes behavior.
- Added a DB-backed one-character-key test proving short non-blank keys are
  still accepted until that decision is made.
- Guarded that create-proposal still has no proposal ledger, no stored proposal
  replay, no same-key/different-body conflicts, no appointment/audit writes,
  and no slot reservations.
- Updated the programme and handover pointers so Sprint 152 is either a
  client-readiness decision for `minLength: 8` or the next proposal-only
  preflight.
- No route behavior changed.

## Sprint 151 Verification

- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_create_proposal_header_alignment.py tests/test_api_spine_appointment_openapi_drift_guard.py tests/test_api_spine_create_proposal_idempotency_route_contract.py tests/test_api_spine_create_proposal_replay_model_decision.py tests/test_phase_programmes_current_checkpoint.py tests/test_sprint_closeout_protocol.py -q`
  (`41 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_create_proposal_header_alignment.py tests\test_api_spine_create_proposal_idempotency_route_contract.py tests\test_phase_programmes_current_checkpoint.py tests\test_sprint_closeout_protocol.py`.
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean.

Publication state:

- Integration commit SHA: `e5647b9`.
- Closeout metadata commit SHA: `9e8dc80`.
- Push result: pushed to `origin/master`; GitHub reported the known moved-repo
  notice and 1 moderate Dependabot alert.
- Final `git status --short --branch`: `## master...origin/master`.

Sprint engine state: paused after formal closeout at Yuri's request. Next
recommended slice when resumed is Sprint 152, either client-readiness for
create-proposal `minLength: 8` runtime enforcement or a guarded preflight for
the next proposal-only header surface.

---

## Previous Closeout - Sprint 145

## Sprint 145 What Changed

- Added
  `orchestration/api_spine_appointment_idempotency_confirmation_family_checkpoint.md`.
- Added
  `tests/test_api_spine_confirmation_family_idempotency_checkpoint.py` to guard
  the five wired proposal-confirm appointment idempotency families: staff
  create, Bernie create, status, update, and delete confirm.
- Recorded the shared fail-closed decision map for replay, conflict,
  in-progress, stale-in-progress, and failed-transient ledger states.
- Preserved raw/proposal-only/provider/GraphQL/H15/memory/trove gates as closed
  checkpoint boundaries.
- Integrated DeepSeek worker review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint145-confirmation-family-checkpoint.md`.
- Added Claude and Antigravity Sprint 145 packets:
  `orchestration/agent_inbox/claude/claude-sprint145-confirmation-family-checkpoint-review.md`
  and
  `orchestration/agent_inbox/antigravity/antigravity-sprint145-confirmation-family-checkpoint-acceptance.md`.
- No route behavior changed.

## Sprint 145 Verification

- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_confirmation_family_idempotency_checkpoint.py tests\test_api_spine_appointment_idempotency_route_integration_preflight.py tests\test_phase_programmes_current_checkpoint.py -q`
  (`15 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_confirmation_family_idempotency_checkpoint.py tests\test_phase_programmes_current_checkpoint.py tests\test_sprint_closeout_protocol.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_confirmation_family_idempotency_checkpoint.py tests/test_api_spine_appointment_idempotency_route_integration_preflight.py tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py tests/test_api_spine_bernie_create_confirm_idempotency_route_contract.py tests/test_api_spine_status_confirm_idempotency_route_contract.py tests/test_api_spine_update_confirm_idempotency_route_contract.py tests/test_api_spine_delete_confirm_idempotency_route_contract.py tests/test_phase_programmes_current_checkpoint.py tests/test_sprint_closeout_protocol.py -q`
  (`118 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean apart from the known CRLF notice on
  `orchestration/integration_log.md`.

Sprint engine state: continuing. Next recommended slice is Sprint 146,
cross-family route-level idempotency integration tests across all five wired
confirmation families.

---

## Previous Closeout - Sprint 144

| Item | Value |
|---|---|
| Batch | Sprint 144 Delete-Confirm Idempotency Route Wiring |
| Integrated through | Ariadne implementation with EMR4 API Steward skill; DeepSeek worker advice integrated; Claude and Antigravity protocol packets remain queued locally |
| Status | Committed and pushed in Sprint 144 closeout commit; sprint engine continuing |
| Last updated | 2026-07-07 |

## Sprint 144 What Changed

- Wired HTTP `Idempotency-Key` enforcement for
  `POST /api/v1/appointments/proposals/delete-confirm` only.
- Added `_DELETE_CONFIRM_OPERATION_ID` and `_DELETE_CONFIRM_ROUTE_FAMILY`, with
  route-wrapper claim/replay handling before destructive soft-cancel checks or
  mutation run.
- Added a scoped `commit=False` path to `_apply_appointment_delete()` so
  delete-confirm soft-cancel, audit row, ledger completion, and commit happen
  in one transaction; raw `DELETE /api/v1/appointments/{appointment_id}` still
  uses the default commit path and no idempotency semantics.
- Converted the Sprint 143 guarded route-test contract into executable tests
  covering missing/blank keys, invalid payloads, first delete, replay,
  replay after raw delete, conflict, active/stale/failed preclaims, blocked
  confirmation rollback, already-cancelled/missing appointment behavior,
  warning/nested body conflicts, signed-evidence blocks, waiting-area drift
  directions, and different-key destructive concurrency.
- Updated existing delete-confirm semantic tests to send `Idempotency-Key` and
  commit rollback-sensitive fixtures before intentionally blocked confirms.
- Integrated DeepSeek worker review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint144-delete-confirm-idempotency-wiring.md`.
- Added Claude and Antigravity Sprint 144 packets:
  `orchestration/agent_inbox/claude/claude-sprint144-delete-confirm-idempotency-wiring-review.md`
  and
  `orchestration/agent_inbox/antigravity/antigravity-sprint144-delete-confirm-idempotency-acceptance.md`.
- Preserved fake/default-disabled behavior; no raw/proposal-only idempotency
  wiring, provider call, live smoke, runtime FGA client, external patient
  client, GraphQL mutation, H15/H-series runtime import, memory/RAG/GraphRAG,
  or broad trove mining was added.

## Sprint 144 Verification

- `.venv\Scripts\python.exe -m py_compile app\routers\appointments.py tests\test_api_spine_delete_confirm_idempotency_route_contract.py tests\test_appointment_status_mutations.py`.
- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_delete_confirm_idempotency_route_contract.py -q`
  (`30 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_appointment_status_mutations.py -q`
  (`52 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_appointment_idempotency_route_integration_preflight.py tests/test_api_spine_appointment_idempotency_gap.py tests/test_api_spine_update_confirm_idempotency_route_contract.py tests/test_api_spine_delete_confirm_idempotency_preflight.py tests/test_api_spine_delete_confirm_idempotency_route_contract.py tests/test_appointment_status_mutations.py -q`
  (`121 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py tests/test_api_spine_bernie_create_confirm_idempotency_route_contract.py tests/test_api_spine_status_confirm_idempotency_route_contract.py tests/test_api_spine_update_confirm_idempotency_route_contract.py tests/test_api_spine_delete_confirm_idempotency_route_contract.py tests/test_api_spine_appointment_idempotency_route_integration_preflight.py tests/test_api_spine_appointment_idempotency_gap.py tests/test_api_spine_delete_confirm_idempotency_preflight.py tests/test_phase_programmes_current_checkpoint.py tests/test_sprint_closeout_protocol.py -q`
  (`122 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests/test_appointment_status_mutations.py tests/test_api_spine_delete_confirm_idempotency_route_contract.py tests/test_appointment_update_proposal.py tests/test_api_spine_update_confirm_idempotency_route_contract.py tests/test_appointment_audit.py tests/test_reason_code_backend.py tests/test_appointment_proposals.py tests/test_bernie_confirm_create_proposal.py tests/test_bernie_evidence_contract.py tests/test_bernie_route_outcome_events.py tests/test_bernie_signed_confirmation_evidence.py tests/test_bernie_sprint98_confirm_contract.py tests/test_bernie_turn_contract.py -q`
  (`265 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m py_compile app\routers\appointments.py tests\test_api_spine_delete_confirm_idempotency_route_contract.py tests\test_appointment_status_mutations.py tests\test_appointment_audit.py tests\test_reason_code_backend.py tests\test_api_spine_appointment_idempotency_route_integration_preflight.py tests\test_api_spine_appointment_idempotency_gap.py tests\test_api_spine_delete_confirm_idempotency_preflight.py tests\test_api_spine_update_confirm_idempotency_route_contract.py tests\test_api_spine_staff_create_confirm_idempotency_route_contract.py tests\test_api_spine_status_confirm_idempotency_route_contract.py tests\test_phase_programmes_current_checkpoint.py tests\test_sprint_closeout_protocol.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_phase_programmes_current_checkpoint.py tests/test_sprint_closeout_protocol.py -q`
  (`5 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean apart from known CRLF notices on
  `orchestration/integration_log.md`, `tests/test_appointment_status_mutations.py`,
  and `tests/test_reason_code_backend.py`.

Sprint engine state: continuing. Next recommended slice is Sprint 145, a
confirmation-family idempotency checkpoint/audit before broader proposal-only
or command-surface decisions.

---

## Previous Closeout - Sprint 143

| Item | Value |
|---|---|
| Batch | Sprint 143 Delete-Confirm Idempotency Route-Test Contract |
| Integrated through | Ariadne implementation with EMR4 API Steward skill; DeepSeek worker advice integrated; Claude and Antigravity protocol packets remain queued locally |
| Status | Committed and pushed in Sprint 143 closeout commit; sprint engine continuing |
| Last updated | 2026-07-07 |

## Sprint 143 What Changed

- Added
  `orchestration/api_spine_appointment_idempotency_delete_confirm_route_tests.md`.
- Added
  `tests/test_api_spine_delete_confirm_idempotency_route_contract.py` with
  passing static scope checks and skipped future behavior tests for Sprint 144
  wiring.
- Integrated DeepSeek worker review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint143-delete-confirm-idempotency-route-contract.md`.
- Added Claude and Antigravity Sprint 143 packets:
  `orchestration/agent_inbox/claude/claude-sprint143-delete-confirm-idempotency-route-contract.md`
  and
  `orchestration/agent_inbox/antigravity/antigravity-sprint143-delete-confirm-idempotency-acceptance.md`.
- Recorded destructive delete-confirm gotchas: `_apply_appointment_delete()`
  currently commits internally; replay must return before destructive checks;
  raw `DELETE` keeps default commit/no-idempotency behavior; merged warning
  responses must be preserved; invalid reason codes, missing signed evidence,
  waiting-area mismatch directions, already-cancelled appointments, and
  non-existent appointments block without mutation.
- Preserved fake/default-disabled behavior; no delete-confirm route wiring,
  raw/proposal-only idempotency wiring, provider call, live smoke, runtime FGA
  client, external patient client, GraphQL mutation, H15/H-series runtime
  import, memory/RAG/GraphRAG, or broad trove mining was added.

## Sprint 143 Verification

- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_delete_confirm_idempotency_route_contract.py tests\test_api_spine_delete_confirm_idempotency_preflight.py -q`
  (`13 passed, 22 skipped`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_delete_confirm_idempotency_route_contract.py tests\test_api_spine_delete_confirm_idempotency_preflight.py`.
- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_delete_confirm_idempotency_route_contract.py tests\test_api_spine_delete_confirm_idempotency_preflight.py tests\test_phase_programmes_current_checkpoint.py tests\test_sprint_closeout_protocol.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_delete_confirm_idempotency_route_contract.py tests/test_api_spine_delete_confirm_idempotency_preflight.py tests/test_phase_programmes_current_checkpoint.py tests/test_sprint_closeout_protocol.py tests/test_api_spine_update_confirm_idempotency_route_contract.py tests/test_api_spine_appointment_idempotency_route_integration_preflight.py -q`
  (passed with the expected Sprint 144 future behavior skips; existing
  Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean apart from the known CRLF notice on
  `orchestration/integration_log.md`.

Sprint engine state: continuing. Next recommended slice is Sprint 144, narrow
delete-confirm idempotency route wiring only.

---

## Previous Closeout - Sprint 142

| Item | Value |
|---|---|
| Batch | Sprint 142 Delete-Confirm Idempotency Preflight |
| Integrated through | Ariadne implementation with EMR4 API Steward skill; DeepSeek worker advice integrated; Claude and Antigravity protocol packets remain queued locally |
| Status | Committed and pushed in Sprint 142 closeout commit; sprint engine continuing |
| Last updated | 2026-07-07 |

## Sprint 142 What Changed

- Added
  `orchestration/api_spine_appointment_idempotency_delete_confirm_preflight.md`.
- Chose `POST /api/v1/appointments/proposals/delete-confirm` as the final
  proposal-confirm appointment mutation family for idempotency route-test
  coverage before any wiring.
- Added `tests/test_api_spine_delete_confirm_idempotency_preflight.py` to
  preserve the no-wiring posture, destructive soft-cancel boundary, claim order,
  commit-boundary gotcha, future route-test matrix, and closed gates.
- Integrated DeepSeek worker review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint142-delete-confirm-idempotency-preflight.md`.
- Added Claude and Antigravity Sprint 142 packets:
  `orchestration/agent_inbox/claude/claude-sprint142-delete-confirm-idempotency-preflight-review.md`
  and
  `orchestration/agent_inbox/antigravity/antigravity-sprint142-delete-confirm-idempotency-acceptance.md`.
- Preserved fake/default-disabled behavior; no delete-confirm route wiring,
  raw/proposal-only idempotency wiring, provider call, live smoke, runtime FGA
  client, external patient client, GraphQL mutation, H15/H-series runtime import,
  memory/RAG/GraphRAG, or broad trove mining was added.

## Sprint 142 Verification

- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_delete_confirm_idempotency_preflight.py -q`
  (`6 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_delete_confirm_idempotency_preflight.py tests\test_phase_programmes_current_checkpoint.py tests\test_sprint_closeout_protocol.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_delete_confirm_idempotency_preflight.py tests/test_phase_programmes_current_checkpoint.py tests/test_sprint_closeout_protocol.py tests/test_api_spine_update_confirm_idempotency_route_contract.py tests/test_api_spine_appointment_idempotency_route_integration_preflight.py -q`
  (`39 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean apart from the known CRLF notice on
  `orchestration/integration_log.md`.

Sprint engine state: continuing. Next recommended slice is Sprint 143, a
guarded delete-confirm idempotency route-test contract before any destructive
soft-cancel route wiring.

---

## Previous Closeout - Sprint 141

| Item | Value |
|---|---|
| Batch | Sprint 141 Update-Confirm Idempotency Route Wiring |
| Integrated through | Ariadne implementation with EMR4 API Steward skill; DeepSeek worker advice integrated; Claude and Antigravity protocol packets remain queued locally |
| Status | Committed and pushed in Sprint 141 closeout commit; sprint engine continuing |
| Last updated | 2026-07-07 |

## Sprint 141 What Changed

- Wired HTTP `Idempotency-Key` enforcement for
  `POST /api/v1/appointments/proposals/update/confirm` only.
- Added `_UPDATE_CONFIRM_OPERATION_ID` and `_UPDATE_CONFIRM_ROUTE_FAMILY`, and
  route-wrapper claim/replay handling before `confirm_update_proposal()` can
  re-run `propose_update_appointment()`.
- Added a scoped `commit=False` path to `_apply_appointment_update()` so update,
  audit row, ledger completion, and commit happen in one transaction for
  update-confirm.
- Converted the Sprint 140 guarded route-test contract into executable tests
  covering missing/blank key, invalid payload, first update, replay, conflict,
  active/stale/failed preclaims, blocked confirmation rollback, warning-body
  conflict, and replay after an intervening raw update.
- Updated existing update-confirm semantic tests to send `Idempotency-Key`.
- Integrated DeepSeek worker review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint141-update-confirm-idempotency-wiring.md`.
- Preserved fake/default-disabled behavior; no delete-confirm route wiring,
  raw/proposal-only idempotency wiring, provider call, live smoke, runtime FGA
  client, external patient client, GraphQL mutation, H15/H-series runtime import,
  memory/RAG/GraphRAG, or broad trove mining was added.

## Sprint 141 Verification

- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_update_confirm_idempotency_route_contract.py -q`
  (`22 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_appointment_update_proposal.py tests\test_api_spine_update_confirm_idempotency_preflight.py tests\test_api_spine_update_confirm_idempotency_route_contract.py -q`
  (`61 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m py_compile app\routers\appointments.py tests\test_api_spine_update_confirm_idempotency_route_contract.py tests\test_api_spine_update_confirm_idempotency_preflight.py tests\test_appointment_update_proposal.py tests\test_phase_programmes_current_checkpoint.py tests\test_sprint_closeout_protocol.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py tests/test_api_spine_bernie_create_confirm_idempotency_route_contract.py tests/test_api_spine_status_confirm_idempotency_route_contract.py tests/test_api_spine_update_confirm_idempotency_route_contract.py tests/test_api_spine_update_confirm_idempotency_preflight.py tests/test_api_spine_appointment_idempotency_gap.py tests/test_api_spine_appointment_idempotency_route_integration_preflight.py tests/test_phase_programmes_current_checkpoint.py tests/test_sprint_closeout_protocol.py -q`
  (`92 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests/test_appointment_update_proposal.py tests/test_api_spine_update_confirm_idempotency_route_contract.py tests/test_appointment_status_mutations.py tests/test_reason_code_backend.py tests/test_appointment_audit.py tests/test_appointment_proposals.py tests/test_bernie_confirm_create_proposal.py tests/test_bernie_evidence_contract.py tests/test_bernie_route_outcome_events.py tests/test_bernie_signed_confirmation_evidence.py tests/test_bernie_sprint98_confirm_contract.py tests/test_bernie_turn_contract.py -q`
  (`235 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean apart from the known CRLF notice on
  `orchestration/integration_log.md`.

Sprint engine state: continuing. Next recommended slice is Sprint 142,
delete-confirm idempotency preflight before any destructive soft-cancel route
wiring.

---

## Previous Closeout - Sprint 140

| Item | Value |
|---|---|
| Batch | Sprint 140 Update-Confirm Idempotency Route-Test Contract |
| Integrated through | Ariadne implementation with EMR4 API Steward skill; DeepSeek worker advice integrated; Claude and Antigravity protocol packets remain queued locally |
| Status | Committed and pushed in Sprint 140 closeout commit; sprint engine continuing |
| Last updated | 2026-07-07 |

## Sprint 140 What Changed

- Added
  `orchestration/api_spine_appointment_idempotency_update_confirm_route_tests.md`.
- Added
  `tests/test_api_spine_update_confirm_idempotency_route_contract.py` with
  passing static route-scope checks and skipped future behavior tests for
  Sprint 141 wiring.
- Integrated DeepSeek worker review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint140-update-confirm-idempotency-route-contract.md`.
- Preserved the route-wrapper ownership decision: replay must return before
  `confirm_update_proposal()` can re-run `propose_update_appointment()`.
- Recorded that `_apply_appointment_update()` currently commits internally and
  must gain a scoped `commit=False` path before ledger completion.
- Chose transactional rollback for blocked started claims, matching
  status-confirm.
- Recorded the canonicalization boundary: full validated confirmation-body
  hashing includes signed evidence, freshness, turn/session metadata, and
  `confirmed_warnings`; `_UPDATE_CONFIRM_METADATA_FIELDS` remains signed
  evidence payload shaping only.
- Preserved fake/default-disabled behavior; no update-confirm route wiring,
  delete/raw/proposal-only idempotency wiring, provider call, live smoke,
  runtime FGA client, external patient client, GraphQL mutation, H15/H-series
  runtime import, memory/RAG/GraphRAG, or broad trove mining was added.

## Sprint 140 Verification

- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_update_confirm_idempotency_route_contract.py tests\test_api_spine_update_confirm_idempotency_preflight.py -q`
  (`15 passed, 13 skipped`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_update_confirm_idempotency_route_contract.py tests\test_api_spine_update_confirm_idempotency_preflight.py tests\test_phase_programmes_current_checkpoint.py tests\test_sprint_closeout_protocol.py`.
- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_update_confirm_idempotency_route_contract.py tests\test_api_spine_update_confirm_idempotency_preflight.py tests\test_phase_programmes_current_checkpoint.py tests\test_sprint_closeout_protocol.py -q`
  (`20 passed, 13 skipped`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean apart from the known CRLF notice on
  `orchestration/integration_log.md`.

Sprint engine state: continuing. Next recommended slice is Sprint 141, narrow
update-confirm idempotency route wiring only, with delete/raw/proposal-only
families still out of scope.

---

## Previous Closeout - Sprint 139

| Item | Value |
|---|---|
| Batch | Sprint 139 Update-Confirm Idempotency Preflight |
| Integrated through | Ariadne implementation with EMR4 API Steward skill; DeepSeek worker advice integrated; Claude and Antigravity protocol packets remain queued locally |
| Status | Committed and pushed in batch commit `37767ac51ef266b7c454d4c215dacaa14a44a319`; sprint engine continuing |
| Last updated | 2026-07-07 |

## Sprint 139 What Changed

- Added
  `orchestration/api_spine_appointment_idempotency_update_confirm_preflight.md`.
- Chose `POST /api/v1/appointments/proposals/update/confirm` as the next
  confirmation family for idempotency route-test coverage before any wiring.
- Integrated DeepSeek worker review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint139-update-confirm-idempotency-preflight.md`;
  the review affirmed update-confirm before delete-confirm because it is
  reversible and exercises revalidation before the destructive soft-cancel path.
- Added
  `tests/test_api_spine_update_confirm_idempotency_preflight.py` to preserve
  the preflight decision, no-route-wiring posture, future route-test matrix,
  commit-boundary gotchas, canonicalization stance, and closed gates.
- Added Claude and Antigravity Sprint 139 packets:
  `orchestration/agent_inbox/claude/claude-sprint139-update-confirm-idempotency-preflight-review.md`
  and
  `orchestration/agent_inbox/antigravity/antigravity-sprint139-update-confirm-idempotency-acceptance.md`.
- Preserved fake/default-disabled behavior; no update-confirm route wiring,
  delete/raw/proposal-only idempotency wiring, provider call, live smoke,
  runtime FGA client, external patient client, GraphQL mutation, H15/H-series
  runtime import, memory/RAG/GraphRAG, or broad trove mining was added.

## Sprint 139 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_update_confirm_idempotency_preflight.py`.
- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_update_confirm_idempotency_preflight.py tests\test_phase_programmes_current_checkpoint.py -q`
  (`8 passed`; existing Starlette/Google GenAI warnings only).

Sprint engine state: continuing. Next recommended slice is Sprint 140, a
guarded update-confirm idempotency route-test contract before any route wiring.

Publication status after cleanup: committed and pushed to `origin/master` in
`37767ac51ef266b7c454d4c215dacaa14a44a319`; final status was clean
(`master...origin/master`).

---

## Previous Closeout - Sprint 138

| Item | Value |
|---|---|
| Batch | Sprint 138 Status-Confirm Idempotency Route Wiring |
| Integrated through | Ariadne implementation with EMR4 API Steward skill; DeepSeek worker advice integrated; Claude and Antigravity protocol packets remain queued locally |
| Status | Local route wiring integrated; sprint engine continuing |
| Last updated | 2026-07-07 |

## Sprint 138 What Changed

- Wired HTTP `Idempotency-Key` enforcement for
  `POST /api/v1/appointments/proposals/status-confirm` only.
- Accepted DeepSeek's canonicalization review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint138-status-confirm-canonicalization.md`:
  Sprint 138 uses full validated confirmation-body hashing for consistency
  with staff and Bernie create-confirm routes.
- Added `_STATUS_CONFIRM_OPERATION_ID` and `_STATUS_CONFIRM_ROUTE_FAMILY`, and
  claims/replays through the appointment command ledger before
  `confirmed=true`, signed-evidence, freshness, waiting-area, appointment, or
  audit mutation checks.
- Added a `commit=False` path to `_apply_appointment_status_update()` so
  status/waiting-area update, audit write, ledger completion, and commit happen
  in one transaction for status-confirm.
- Converted
  `tests/test_api_spine_status_confirm_idempotency_route_contract.py` from a
  guarded contract into executable tests covering missing key, invalid payload,
  first status write, first waiting-area write, status replay, waiting-area
  replay, conflict, active/stale/failed preclaims, block rollback, union
  variants, and telemetry shape.
- Updated existing status-confirm callers in status/reason-code tests to send
  idempotency keys and committed two rollback-sensitive tampered-status
  fixtures before blocked confirmation.
- Updated API-spine static guards so exactly staff create-confirm, Bernie
  create-confirm, and status-confirm may be wired; update/delete/raw/
  proposal-only families remain out of scope.
- Preserved fake/default-disabled behavior; no update/delete/raw/proposal-only
  idempotency wiring, provider call, live smoke, runtime FGA client, external
  patient client, GraphQL mutation, H15/H-series runtime import,
  memory/RAG/GraphRAG, or broad trove mining was added.

## Sprint 138 Verification

- `.venv\Scripts\python.exe -m py_compile app\routers\appointments.py tests\test_api_spine_status_confirm_idempotency_route_contract.py tests\test_appointment_status_mutations.py tests\test_reason_code_backend.py`.
- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_status_confirm_idempotency_route_contract.py tests\test_api_spine_status_confirm_idempotency_preflight.py tests\test_api_spine_appointment_idempotency_gap.py tests\test_api_spine_appointment_idempotency_route_integration_preflight.py tests\test_api_spine_staff_create_confirm_idempotency_route_contract.py -q`
  (`47 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests\test_appointment_status_mutations.py tests\test_reason_code_backend.py tests\test_appointment_audit.py -q`
  (`103 passed`; existing warnings only; rerun after safely resetting only
  `gp_pms_test` public schema due to the known PostgreSQL enum setup conflict).

Sprint engine state: continuing. Next recommended slice is Sprint 139, a
narrow next confirmation-family preflight choosing update-confirm or
delete-confirm before any route wiring.

---

## Previous Closeout - Sprint 137

| Item | Value |
|---|---|
| Batch | Sprint 137 Status-Confirm Idempotency Route-Test Contract |
| Integrated through | Ariadne implementation with EMR4 API Steward skill; DeepSeek worker advice integrated; Claude and Antigravity protocol packets remain queued locally |
| Status | Local guarded contract integrated; sprint engine continuing |
| Last updated | 2026-07-07 |

## Sprint 137 What Changed

- Added
  `orchestration/api_spine_appointment_idempotency_status_confirm_route_tests.md`.
- Added
  `tests/test_api_spine_status_confirm_idempotency_route_contract.py` with
  passing static scope checks and skipped future behavior tests for:
  missing key, invalid payload, first status write, first waiting-area write,
  status replay, waiting-area replay, conflict, active/stale/failed preclaims,
  confirmation/signed-evidence/freshness bypass prevention, and union variants.
- Integrated DeepSeek worker review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint137-status-confirm-idempotency-route-contract.md`.
- Recorded the critical Sprint 138 wiring gotcha that
  `_apply_appointment_status_update()` commits internally and must gain a
  status-confirm-scoped no-early-commit path or equivalent proof before ledger
  completion is added.
- Recorded DeepSeek's metadata-canonicalization suggestion as an explicit
  Sprint 138 decision, not settled policy, because current storage design and
  create-confirm wiring hash the validated confirmation body.
- Preserved fake/default-disabled behavior; no status-confirm route wiring,
  update/delete/raw/proposal-only idempotency wiring, provider call, live smoke,
  runtime FGA client, external patient client, GraphQL mutation, H15/H-series
  runtime import, memory/RAG/GraphRAG, or broad trove mining was added.

## Sprint 137 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_status_confirm_idempotency_route_contract.py tests\test_api_spine_status_confirm_idempotency_preflight.py`.
- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_status_confirm_idempotency_route_contract.py tests\test_api_spine_status_confirm_idempotency_preflight.py -q`
  (`13 passed, 12 skipped`; existing Starlette/Google GenAI warnings only).

Sprint engine state: continuing. Next recommended slice is Sprint 138, narrow
status-confirm idempotency route wiring, after an explicit metadata
canonicalization decision and with update/delete/raw/proposal-only families out
of scope.

---

## Previous Closeout - Sprint 136

| Item | Value |
|---|---|
| Batch | Sprint 136 Status-Confirm Idempotency Preflight |
| Integrated through | Ariadne implementation with EMR4 API Steward skill; DeepSeek worker advice integrated; Claude and Antigravity protocol packets remain queued locally |
| Status | Local preflight integrated; sprint engine continuing |
| Last updated | 2026-07-07 |

## Sprint 136 What Changed

- Added
  `orchestration/api_spine_appointment_idempotency_status_confirm_preflight.md`.
- Chose `POST /api/v1/appointments/proposals/status-confirm` as the next
  confirmation family for idempotency route-test coverage before any wiring.
- Integrated DeepSeek worker review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint136-status-confirm-idempotency-preflight.md`;
  the review pivoted the decision from the initial update-confirm draft to
  status-confirm because it is self-contained, has a simpler body, avoids the
  update proposal revalidation window, and is less destructive than delete.
- Added
  `tests/test_api_spine_status_confirm_idempotency_preflight.py` to preserve
  the preflight decision, no-route-wiring posture, future route-test matrix,
  and closed gates.
- Added Claude and Antigravity Sprint 136 packets:
  `orchestration/agent_inbox/claude/claude-sprint136-status-confirm-idempotency-preflight-review.md`
  and
  `orchestration/agent_inbox/antigravity/antigravity-sprint136-status-confirm-idempotency-acceptance.md`.
- Preserved fake/default-disabled behavior; no status-confirm route wiring,
  update/delete/raw/proposal-only idempotency wiring, provider call, live smoke,
  runtime FGA client, external patient client, GraphQL mutation, H15/H-series
  runtime import, memory/RAG/GraphRAG, or broad trove mining was added.

## Sprint 136 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_status_confirm_idempotency_preflight.py`.
- `.venv\Scripts\python.exe -m pytest tests\test_api_spine_status_confirm_idempotency_preflight.py tests\test_phase_programmes_current_checkpoint.py tests\test_api_spine_appointment_idempotency_gap.py -q`
  (`13 passed`; existing Starlette/Google GenAI warnings only).

Sprint engine state: continuing. Next recommended slice is Sprint 137, a
guarded status-confirm idempotency route-test contract before any route wiring.

---

## Previous Closeout - Sprint 135

| Item | Value |
|---|---|
| Batch | Sprint 135 Bernie Create-Confirm Idempotency Route Wiring |
| Integrated through | Ariadne implementation with EMR4 API Steward skill; DeepSeek worker advice integrated; Claude and Antigravity protocol packets remain queued locally |
| Status | Local route wiring integrated; sprint engine continuing |
| Last updated | 2026-07-07 |

## Sprint 135 What Changed

- Wired HTTP `Idempotency-Key` enforcement for
  `POST /api/v1/appointments/proposals/create/confirm-bernie` only.
- The route now validates `BernieCreateProposalConfirmationIn`, claims the
  appointment command idempotency ledger with route family
  `create-confirm-bernie`, and returns replay/conflict/in-progress/stale/
  failed-transient decisions before signed evidence, session binding, or Bernie
  session events can run.
- Changed Bernie create-confirm appointment creation to `commit=False`, then
  completes the ledger and commits once after appointment/audit/response
  preparation.
- Enabled the Sprint 134 route-test contract as executable tests covering
  missing key, invalid payload, first bound confirmed write, session-bound
  replay, non-session-bound replay, body conflict, active/stale/failed
  preclaims, stale session binding, business-rule rollback, and replay telemetry
  shape.
- Updated existing Bernie confirm test callers to send idempotency keys.
- Stabilized older deterministic Bernie suites with explicit clock freezes and a
  committed stale-conflict fixture setup where route rollback now matters.
- Updated historical API-spine guards so they now permit exactly staff
  create-confirm and Bernie create-confirm idempotency wiring while keeping
  update/status/delete/raw/proposal-only families out of scope.
- Preserved fake/default-disabled behavior; no update/status/delete confirmation
  route, raw compatibility write, proposal-only idempotency ledger, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, or broad trove
  mining was added.

## Sprint 135 Verification

- `.venv\Scripts\python.exe -m py_compile app\routers\appointments.py tests\test_api_spine_bernie_create_confirm_idempotency_route_contract.py tests\test_bernie_confirm_create_proposal.py tests\test_bernie_route_outcome_events.py tests\test_bernie_signed_confirmation_evidence.py tests\test_bernie_sprint98_confirm_contract.py tests\test_bernie_turn_contract.py tests\test_bernie_evidence_contract.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_bernie_create_confirm_idempotency_route_contract.py tests/test_bernie_confirm_create_proposal.py tests/test_bernie_route_outcome_events.py tests/test_bernie_signed_confirmation_evidence.py tests/test_bernie_sprint98_confirm_contract.py tests/test_bernie_turn_contract.py tests/test_bernie_evidence_contract.py -q`
  (`86 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py tests/test_api_spine_appointment_idempotency_route_integration_preflight.py tests/test_api_spine_bernie_create_confirm_idempotency_route_contract.py tests/test_api_spine_bernie_create_confirm_idempotency_preflight.py tests/test_appointment_proposals.py tests/test_api_spine_appointment_idempotency_storage_helper.py tests/test_api_spine_appointment_idempotency_model_migration.py tests/test_api_spine_appointment_idempotency_storage_artifact_guard.py tests/test_api_spine_appointment_idempotency_gap.py -q`
  (`75 passed`; existing warnings only).

Note: local broad DB-backed pytest was rerun serially after resetting only the
`gp_pms_test` public schema to avoid the known PostgreSQL enum setup conflict
from overlapping pytest sessions.

Sprint engine state: continuing. Next recommended slice is Sprint 136, a narrow
preflight to choose the next confirmation family before any update/status/delete
idempotency wiring.

---

## Previous Closeout - Sprint 134

| Item | Value |
|---|---|
| Batch | Sprint 134 Bernie Create-Confirm Idempotency Route-Test Contract |
| Integrated through | Ariadne implementation with EMR4 API Steward skill; DeepSeek worker review integrated; Claude and Antigravity protocol packets queued locally |
| Status | Local contract integrated; sprint engine continuing |
| Last updated | 2026-07-07 |

## Sprint 134 What Changed

- Added
  `orchestration/api_spine_appointment_idempotency_bernie_create_confirm_route_tests.md`
  for the guarded `confirm-bernie` idempotency route-test contract.
- Added
  `tests/test_api_spine_bernie_create_confirm_idempotency_route_contract.py`
  with passing static scope checks and skipped future behavior tests for:
  missing key, invalid payload, first write, same-key replay, same-key conflict,
  in-progress, stale in-progress, failed transient, stale session binding,
  blocked-claim rollback, replay telemetry, and non-session-bound replay.
- Integrated DeepSeek worker review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint134-bernie-create-confirm-idempotency-route-contract.md`.
  The review identified `confirmation_outcome` as the most concrete
  double-session-event replay risk.
- Added Claude and Antigravity Sprint 134 protocol packets:
  `orchestration/agent_inbox/claude/claude-sprint134-bernie-create-confirm-idempotency-contract.md`
  and
  `orchestration/agent_inbox/antigravity/antigravity-sprint134-bernie-create-confirm-idempotency-acceptance.md`.
  They are queued locally pending baton/worker pickup; Antigravity availability
  is not determined by the missing shell alias.
- Stabilized `tests/test_bernie_route_outcome_events.py` by freezing its
  deterministic `2026-06-22` clock, matching adjacent Bernie confirmation
  tests and preventing date drift from blocking supervised booking setup.
- Updated Programme 2G planning guidance and checkpoint tests so the sprint
  engine points to Sprint 135: Bernie create-confirm idempotency route wiring.
- Preserved fake/default-disabled behavior; no `confirm-bernie` route wiring,
  update/status/delete confirmation route, raw compatibility write,
  proposal-only idempotency ledger, provider call, live smoke, runtime FGA
  client, external patient client, GraphQL mutation, H15/H-series runtime
  import, memory/RAG/GraphRAG, or broad trove mining was added.

## Sprint 134 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_bernie_route_outcome_events.py tests\test_api_spine_bernie_create_confirm_idempotency_route_contract.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_bernie_create_confirm_idempotency_route_contract.py tests/test_api_spine_bernie_create_confirm_idempotency_preflight.py tests/test_bernie_route_outcome_events.py tests/test_bernie_confirm_create_proposal.py -q`
  (`33 passed`, `12 skipped`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean apart from the known CRLF notice on
  `orchestration/integration_log.md`.

Sprint engine state: continuing. Next recommended slice is Sprint 135, narrow
Bernie create-confirm idempotency route wiring, with the route-level replay
decision before any `confirm_submitted` or `confirmation_outcome` append.

---

## Previous Closeout - Sprint 133

| Item | Value |
|---|---|
| Batch | Sprint 133 Bernie Create-Confirm Idempotency Preflight |
| Integrated through | Ariadne implementation with EMR4 API Steward skill |
| Status | Local preflight integrated; sprint engine continuing |
| Last updated | 2026-07-07 |

## Sprint 133 What Changed

- Added
  `orchestration/api_spine_appointment_idempotency_bernie_create_confirm_preflight.md`
  for the next confirmation family:
  `POST /api/v1/appointments/proposals/create/confirm-bernie` /
  `confirm_bernie_create_proposal`.
- Kept canonical operation id `confirmAppointmentCreateProposal` aligned with
  staff create-confirm while assigning a distinct proposed route-family label,
  `create-confirm-bernie`, for audit/reporting clarity.
- Documented the extra boundary that Bernie create-confirm has session-event
  side effects (`confirm_submitted` and `confirmation_outcome`) as well as the
  appointment/audit/ledger transaction.
- Added `tests/test_api_spine_bernie_create_confirm_idempotency_preflight.py`
  to prove the preflight names the correct route, records the session-event
  replay boundary, keeps closed gates closed, and leaves the current
  `confirm-bernie` route unwired for `Idempotency-Key`.
- Updated Programme 2G planning guidance and checkpoint tests so the sprint
  engine is no longer paused after Sprint 132 and now points to Sprint 134:
  Bernie create-confirm idempotency route-test contract.
- Preserved fake/default-disabled behavior; no Bernie route idempotency wiring,
  update/status/delete confirmation route, raw compatibility write,
  proposal-only idempotency ledger, provider call, live smoke, runtime FGA
  client, external patient client, GraphQL mutation, H15/H-series runtime
  import, memory/RAG/GraphRAG, or broad trove mining was added.

## Sprint 133 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_bernie_create_confirm_idempotency_preflight.py tests\test_phase_programmes_current_checkpoint.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_bernie_create_confirm_idempotency_preflight.py tests/test_phase_programmes_current_checkpoint.py tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py tests/test_appointment_proposals.py tests/test_api_spine_appointment_idempotency_route_integration_preflight.py -q`
  (`32 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`
  (`historical diary leakage lint safe`).
- `git diff --check` clean apart from the known CRLF notice on
  `orchestration/integration_log.md`.

Note: an earlier parallel pytest attempt against the local PostgreSQL test DB
hit a leftover enum setup conflict (`userrole` already existed). Ariadne reset
only the `gp_pms_test` public schema after verifying the database name, then
reran the focused suite serially successfully.

Sprint engine state: continuing. Next recommended slice is Sprint 134, a
guarded route-test contract for Bernie create-confirm idempotency before any
`confirm-bernie` route wiring.

---

## Previous Closeout - Sprint 132

| Item | Value |
|---|---|
| Batch | Sprint 132 Staff Create-Confirm Idempotency Route Wiring |
| Integrated through | Ariadne implementation with EMR4 API Steward skill; Claude available; Antigravity UI quota available but shell alias missing; DeepSeek extra lane could not be spawned because the worker thread limit was reached |
| Status | Local integration verified; sprint engine later resumed for Sprint 133 |
| Last updated | 2026-07-07 |

## Sprint 132 What Changed

- Wired HTTP `Idempotency-Key` enforcement for the first approved appointment
  command family only:
  `POST /api/v1/appointments/proposals/create/confirm` /
  `confirm_create_proposal_route`, canonical operation
  `confirmAppointmentCreateProposal`, route family `create-confirm`.
- Added route-level claim/replay/conflict handling through
  `app/services/appointment_idempotency.py` while keeping the router away from
  direct `AppointmentCommandIdempotency` model/table imports.
- Refactored `_create_appointment_from_body(..., commit=True)` so the staff
  create-confirm route can write the appointment, audit row, and completed
  idempotency ledger in one route-level transaction.
- Enabled the Sprint 131 guarded behavior matrix as live route tests covering:
  missing key, first write, same-key replay, same-key/different-body conflict,
  active in-progress, stale in-progress, failed-transient, post-claim
  business-block rollback, and proposal-only out-of-scope behavior.
- Updated existing appointment proposal tests to send `Idempotency-Key` on the
  staff create-confirm route.
- Updated older gap/preflight/model/helper guards so they now assert the narrow
  Sprint 132 wiring boundary rather than the former absolute unwired state.
- Updated protocol alerts after Yuri corrected Ariadne's availability check:
  Antigravity/Gemini UI quota availability counts even if a bare
  `antigravity --version` PATH probe fails.
- Preserved fake/default-disabled behavior; no Bernie create-confirm,
  update/status/delete confirmation route, raw compatibility write,
  proposal-only idempotency ledger, provider call, live smoke, runtime FGA
  client, external patient client, GraphQL mutation, H15/H-series runtime
  import, memory/RAG/GraphRAG, or broad trove mining was added.

## Sprint 132 Verification

- `.venv\Scripts\python.exe -m py_compile app\routers\appointments.py tests\test_api_spine_staff_create_confirm_idempotency_route_contract.py tests\test_appointment_proposals.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py tests/test_appointment_proposals.py tests/test_api_spine_appointment_idempotency_route_integration_preflight.py tests/test_api_spine_appointment_idempotency_storage_helper.py tests/test_api_spine_appointment_idempotency_model_migration.py tests/test_api_spine_appointment_idempotency_storage_artifact_guard.py tests/test_api_spine_appointment_idempotency_gap.py -q`
  (`53 passed`; existing Starlette/Google GenAI warnings only).

Sprint engine state at closeout: paused at Yuri's request after completing
Sprint 132. Yuri resumed the engine on 2026-07-07; Sprint 133 is now the current
closeout above.

---

## Previous Closeout - Sprint 131

## Sprint 131 What Changed

- Added
  `orchestration/api_spine_appointment_idempotency_staff_create_confirm_route_tests.md`,
  a guarded route-test contract for the staff create-confirm idempotency wiring
  sprint.
- Added
  `tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py` to
  guard the scope, enumerate future behavior tests, prove the current router is
  still unwired, and keep behavior tests skipped until Sprint 132 wiring.
- Folded DeepSeek review residuals by pinning the exact skip metadata: the nine
  skipped behavior tests must match the contract and only static scope/router
  guards may pass before wiring.
- Scoped the future executable tests to
  `POST /api/v1/appointments/proposals/create/confirm` /
  `confirm_create_proposal_route`, canonical operation
  `confirmAppointmentCreateProposal`, route family `create-confirm`.
- Explicitly excluded Bernie create-confirm, update/status/delete confirmation
  routes, raw compatibility writes, proposal-only create, slot-search, and
  Bernie command-style reads.
- Preserved fake/default-disabled behavior; no appointment route behavior
  change, provider call, live smoke, runtime FGA client, external patient
  client, GraphQL mutation, H15/H-series runtime import, memory/RAG/GraphRAG,
  broad trove mining, or route-level model-to-database write was added.

## Sprint 131 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_staff_create_confirm_idempotency_route_contract.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py -q`
  (`5 passed, 9 skipped`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py tests/test_api_spine_appointment_idempotency_route_integration_preflight.py tests/test_api_spine_appointment_idempotency_storage_helper.py tests/test_api_spine_appointment_idempotency_model_migration.py tests/test_api_spine_appointment_idempotency_storage_artifact_guard.py tests/test_api_spine_appointment_idempotency_storage_design.py tests/test_api_spine_appointment_idempotency_policy_packet.py tests/test_api_spine_appointment_idempotency_gap.py tests/test_api_spine_openapi_backend_alignment.py tests/test_api_spine_appointment_openapi_drift_guard.py tests/test_api_spine_appointment_command_alignment_inventory.py tests/test_api_spine_post_sprint118_checkpoint.py tests/test_api_spine_artifacts.py tests/test_phase_programmes_current_checkpoint.py -q`
  (`106 passed, 9 skipped`; existing Starlette/Google GenAI warnings only).
- `git diff --check` (known CRLF notice on `orchestration/integration_log.md`
  only).
- DeepSeek Flash review found no blockers. Ariadne folded its skip-metadata
  residuals into the guard before closeout.

Sprint engine state: continuing. Next recommended direction is Sprint 132:
staff create-confirm idempotency route wiring, excluding Bernie/update/status/
delete/raw families.

---

## Previous Closeout - Sprint 130

## Sprint 130 What Changed

- Added
  `orchestration/api_spine_appointment_idempotency_route_integration_preflight.md`,
  a static route-integration contract for the first idempotency-wired confirm
  family.
- Added
  `tests/test_api_spine_appointment_idempotency_route_integration_preflight.py`
  to guard the first-family scope, helper-before-write call order, fail-closed
  mappings, required future route tests, current router isolation, and helper
  surface availability.
- Scoped the first future wiring target to
  `POST /api/v1/appointments/proposals/create/confirm` /
  `confirm_create_proposal_route`, canonical operation
  `confirmAppointmentCreateProposal`, route family `create-confirm`.
- Explicitly excluded `confirm-bernie`, update, status, delete, raw
  compatibility writes, and proposal-only routes from the first wiring sprint.
- Defined fail-closed preflight mappings for conflict, active in-progress,
  stale in-progress, and failed-transient decisions; no stale overwrite behavior
  is approved.
- Folded DeepSeek review notes into the preflight: concrete response-map
  expectations, rollback/removal on post-claim business-rule failure, explicit
  `expires_at` omission rationale, and proposal-only route separation.
- Updated `AGENTS.md`, `orchestration/phase_programmes.md`,
  `orchestration/integration_log.md`, and the phase checkpoint test so
  Programme 2G now names Sprint 131 staff create-confirm idempotency route tests
  as the next slice.
- Preserved fake/default-disabled behavior; no appointment route behavior
  change, provider call, live smoke, runtime FGA client, external patient
  client, GraphQL mutation, H15/H-series runtime import, memory/RAG/GraphRAG,
  broad trove mining, or route-level model-to-database write was added.

## Sprint 130 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_appointment_idempotency_route_integration_preflight.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_appointment_idempotency_route_integration_preflight.py -q`
  (`6 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_appointment_idempotency_route_integration_preflight.py tests/test_api_spine_appointment_idempotency_storage_helper.py tests/test_api_spine_appointment_idempotency_model_migration.py tests/test_api_spine_appointment_idempotency_storage_artifact_guard.py tests/test_api_spine_appointment_idempotency_storage_design.py tests/test_api_spine_appointment_idempotency_policy_packet.py tests/test_api_spine_appointment_idempotency_gap.py tests/test_api_spine_openapi_backend_alignment.py tests/test_api_spine_appointment_openapi_drift_guard.py tests/test_api_spine_appointment_command_alignment_inventory.py tests/test_api_spine_post_sprint118_checkpoint.py tests/test_api_spine_artifacts.py tests/test_phase_programmes_current_checkpoint.py -q`
  (`101 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check` (known CRLF notice on `orchestration/integration_log.md`
  only).
- DeepSeek Flash review found no blockers. Ariadne folded its Sprint 131 design
  notes into the preflight before closeout.

Sprint engine state: continuing. Next recommended direction is Sprint 131:
staff create-confirm idempotency route tests before implementation.

---

## Previous Closeout - Sprint 129

## Sprint 129 What Changed

- Added `app/services/appointment_idempotency.py`, a storage-layer helper module
  for appointment command idempotency.
- Added canonical JSON serialization, SHA-256 body hashing, HMAC/SHA-256
  idempotency-key hashing, ledger-first claim decisions with
  `with_for_update()`, and completion metadata storage.
- Added storage decisions for `started`, `replay`, `conflict`, `in_progress`,
  `stale_in_progress`, and `failed_transient`.
- Added `tests/test_api_spine_appointment_idempotency_storage_helper.py` with
  DB-backed tests for stable hashes, no raw key storage, in-progress creation,
  completed same-key/same-body replay, same-key/different-body conflict,
  in-progress retry refusal, stale `in_progress` refusal, no helper commits, no
  appointment writes, and no appointment-router wiring.
- Added `orchestration/api_spine_appointment_idempotency_storage_helper.md` to
  record the helper-only scope and Sprint 130 route integration preflight.
- Folded DeepSeek review residuals by adding explicit `failed_transient`
  coverage and documenting stale `in_progress`/`expires_at` as Sprint 130 caller
  contract decisions.
- Updated `AGENTS.md`, `orchestration/phase_programmes.md`,
  `orchestration/integration_log.md`, and the phase checkpoint test so
  Programme 2G now names Sprint 130 appointment idempotency route integration
  preflight as the next slice.
- Preserved fake/default-disabled behavior; no appointment route behavior
  change, provider call, live smoke, runtime FGA client, external patient
  client, GraphQL mutation, H15/H-series runtime import, memory/RAG/GraphRAG,
  broad trove mining, or route-level model-to-database write was added.

## Sprint 129 Verification

- `.venv\Scripts\python.exe -m py_compile app\services\appointment_idempotency.py tests\test_api_spine_appointment_idempotency_storage_helper.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_appointment_idempotency_storage_helper.py -q`
  (`9 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_appointment_idempotency_storage_helper.py tests/test_api_spine_appointment_idempotency_model_migration.py tests/test_api_spine_appointment_idempotency_storage_artifact_guard.py tests/test_api_spine_appointment_idempotency_storage_design.py tests/test_api_spine_appointment_idempotency_policy_packet.py tests/test_api_spine_appointment_idempotency_gap.py tests/test_api_spine_openapi_backend_alignment.py tests/test_api_spine_appointment_openapi_drift_guard.py tests/test_api_spine_appointment_command_alignment_inventory.py tests/test_api_spine_post_sprint118_checkpoint.py tests/test_api_spine_artifacts.py tests/test_phase_programmes_current_checkpoint.py -q`
  (`95 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check` (known CRLF notice on `orchestration/integration_log.md`
  only).
- DeepSeek Flash review found no blockers. Ariadne folded its
  `failed_transient` residual into test coverage and recorded the stale/expiry
  caller-contract decisions for Sprint 130.

Sprint engine state: continuing. Next recommended direction is Sprint 130:
appointment idempotency route integration preflight for one confirm family.

---

## Previous Closeout - Sprint 128

## Sprint 128 What Changed

- Added `AppointmentCommandIdempotency` to `app/models/appointments.py` and the
  model package exports.
- Added Alembic migration
  `alembic/versions/l1m2n3o4p5q6_add_appointment_command_idempotency.py` for
  the `appointment_command_idempotency` replay ledger.
- Added
  `orchestration/api_spine_appointment_idempotency_model_migration_preflight.md`
  to record that this is storage artifact preflight only, not route
  enforcement.
- Added `tests/test_api_spine_appointment_idempotency_model_migration.py` to
  guard model columns, nullability, actor-id shape, unique scope, indexes,
  state/completed-response CHECK constraints, migration parity, no raw key/body
  storage fields, and no appointment-router wiring.
- The existing Sprint 127 artifact guard now actively checks the model and
  migration instead of remaining dormant.
- Updated `AGENTS.md`, `orchestration/phase_programmes.md`,
  `orchestration/integration_log.md`, and the phase checkpoint test so
  Programme 2G now names Sprint 129 appointment idempotency storage helper
  tests as the next slice.
- Preserved fake/default-disabled behavior; no appointment route behavior
  change, provider call, live smoke, runtime FGA client, external patient
  client, GraphQL mutation, H15/H-series runtime import, memory/RAG/GraphRAG,
  broad trove mining, or model-to-database write beyond the migration artifact
  was added.

## Sprint 128 Verification

- `.venv\Scripts\python.exe -m py_compile app\models\appointments.py app\models\__init__.py alembic\versions\l1m2n3o4p5q6_add_appointment_command_idempotency.py tests\test_api_spine_appointment_idempotency_model_migration.py tests\test_api_spine_appointment_idempotency_storage_artifact_guard.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_appointment_idempotency_model_migration.py tests/test_api_spine_appointment_idempotency_storage_artifact_guard.py -q`
  (`13 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_appointment_idempotency_model_migration.py tests/test_api_spine_appointment_idempotency_storage_artifact_guard.py tests/test_api_spine_appointment_idempotency_storage_design.py tests/test_api_spine_appointment_idempotency_policy_packet.py tests/test_api_spine_appointment_idempotency_gap.py tests/test_api_spine_openapi_backend_alignment.py tests/test_api_spine_appointment_openapi_drift_guard.py tests/test_api_spine_appointment_command_alignment_inventory.py tests/test_api_spine_post_sprint118_checkpoint.py tests/test_api_spine_artifacts.py tests/test_phase_programmes_current_checkpoint.py -q`
  (`86 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check` (known CRLF notice on `orchestration/integration_log.md`
  only).
- DeepSeek Flash review found no blockers and confirmed model/migration
  alignment, route isolation, forbidden-field absence, preflight-doc accuracy,
  and `models/__init__.py` export coverage.

Sprint engine state: continuing. Next recommended direction is Sprint 129:
appointment command idempotency storage helper tests, still without appointment
route enforcement.

---

## Previous Closeout - Sprint 127

## Sprint 127 What Changed

- Added `orchestration/api_spine_appointment_idempotency_storage_artifact_guard.md`,
  a non-runtime guard packet for the future appointment command idempotency
  model/migration artifacts.
- Added
  `tests/test_api_spine_appointment_idempotency_storage_artifact_guard.py` to
  enforce that any future `appointment_command_idempotency` model and migration
  land together.
- Guarded future model signals for the Sprint 126 storage contract: required
  columns, unique scope, indexes, no raw idempotency key storage, no raw request
  body storage, and canonical artifact names.
- Guarded route-enforcement ordering: appointment routes must not bind or
  enforce HTTP `Idempotency-Key` before matching model and migration artifacts
  exist.
- Folded DeepSeek review residuals into the guard: forbid future request-body
  JSON storage, require storage-helper scenario tests before route enforcement,
  and make future model/migration checks expect state/check/nullability signals.
- Preserved the current distinction between existing Bernie session
  idempotency fields and future appointment-command HTTP idempotency.
- Updated `AGENTS.md`, `orchestration/phase_programmes.md`,
  `orchestration/integration_log.md`, and the phase checkpoint test so
  Programme 2G now names Sprint 128 appointment idempotency model/migration
  preflight as the next slice.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.

## Sprint 127 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_appointment_idempotency_storage_artifact_guard.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_appointment_idempotency_storage_artifact_guard.py tests/test_api_spine_appointment_idempotency_storage_design.py tests/test_api_spine_appointment_idempotency_policy_packet.py -q`
  (`21 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_appointment_idempotency_storage_artifact_guard.py tests/test_api_spine_appointment_idempotency_storage_design.py tests/test_api_spine_appointment_idempotency_policy_packet.py tests/test_api_spine_appointment_idempotency_gap.py tests/test_api_spine_openapi_backend_alignment.py tests/test_api_spine_appointment_openapi_drift_guard.py tests/test_api_spine_appointment_command_alignment_inventory.py tests/test_api_spine_post_sprint118_checkpoint.py tests/test_api_spine_artifacts.py tests/test_phase_programmes_current_checkpoint.py -q`
  (`80 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check` (known CRLF notice on `orchestration/integration_log.md`
  only).
- DeepSeek Flash review found no blockers. Ariadne folded its three residuals
  into the guard before closeout.

Sprint engine state: continuing. Next recommended direction is Sprint 128:
appointment command idempotency model/migration preflight, still without route
enforcement.

---

## Previous Closeout - Sprint 126

## Sprint 126 What Changed

- Added `orchestration/api_spine_appointment_idempotency_storage_design.md`, a
  storage-design-only packet for the future appointment command replay ledger.
- Defined proposed `appointment_command_idempotency` columns, indexes,
  constraints, states, retention posture, and no raw key/raw request body
  storage boundary.
- Pinned canonical operation ids across backend aliases, including
  `confirm-bernie`, `status-confirm`, and `delete-confirm`.
- Defined deterministic request body hashing: typed schema first, sorted keys,
  compact JSON, canonical UUID/date/time/datetime strings, and keyed hashing of
  submitted idempotency keys.
- Defined the transaction boundary: insert or lock the replay row before any
  appointment write; only the owner transaction may run confirmation checks and
  mutate; appointment mutation, audit evidence, and completed replay result must
  commit atomically.
- Defined replay, recovery, raw compatibility, and implementation-test
  requirements.
- Folded DeepSeek's storage residuals into explicit requirements for stale
  `in_progress` recovery, non-confirmation TTL policy, replay audit/telemetry,
  scoped system actor identities, and ledger-first lock ordering.
- Added `tests/test_api_spine_appointment_idempotency_storage_design.py` to
  guard the storage design.
- Updated `AGENTS.md` and `orchestration/phase_programmes.md` so Programme 2G
  now names Sprint 127 appointment idempotency storage artifact guard/model
  preflight as the next implementation slice.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.

## Sprint 126 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_appointment_idempotency_storage_design.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_appointment_idempotency_storage_design.py tests/test_api_spine_appointment_idempotency_policy_packet.py tests/test_api_spine_appointment_idempotency_gap.py tests/test_api_spine_openapi_backend_alignment.py tests/test_api_spine_appointment_openapi_drift_guard.py tests/test_api_spine_appointment_command_alignment_inventory.py tests/test_api_spine_post_sprint118_checkpoint.py tests/test_api_spine_artifacts.py tests/test_phase_programmes_current_checkpoint.py -q`
  (`73 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check` (known CRLF notice on `orchestration/integration_log.md`
  only).
- DeepSeek Flash review found no blockers. Ariadne folded its five
  storage-design residuals into the packet before closeout.

Sprint engine state: continuing. Next recommended direction is Sprint 127:
add the appointment idempotency storage artifact guard or model/migration
preflight before route enforcement.

---

## Previous Closeout - Sprint 125

## Sprint 125 What Changed

- Added `orchestration/api_spine_appointment_idempotency_policy_packet.md`, a
  policy-only packet defining appointment command idempotency behavior before
  implementation.
- Defined route-family decisions for proposal routes, confirmation routes,
  backend alias confirmations, Bernie create confirmation, slot-search reads,
  Bernie command-style reads, and raw compatibility writes.
- Specified replay ledger binding fields, uniqueness, retention, response
  replay, conflict behavior, and no raw request body storage by default.
- Folded review-driven storage constraints into the policy: same-transaction
  appointment write/replay ledger/audit commit, replay-row locking before
  writes, non-expiring confirmation-write entries while clinically/audit
  relevant, deterministic JSON canonicalization, shared operation IDs for
  aliases, and actor-role audit semantics.
- Defined confirmation execution ordering so idempotency cannot bypass
  `confirmed=true`, freshness, signed confirmation evidence, warning
  acknowledgement, current-state revalidation, role/tenant policy, or audit.
- Required future regression tests proving no duplicate appointment write on
  replay, conflict on same key/different body, scoping by practice/actor/
  operation, stale evidence behavior, raw compatibility policy, and audit
  evidence without raw body exposure.
- Added `tests/test_api_spine_appointment_idempotency_policy_packet.py` to
  guard the packet.
- Updated `AGENTS.md` and `orchestration/phase_programmes.md` so Programme 2G
  now names Sprint 126 appointment command idempotency storage design as the
  next implementation slice.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.

## Sprint 125 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_appointment_idempotency_policy_packet.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_appointment_idempotency_policy_packet.py tests/test_api_spine_appointment_idempotency_gap.py tests/test_api_spine_openapi_backend_alignment.py tests/test_api_spine_appointment_openapi_drift_guard.py tests/test_api_spine_appointment_command_alignment_inventory.py tests/test_api_spine_post_sprint118_checkpoint.py tests/test_api_spine_artifacts.py tests/test_phase_programmes_current_checkpoint.py -q`
  (`65 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check`.
- DeepSeek Flash review found no blockers. Ariadne folded its storage-design
  residuals into the packet before closeout so Sprint 126 starts with hard
  transaction/concurrency/canonicalization/alias-scope constraints.

Sprint engine state: continuing. Next recommended direction is Sprint 126:
draft the appointment command idempotency storage design before route
enforcement.

---

## Previous Closeout - Sprint 124

## Sprint 124 What Changed

- Added `orchestration/api_spine_appointment_idempotency_gap.md`, a
  documentation/test-only inspection of the appointment command
  `Idempotency-Key` gap.
- Recorded that the OpenAPI draft requires `Idempotency-Key` on eight
  proposal/confirmation-grade appointment command paths.
- Documented that current `app/routers/appointments.py` has no `Header(...)`
  binding and no `Idempotency-Key` HTTP-header enforcement for appointment
  proposal, confirmation, compatibility write, or slot-search routes.
- Distinguished existing freshness ids, signed confirmation evidence,
  `confirmed=true`, raw compatibility audit posture, and Bernie session
  idempotency from durable appointment command-plane idempotency.
- Recorded raw compatibility writes as a separate policy decision, not a hidden
  implementation requirement.
- Added `tests/test_api_spine_appointment_idempotency_gap.py` to guard the gap
  artifact, the eight OpenAPI idempotency paths, current absence of HTTP header
  binding, non-equivalence boundaries, closed gates, and the Sprint 125 policy
  packet recommendation.
- Updated `AGENTS.md` and `orchestration/phase_programmes.md` so Programme 2G
  now names Sprint 125 appointment command idempotency policy packet as the
  next implementation slice.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.

## Sprint 124 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_appointment_idempotency_gap.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_appointment_idempotency_gap.py tests/test_api_spine_openapi_backend_alignment.py tests/test_api_spine_appointment_openapi_drift_guard.py tests/test_api_spine_appointment_command_alignment_inventory.py tests/test_api_spine_post_sprint118_checkpoint.py tests/test_api_spine_artifacts.py tests/test_phase_programmes_current_checkpoint.py -q`
  (`58 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check`.
- DeepSeek Flash review found no blockers. Ariadne folded in its two
  test-quality residuals before closeout: source-pass assertions now cover all
  listed sources, and the router guard checks idempotency-specific header
  patterns rather than banning unrelated future headers.

Sprint engine state: continuing. Next recommended direction is Sprint 125:
draft the appointment command idempotency policy packet before implementation.

---

## Previous Closeout - Sprint 123

## Sprint 123 What Changed

- Added an `x-emr4-current-backend-alignment` extension to
  `docs/api-spine/openapi/appointment-commands.yaml`.
- The extension documents current backend path drift against canonical OpenAPI
  paths for status confirmation, delete confirmation, and slot-search
  selection.
- It records current compatibility write routes as legacy paths outside the
  proposal-confirm envelope.
- It records Bernie intent, interpreter, supervised booking, confirm-Bernie,
  no-slot suggestion, pilot eligibility, and session lifecycle variants as
  current backend variants without adding them as canonical `paths:` entries.
- It preserves blocked gates in a `blocked_gates` section so existing API Spine
  artifact safety scanning treats them as exclusions, not enabled capabilities.
- Added `tests/test_api_spine_openapi_backend_alignment.py` to parse the
  OpenAPI YAML and guard the alignment extension.
- The test validates the metadata review date shape and cross-checks extension
  paths/handlers against the AST-backed Sprint 122 route inventory guard.
- Updated the Sprint 122 drift guard so Bernie variants may appear in OpenAPI
  metadata while remaining absent from explicit OpenAPI `paths:`.
- Updated `AGENTS.md` and `orchestration/phase_programmes.md` so Programme 2G
  now names Sprint 124 appointment command `Idempotency-Key` enforcement gap
  inspection as the next implementation slice.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.

## Sprint 123 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_openapi_backend_alignment.py tests\test_api_spine_appointment_openapi_drift_guard.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_openapi_backend_alignment.py tests/test_api_spine_appointment_openapi_drift_guard.py tests/test_api_spine_appointment_command_alignment_inventory.py tests/test_api_spine_post_sprint118_checkpoint.py tests/test_api_spine_artifacts.py tests/test_phase_programmes_current_checkpoint.py -q`
  (`53 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check`.
- DeepSeek Flash review found no blockers. Ariadne folded in its metadata date
  and route/handler cross-check residuals before closeout.

Sprint engine state: continuing. Next recommended direction is Sprint 124:
inspect the appointment command `Idempotency-Key` enforcement gap before any
route behavior change.

---

## Previous Closeout - Sprint 122

## Sprint 122 What Changed

- Added `tests/test_api_spine_appointment_openapi_drift_guard.py`, a
  non-invasive static guard over the appointment API spine.
- The guard parses `app/routers/appointments.py` with `ast` and requires every
  current appointment-router route to appear in the Sprint 121 inventory with
  the exact handler name and classification.
- It caught and corrected three stale handler names in
  `orchestration/api_spine_appointment_command_alignment_inventory.md`:
  `get_waiting_room`, `get_checkin_defaults`, and `get_available_slots`.
- It pins the three deliberate current OpenAPI path mismatches:
  `status-confirm` vs `/appointments/proposals/status/confirm`,
  `delete-confirm` vs `/appointments/proposals/delete/confirm`, and
  `slot-search/selection` vs `/appointments/proposals/slot-search/select`.
- The drift assertions are row-scoped, and the guard pins the current OpenAPI
  path set so future OpenAPI path additions are deliberate.
- It also proves the Sprint 101 OpenAPI draft does not yet explicitly document
  Bernie intent, interpreter, supervised-booking, confirm-Bernie, no-slot, or
  session route variants.
- Updated `AGENTS.md` and `orchestration/phase_programmes.md` so Programme 2G
  now names Sprint 123 OpenAPI backend compatibility alias and Bernie variant
  documentation as the next implementation slice.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.

## Sprint 122 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_appointment_openapi_drift_guard.py tests\test_api_spine_appointment_command_alignment_inventory.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_appointment_openapi_drift_guard.py tests/test_api_spine_appointment_command_alignment_inventory.py tests/test_api_spine_post_sprint118_checkpoint.py tests/test_api_spine_artifacts.py tests/test_phase_programmes_current_checkpoint.py -q`
  (`47 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check`.
- DeepSeek Flash review found no blockers. Ariadne folded in its row-scoping
  and OpenAPI path-count residuals before closeout; the remaining AST-literal
  and markdown-table strictness notes are acceptable for this static guard.

Sprint engine state: continuing. Next recommended direction is Sprint 123:
document backend compatibility aliases and Bernie-specific variants in the
OpenAPI layer without adding runtime aliases.

---

## Previous Closeout - Sprint 121

## Sprint 121 What Changed

- Added
  `orchestration/api_spine_appointment_command_alignment_inventory.md`, a
  documentation/test-only inventory mapping current FastAPI appointment routes
  to the API Spine command-plane families.
- Classified current appointment routes as proposal commands, confirm commands,
  command-style reads, compatibility writes, or read-only routes.
- Recorded alignment for create, update, status/waiting-area, delete/cancel,
  slot-search normalize/search/normalized/selection, Bernie intent,
  interpretation, supervised booking, no-slot suggestion selection, session
  lifecycle, Bernie create confirmation, raw compatibility writes, and
  read-only appointment/slot/audit/reference surfaces.
- Identified deliberate current drift between backend paths and the Sprint 101
  OpenAPI draft: `status-confirm` vs `/status/confirm`, `delete-confirm` vs
  `/delete/confirm`, `slot-search/selection` vs `slot-search/select`, missing
  explicit Bernie intent/session/supervised/confirm variants, compatibility
  writes outside the proposal-confirm envelope, and unproven `Idempotency-Key`
  enforcement.
- Added `tests/test_api_spine_appointment_command_alignment_inventory.py` to
  statically guard the inventory against current router route families, expected
  classification vocabulary, OpenAPI drift entries, and closed-gate posture.
- Updated `AGENTS.md` and `orchestration/phase_programmes.md` so Programme 2G
  now names Sprint 122 appointment command OpenAPI drift guard as the next
  implementation slice.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.

## Sprint 121 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_appointment_command_alignment_inventory.py tests\test_phase_programmes_current_checkpoint.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_appointment_command_alignment_inventory.py tests/test_api_spine_post_sprint118_checkpoint.py tests/test_api_spine_artifacts.py tests/test_phase_programmes_current_checkpoint.py -q`
  (`42 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check` passed with the known CRLF notice on
  `orchestration/integration_log.md`.
- DeepSeek Flash review initially found a Bernie-route coverage gap. Ariadne
  folded it in before closeout by adding Bernie intent, interpreter, no-slot,
  pilot eligibility, and session lifecycle routes to the inventory and guard.
- DeepSeek Flash re-check confirmed the Bernie route coverage gap was resolved.
  Its remaining blocker was isolated to the DeepSeek worker's inaccessible
  Python interpreter; Ariadne's integration worktree verification passed.

Sprint engine state: continuing. Next recommended direction is Sprint 122:
add a non-invasive appointment command OpenAPI drift guard.

---

## Previous Closeout - Sprint 120

## Sprint 120 What Changed

- Added `orchestration/api_spine_post_sprint118_checkpoint.md`, a
  documentation/test-only API Spine checkpoint after Sprint 110-118
  provider-boundary guard consolidation.
- The checkpoint records the required API Steward source pass over the ADR,
  API Spine programme, Access AI design, Bernie release gates, API-spine
  prototype artifacts, and artifact tests.
- It confirms the accepted mixed API spine still holds: GraphQL read/context
  graph only, REST/OpenAPI command plane for high-risk actions, async contracts
  as observed/ingested events, YAML as declarative posture, and Access AI as the
  provider invocation boundary.
- It names Sprint 121 as the next implementation slice: a non-invasive
  appointment command envelope alignment inventory over current FastAPI
  appointment proposal, confirmation, slot-search, and compatibility write
  routes.
- Updated `orchestration/phase_programmes.md` so Programme 2G now marks the
  checkpoint complete and names Sprint 121 as the next candidate.
- Added `tests/test_api_spine_post_sprint118_checkpoint.py` and updated
  `tests/test_phase_programmes_current_checkpoint.py` to guard the checkpoint
  and selected next slice.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.
- DeepSeek Flash review found no blockers. Its venv warning was isolated to the
  DeepSeek worker environment; Ariadne's focused verification passed locally.

## Sprint 120 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_post_sprint118_checkpoint.py tests\test_phase_programmes_current_checkpoint.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_api_spine_post_sprint118_checkpoint.py tests/test_api_spine_artifacts.py tests/test_phase_programmes_current_checkpoint.py -q`
  (`37 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check -- orchestration/api_spine_post_sprint118_checkpoint.md orchestration/phase_programmes.md tests/test_api_spine_post_sprint118_checkpoint.py tests/test_phase_programmes_current_checkpoint.py`.

Sprint engine state: continuing. Next recommended direction is Sprint 121:
build the non-invasive appointment command envelope alignment inventory.

---

## Previous Closeout - Sprint 119

## Sprint 119 What Changed

- Refreshed `orchestration/phase_programmes.md` so the recommended next
  planning move now reflects the current post-Sprint-118 state instead of stale
  H69/Sprint 97 wording.
- Recorded that the Ariadne/Fable strategy map has been created, stale worktree
  residue has been cleaned, and the provider-boundary guard stack has been
  consolidated.
- Refreshed the Programme 2G table to mark a checkpoint refresh due after
  Sprint 118, include Sprint 110-118 provider-boundary guard consolidation, and
  name the post-Sprint-118 API Spine checkpoint as the next candidate sprint.
- Added `tests/test_phase_programmes_current_checkpoint.py` to guard the current
  post-Sprint-118 guidance and prevent stale H69/Sprint 97 next-move wording
  from returning.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.
- DeepSeek Flash review found no blockers. Its Programme 2G table-refresh
  residual was folded into the sprint before closeout.

## Sprint 119 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_phase_programmes_current_checkpoint.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_phase_programmes_current_checkpoint.py -q`
  (`2 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check -- orchestration/phase_programmes.md tests/test_phase_programmes_current_checkpoint.py`.

Sprint engine state: continuing. Next recommended direction is Sprint 120:
run the compact post-Sprint-118 API Spine checkpoint comparing the existing ADR,
schema prototypes, and API steward skill against the provider-boundary guard
stack, then name the next implementation slice.

---

## Previous Closeout - Sprint 118

## Sprint 118 What Changed

- Updated `orchestration/bernie_release_gates.md` so the provider-boundary
  report's `proposal_citation_required_fields` list is named as the source of
  truth for provider-boundary proposal citations.
- Listed the current eight provider-boundary citation fields in the release-gate
  docs immediately before the proposal surface guard instructions.
- Strengthened `tests/test_bernie_interpretation_readiness_release_gate.py` so
  every field from `PROVIDER_BOUNDARY_PROPOSAL_CITATION_FIELDS` must appear in
  the release-gate docs as a backtick-wrapped field token.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.
- DeepSeek Flash review found no blockers. Its field-token residual was folded
  in by requiring backtick-wrapped field names in the docs test.

## Sprint 118 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_bernie_interpretation_readiness_release_gate.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_bernie_interpretation_readiness_release_gate.py tests/test_bernie_provider_boundary_readiness_report.py tests/test_bernie_interpretation_proposal_surface_guard.py -q`
  (`22 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check -- orchestration/bernie_release_gates.md tests/test_bernie_interpretation_readiness_release_gate.py`.

Sprint engine state: continuing. Next recommended direction is Sprint 119:
step back to the Ariadne/Fable strategy map and pick the next highest-leverage
programme checkpoint beyond provider-boundary guard consolidation.

---

## Previous Closeout - Sprint 117

## Sprint 117 What Changed

- Added `PROVIDER_BOUNDARY_PROPOSAL_CITATION_FIELDS` to
  `scripts/bernie_provider_boundary_readiness_report.py`.
- The provider-boundary readiness report now emits the static
  `proposal_citation_required_fields` list so proposal authors and guards can
  see which report fields must be cited.
- `assert_provider_boundary_report_safety()` now rejects citation-field-list
  drift, and the report test includes a negative drift case.
- Strengthened the proposal surface guard test so
  `PROVIDER_BOUNDARY_EXPECTED_VALUES` must have the same key set as the report's
  proposal-citation field contract and still match the actual report values.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.
- DeepSeek Flash review found no blockers. Residual risks are low and bounded:
  the report snapshot still intentionally pins `live_alias_count=4`, and the
  report retains its existing static imports of provider metadata modules.

## Sprint 117 Verification

- `.venv\Scripts\python.exe -m py_compile scripts\bernie_provider_boundary_readiness_report.py tests\test_bernie_provider_boundary_readiness_report.py tests\test_bernie_interpretation_proposal_surface_guard.py`.
- `.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_bernie_provider_boundary_readiness_report.py tests/test_bernie_interpretation_proposal_surface_guard.py -q`
  (`18 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check -- scripts/bernie_provider_boundary_readiness_report.py tests/test_bernie_provider_boundary_readiness_report.py tests/test_bernie_interpretation_proposal_surface_guard.py`.

Sprint engine state: continuing. Next recommended direction is Sprint 118:
move to the next Ariadne/Fable provider-boundary checkpoint, likely a small
proposal-doc or release-gate consolidation, unless a broader programme
checkpoint is now higher leverage.

---

## Previous Closeout - Sprint 116

## Sprint 116 What Changed

- Added a focused drift test tying
  `PROVIDER_BOUNDARY_EXPECTED_VALUES` in
  `scripts/bernie_interpretation_proposal_surface_guard.py` to the actual safe
  aggregate output of `build_provider_boundary_report()`.
- Scoped the provider-boundary report import inside the drift test so the wider
  report/app import path is not loaded at test collection time for the rest of
  the proposal surface guard suite.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.
- DeepSeek Flash review found no blockers. Its collection-time import residual
  was folded into the sprint. Remaining residual risk: the test intentionally
  checks only the explicit proposal-citation contract, not every field in the
  full provider-boundary report schema.

## Sprint 116 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_bernie_interpretation_proposal_surface_guard.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_bernie_interpretation_proposal_surface_guard.py tests/test_bernie_provider_boundary_readiness_report.py -q`
  (`17 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check -- tests/test_bernie_interpretation_proposal_surface_guard.py`.

Sprint engine state: continuing. Next recommended direction is Sprint 117:
either add a reverse/explicit proposal-citation field contract for the
provider-boundary report, or move to the next Ariadne/Fable provider-boundary
checkpoint if the current guard stack is sufficient.

---

## Previous Closeout - Sprint 115

## Sprint 115 What Changed

- Extended `scripts/bernie_interpretation_proposal_surface_guard.py` so
  provider-boundary proposal markdown must cite both:
  `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`
  and
  `.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py`.
- Provider-boundary proposal markdown must now include the existing blocked
  interpretation readiness values plus the provider-boundary blocked/static
  values: `default_provider=disabled`,
  `runtime_or_provider_wiring_ready=false`, `live_provider_enabled=false`,
  `provider_calls_performed=false`, `route_behavior_changed=false`,
  `database_access_performed=false`, `memory_or_rag_access_performed=false`,
  and `historical_diary_material_access_performed=false`.
- Added rejection/acceptance tests for provider-boundary proposal markdown.
- Upgraded `docs/bernie-band2-provider-gate-criteria.md` to satisfy the new
  provider-boundary guard.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.
- DeepSeek Flash review found no blockers and confirmed guard expected values
  match the current provider-boundary report output. Residual risk: this remains
  static text scanning, not proof that proposal authors actually reran the
  commands immediately before writing.

## Sprint 115 Verification

- `.venv\Scripts\python.exe -m py_compile scripts\bernie_interpretation_proposal_surface_guard.py tests\test_bernie_interpretation_proposal_surface_guard.py`.
- `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_guard.py docs\adversarial\h63_interpretation_independent_review_brief.md docs\bernie-band2-provider-gate-criteria.md`.
- `.venv\Scripts\python.exe -m pytest tests/test_bernie_interpretation_proposal_surface_guard.py tests/test_bernie_interpretation_readiness_release_gate.py -q`
  (`10 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check -- scripts/bernie_interpretation_proposal_surface_guard.py tests/test_bernie_interpretation_proposal_surface_guard.py docs/bernie-band2-provider-gate-criteria.md`.

Sprint engine state: continuing. Next recommended direction is Sprint 116:
consider an optional live-value verification mode for the proposal surface guard,
or move to the next Ariadne/Fable provider-boundary checkpoint if that would add
too much automation to proposal docs.

---

## Previous Closeout - Sprint 114

## Sprint 114 What Changed

- Updated `orchestration/bernie_release_gates.md` so any sprint proposing to
  enable, expand, alias, or dry-run a Bernie booking interpreter provider
  boundary must run and record:
  `.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py`.
- Documented the expected current blocked/static values:
  `default_provider=disabled`, `runtime_or_provider_wiring_ready=false`,
  `live_provider_enabled=false`, `provider_calls_performed=false`,
  `route_behavior_changed=false`, `database_access_performed=false`,
  `memory_or_rag_access_performed=false`, and
  `historical_diary_material_access_performed=false`.
- Strengthened `tests/test_bernie_interpretation_readiness_release_gate.py` so
  the release-gate docs must continue to cite the provider-boundary report and
  those expected blocked values.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.
- DeepSeek Flash review found no blockers. Residual risk matches the existing
  documentation-gate pattern: docs tests assert required text, while the actual
  command output must be run and recorded before provider-boundary proposals.

## Sprint 114 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_bernie_interpretation_readiness_release_gate.py`.
- `.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_bernie_interpretation_readiness_release_gate.py tests/test_bernie_provider_boundary_readiness_report.py -q`
  (`14 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check -- orchestration/bernie_release_gates.md tests/test_bernie_interpretation_readiness_release_gate.py`.

Sprint engine state: continuing. Next recommended direction is Sprint 115:
extend the proposal surface guard so provider-boundary proposal markdown must
cite both the existing interpretation readiness command and the provider-boundary
readiness report before review.

---

## Previous Closeout - Sprint 113

## Sprint 113 What Changed

- Added `scripts/bernie_provider_boundary_readiness_report.py`, an importable
  CLI helper that emits only safe aggregate/static provider-boundary posture.
- The report summarizes provider metadata counts, declared provider values,
  live alias count, canonical live-provider count, metadata uniqueness,
  schema-declared metadata posture, and disabled/fake/live allowlist posture.
- The report hard-codes and safety-asserts blocked runtime posture:
  `default_provider="disabled"`, `runtime_or_provider_wiring_ready=false`,
  `live_provider_enabled=false`, `provider_calls_performed=false`,
  `route_behavior_changed=false`, and no DB/memory/RAG/trove access.
- Added `tests/test_bernie_provider_boundary_readiness_report.py` covering the
  exact aggregate payload and fail-closed negative cases for opened posture,
  alias/metadata drift, and non-aggregate source.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.
- DeepSeek Flash review found no blockers. Residual constructor/import coupling
  risk is future-facing; current constructors are inert and provider eagerness
  remains guarded by the blocked runtime gate/isolation tests.

## Sprint 113 Verification

- `.venv\Scripts\python.exe -m py_compile scripts\bernie_provider_boundary_readiness_report.py tests\test_bernie_provider_boundary_readiness_report.py`.
- `.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_bernie_provider_boundary_readiness_report.py tests/test_bernie_provider_runtime_gate.py tests/test_bernie_interpret_booking_instruction.py -q`
  (`53 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check -- scripts/bernie_provider_boundary_readiness_report.py tests/test_bernie_provider_boundary_readiness_report.py`.

Sprint engine state: continuing. Next recommended direction is Sprint 114:
fold the provider-boundary readiness report into the existing Bernie readiness
command or release-gate docs so reviewers run one preflight before any
provider-boundary proposal.

---

## Previous Closeout - Sprint 112

## Sprint 112 What Changed

- Extended `tests/test_bernie_provider_runtime_gate.py` with provider metadata
  readiness invariants.
- Disabled and fake Bernie interpreters must keep `live_provider=false` and
  remain outside `LIVE_BERNIE_INTERPRETER_PROVIDERS`.
- The Gemini Vertex interpreter must keep `live_provider=true`, `mode="live"`,
  and a canonical provider value inside the live-provider allowlist.
- Every current live alias must resolve to the same canonical metadata provider.
- Current interpreter provider metadata values must be unique and declared by
  the response schema.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.
- DeepSeek Flash review found no blockers. Its metadata-uniqueness residual
  risk was folded into the sprint before closeout.

## Sprint 112 Verification

- `.venv\Scripts\python.exe -m py_compile tests\test_bernie_provider_runtime_gate.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_bernie_provider_runtime_gate.py tests/test_bernie_interpret_booking_instruction.py -q`
  (`43 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check -- tests/test_bernie_provider_runtime_gate.py`.

Sprint engine state: continuing. Next recommended direction is Sprint 113:
add a lightweight provider-boundary readiness report or static check that
summarizes disabled/fake/live provider posture for reviewers, still
blocked/default-disabled and without live calls or route behavior changes.

---

## Previous Closeout - Sprint 111

## Sprint 111 What Changed

- Updated `get_booking_instruction_interpreter()` so live Bernie provider
  aliases are resolved through `LIVE_BERNIE_INTERPRETER_PROVIDERS` from
  `app/config.py` instead of a duplicated inline set.
- Extended `tests/test_bernie_provider_runtime_gate.py` so every live alias
  resolves to `GeminiVertexBookingInstructionInterpreter`, while `fake`,
  `disabled`, and unknown provider names remain local/disabled.
- Added a static route guard proving
  `interpret_bernie_booking_instruction()` obtains its provider through
  `settings.bernie_booking_interpreter_provider` plus
  `get_booking_instruction_interpreter()` and does not hardcode live provider
  names or the live provider class.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.
- DeepSeek Flash review found no blockers. Residual risks are future-facing:
  textual source guards may need refactoring if the route wrapper changes, and
  a future second live provider should introduce a richer provider registry.

## Sprint 111 Verification

- `.venv\Scripts\python.exe -m py_compile app\services\bernie_booking_interpreter.py tests\test_bernie_provider_runtime_gate.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_bernie_provider_runtime_gate.py tests/test_bernie_interpret_booking_instruction.py -q`
  (`40 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check -- app/services/bernie_booking_interpreter.py tests/test_bernie_provider_runtime_gate.py`.

Sprint engine state: continuing. Next recommended direction is Sprint 112:
add a provider-boundary audit/readiness invariant for future multi-provider
growth, still blocked/default-disabled and without live calls or route behavior
changes.

---

## Previous Closeout - Sprint 110

## Sprint 110 What Changed

- Added `LIVE_BERNIE_INTERPRETER_PROVIDERS` and
  `assert_bernie_provider_allowed_by_runtime_gate()` in `app/config.py`.
- `Settings` now fails closed at startup if
  `BERNIE_BOOKING_INTERPRETER_PROVIDER` is configured to a live Bernie
  interpreter provider while
  `docs/bernie-interpretation-harness-runtime-gate.json` remains blocked or
  lacks explicit provider scope.
- Covered the current live alias family accepted by the interpreter:
  `gemini`, `gemini_vertex`, `vertex`, and `vertex_gemini`.
- Preserved fake/default-disabled behavior; no route behavior change, provider
  call, live smoke, runtime FGA client, external patient client, GraphQL
  mutation, H15/H-series runtime import, memory/RAG/GraphRAG, broad trove
  mining, or model-to-database write was added.
- DeepSeek Flash review found no blockers on the initial guard and noted the
  live-provider allowlist drift risk; Ariadne fixed that by adding alias
  coverage before closeout.

## Sprint 110 Verification

- `.venv\Scripts\python.exe -m py_compile app\config.py tests\test_bernie_provider_runtime_gate.py`.
- `.venv\Scripts\python.exe -m pytest tests/test_bernie_provider_runtime_gate.py tests/test_bernie_interpretation_runtime_gate.py tests/test_bernie_interpretation_runtime_gate_check.py tests/test_bernie_interpret_booking_instruction.py -q`
  (`48 passed`; existing Starlette/Google GenAI warnings only).
- `git diff --check -- app/config.py tests/test_bernie_provider_runtime_gate.py`.

Sprint engine state: continuing. Next recommended direction is Sprint 111: add
a broader static route/config drift guard that proves all Bernie interpreter
live-provider entry points remain covered by the startup gate and fake/disabled
route behavior remains provider-free.

---

## Previous Closeout - Sprint 109

## Sprint 109 What Changed

- Added `docs/bernie-band2-provider-gate-criteria.md`, a proposal-only gate
  checkpoint artifact.
- Captured Claude's Sprint 109 criteria plan in
  `orchestration\agent_inbox\codex\plan-claude-claude-sprint109-band2-provider-gate-criteria.md`.
- Captured Antigravity's Sprint 109 UX readiness plan in
  `orchestration\agent_inbox\codex\plan-antigravity-antigravity-sprint109-live-smoke-ux-readiness.md`.
- Captured DeepSeek Flash's adversarial provider-gate review in
  `orchestration\agent_inbox\codex\review-deepseek-sprint109-provider-gate-adversarial-review.md`.
- Defined the future approval payload shape, blocking criteria, staff UX
  criteria, and non-approval statement for any future runtime-provider or
  no-write live-smoke movement.
- No provider was enabled. No live call, runtime FGA client, external patient
  client, GraphQL mutation, route/model/schema/UI behavior change, broad trove
  mining, H15/H-series runtime import, memory/RAG/GraphRAG, database write from
  model output, or raw/ignored local-data read was added.

## Sprint 109 Verification

- `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_guard.py docs\bernie-band2-provider-gate-criteria.md`.
- `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`.
- `git diff --check` for Sprint 109 artifacts.

Sprint engine state: continuing. Next recommended direction is Sprint 110:
add a provider-gate runtime/startup assertion or health-check test that fails
closed if live-provider configuration appears while the gate decision remains
`blocked`, without enabling providers or changing route behavior.

---

## Previous Closeout - Sprint 108

## Sprint 108 What Changed

- Corrected the active chronology: the Bernie interpreter Access AI migration is
  Sprint 108 in the current Ariadne/Fable map. Older Access AI design notes may
  call the same item "Sprint 85", but future current-track references should not
  restart there.
- Checked worker availability at sprint start:
  - Claude CLI was available and submitted a backend plan.
  - Antigravity CLI was available and submitted the UX implementation.
  - DeepSeek Flash was used as the backend hardening lane.
- Claude's accepted plan found that the main migration already existed:
  `GeminiVertexBookingInstructionInterpreter` invokes `AccessAiService`, the
  route persists Access AI audit events, and fake/disabled paths remain local.
  Claude stood down from implementation after DeepSeek covered the focused test
  gaps, avoiding same-file worker overlap.
- DeepSeek/Ariadne backend hardening added tests that prove:
  - live-provider audit metadata excludes forbidden key fragments and raw
    instruction text;
  - the route does not import or call `AccessAiService` directly;
  - disabled and fake interpreters do not emit Access AI audit events;
  - provider-exception fallback persists only Access AI allowed/failed events;
  - provider-exception fallback does not write appointments or appointment audit
    rows.
- Antigravity UX acceptance added honest debug metadata:
  `Provider: fake (mode: mocked; live_provider: false)` and
  `Provider: gemini_vertex (mode: live; live_provider: true)`, plus
  route-intercepted smoke coverage and a `diary.js` cache-bust.
- No live provider default was enabled. No runtime FGA client, external patient
  client, GraphQL mutation, broad trove mining, H15/H-series runtime import,
  memory/RAG/GraphRAG, database write from model output, or raw/ignored
  local-data read was added.

## Sprint 108 Verification

- `.venv\Scripts\python.exe -m pytest tests/test_bernie_interpret_booking_instruction.py -q`
  (`29 passed`; existing Starlette/Google GenAI warnings only).
- `.venv\Scripts\python.exe -m pytest tests/test_access_ai_service.py tests/test_ai_audit_events.py tests/test_smoke_bernie_interpreter_script.py -q`
  (`46 passed`; existing Starlette/Google GenAI warnings only).
- `node --check docs\diary\diary.js`.
- `.venv\Scripts\python.exe -m pytest review/test_diary_smoke.py -k test_bernie_debug_provider_metadata_honest -q`
  (`2 passed`).
- `git diff --check` passed after integration hygiene.

Sprint engine state: continuing. Next recommended direction is Sprint 109
Band-2 checkpoint/gate proposal before any runtime-provider or live-smoke
movement. Continue no-runtime, no-provider-enabling work autonomously, but pause
for Yuri before changing blocked gates to enabled.

---

## Previous Batch Context

- Captured Fable's 100+ sprint strategy review at
  `orchestration\agent_inbox\codex\review-claude-fable-100-sprint-strategy-map.md`.
- Added Ariadne's durable synthesis at
  `orchestration\ariadne_fable_100_sprint_strategy_map.md`.
- Updated planning docs so the next arc is explicit: close the Bernie/API-spine/
  Access-AI consumer gap before adding more provider-free harness guardrails.
- Performed bounded inbox hygiene by marking historically integrated/superseded
  R27-R30, D1, D8, K1/K1b, R1, Sprint 105/107, and related review packets from
  the integration ledger.
- Launched three parallel Sprint 98 worker lanes:
  - backend/API confirm contract;
  - Diary UI/review harness;
  - smoke/release-gate evidence.
- Integrated the Sprint 98 backend changes:
  - malformed `confirm-bernie` payloads now return a typed blocked Bernie
    confirmation envelope instead of raw validation copy;
  - stale/tampered confirm payloads surface precise entity blocks such as
    `practitioner_not_found` before revalidation;
  - the missing-practitioner selection copy no longer exposes raw
    `practitioner_id` wording.
- Integrated the Sprint 98 Diary UI/review changes:
  - ordinary staff-facing Bernie block copy now scrubs raw internal identifiers,
    snake_case fragments, UUID-like values, and bare `Not Found`;
  - route-intercepted smoke coverage proves candidate selection, choose-another
    slot affordance, configured confirm endpoint use, and ordinary-copy
    redaction.
- Integrated smoke/release-gate evidence:
  - ordinary Margaret Thompson / Dr Shera prompt evidence now checks 14:00-15:45
    parsing, fake/mocked provider labeling, `live_provider=false`, and compact
    redaction.
- No live providers, broad historical diary mining, H15/H-series runtime imports,
  memory/RAG/GraphRAG wiring, database writes from model output, or raw/ignored
  local-data reads were added.
- Synthesised the three API root-to-branch planning lanes into
  `orchestration\api_spine_adr.md`.
- Added Sprint 101 non-invasive API Spine prototype artifacts:
  - `docs\api-spine\graphql\appointment-diary-read.graphql`;
  - `docs\api-spine\openapi\appointment-commands.yaml`;
  - `docs\api-spine\manifests\agent-capability-charters.yaml`;
  - `docs\api-spine\manifests\practice-onboarding-example.yaml`;
  - `docs\api-spine\async\integration-events.yaml`;
  - `docs\api-spine\security\permission-matrix.yaml`;
  - `tests\test_api_spine_artifacts.py`.
- Created and validated personal Codex skill `$emr4-api-steward` at
  `C:\Users\sarashera\.codex\skills\emr4-api-steward` for future API-spine
  review/design/implementation consistency checks.
- Verified the existing Access AI invocation service as the fake-provider
  backend choke point and repaired its test harness so it no longer depends on
  `pytest-asyncio`.
- Hardened the Access AI cost/audit envelope:
  - `AiCostEnvelope.audit_metadata()` now emits deterministic budget posture
    fields: `budget_limit_present`, `budget_threshold_ratio`, and
    `budget_warning`;
  - adversarial tests prove blocked entitlement variants, blocked estimate-cost
    calls, dry-run calls, provider failures, capped capability metadata, and
    PHI-like request metadata all preserve audit-safety and do not open provider
    calls when blocked.
- Integrated Sprint 84 enterprise-auth/FGA boundary mapping:
  - added `docs\access-ai-enterprise-auth-fga-boundary.md`;
  - added static FGA-like external attribute mapping into EMR4-owned
    `AiAccessRole` values without runtime FGA clients;
  - fail-closed filtering prevents misconfigured external mappings from
    emitting arbitrary role strings;
  - API Spine permission-matrix guards now require enterprise-auth/FGA to remain
    `static_mapping_only` and keep runtime FGA clients, live providers, external
    patient clients, GraphQL mutations, memory/RAG/GraphRAG, H15/trove access,
    and model-to-database writes denied.
- Protocol correction: Sprint 84 completed with native Codex subagents already
  assigned before Yuri corrected the worker-lane interpretation. Future
  non-trivial sprints must start with Claude and Antigravity availability checks
  and use Claude + Antigravity + DeepSeek Flash as the preferred three-lane mix;
  native Codex subagents are fallback/integration helpers, not the default
  meaning of "three lane sprint".

## Larger Plan Position

This batch sits in Phase 2B / Bernie Receptionist Copilot, Programme 2G / EMR4
API Spine, Programme 2F / Access AI API, and Programme 2C / Ariadne Tooling and
Review Automation. It was a strategy-and-launch batch plus concrete Sprint 98,
Sprint 99/100, and Sprint 101 increments. Its size was appropriate because the
strategy map identified the consumer gap, bounded cleanup restored enough
orchestration signal to proceed, Sprint 98's three blockers split cleanly across
backend/UI/smoke lanes, and the API Spine work split cleanly into plan review,
ADR synthesis, non-invasive schema artifacts, API stewardship, and Access AI
fake-provider hardening, and Sprint 84 static enterprise-auth/FGA boundary
mapping. The next planned step is Sprint 108 Bernie interpreter migration
through Access AI while preserving fake-provider/default-disabled/no-write
behavior. Older Access AI design notes call this "Sprint 85"; current chronology
should use Sprint 108 unless Sprint 98 live/manual review finds a release
blocker first.

## Verification

- Compile check passed:
  `.venv\Scripts\python.exe -m py_compile app\routers\appointments.py tests\test_bernie_sprint98_confirm_contract.py tests\test_bernie_sprint98_release_gates.py tests\test_bernie_sprint97_interpreter_readiness.py tests\test_smoke_bernie_interpreter_script.py`.
- JS syntax check passed:
  `node --check docs\diary\diary.js`.
- Focused backend/smoke pytest passed:
  `.venv\Scripts\python.exe -m pytest tests/test_bernie_sprint98_confirm_contract.py tests/test_bernie_sprint98_release_gates.py tests/test_bernie_sprint97_interpreter_readiness.py tests/test_smoke_bernie_interpreter_script.py -q`
  (`41 passed`; existing Starlette/Google GenAI warnings only).
- Route-intercepted Diary review pytest passed:
  `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q -k "bernie_review_candidate_selection or bernie_choose_different_time_restores_candidates or bernie_generic_confirm_not_found_calm_copy or sprint98_ordinary_block_copy_scrubs_raw_booking_internals or bernie_route_intercepted_confirm_flow_harness_success"`
  (`6 passed`).
- `git diff --check` passed with line-ending warnings only on existing CRLF
  files touched by status cleanup and Sprint 98 tests.
- API Spine artifact compile/test passed:
  `.venv\Scripts\python.exe -m py_compile tests\test_api_spine_artifacts.py`
  and `.venv\Scripts\python.exe -m pytest tests\test_api_spine_artifacts.py -q`
  (`28 passed`; existing Starlette/Google GenAI warnings only).
- Artifact diff hygiene passed:
  `git diff --check -- docs/api-spine tests/test_api_spine_artifacts.py orchestration/api_spine_adr.md`.
- Access AI invocation service compile/test passed:
  `.venv\Scripts\python.exe -m py_compile tests\test_access_ai_service.py app\services\ai\access_service.py`
  and `.venv\Scripts\python.exe -m pytest tests/test_access_ai_service.py tests/test_ai_audit_events.py tests/test_ai_costing.py tests/test_ai_entitlements.py tests/test_ai_capability_registry.py -q`
  (`33 passed`; existing Starlette/Google GenAI warnings only).
- Access AI audit/cost hardening compile/test passed:
  `.venv\Scripts\python.exe -m py_compile app\services\ai\access_service.py app\services\ai\costing.py app\services\ai\audit_events.py tests\test_access_ai_service.py tests\test_ai_costing.py tests\test_ai_audit_events.py`
  and `.venv\Scripts\python.exe -m pytest tests/test_access_ai_service.py tests/test_ai_audit_events.py tests/test_ai_costing.py tests/test_ai_entitlements.py tests/test_ai_capability_registry.py -q`
  (`61 passed`; existing Starlette/Google GenAI warnings only).
- Access AI patch diff hygiene passed:
  `git diff --check -- app/services/ai/costing.py tests/test_access_ai_service.py tests/test_ai_costing.py tests/test_ai_audit_events.py`
  with known CRLF notices on touched test files.
- Sprint 84 enterprise-auth/FGA compile/test passed:
  `.venv\Scripts\python.exe -m py_compile app\services\ai\external_identity.py tests\test_ai_external_identity.py tests\test_ai_entitlements.py tests\test_access_ai_service.py tests\test_api_spine_artifacts.py`
  and `.venv\Scripts\python.exe -m pytest tests/test_ai_external_identity.py tests/test_ai_entitlements.py tests/test_access_ai_service.py tests/test_api_spine_artifacts.py -q`
  (`64 passed`; existing Starlette/Google GenAI warnings only).
- Sprint 84 diff hygiene passed:
  `git diff --check -- app/services/ai/external_identity.py tests/test_ai_external_identity.py docs/access-ai-enterprise-auth-fga-boundary.md docs/api-spine/security/permission-matrix.yaml tests/test_api_spine_artifacts.py`.

Sprint engine state: continuing locally. Next recommended direction is Sprint
108 Bernie interpreter migration through Access AI, fake-provider and
default-disabled only, with runtime FGA clients, live-provider, trove,
H15/H-series runtime import, memory/RAG/GraphRAG, GraphQL mutation, external
patient-client, and model-write gates still blocked.

---

## Previous Closeout

- Added `scripts\bernie_interpretation_proposal_surface_guard.py`, a reusable
  markdown guard for runtime/provider/trove proposal artifacts.
- Added `tests\test_bernie_interpretation_proposal_surface_guard.py`.
- Updated `orchestration\bernie_release_gates.md` so future interpretation
  runtime/provider/trove proposals must run the guard and include readiness
  command evidence plus blocked expected values.
- Updated `docs\bernie-interpretation-harness-scaffold.md`, `AGENTS.md`,
  `orchestration\parallel_workstreams.md`, and
  `orchestration\integration_log.md`.
- No runtime routes, UI, providers, database access, memory/RAG/GraphRAG,
  H15/H-series runtime imports, raw trove reads, or ignored local-data reads
  were added.

## Verification

- Compile check passed:
  `.venv\Scripts\python.exe -m py_compile scripts\bernie_interpretation_proposal_surface_guard.py tests\test_bernie_interpretation_proposal_surface_guard.py`.
- Proposal guard CLI passed:
  `.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_guard.py docs\adversarial\h63_interpretation_independent_review_brief.md`.
- Focused pytest passed:
  `.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_proposal_surface_guard.py tests\test_bernie_interpretation_readiness_release_gate.py tests\test_bernie_interpretation_h64_review_artifact.py -q`
  (`10 passed`; existing deprecation warnings only).
- Readiness CLI sample passed:
  `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`.
- Leakage lint passed:
  `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- `git diff --check` passed with the known CRLF warning on
  `orchestration/integration_log.md`.

---

## Previous Closeout

- Updated `scripts\bernie_interpretation_harness_report.py` so report safety
  derives forbidden report text from every committed fixture `utterance` in the
  active fixture directory.
- Updated `scripts\bernie_interpretation_readiness_check.py` so custom fixture
  directories flow into the report-safety assertion.
- Added a focused synthetic test proving a newly authored fixture utterance is
  automatically rejected if it appears in an aggregate report.
- Updated `docs\bernie-interpretation-harness-scaffold.md`, `AGENTS.md`,
  `orchestration\parallel_workstreams.md`, and
  `orchestration\integration_log.md`.
- No runtime routes, UI, providers, database access, memory/RAG/GraphRAG,
  H15/H-series runtime imports, raw trove reads, or ignored local-data reads
  were added.

## Verification

- Compile check passed:
  `.venv\Scripts\python.exe -m py_compile scripts\bernie_interpretation_harness_report.py scripts\bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_harness_report.py`.
- Report CLI passed:
  `.venv\Scripts\python.exe scripts\bernie_interpretation_harness_report.py`.
- Readiness CLI sample passed:
  `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`.
- Leakage lint passed:
  `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- Focused pytest passed:
  `.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness_report.py tests\test_bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_readiness_snapshot.py tests\test_bernie_interpretation_h64_review_artifact.py -q`
  (`26 passed`; existing deprecation warnings only).
- `git diff --check` passed with the known CRLF warning on
  `orchestration/integration_log.md`.

---

## Previous Closeout

- Updated `app\services\bernie\interpretation_harness.py` so
  `interpretation_result_to_frame()` validates each input result and each
  projected frame before returning.
- Tightened clarification frame consistency so exactly one subtype is active:
  patient-context clarification or reason-code clarification.
- Added tests rejecting mixed clarify frames and inconsistent projection inputs.
- Updated `docs\bernie-interpretation-harness-scaffold.md`, `AGENTS.md`,
  `orchestration\parallel_workstreams.md`, and
  `orchestration\integration_log.md`.
- No runtime routes, UI, providers, database access, memory/RAG/GraphRAG,
  H15/H-series runtime imports, raw trove reads, or ignored local-data reads
  were added.

## Verification

- Compile check passed:
  `.venv\Scripts\python.exe -m py_compile app\services\bernie\interpretation_harness.py tests\test_bernie_interpretation_harness.py`.
- Readiness CLI sample passed:
  `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`.
- Leakage lint passed:
  `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- Focused pytest passed:
  `.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_interpretation_h64_review_artifact.py tests\test_bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_readiness_snapshot.py tests\test_bernie_interpretation_runtime_gate_check.py -q`
  (`245 passed`; existing deprecation warnings only).
- `git diff --check` passed with the known CRLF warning on
  `orchestration/integration_log.md`.

---

## Previous Closeout

- Updated `scripts\bernie_interpretation_runtime_gate_check.py` so runtime-gate
  status derives `runtime_or_provider_wiring_ready` and
  `raw_trove_access_ready` from named gate scope keys.
- Updated `scripts\bernie_interpretation_readiness_check.py` so combined
  readiness consumes those derived gate-status fields instead of standalone
  constants.
- Added focused tests proving gate-status derivation and combined-readiness
  consumption.
- Updated `docs\bernie-interpretation-harness-scaffold.md`, `AGENTS.md`,
  `orchestration\parallel_workstreams.md`, and
  `orchestration\integration_log.md`.
- No runtime routes, UI, providers, database access, memory/RAG/GraphRAG,
  H15/H-series runtime imports, raw trove reads, or ignored local-data reads
  were added.

## Verification

- Compile check passed:
  `.venv\Scripts\python.exe -m py_compile scripts\bernie_interpretation_runtime_gate_check.py scripts\bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_runtime_gate_check.py tests\test_bernie_interpretation_readiness_check.py`.
- Runtime gate CLI passed:
  `.venv\Scripts\python.exe scripts\bernie_interpretation_runtime_gate_check.py`.
- Readiness CLI sample passed:
  `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`.
- Focused pytest passed:
  `.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_runtime_gate_check.py tests\test_bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_readiness_snapshot.py tests\test_bernie_interpretation_runtime_gate.py tests\test_bernie_interpretation_h64_review_artifact.py tests\test_bernie_interpretation_harness_report.py -q`
  (`35 passed`; existing deprecation warnings only).
- Leakage lint passed:
  `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- `git diff --check` passed with the known CRLF warning on
  `orchestration/integration_log.md`.

---

## Previous Closeout

- Integrated a read-only DeepSeek Flash adversarial review in `docs\adversarial\h64_interpretation_readiness_independent_review.md`.
- Added `tests\test_bernie_interpretation_h64_review_artifact.py` to preserve the no-critical/high verdict, blocked runtime/provider/trove boundary, and H65-H67 follow-up sequence.
- Updated `docs\bernie-interpretation-harness-scaffold.md`, `AGENTS.md`, `orchestration\parallel_workstreams.md`, and `orchestration\integration_log.md`.
- The review accepted three medium hardening follow-ups: derive readiness booleans from runtime-gate scope, add more mechanical readiness-command enforcement before runtime/provider/trove proposals, and make interpretation result/frame helpers self-validating.
- No runtime routes, UI, providers, database access, memory/RAG/GraphRAG, H15/H-series runtime imports, raw trove reads, or ignored local-data reads were added.

## Verification

- Compile check passed:
  `.venv\Scripts\python.exe -m py_compile tests\test_bernie_interpretation_h64_review_artifact.py`.
- Readiness CLI sample passed:
  `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`.
- Leakage lint passed:
  `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- Focused pytest passed:
  `.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_h64_review_artifact.py tests\test_bernie_interpretation_independent_review_brief.py tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_readiness_release_gate.py tests\test_bernie_interpretation_readiness_review_artifact.py tests\test_bernie_interpretation_readiness_snapshot.py tests\test_bernie_interpretation_runtime_gate.py tests\test_bernie_interpretation_runtime_gate_check.py tests\test_bernie_interpretation_runtime_isolation.py tests\test_bernie_interpretation_protocol_alert.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q`
  (`306 passed`; existing deprecation warnings only).
- `git diff --check` passed with the known CRLF warning on
  `orchestration/integration_log.md`.

---

## Previous Closeout

- Added `docs\adversarial\h63_interpretation_independent_review_brief.md`, a bounded source-safe handoff for a future independent review of the Bernie Interpretation Harness readiness/gate stack.
- Added `tests\test_bernie_interpretation_independent_review_brief.py` to require the readiness preflight, blocked expected values, review-artifact-only output, and explicit out-of-scope runtime/provider/trove boundaries.
- Added a protocol alert explicitly preventing Ariadne-only sprint drift except for tiny coupled guardrails, mechanical docs, or urgent hotfixes.
- Updated `docs\bernie-interpretation-harness-scaffold.md`, `AGENTS.md`, `orchestration\parallel_workstreams.md`, and `orchestration\integration_log.md`.
- No runtime routes, UI, providers, database access, memory/RAG/GraphRAG, H15/H-series runtime imports, raw trove reads, or ignored local-data reads were added.

## Verification

- Compile check passed:
  `.venv\Scripts\python.exe -m py_compile tests\test_bernie_interpretation_independent_review_brief.py tests\test_bernie_interpretation_protocol_alert.py`.
- Readiness CLI sample passed:
  `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`.
- Leakage lint passed:
  `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- Focused pytest passed:
  `.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_independent_review_brief.py tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_readiness_release_gate.py tests\test_bernie_interpretation_readiness_review_artifact.py tests\test_bernie_interpretation_readiness_snapshot.py tests\test_bernie_interpretation_runtime_gate.py tests\test_bernie_interpretation_runtime_gate_check.py tests\test_bernie_interpretation_runtime_isolation.py tests\test_bernie_interpretation_protocol_alert.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q`
  (`303 passed`; existing deprecation warnings only).
- `git diff --check` passed with the known CRLF warning on
  `orchestration/integration_log.md`.

---

## Previous Closeout

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
- Added `tests\h15_advisory_adapter.py`.
- Added `tests\test_historical_diary_advisory_adapter.py`.
- Added `docs\historical-diary-trove-h15-advisory-adapter-proposal.md`.
- Added `tests\test_historical_diary_route_explanation_boundary.py`.
- Added `docs\historical-diary-trove-h15-route-explanation-boundary.md`.
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
- H32 leakage lint passed: `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- H32 advisory/boundary pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_advisory_adapter.py tests\test_practice_knowledge_advisory_boundary.py tests\test_historical_diary_memory_boundary.py tests\test_h15_semantic_candidate_fixtures.py -q` (42 passed).
- H33 leakage lint passed: `.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs`.
- H33 route/advisory boundary pytest passed: `.venv\Scripts\pytest.exe tests\test_historical_diary_route_explanation_boundary.py tests\test_historical_diary_advisory_adapter.py tests\test_practice_knowledge_advisory_boundary.py tests\test_historical_diary_memory_boundary.py tests\test_h15_semantic_candidate_fixtures.py -q` (44 passed).

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
- H32 proves, in tests only, that H15 candidates can become advisory-only practice knowledge and Bernie advisory frames without authority over slots, policy, confirmation, or writes.
- H33 proves those advisory frames remain read-only at the reception context and current API routers do not import H15 candidate material.

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

- Consider an explicit read-only explanation endpoint/test harness, still without provider/memory integration.
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

---

## Sprint H34 Closeout - H15 Read-Only Explanation Preview

Integrated outcome:

- Added `GET /api/v1/appointments/dev/h15-read-only-explanation-preview` as a
  dev-only/auth-gated static boundary preview in `app/routers/bernie_dev.py`.
- Added route tests proving the preview is advisory/read-only, blocked outside
  dev, auth-gated, and writes no appointment or audit rows.
- Documented that the endpoint does not authorize H15 runtime fixture imports,
  provider calls, Access AI/RAG/GraphRAG/memory, diary writes, or broad full
  trove processing.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile app\routers\bernie_dev.py tests\test_bernie_dev_fixtures.py tests\test_historical_diary_route_explanation_boundary.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_dev_fixtures.py tests\test_historical_diary_route_explanation_boundary.py tests\test_historical_diary_advisory_adapter.py tests\test_practice_knowledge_advisory_boundary.py tests\test_historical_diary_memory_boundary.py tests\test_h15_semantic_candidate_fixtures.py -q
git diff --check
```

Result: `65 passed`; leakage lint safe; whitespace check clean.

Sprint engine state: continuing. No user intervention is required; recommended
next direction is either tightening no-provider/no-write dev route contracts or
returning to native Bernie/Diary grammar coverage.

---

## Sprint H35 Closeout - Action-Grammar Replay Fixture Schema

Integrated outcome:

- Hardened `tests/action_grammar_replay/loader.py` with allowlisted top-level
  and per-action keys for authored synthetic replay fixtures.
- Added negative tests rejecting payload-like action fields such as `payload`,
  `endpoint`, and identity keys before they can become route or evidence
  scaffolding.
- Preserved the replay harness as grammar-shape evidence only: no routes, UI,
  providers, database writes, raw trove files, ignored local payloads, H-series
  profile consumption, H15 runtime wiring, RAG, GraphRAG, or memory.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile tests\action_grammar_replay\loader.py tests\action_grammar_replay\test_grammar_replay.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\action_grammar_replay\test_grammar_replay.py tests\test_diary_action_grammar.py tests\test_h15_semantic_candidate_fixtures.py -q
git diff --check
```

Result: `50 passed`; leakage lint safe; whitespace check clean.

Sprint engine state: continuing. No user intervention is required; recommended
next direction is further native Bernie/Diary grammar coverage, with broader
route-contract review only if drift appears.

---

## Sprint H36 Closeout - Native Diary Action Alias Coverage

Integrated outcome:

- Added a parametrized public action-name alias matrix for every current native
  Diary grammar verb.
- Added explicit coverage for planned aliases `check_in`, `waiting_area_move`,
  and `link_patient`: they resolve to confirm-tier mutating descriptors but
  remain `implemented=False` with no confirm actions.
- Kept the change tests-only: no routes, UI, providers, database writes,
  local trove processing, H-series profile consumption, H15 runtime wiring,
  RAG, GraphRAG, or memory.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile tests\test_diary_action_grammar.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_diary_action_grammar.py tests\action_grammar_replay\test_grammar_replay.py tests\test_h15_semantic_candidate_fixtures.py -q
git diff --check
```

Result: `71 passed`; leakage lint safe; whitespace check clean.

Sprint engine state: continuing. No user intervention is required; recommended
next direction is additional native Bernie/Diary grammar coverage unless a
route-contract drift risk appears.

---

## Sprint H37 Closeout - Grammar-To-Route Contract Inventory

Integrated outcome:

- Added `app/services/diary/action_route_contract.py`, a pure static inventory
  mapping every `DiaryActionVerb` to current route authority:
  `signed_confirm`, `read_only`, `meta`, or `planned_not_implemented`.
- Added tests proving implemented confirm verbs map to existing
  `DiaryConfirmAction` endpoints.
- Proved adjacent planned surfaces such as check-in defaults, status proposals,
  and waiting-area proposals do not make `check_in`, `waiting_area_move`, or
  `link_patient` executable.
- Documented the route-contract boundary in `docs/diary-action-route-contract.md`.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile app\services\diary\action_route_contract.py tests\test_diary_action_route_contract.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_contract.py tests\test_diary_action_grammar.py tests\action_grammar_replay\test_grammar_replay.py -q
git diff --check
```

Result: `75 passed`; leakage lint safe; whitespace check clean.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is H38 read-only vs mutating route boundary tests.

---

## Sprint H38 Closeout - Read-Only Vs Mutating Route Boundary

Integrated outcome:

- Extended `tests/test_diary_action_route_contract.py` with route-boundary
  checks over the H37 static contract.
- Read-only/meta contracts now fail if they point at proposal, confirm, or raw
  mutation route surfaces.
- Implemented mutating contracts must retain proposal and signed-confirm routes
  instead of relying only on raw mutation routes.
- Planned mutating contracts may document adjacent read/proposal surfaces, but
  must not carry confirm or raw mutation route authority.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile tests\test_diary_action_route_contract.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_contract.py tests\test_diary_action_grammar.py -q
git diff --check
```

Result: `64 passed`; leakage lint safe; whitespace check clean.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is H39 planned action promotion checklist.

---

## Sprint H39 Closeout - Planned Action Promotion Checklist

Integrated outcome:

- Added `app/services/diary/planned_action_promotion.py`, a static checklist
  for promoting planned grammar verbs.
- Covered `check_in`, `waiting_area_move`, and `link_patient`.
- Required every promotion to satisfy route contract, signed confirm action,
  signed evidence, audit contract, staff confirmation affordance, role/tenancy
  policy, UI affordance, and regression tests.
- Added tests proving the planned verbs remain non-executable until promoted:
  no confirm actions, no confirm routes, and no raw mutation route authority.
- Documented the checklist in `docs/diary-planned-action-promotion-checklist.md`.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile app\services\diary\planned_action_promotion.py tests\test_diary_planned_action_promotion.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_diary_planned_action_promotion.py tests\test_diary_action_route_contract.py tests\test_diary_action_grammar.py -q
git diff --check
```

Result: `71 passed`; leakage lint safe; whitespace check clean.

Sprint engine state: continuing. No user intervention is required; Yuri approved
continuing past H39 into Bernie Interpretation Harness sprints.

---

## Sprint H40 Closeout - Provider-Free Bernie Interpretation Harness

Integrated outcome:

- Added `app/services/bernie/interpretation_harness.py`, a deterministic
  provider-free scaffold mapping authored synthetic receptionist utterances to
  native `DiaryActionVerb` decisions.
- Added authored synthetic fixtures under
  `tests/fixtures/bernie_interpretation_harness/`.
- Added tests proving expected dispatch labels for read-only, signed-confirm,
  meta, planned-not-implemented, and unknown utterances.
- Guarded the harness against provider, route, DB, memory, H15, H-series, and
  local diary coupling.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile app\services\bernie\interpretation_harness.py tests\test_bernie_interpretation_harness.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_diary_action_route_contract.py tests\test_diary_action_grammar.py -q
git diff --check
```

Result: `82 passed`; leakage lint safe; whitespace check clean.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is adversarial synthetic utterance coverage for the
provider-free interpretation harness.

---

## Sprint H41 Closeout - Adversarial Interpretation Harness Coverage

Integrated outcome:

- Added `refuse_unsafe_instruction` dispatch to the provider-free Bernie
  interpretation harness.
- Added adversarial authored fixtures for provider/LLM injection, endpoint
  spoofing, direct DB/raw-write wording, no-confirmation wording, and mixed
  planned-action phrases.
- Unsafe wording is refused before grammar matching.
- Mixed planned-action phrases remain planned rather than falling through to
  implemented mutating verbs.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile app\services\bernie\interpretation_harness.py tests\test_bernie_interpretation_harness.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_diary_action_route_contract.py tests\test_diary_action_grammar.py -q
git diff --check
```

Result: `89 passed` after correcting the static provider-coupling scan to allow
provider names inside refusal regexes; leakage lint safe; whitespace check clean.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is harness result invariants.

---

## Sprint H42 Closeout - Interpretation Harness Result Invariants

Integrated outcome:

- Added `assert_interpretation_result_consistency()` to the provider-free
  Bernie interpretation harness.
- Applied result invariants across all authored normal/adversarial fixtures.
- Added negative tests for impossible result shapes.
- Dispatch and authority now stay aligned: confirm requires signed-confirm,
  read-only requires read-only, meta requires meta, planned refusal requires
  planned authority, and unsafe/unknown refusals carry no verb or authority.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile app\services\bernie\interpretation_harness.py tests\test_bernie_interpretation_harness.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_diary_action_route_contract.py tests\test_diary_action_grammar.py -q
git diff --check
```

Result: `91 passed`; leakage lint safe; whitespace check clean.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is fake-provider frame-shape preparation for the
interpretation harness.

---

## Sprint H43 Closeout - Interpretation Frame-Shape Preparation

Integrated outcome:

- Added `interpretation_result_to_frame()` to project deterministic
  interpretation harness results into fake-provider-compatible frame shapes.
- Confirm-route labels become `proposal` frames requiring staff confirmation
  with `writes_authorized=false`.
- Read-only labels become `read_request` frames requiring backend checks with
  `writes_authorized=false`.
- Meta, planned, unsafe, and unknown results become blocked `refusal` frames
  with `writes_authorized=false`.
- Tests validate every authored interpretation fixture through the existing
  manifest frame-shape and safety evaluators without provider calls.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile app\services\bernie\interpretation_harness.py tests\test_bernie_interpretation_harness.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `97 passed`; leakage lint safe; whitespace check clean.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is richer fake-provider-style frame scenarios or external
reviewer dispatch for the harness.

---

## Sprint H44 Closeout - Reviewer-Informed Interpretation Coverage

Integrated outcome:

- Added `expected_frame_kind` to every authored interpretation fixture case.
- Added receptionist-phrase fixture coverage from external review for gaps/free
  times/squeeze-in availability, short check-in phrasing, cancellation phrasing,
  resize/move/create variants, and handoff ambiguity.
- Folded adversarial safety review fixes into the harness:
  broader confirmation-bypass refusal patterns, false-precondition refusals,
  narrower slot-search matching, Unicode normalization plus format-control
  stripping, and `refusal_reason_kind` on projected frames.
- Added fixture/test coverage for compound planned-action phrases and generic
  find/show wording that must not become slot search without availability cues.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile app\services\bernie\interpretation_harness.py tests\test_bernie_interpretation_harness.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `148 passed`; leakage lint safe; whitespace check clean.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is richer fake-provider-style frame scenarios or another
bounded external review after the next harness increment.

---

## Sprint H45 Closeout - Projected Frame Invariants

Integrated outcome:

- Added `assert_interpretation_frame_consistency()` to the provider-free Bernie
  interpretation harness.
- Every projected frame must keep `writes_authorized=false`.
- Confirm dispatch must project to a staff-confirmation `proposal` frame.
- Read-only dispatch must project to a backend-check `read_request` frame.
- Refusal frames must carry the expected `refusal_reason_kind`; unsafe/unknown
  refusals must not carry `refused_action`.
- Added negative tests for plausible drifted frames that the harness must reject.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile app\services\bernie\interpretation_harness.py tests\test_bernie_interpretation_harness.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `152 passed`; leakage lint safe; whitespace check clean.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is richer fake-provider-style frame scenarios.

---

## Sprint H46 Closeout - Provider-Style Copy Contract

Integrated outcome:

- Added safe receptionist-facing `copy` fields to projected interpretation
  frames.
- Proposal copy stages a diary proposal for staff review instead of claiming a
  completed booking.
- Read-request copy defers to backend diary checks instead of asserting live
  availability.
- Refusal copy blocks the request without write authority.
- Added positive fixture-wide tests and negative drift tests for copy that
  claims completion, asserts availability, or loses refusal posture.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile app\services\bernie\interpretation_harness.py tests\test_bernie_interpretation_harness.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `195 passed`; leakage lint safe; whitespace check clean apart from the
known CRLF notice on `orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is clarify/ambiguity-style projected frame preparation or
another bounded reviewer pass after the next harness increment.

---

## Sprint H47 Closeout - Clarify-Frame Dispatch

Integrated outcome:

- Added `request_clarification` to the provider-free Bernie interpretation
  harness.
- Added authored synthetic clarification fixtures for explicit patient-context
  ambiguity and unclear/invalid reason-code wording.
- Patient ambiguity projects to a `clarify` frame with synthetic display
  choices and no IDs.
- Reason-code ambiguity projects to a `clarify` frame with valid reason-code
  options and no selected/defaulted reason.
- Clarification carries no verb, no route authority, no writes, and runs after
  unsafe-instruction refusal so unsafe bypass attempts still fail closed.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile app\services\bernie\interpretation_harness.py tests\test_bernie_interpretation_harness.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `213 passed`; leakage lint safe; whitespace check clean apart from the
known CRLF notice on `orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is structured provider-style frame fixtures or another
bounded reviewer pass after the next harness increment.

---

## Sprint H48 Closeout - Frame Contract Matrix

Integrated outcome:

- Added
  `tests/fixtures/bernie_interpretation_harness/projected_frame_contracts.json`
  as an authored synthetic contract matrix for projected frames.
- The matrix covers every `InterpretationDispatch` and records expected frame
  kind, required true/false/null fields, absent fields, refusal reason kinds,
  and safe copy fragments.
- Tests prove every dispatch has a contract, every contract is observed by the
  authored utterance fixtures, and every projected frame satisfies the matching
  contract before broader manifest evaluation.
- The contract fixture remains payload-free and does not quote route, endpoint,
  patient/practitioner/appointment ID fragments.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile app\services\bernie\interpretation_harness.py tests\test_bernie_interpretation_harness.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `259 passed`; leakage lint safe; whitespace check clean apart from the
known CRLF notice on `orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is a bounded reviewer pass over the harness or small
projected-frame validator hardening.

---

## Sprint H49 Closeout - Bounded Contract Review

Integrated outcome:

- Added
  `docs/adversarial/h49_interpretation_harness_contract_review.md`.
- Reviewed the provider-free interpretation harness projected-frame contract
  surface after H48.
- Hardened `assert_interpretation_frame_consistency()` so unknown
  `interpretation_dispatch` values fail as `AssertionError` instead of leaking a
  raw enum `ValueError`.
- Added a drifted-frame regression case for unknown dispatch.
- Added no new runtime interpretation behavior, provider calls, route wiring,
  database access, H15/H-series input, RAG, GraphRAG, or memory.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile app\services\bernie\interpretation_harness.py tests\test_bernie_interpretation_harness.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `260 passed`; leakage lint safe; whitespace check clean apart from the
known CRLF notice on `orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is projected-frame validator hardening or a provider-free
harness summary/report artifact.

---

## Sprint H50 Closeout - Safe Aggregate Report

Integrated outcome:

- Added `scripts/bernie_interpretation_harness_report.py`.
- Added `tests/test_bernie_interpretation_harness_report.py`.
- The report emits safe aggregate counts only: 44 authored cases, 4 case
  fixture files, 7 dispatch contracts, dispatch counts, frame-kind counts, and
  fixture-level case counts.
- The report declares omitted fields and avoids utterance text, payload fields,
  and patient/practitioner/appointment ID fields.
- The CLI was verified from the repo root; it calls no providers, routes,
  database access, raw trove processing, or runtime memory.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile scripts\bernie_interpretation_harness_report.py tests\test_bernie_interpretation_harness_report.py
.venv\Scripts\python.exe scripts\bernie_interpretation_harness_report.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `263 passed`; report CLI sample succeeded; leakage lint safe;
whitespace check clean apart from the known CRLF notice on
`orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is small report/validator hardening or a bounded review
before any runtime/provider wiring.

---

## Sprint H51 Closeout - Report Safety Assertion

Integrated outcome:

- Added `assert_harness_report_safety()` to
  `scripts/bernie_interpretation_harness_report.py`.
- The CLI now validates the report before printing.
- The assertion checks schema/source, non-empty counts, prohibited runtime
  boundary posture, omitted-field declarations, dispatch/contract alignment, and
  representative forbidden text/payload fragments.
- Added negative tests for embedded utterance text, weakened provider
  boundaries, and contract-dispatch drift.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile scripts\bernie_interpretation_harness_report.py tests\test_bernie_interpretation_harness_report.py
.venv\Scripts\python.exe scripts\bernie_interpretation_harness_report.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `266 passed`; report CLI sample succeeded; leakage lint safe;
whitespace check clean apart from the known CRLF notice on
`orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is continued report/validator hardening before any
runtime/provider wiring.

---

## Sprint H52 Closeout - Report Input Guards

Integrated outcome:

- Hardened `build_harness_report()` so alternate fixture-directory inputs fail
  closed.
- Missing paths, non-directory paths, empty fixture directories, empty case
  lists, empty contract lists, directories without case fixtures, and
  directories without contract fixtures now raise `ValueError`.
- Added temporary-directory negative tests for missing, empty, case-less, and
  contract-less inputs.
- The report remains aggregate-only, provider-free, route-free, DB-free, and
  disconnected from local historical diary material.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile scripts\bernie_interpretation_harness_report.py tests\test_bernie_interpretation_harness_report.py
.venv\Scripts\python.exe scripts\bernie_interpretation_harness_report.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `270 passed`; report CLI sample succeeded; leakage lint safe;
whitespace check clean apart from the known CRLF notice on
`orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is continued report/validator hardening before runtime or
provider wiring.

---

## Sprint H53 Closeout - Runtime/Provider Wiring Gate

Integrated outcome:

- Added `docs/bernie-interpretation-harness-runtime-gate.json`.
- Added `tests/test_bernie_interpretation_runtime_gate.py`.
- The gate is blocked by default for runtime wiring, provider dry-run wiring,
  route integration, database access, memory/RAG access, and historical diary
  material access.
- Current allowed uses are limited to provider-free fixture tests, safe aggregate
  reports, contract validation, and bounded review artifacts.
- Any decision change away from `blocked`, true scope value, or change to
  required/forbidden lists requires a sprint-engine pause and explicit review.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile tests\test_bernie_interpretation_runtime_gate.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_interpretation_runtime_gate.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `274 passed`; leakage lint safe; whitespace check clean apart from the
known CRLF notice on `orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded gate/review hardening before runtime/provider
wiring.

---

## Sprint H54 Closeout - Runtime Gate Checker

Integrated outcome:

- Added `scripts/bernie_interpretation_runtime_gate_check.py`.
- Added `tests/test_bernie_interpretation_runtime_gate_check.py`.
- The checker validates the blocked H53 runtime gate and emits only safe
  aggregate status: blocked scope count, required review count, forbidden use
  count, pause trigger count, `sprint_engine_state: continuing`, and
  `pause_required: false`.
- Negative tests reject unblocked decisions, true scope values, and missing
  pause triggers.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile scripts\bernie_interpretation_runtime_gate_check.py tests\test_bernie_interpretation_runtime_gate_check.py
.venv\Scripts\python.exe scripts\bernie_interpretation_runtime_gate_check.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_interpretation_runtime_gate.py tests\test_bernie_interpretation_runtime_gate_check.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `279 passed`; gate-check CLI and report CLI samples succeeded; leakage
lint safe; whitespace check clean apart from the known CRLF notice on
`orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded gate/checker hardening before runtime/provider
wiring.

---

## Sprint H55 Closeout - Combined Readiness Check

Integrated outcome:

- Added `scripts/bernie_interpretation_readiness_check.py`.
- Added `tests/test_bernie_interpretation_readiness_check.py`.
- The command combines the safe aggregate report and runtime gate checker into a
  single provider-free status.
- The status reports counts and schema versions while explicitly keeping
  `runtime_or_provider_wiring_ready=false` and `raw_trove_access_ready=false`.
- The command is a "still boxed in" check, not permission for runtime routes,
  providers, database access, memory, H15/H-series runtime imports, or raw trove
  access.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile scripts\bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_runtime_gate.py tests\test_bernie_interpretation_runtime_gate_check.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `282 passed`; readiness CLI sample succeeded; leakage lint safe;
whitespace check clean apart from the known CRLF notice on
`orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded readiness/gate hardening before
runtime/provider wiring.

---

## Sprint H56 Closeout - Readiness Release Gate

Integrated outcome:

- Added a provider-free interpretation harness gate section to
  `orchestration/bernie_release_gates.md`.
- The release gate requires
  `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`
  before any sprint proposes runtime route wiring, provider prompt/dry-run
  wiring, memory/RAG/GraphRAG use, H15/H-series runtime imports, or historical
  diary material access from the interpretation harness.
- Expected current values remain `runtime_or_provider_wiring_ready=false`,
  `raw_trove_access_ready=false`, and `runtime_gate_decision=blocked`.
- A changed value or failing readiness command requires sprint-engine pause and
  explicit review.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile tests\test_bernie_interpretation_readiness_release_gate.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_readiness_release_gate.py tests\test_bernie_interpretation_runtime_gate.py tests\test_bernie_interpretation_runtime_gate_check.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `284 passed`; readiness CLI sample succeeded; leakage lint safe;
whitespace check clean apart from the known CRLF notice on
`orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded readiness/gate hardening before runtime/provider
wiring.

---

## Sprint S5 Closeout - Receptionist Workflow Audit

- D-1 frontend audit completed with no material static defect.
- D-2 backend audit confirmed terminal-status reversal behavior and recorded a
  failing-test proposal; product policy remains deferred.
- A-1 returned Conditional Go and identified silent-refresh selection loss.
- Fable selected one Phase B repair: preserve active diary selection.
- D-1 implemented the repair and focused test; D-2 cross-review passed.
- Focused Playwright: `3 passed`; JavaScript syntax passed.
- Diary smoke baseline remains exactly 8 known failures with no new B-1 failure.
- Full project tests remain non-clean for pre-existing environment/readiness
  reasons and were not claimed as passing.

Evidence: `docs/emr4-s5-receptionist-workflow-audit-closeout.md`.

Sprint engine state: continuing directly to Conductor next-sprint planning.

---

## Sprint S6 Closeout - Diary Contract Repair

- Restored the full diary browser suite from eight known failures to 139/139
  passing tests.
- Repaired the production `saveBooking()` AHPRA `ReferenceError` without
  treating directory UUIDs as AHPRA identifiers.
- Updated default-on GraphQL practitioner-directory route interception and
  security/authorization assertions; signed-confirm tests remain intact.
- Exercised DeepSeek 4 Pro as the real Claude-limit Conductor fallback and two
  separate DeepSeek Flash implementation/review sessions.
- Quarantined two invalid review attempts; only corrected v3 review evidence is
  acceptance-bearing.
- Recorded six stale Pro-fallback settings-test failures and five transport/
  evidence incidents as required S7 contract-audit inputs.

Verification: diary Playwright `139 passed`; closeout/PTY adapter `21 passed`;
JavaScript syntax, frontend asset version, and whitespace checks passed. Wider
Ariadne batch: `47 passed, 6 failed`, all six stale pre-S6 resource assumptions
in `tests/test_ariadne_deepcode_adapter_settings.py` and deferred explicitly to
S7.

Evidence: `docs/emr4-s6-diary-contract-repair-closeout.md`.

Sprint engine state: continuing automatically to S7 contract audit. No user
intervention is required.

---

## Sprint S7 Closeout - Review Acceptance Contract Audit

- Reconciled all stale Deep Code adapter settings tests with the approved
  `deepseek-pro-conductor-fallback`.
- Added the standard-library review acceptance gate and direct CLI.
- Bound acceptance to exact artifact/receipt identity, marker parity,
  worktree/branch, candidate ancestry, cleanup, review mode, and authoritative
  pytest collection.
- Rejected the first candidate in a real gate run, returned the multi-file
  aggregation defect to Lane 1, and required a fresh Lane 2 review.
- Final executable gate decision is accepted with 88 authoritative focused
  tests and no worker count mismatch.

Verification: focused `88 passed`; adjacent Deep Code PTY/mailbox `22 passed`;
broad Ariadne closeout `121 passed`; direct CLI, Python compilation, and
whitespace checks passed.

Evidence: `docs/ariadne-s7-review-acceptance-closeout.md` and
`orchestration/harness_evidence/s7-review-v2-acceptance.json`.

Sprint engine state: continuing automatically to the next Conductor planning
boundary. No user intervention is required.

---

## Sprint S8 Closeout - Receptionist Workflow Implementation

- Implemented taskpane Diary launch reliability and actionable Office dialog
  failure handling.
- Implemented four diary usability affordances: terminal-reason guidance,
  webview date fallback, same-day search, and read-only detail preview.
- Required same-lane revisions for eight W1 test failures, a W1 ownership breach,
  W2 navigation overlap, and incomplete/stalled transport closeouts.
- Gate-accepted both W3 reviews and integrated Antigravity's GO verdict.
- Enabled DeepCode local candidate commits while preserving push/integration
  prohibition; W2 created candidate `a2effefd` under the corrected policy.

Verification: product focused `28 passed`; smoke/selection `142 passed`;
GraphQL/deprecation `15 passed`; DeepCode permission contract `53 passed`;
JavaScript syntax, frontend versions, executable review gates, and whitespace
checks passed.

Evidence: `docs/emr4-s8-receptionist-workflow-closeout.md`.

Sprint engine state: continuing to the next Conductor boundary after closeout
publication. No user intervention is required for routine execution.

---

## Sprint H62 Closeout - Readiness Snapshot Assertion

Integrated outcome:

- Hardened `scripts/bernie_interpretation_readiness_check.py` so the CLI loads
  the committed blocked-readiness snapshot before printing.
- Added `assert_matches_blocked_readiness_snapshot()`.
- The CLI now fails closed if generated readiness differs from
  `tests/fixtures/bernie_interpretation_readiness/blocked_readiness_status.json`.
- Added tests for snapshot mismatch and missing snapshot.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile scripts\bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_interpretation_protocol_alert.py tests\test_bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_readiness_release_gate.py tests\test_bernie_interpretation_readiness_review_artifact.py tests\test_bernie_interpretation_readiness_snapshot.py tests\test_bernie_interpretation_runtime_gate.py tests\test_bernie_interpretation_runtime_gate_check.py tests\test_bernie_interpretation_runtime_isolation.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `300 passed`; readiness CLI sample succeeded; leakage lint safe;
whitespace check clean apart from the known CRLF notice on
`orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded readiness/gate hardening before runtime/provider
wiring.

---

## Sprint H61 Closeout - Combined Readiness Fail-Closed Tests

Integrated outcome:

- Strengthened `tests/test_bernie_interpretation_readiness_check.py`.
- The combined readiness layer now directly rejects:
  - an unblocked runtime gate decision;
  - a missing fixture directory;
  - an empty fixture directory.
- This duplicates key lower-level fail-closed checks at the command future
  agents are expected to run before runtime/provider/trove proposals.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile tests\test_bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_interpretation_protocol_alert.py tests\test_bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_readiness_release_gate.py tests\test_bernie_interpretation_readiness_review_artifact.py tests\test_bernie_interpretation_readiness_snapshot.py tests\test_bernie_interpretation_runtime_gate.py tests\test_bernie_interpretation_runtime_gate_check.py tests\test_bernie_interpretation_runtime_isolation.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `297 passed`; readiness CLI sample succeeded; leakage lint safe;
whitespace check clean apart from the known CRLF notice on
`orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded readiness/gate hardening before runtime/provider
wiring.

---

## Sprint H60 Closeout - Readiness Protocol Alert

Integrated outcome:

- Added a worker-facing Bernie Interpretation Harness readiness alert to
  `orchestration/protocol_alerts.md`.
- Added `tests/test_bernie_interpretation_protocol_alert.py`.
- The alert requires
  `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`
  before runtime route wiring, provider prompt/dry-run wiring,
  memory/RAG/GraphRAG use, H15/H-series runtime imports, or historical diary
  material access from the provider-free interpretation harness.
- The alert preserves expected blocked values and says the sprint engine must
  pause for explicit review if the command fails or values change.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile tests\test_bernie_interpretation_protocol_alert.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_interpretation_protocol_alert.py tests\test_bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_readiness_release_gate.py tests\test_bernie_interpretation_readiness_review_artifact.py tests\test_bernie_interpretation_readiness_snapshot.py tests\test_bernie_interpretation_runtime_gate.py tests\test_bernie_interpretation_runtime_gate_check.py tests\test_bernie_interpretation_runtime_isolation.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `294 passed`; readiness CLI sample succeeded; leakage lint safe;
whitespace check clean apart from the known CRLF notice on
`orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded readiness/gate hardening before runtime/provider
wiring.

---

## Sprint 150 Closeout - Create-Proposal Syntactic Idempotency Wiring

Publication state:

- Integration commit SHA: `pending Sprint 150 closeout commit`.
- Push result: pending.
- Final `git status --short --branch`: pending final closeout check.

Programme position:

- Phase/programme: Programme 2G / EMR4 API Spine.
- Classification: narrow route wiring and guardrail hardening.
- Larger objective advanced: the first proposal-only route now enforces
  syntactic `Idempotency-Key` discipline without gaining write replay authority.
- Next planned step: Sprint 151 OpenAPI/FastAPI header alignment guard for
  create-proposal, including the deferred `minLength: 8` compatibility decision.

Integrated outcome:

- Updated `app/routers/appointments.py` so
  `POST /api/v1/appointments/proposals/create` requires a non-blank
  `Idempotency-Key` header.
- Added a proposal-specific missing-key error message:
  `Idempotency-Key is required for creating appointment proposals.`
- Kept `_build_create_appointment_proposal` idempotency-free.
- Enabled the Sprint 148 future DB-backed behavior tests in
  `tests/test_api_spine_create_proposal_idempotency_route_contract.py`.
- Updated existing create-proposal callers in focused tests to send the new
  header deliberately.
- Proved keyed create-proposal calls create no appointment, audit, or
  `AppointmentCommandIdempotency` rows.
- Proved same-key/same-body retries re-evaluate fresh current state, and
  same-key/different-body retries return fresh proposal envelopes without
  `409 idempotency_key_conflict`.
- Deliberately deferred OpenAPI `minLength: 8` enforcement for a compatibility
  alignment sprint.
- Raw compatibility, other proposal families, provider, GraphQL, H15/H-series,
  memory/RAG/GraphRAG, and historical diary trove gates remain closed.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_api_spine_create_proposal_idempotency_route_contract.py tests/test_api_spine_create_proposal_replay_model_decision.py tests/test_api_spine_proposal_only_idempotency_preflight.py tests/test_appointment_proposals.py tests/test_appointment_audit.py tests/test_appointment_raw_temporal_guard.py tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py -q
```

Result: `88 passed`; existing Starlette and Google GenAI deprecation warnings
only.

Note: `tests/test_appointment_audit_warning_summary.py` remains time-sensitive
around raw compatibility `TODAY` fixtures and currently fails independently of
Sprint 150 with same-day elapsed/raw-compat audit expectations.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is the create-proposal OpenAPI/FastAPI header alignment
guard.

---

## Sprint 149 Closeout - Create-Proposal Replay Model Decision

Publication state:

- Integration commit SHA: `pending Sprint 149 closeout commit`.
- Push result: pending.
- Final `git status --short --branch`: pending final closeout check.

Programme position:

- Phase/programme: Programme 2G / EMR4 API Spine.
- Classification: replay-model policy decision.
- Larger objective advanced: create-proposal idempotency now has an explicit
  semantics choice before route enforcement wiring.
- Next planned step: Sprint 150 create-proposal route wiring with deterministic
  re-evaluation semantics only.

Integrated outcome:

- Added
  `orchestration/api_spine_appointment_idempotency_create_proposal_replay_model.md`.
- Added `tests/test_api_spine_create_proposal_replay_model_decision.py`.
- Integrated DeepSeek's Sprint 149 review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint149-create-proposal-replay-model.md`.
- Selected deterministic re-evaluation with required syntactic
  `Idempotency-Key` as the future create-proposal model.
- Rejected short-retention proposal markers and stored proposal-envelope replay
  for the first create-proposal pass.
- Recorded that future wiring is header-only, syntactic validation only,
  `proposeAppointmentCreate` is logging/review metadata only, and no
  `AppointmentCommandIdempotency` rows are created.
- Recorded that same-key/same-body and same-key/different-body retries should
  return fresh proposal evaluations, not cached envelopes or `409` conflicts.
- No route behavior changed. Raw compatibility, other proposal families,
  provider, GraphQL, H15/H-series, memory/RAG/GraphRAG, and historical diary
  trove gates remain closed.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_api_spine_create_proposal_replay_model_decision.py -q
```

Result: `9 passed`; existing Starlette and Google GenAI deprecation warnings
only.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is create-proposal route wiring with deterministic
re-evaluation semantics only.

---

## Sprint 148 Closeout - Create-Proposal Idempotency Route-Test Contract

Publication state:

- Integration commit SHA: `pending Sprint 148 closeout commit`.
- Push result: pending.
- Final `git status --short --branch`: pending final closeout check.

Programme position:

- Phase/programme: Programme 2G / EMR4 API Spine.
- Classification: guarded route-test contract.
- Larger objective advanced: proposal-only idempotency now has a first
  create-proposal contract without route behavior changes.
- Next planned step: Sprint 149 focused create-proposal replay-model decision
  before any proposal-route enforcement wiring.

Integrated outcome:

- Added
  `orchestration/api_spine_appointment_idempotency_create_proposal_route_tests.md`.
- Added `tests/test_api_spine_create_proposal_idempotency_route_contract.py`.
- Added Claude, Antigravity, and DeepSeek review/acceptance lane packets for
  Sprint 148.
- The current no-wiring guards prove `propose_create_appointment` still has no
  `Idempotency-Key` header binding and no appointment command ledger calls.
- The dynamic create-proposal test now also proves proposal calls do not create
  appointment command idempotency ledger rows.
- The contract preserves the existing create-proposal confirmation evidence and
  freshness path.
- DeepSeek's review was integrated: Sprint 149 must choose deterministic
  re-evaluation, a short-retention proposal marker, or stored proposal-envelope
  replay before any wiring.
- Six future behavior tests are present but skipped until a later sprint
  explicitly wires proposal-route enforcement.
- Raw compatibility, other proposal families, provider, GraphQL, H15/H-series,
  memory/RAG/GraphRAG, and historical diary trove gates remain closed.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_api_spine_create_proposal_idempotency_route_contract.py -q
.venv\Scripts\python.exe -m pytest tests/test_api_spine_create_proposal_idempotency_route_contract.py tests/test_appointment_proposals.py tests/test_diary_action_route_contract.py -q
```

Result: focused contract `7 passed, 6 skipped`; adjacent closeout suite
`30 passed, 6 skipped`; existing Starlette and Google GenAI deprecation
warnings only.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is a focused create-proposal replay-model decision before
proposal-route enforcement wiring.

---

## Sprint 147 Closeout - Proposal-Only Idempotency Preflight

Publication state:

- Integration commit SHA: `pending Sprint 147 closeout commit`.
- Push result: pending.
- Final `git status --short --branch`: pending final closeout check.

Programme position:

- Phase/programme: Programme 2G / EMR4 API Spine.
- Classification: policy/preflight and guardrail hardening.
- Larger objective advanced: appointment command idempotency now has an
  explicit next-surface policy before expanding beyond confirmation routes.
- Next planned step: Sprint 148 guarded create-proposal route-test contract
  only, with no proposal-route enforcement wiring yet.

Integrated outcome:

- Added
  `orchestration/api_spine_appointment_idempotency_proposal_only_preflight.md`.
- Added `tests/test_api_spine_proposal_only_idempotency_preflight.py`.
- Integrated DeepSeek's Sprint 147 review in
  `orchestration/agent_inbox/codex/review-deepseek-sprint147-proposal-only-idempotency-preflight.md`.
- Selected proposal-only appointment routes as the next preflight surface before
  raw compatibility writes because they are canonical OpenAPI command-plane
  routes and non-mutating.
- Recorded the key distinction that proposal idempotency must be
  proposal-specific client discipline and must not copy confirmation-write
  replay authority.
- Preserved no route behavior changes. Proposal-only routes remain unwired;
  raw compatibility, provider, GraphQL, H15/H-series, memory/RAG/GraphRAG, and
  historical diary trove gates remain closed.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_api_spine_proposal_only_idempotency_preflight.py -q
```

Result: `8 passed`; existing Starlette and Google GenAI deprecation warnings
only.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is a guarded create-proposal route-test contract before
proposal-route enforcement.

---

## Sprint 146 Closeout - Confirmation-Family Idempotency Integration Tests

Publication state:

- Integration commit SHA: `pending Sprint 146 closeout commit`.
- Push result: pending.
- Final `git status --short --branch`: pending final closeout check.

Programme position:

- Phase/programme: Programme 2G / EMR4 API Spine.
- Classification: guardrail hardening and route-level integration coverage.
- Larger objective advanced: appointment command idempotency now has both
  per-family contract tests and one shared DB-backed integration matrix across
  all proposal-confirm mutation families.
- Next planned step: Sprint 147 policy/preflight decision before proposal-only,
  raw compatibility, or broader command-surface idempotency expansion.

Integrated outcome:

- Added
  `tests/test_api_spine_confirmation_family_idempotency_integration.py`.
- Added
  `orchestration/api_spine_appointment_idempotency_confirmation_family_integration_tests.md`.
- Added Claude, Antigravity, and DeepSeek review/acceptance lane packets for
  Sprint 146.
- The new test matrix drives staff create, Bernie create, status, update, and
  delete confirmation routes through missing-key, replay, conflict,
  in-progress, stale-in-progress, and failed-transient cases.
- The matrix asserts no duplicate appointment, audit, ledger, or Bernie
  session-event side effects on replay or fail-closed paths.
- No route behavior changed. Proposal-only, raw compatibility, provider,
  GraphQL, H15/H-series, memory/RAG/GraphRAG, and historical diary trove gates
  remain closed.

Verification:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_api_spine_confirmation_family_idempotency_integration.py -q
```

Result: `30 passed`; existing Starlette and Google GenAI deprecation warnings
only.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is a narrow policy/preflight decision before broader
idempotency expansion.

---

## Sprint H59 Closeout - Blocked-Readiness Snapshot

Integrated outcome:

- Added
  `tests/fixtures/bernie_interpretation_readiness/blocked_readiness_status.json`.
- Added `tests/test_bernie_interpretation_readiness_snapshot.py`.
- Generated readiness status must now match the committed blocked snapshot
  exactly.
- The snapshot records aggregate counts only: 44 cases, 7 contracts, 7
  dispatches, 4 frame kinds, gate decision `blocked`, sprint engine
  `continuing`, and both runtime/provider and raw-trove readiness false.
- The snapshot contains no utterance text, payload fields, route fragments,
  local-data paths, H15 fragments, or H-series fragments.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile tests\test_bernie_interpretation_readiness_snapshot.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_readiness_release_gate.py tests\test_bernie_interpretation_readiness_review_artifact.py tests\test_bernie_interpretation_readiness_snapshot.py tests\test_bernie_interpretation_runtime_gate.py tests\test_bernie_interpretation_runtime_gate_check.py tests\test_bernie_interpretation_runtime_isolation.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `292 passed`; readiness CLI sample succeeded; leakage lint safe;
whitespace check clean apart from the known CRLF notice on
`orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded readiness/gate hardening before runtime/provider
wiring.

---

## Sprint H58 Closeout - Readiness/Gate Review

Integrated outcome:

- Added `docs/adversarial/h58_interpretation_readiness_gate_review.md`.
- Added `tests/test_bernie_interpretation_readiness_review_artifact.py`.
- The review records that the readiness/gate stack is suitable as a
  blocked-by-default preflight for continued provider-free harness work.
- The review explicitly says it is not evidence that runtime routes, provider
  prompts, live provider dry-runs, memory/RAG/GraphRAG, H15/H-series runtime
  imports, or historical diary material access are ready.
- The guard test preserves the blocked verdict and sprint-engine pause
  recommendation if readiness values change.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile tests\test_bernie_interpretation_readiness_review_artifact.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_readiness_release_gate.py tests\test_bernie_interpretation_readiness_review_artifact.py tests\test_bernie_interpretation_runtime_gate.py tests\test_bernie_interpretation_runtime_gate_check.py tests\test_bernie_interpretation_runtime_isolation.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `289 passed`; readiness CLI sample succeeded; leakage lint safe;
whitespace check clean apart from the known CRLF notice on
`orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded readiness/gate hardening before runtime/provider
wiring.

---

## Sprint H57 Closeout - Runtime Isolation Guard

Integrated outcome:

- Added `tests/test_bernie_interpretation_runtime_isolation.py`.
- The guard scans production `app/` Python sources and proves they do not import
  or reference interpretation harness report/readiness/gate tooling.
- It also guards against runtime references to harness fixture paths,
  projected-frame contracts, H15 semantic candidate fixtures, H-series profile
  fixtures, historical diary candidate builders, `local_data`, or historical
  diary trove paths.
- No runtime code was changed.

Verification:

```powershell
.venv\Scripts\python.exe -m py_compile tests\test_bernie_interpretation_runtime_isolation.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py tests\test_bernie_interpretation_readiness_check.py tests\test_bernie_interpretation_readiness_release_gate.py tests\test_bernie_interpretation_runtime_gate.py tests\test_bernie_interpretation_runtime_gate_check.py tests\test_bernie_interpretation_runtime_isolation.py tests\test_bernie_manifest_receptionist_scenarios.py tests\test_diary_action_route_contract.py -q
git diff --check
```

Result: `287 passed`; readiness CLI sample succeeded; leakage lint safe;
whitespace check clean apart from the known CRLF notice on
`orchestration/integration_log.md`.

Sprint engine state: continuing. No user intervention is required; next
recommended direction is bounded readiness/gate hardening before runtime/provider
wiring.
