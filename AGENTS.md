# EMR4 Centaur — Live Agent Handover

> **Purpose:** This compact file is the authoritative starting point for every
> human or AI agent working in EMR4. Read it completely. It controls current
> authority, protected boundaries, baton state, and next work. Historical
> detail lives in the indexed ledgers and immutable snapshot below.

## 1. Project

EMR4 Centaur is an AI-native, open-source General Practice management system
for Australia. FastAPI/PostgreSQL owns clinical and diary truth. Microsoft Word
with an Office.js add-in is the clinical workspace, and the native browser
Diary is the scheduling surface. The full phase and architecture blueprint is
[`implementation_plan.md`](implementation_plan.md).

## 2. Mandatory Rehydration

At a new session, after conversation compaction/restoration, after a
model/provider change, and before a new sprint plan or dispatch:

1. Read this file completely.
2. Read the active acceptance/plan documents named in the Current Baton.
3. Restore the protected-evidence and user-decision boundaries in sections 5
   and 6.
4. Verify `git status`, `HEAD`, `master`, `handoff/current`, `origin/master`,
   and `origin/handoff/current`.
5. Generate a fresh Ariadne orchestrator receipt naming all five sources:
   `live_handover_current_baton`, `current_authority_allocation`,
   `active_plan_and_acceptance`, `protected_evidence_boundaries`, and
   `git_refs_and_worktree`.

A conversation summary is a continuity aid only. It is never authoritative for
model allocation, provider transport, holdout rules, write authority, or user
decision boundaries. `rehydrated_from_receipt: true` without the five named
sources is insufficient and must return `revision_required`.

## 3. Current Baton

| Item | Current value |
|---|---|
| Mode | Parallel-capable Ariadne workflow; protected single-track integration |
| Baton ref | `handoff/current` |
| Integration worktree | `C:\Users\sarashera\emr4` on `master` |
| Worker worktree root | `C:\Users\sarashera\EMR4-worktrees\` |
| Required Git relation | Clean `master`; local and origin `master` and `handoff/current` aligned after closeout |
| Conductor/integrator | GPT Sol |
| Implementation/test worker | DeepSeek V4 Flash/high through Claude Code `--bare` |
| Independent worker/reviewer | Gemini 3.5 Flash through a fresh Antigravity project |
| Active product track | LC4V10 fresh certification passed; synthetic Silver v2 remains complete. T3R5 completed the authorized no-call Australian Vertex feasibility and entitlement design and stopped before a provider call: current Gemini successors lack Sydney availability and the sole Sydney-capable GA candidate has only 90 days of documented runway; mandatory Pushover closeout pings remain restored |
| Active acceptance | `orchestration/agent_inbox/codex/lc4v10-sol-acceptance.md`, `docs/bernie-lc4v10-fresh-certification-closeout.md`, `orchestration/agent_inbox/codex/security-hardening-final-purple-acceptance.md`, `docs/security/secure-sdlc-red-blue-diary-hardening-closeout-2026-07-17.md`, `docs/bernie-post-certification-transition-review.md`, `orchestration/agent_inbox/codex/appointment-call-quarantine-pilot-sol-acceptance.md`, `docs/bernie-appointment-call-quarantine-pilot-closeout.md`, `docs/bernie-synthetic-silver-v2-anchor-contract.md`, `docs/bernie-synthetic-silver-v2-closeout.md`, `orchestration/agent_inbox/antigravity/synthetic-silver-v2-final-review.md`, `orchestration/agent_inbox/codex/synthetic-silver-v2-sol-acceptance.md`, `docs/bernie-t3r1-synthetic-shadow-refresh.md`, `docs/bernie-t3r1-synthetic-shadow-baseline.json`, `orchestration/agent_inbox/codex/t3r1-synthetic-shadow-refresh-sol-acceptance.md`, `docs/bernie-t3r2-synthetic-live-comparison-approval.json`, `docs/bernie-t3r3-three-lane-transport-preflight-closeout.md`, `docs/bernie-t3r4-pragmatic-live-comparison-approval.json`, `docs/bernie-t3r4-pragmatic-live-comparison-report.json`, `docs/bernie-t3r4-pragmatic-live-comparison-closeout.md`, `orchestration/agent_inbox/codex/t3r4-pragmatic-live-comparison-sol-acceptance.md`, `docs/bernie-t3r5-vertex-au-feasibility-and-entitlement-design.md`, `docs/bernie-t3r5-vertex-au-readiness-report.json`, `docs/bernie-t3r5-vertex-au-feasibility-closeout.md`, and `orchestration/agent_inbox/codex/t3r5-vertex-au-feasibility-sol-acceptance.md` |
| Current result | V10 remains a valid bounded `certification_pass`: complete and every dimension 576/576; synthetic Silver v2 remains 192/192. T3R4 validly closed `comparison_complete_with_hard_limit_stop` and remains bounded evidence. T3R5 validly returned `blocked_before_provider_call`: Gemini 3.5 Flash and 3.1 Flash-Lite have no Sydney availability, Gemini 2.5 Flash has only 90 days to documented retirement, the durable entitlement controls fail closed, 71 focused/preservation tests pass, and no model call or cloud mutation occurred |
| Next implementation | No V11 is needed or authorized, and no synthetic v3 is authorized. Reassess no-call Vertex readiness only when a current Gemini successor becomes GA in `australia-southeast1`; even a passing readiness report requires a new explicit provider/model/retention/prompt/budget decision before evaluation. Product runtime, API/database/UI, confirmation, deployment/release, and write authority remain closed |

### LC4V6, LC4V6D1, and LC4V7 state

Fresh V6 used Flash only for the empty framework, Gemini for its pre-content
veto, and Sol for Gold at `0527848b`; its consumed result is
`certification_fail`, complete `540/576`, safety `576/576`. D1 then passed
24/24 fresh layer-specific probes with zero variance and no runtime repair.
Its unknown-practitioner moves established extraction/policy clarification
separation without revealing or rescoring V6.

Yuri authorized V7 on 2026-07-16. Flash breached protected V6 access, so Sol
built clean-room head `186ccf44`; Gemini also passed amended `b4f8cb18` before
content. Sol froze source `403fcafd`. The consumed raw result is
`certification_invalid` because product failures were misclassified as evidence
invalidity; complete `224/576`, safety `576/576`, and product gates miss. V7 is sealed; see active acceptance.

### LC4V8 accepted state

Yuri authorized fresh V8 after V7D1. Flash's fail-open candidate was rejected; Sol recovered, Gemini passed two pre-content vetoes, and Sol froze source `313e6247` plus seal `5d465667`. The sole valid 576-observation attempt returned
`certification_fail`: complete/policy resolution `0/576`, temporal/normalization
`528/576`, all other dimensions including safety `576/576`, and zero variance.
V8 is sealed; accepted D1 supplies no repair target and leaves V9 at Yuri's boundary.

### LC4V9 and LC4V9D1 accepted state

Fresh V9 validly consumed its sole attempt with `certification_fail`: complete
88/576, entity semantics 96/576, exact policy projection 88/576, policy
behavior/clarification/composition/replay 528/576, and all other semantic,
safety, evidence, runtime, and variance gates perfect. All 20 non-create groups
failed and no create group failed; V9 is sealed.

D1 then froze 30 fresh inspectable probes across the five non-create actions.
Its valid baseline contained 7 extraction and 14 policy gaps. Sol rejected
Flash's conceptually invalid Gold/taxonomy, recovered under the lease, and
repaired only the reproduced patient-grammar causes. Final D1 is 30/30 with
zero variance and empty selection. A fresh Gemini project returned
`DECISION: pass`; Sol reproduced 70 focused and 280 broader selected nodes with
three documented immutable historical equality deselections. See
`lc4v9d1-sol-acceptance.md` and `bernie-lc4v9d1-development-closeout.md`.

LC4V4 remains sealed. Its attempt-002 aggregate is complete 70/576 and safety
466/576; no rerun or direct remediation is authorized. The D1/D2 authoring
incident, quarantined rows, recovered parser gaps, immutable hashes, historical
equality nodes, and exact veto provenance are preserved in
`docs/handover-ledgers/bernie-language-evaluation.md` and their named Sol
acceptance/closeout records; they are historical, not current baton authority.

### LC4R10 accepted state

LC1-LC4 and LC4R1-LC4R10 are complete. The current development semantic counts
are `880/814/672/154/330/835`; safety is 1,152/1,152; variance is zero over
2,304 samples.

LC4R10 reconciled the remaining frozen 53 clarification and 40 replay contract
populations. All 93 now pass the complete deterministic interpretation,
replay, and scoring path. The post-reconciliation corpus hash is
`sha256:af8f3276a50a2defcf4e4f65570a5dd4de0d252544ff6d695792d63e7e518195`.
No independently supported parser gap remains and no parser remediation is
authorized.

Sol's recovered focused suite passed 20/20 and the final explicit serial
development gate passed 831 nodes after deselecting exactly 22 immutable
historical equality/queue nodes. Gemini 3.5 Flash/medium returned
`DECISION: pass` on exact recovered source head `01d7ac18`. Its prose counted
26 superseded nodes; Sol directly enumerated the six safe implicated modules
and preserved the corrected 22-node count in the acceptance without another
provider round trip.

DeepSeek V4 Flash/high ran once through Claude Code `--bare`; Sol rejected its
conceptual taxonomy failure and recovered under the lease without a correction
loop. Protected holdout v1 remained sealed. T3.1-T3.4 remain intact and blocked
by default; T3.5 and all live/write authority remain deferred. See the LC4R10
acceptance for exact hashes, provenance, recovery, veto, and gate evidence.

### T3R1 accepted state

Yuri selected the provider-free shadow-evaluation direction after synthetic
Silver v2 completed. Sol bound all 192 admitted v2 dialogues into the existing
default-disabled T3 runner. The projection uses only non-executing proposal,
explanation, clarification, and no-action labels; it adds explicit whole-action
withdrawal scoring and variance detection without exposing a product mutation
tool.

The expected-decision echo ran two offline samples per case: 384/384 perfect
and safe, 2,304/2,304 scored dimensions, and zero variance. This is plumbing
evidence only, not model-quality evidence. No external worker received the
projection and no provider prompt or call occurred. The live T3 gate remains
blocked; see the T3R1 closeout and Sol acceptance.

### T3R2-T3R4 accepted state

T3R3 found only DeepSeek mechanically tool-free. Yuri then approved T3R4's pragmatic systems methodology and DeepSeek's synthetic-only retention posture. T3R4 consumed 89 normalized observations: GPT stopped at its frozen token cap, Gemini completed its primary lane, and DeepSeek completed its reduced auxiliary lane. Every successful response was safe; no raw response, protected/historical/external/patient/practice data, runtime, route, database, confirmation, or write authority moved. Two fresh Gemini review attempts returned no decision and are rejected, so the bounded result is accepted without an independent veto and cannot select a production provider.

### T3R5 accepted state
Yuri authorized a no-call Australian-region Gemini/Vertex feasibility and entitlement design. Official documentary evidence shows the current Gemini 3.5 Flash and 3.1 Flash-Lite successors are not available in Sydney. Gemini 2.5 Flash is available in `australia-southeast1` but has only 90 days of documented runway to retirement, below the frozen 180-day floor. Read-only local checks found a keyless impersonated-service-account ADC and the expected dev project, but billing, Vertex API, regional pins, least-privilege IAM, audit/logging/retention enforcement, and cost/kill-switch controls are not all verified.
The deterministic result is `blocked_before_provider_call`; 71 focused/preservation tests pass. No model call, cloud mutation, content transmission, product runtime, route, database, appointment, confirmation, deployment, release, or write authority moved. Reassess only when a current successor is GA in Sydney; even a passing report cannot authorize a call.

### Post-certification security transition

The reusable fresh-certification discipline is captured in
`docs/bernie-fresh-certification-protocol.md`; its bounded meaning and next
sequence are reviewed in `docs/bernie-post-certification-transition-review.md`.
The current security maintenance replaces `python-jose` with fixed-algorithm
PyJWT, restores independent Bandit execution, retains a two-item reviewed
Git-identity baseline, and documents the dev-only `uuid` alert as blocked by
the latest supported TeamsFX dependency graph.

GitHub has CodeQL, Dependabot, Python/Node SCA, Bandit, leakage lint, secret
scanning, push protection, private vulnerability reporting, and protected
`master`. Four stable security contexts are strict and enforced for admins;
normal integration is PR-only. The ten historical high-classified CodeQL
candidates were individually validated, and the later representative hardening
PR cleared the aggregate alert gate without dismissal. Ariadne now enforces
risk-triggered red/blue/purple evidence. See the final security closeout and
`docs/security/codeql-high-validation-2026-07-17.md`.

Metadata-only dialogue-source triage found the appointment-call Kaggle corpus
promising but provenance/privacy-uncertain. Yuri authorized the small local
quarantine pilot; its preliminary provenance and licence-authority gate stopped
before content download because the clinic/data controller, jurisdiction,
collection basis, uploader authority, content-rights chain, redaction method,
and residual-risk audit remain undocumented. No content was downloaded, opened,
transmitted, or admitted. MedInstruct is not Bernie receptionist evidence.

The replacement synthetic pilot exported 96 dialogue-free semantic anchors
from ordinary LC development evidence and generated two noisy
receptionist-to-Bernie candidates per anchor. The first generation wave and
the first reviewed recovery hash were both rejected before admission: the
former for a Sol-owned dialogue-form selector defect, the latter for 18
unsupported correction-operation labels. Fresh DeepSeek and Gemini contexts
each accepted all 192 records on final canonical hash
`sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665`;
Sol admitted the same exact set as development Silver. It is not real-world,
Gold, protected-holdout, certification, provider/runtime, or write evidence.

The authorized robustness baseline then ran the current interpreter, replay,
and scorer twice over all 192 admitted candidates. Exact report hash
`sha256:18501cf5c8d28c0e660a9f5c7b15f7690622e44c90b248d51301c6ece03973c5`
is `baseline_complete`: 384/384 safety, zero variance, but only 2/192 complete
product passes. Fresh Gemini independently reproduced the adapter, no-oracle-
leakage boundary, counts, and hashes and returned `DECISION: pass`. The primary
candidate failures are action extraction 114, temporal/normalization 68,
entity semantics 6, and replay-only 2. No product repair is authorized by the
diagnostic. A broad discovery command emitted protected-path filenames only;
no protected content or label was opened or used, and the incident is
contained as metadata-only.

Yuri then authorized a frozen 24-candidate action/temporal diagnostic and
remediation tranche. The pre-repair population was 0/24 complete. Sol accepted
only bounded extraction rules supported by surfaced dialogue: all 11 action and
10 temporal assertions now pass without hidden duration/time invention. The
final tranche is 2/24 complete, safety 48/48, and zero variance; the full Silver
set improves from 2/192 to 11/192 with safety 384/384 and zero variance. Exact
parent comparison changes 32 authored resize scenarios and no LC4R10
reconciliation scenario. Fresh Gemini independently reproduced the exact
reports, tests, and impact and returned `DECISION: pass`. The tranche closes as
an accepted `partial_pass`; its residuals point to candidate evidence and
oracle/policy coherence, not an automatically authorized parser repair.

Yuri then authorized the all-192 coherence audit and bounded corpus repair.
The frozen pre-repair audit accepted 85 and found 107 invalid rows. Sol repaired
exactly eight missing resize-action surfaces and four schedule-anaphora
referents without changing IDs, spans, semantics, provenance, or authority.
Final current admission is 90 coherent and 102 quarantined: 78 primary oracle-
policy conflicts, 16 whole-action reversal conflicts, and 8 replay-contract
conflicts. All clarification and reversal forms are absent from current
admission. The accepted 90 run twice with 4/90 product complete, safety 180/180,
and zero variance. Fresh Gemini independently reproduced and conceptually
accepted the result. A balanced replacement corpus now requires a new coherent
v2 anchor contract rather than relabelling or parser-fitting these rows.

Yuri then authorized the fresh coherent synthetic Silver v2 anchor contract
and successive evidence-backed ordinary-development refinements. That course
is complete: 96 coherent anchors, 192/192 candidates complete over two
observations each, safety 384/384, and zero variance. Final exact robustness
hash is `sha256:ea4217943fa3a2ec83ec4afcff12cd7eebeba520f225d4e0fb290abb7850dedd`.
Fresh Gemini independently reviewed all 192, passed 70/70 focused tests, and
returned `DECISION: pass`, `POLICY_REPLAY_SCORER_CHANGES: false`, and
`PROTECTED_ACCESS: false`. The standing sequence is exhausted and grants no
synthetic v3, V11, protected evidence, external corpus, provider/runtime,
policy/replay/scorer, API/database/UI, confirmation, deployment/release, or
write authority.

### Earlier LC4V2-V3 sequence

The accepted V2, V2R1, V2R2, V2E1, and V3 evidence, hashes, recovery decisions,
and one-shot results are historical and unchanged. Their full current index is
`docs/handover-ledgers/bernie-language-evaluation.md`; all versions remain
sealed under section 5 and none authorizes provider, runtime, or write access.

## 4. Authority Allocation

This section overrides conflicting historical text in archives, ledgers,
packets, or older Ariadne documents.

- **GPT Sol** is Conductor, sprint planner, architecture and acceptance owner,
  recovery owner, and protected integrator.
- **DeepSeek V4 Flash/high via Claude Code `--bare`** is the preferred
  economical bounded implementation/test worker. Launcher:
  `scripts/ariadne_deepseek_claude.py`.
- **Gemini 3.5 Flash via Antigravity** is the preferred economical peer worker
  and independent veto reviewer. Launcher: `scripts/ariadne_antigravity.py`.
- **DeepSeek Pro is not the Conductor** and must not be launched for planning,
  allocation, acceptance revision, or routine fallback without a new explicit
  instruction from Yuri.
- Deep Code is a real-TTY fallback only, not the default DeepSeek transport.
- Claude/Fable/Opus and native Codex workers are leverage- and
  availability-gated options. They never receive integration authority.
- No external worker or consultant may certify its own corpus, accept its own
  implementation, move the baton, or push protected refs.

Use workers only for bounded separable artifacts or genuine veto surfaces.
Tiny, serial, protected, or tightly coupled work may remain Sol-owned. Record
the actual worker mix and any substitution in closeout evidence.

### Flash complexity and correction-loop rule

DeepSeek Flash is the default for stable, bounded implementation contracts,
mechanical test generation, fixture regeneration, and contained code repair. It
does not own cross-sprint taxonomy, frozen-selection meaning, acceptance
semantics, authority allocation, protected-evidence policy, or reconciliation
of several historical evidence layers. Those remain Sol work.

Classify a rejected Flash candidate before redispatch:

- a mechanical defect (for example a missing hash, file, assertion, or
  one-line verifier guard) may receive at most one bounded same-lane revision;
- a conceptual defect involving category meaning, frozen population versus
  corpus-wide population, acceptance criteria, provenance, or authority moves
  immediately to Sol's recovery lease without another Flash correction loop;
- any failed bounded revision ends external correction for that lane. Preserve
  the failure and scope breaches, then recover under Sol ownership or select a
  genuinely different implementation resource when new implementation work has
  clear leverage.

Large cached-token totals, elapsed time, or model reputation do not alone prove
inability. The stop signal is the kind and recurrence of acceptance error.
Gemini Flash remains a fresh-context independent veto after recovered material
changes; it does not inherit the failed worker's acceptance framing.

## 5. Protected Evidence and Closed Gates

### Protected holdouts v1-v10

Protected holdouts v1, v2, and v3 remain sealed. Protected holdouts v1-v10
share the same no-access boundary. Do not open, enumerate, list, search, import, run, regenerate,
evaluate, hash-check, infer labels from, or tune against any protected fixture,
support module, authoring surface, manifest, seal, receipt, or per-case report.
The committed v2 aggregate report and aggregate closeout are the only v2
evidence available for planning; only the committed aggregate report, closeout,
and Sol acceptance are available for v3-v10 planning. Historical metadata-
enumeration incidents do not authorize reuse.

V10 is consumed and sealed; only its committed aggregate report, closeout,
and Sol acceptance are available for future planning.

Yuri preauthorized successive genuinely fresh holdout versions beginning with
V10 until certification passed, progress stalled, or a material fork arose.
V10 passed, so that standing fresh-version cycle is complete and grants no V11.
Development work uses only ordinary development, Silver/pending, newly authored
synthetic, or otherwise explicitly authorized evidence.

### T3 and providers

T3.1-T3.4 remain intact and blocked by default. The dedicated T3R4 synthetic evaluation exception is consumed and closed. T3R5's no-call feasibility authority is also consumed and closed with `blocked_before_provider_call`. T3.5 runtime adapters, further live calls/external prompts, raw-response persistence, provider-executed tools, promotion claims, and runtime wiring remain deferred.

### Historical diary material

Raw historical diary files may contain PHI. Keep them local and ignored under
`local_data/historical-diary-trove/`. Do not commit them, transmit them to an
external model/provider, retrieve from them at runtime, or fine-tune on them.
H15 approval is limited to the exact bounded payload in
`docs/historical-diary-trove-h15-approved-gate.json`; it does not authorize
broad-trove processing or product/runtime access.

### Product authority

Bernie may explain, clarify, issue bounded read requests, and propose actions.
The native backend remains authoritative for identity, availability,
collisions, status transitions, confirmation, writes, and audit. Do not open a
route/API, database, GraphQL, UI, deployment, confirmation, memory/RAG,
GraphRAG, or write-authority surface unless the sprint explicitly authorizes
it.

## 6. User Decision Boundaries

Continue autonomously through ordinary development-only analysis,
implementation, tests, review, recovery, documentation, commit, and push.
The completed fresh-certification authorization grants no V11. Yuri's
2026-07-17 standing synthetic authorization completed with the accepted v2
course and grants no synthetic v3 or further refinement of the frozen v2
population. Pause before:

- a material clarification-policy or product-behaviour choice;
- holdout reuse, or any new holdout outside the standing fresh-version cycle;
- live-provider calls, T3.5 activation, or sensitive-data transmission;
- historical-trove scope expansion beyond an approved payload;
- material licence or cost acceptance;
- renewed download or inspection of the provenance-blocked appointment-call
  corpus, external coordination with its uploader/data controller, or admission
  of any external dialogue corpus into development evidence;
- API/write-authority, database migration, deployment, production, or release
  changes not already explicitly authorized; or
- an action requiring new external authority or affecting people/systems
  outside the user-provided scope.

Dependabot alert 5 remains open. Do not force dependency overrides.

## 7. Ariadne Operating Rules

### Receipts and workspace isolation

Run `scripts/ariadne_orchestrator_preflight.py` for new-session,
post-compaction, pre-plan, pre-dispatch, verifier-acceptance, integration,
commit, and push continuation events as required by the active profile. A
receipt is evidence only; it cannot spawn workers, realign worktrees,
integrate, commit, or push.

Every worker packet must name its worktree, branch, source head, owned files,
forbidden surfaces, tests, durable artifact, and decision format. Observe
protected-master cleanliness before, during, and after external worker runs.

### Recovery lease

Worker closeout provenance is non-transferable. Sol may adopt failed worker
source only as an untrusted candidate under
`docs/ariadne-orchestrator-recovery-lease.md`. Preserve the failure, record
every Sol amendment, and run risk-proportional independent verification.
Apply the Flash complexity and correction-loop rule above before any
same-lane redispatch.

### Tests

Repository pytest processes that load `tests/conftest.py` share a PostgreSQL
test schema and must run serially. Do not parallelize them merely because file
lists differ. Historical committed-report equality nodes may be intentionally
deselected only when the active acceptance document records why their frozen
artifacts must not be regenerated.

The known pre-existing node
`tests/test_bernie_interpretation_runtime_isolation.py::test_runtime_app_code_does_not_import_interpretation_harness_tooling`
rejects the intentionally configured blocked-gate path in `app/config.py`.
Treat it as a documented baseline until a separate maintenance sprint resolves
the contract; do not misattribute it to LC work.

### Git and handoff

- Sprint 156 status/delete confirm client header emission is the accepted historical closeout marker.
- Preserve unrelated user changes in a dirty tree.
- Workers commit only to disposable/task branches and do not push protected
  refs.
- Sol reviews and integrates through a check-gated pull request, then advances
  `master` and `handoff/current`.
- Fetch and verify origin immediately before push. Never force protected refs.
- GitHub Pages deploys only from canonical `master`; a stale worker deployment
  can overwrite the live artifact.

Useful commands:

```powershell
python scripts\agent_worktrees.py handin
python scripts\agent_worktrees.py sync --fetch
python scripts\agent_worktrees.py submit --agent claude --commit-message "..." --message "..."
python scripts\agent_worktrees.py handoff --agent codex --commit-message "..." --message "..."
```

## 8. Product and Environment Guardrails

- Word Online is the target Office surface and is stricter than desktop Word
  about OOXML element order.
- The native browser Diary supersedes the retired Word-table diary for
  interactive scheduling.
- Use the API Spine contracts under `docs/api-spine/` whenever work touches
  GraphQL/read models, REST/OpenAPI commands, proposals/confirmations, Access
  AI, context frames, manifests, async contracts, audit, security, or
  idempotency.
- Production settings fail closed for default secrets and CORS is allowlisted.
  PostgreSQL RLS, comprehensive audit logging, JWT storage hardening, and
  field-level encryption remain structural security work.

Local orientation:

```powershell
.\run_dev.ps1
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Taskpane source is `EMR4 Sidebar/src/taskpane/`; synchronize its published
`docs/taskpane/` copy with `sync_taskpane.py`. Command Centre lives in
`docs/command-centre/`; native Diary assets live in `docs/diary/`.

## 9. Historical and Topic Index

The complete pre-compaction handover is preserved byte-for-byte at:

- `docs/handover-archive/AGENTS-2026-07-15-pre-compaction.md`
- manifest:
  `docs/handover-archive/AGENTS-2026-07-15-pre-compaction.manifest.json`
- SHA-256:
  `ad86887db6b640bdeac40111aa9f83c9e422f4ccab5f2eb61334a49449126b4c`
- source Git blob: `ace44b93507737141a5e44004c24a087755561af`
- source commit: `6801fb214d41c41c14f94b90642f6a7d9ee0a6d6`

Every paragraph removed during the 2026-07-15 compaction remains in that
immutable, manifest-tested snapshot. Archived history does not override this
live file.

Topic ledgers:

- `docs/handover-ledgers/bernie-language-evaluation.md`
- `docs/handover-ledgers/orchestration-and-agent-runtime.md`
- `docs/handover-ledgers/historical-diary-and-interpretation.md`
- `docs/handover-ledgers/product-platform-api-and-security.md`
- index: `docs/handover-ledgers/README.md`
- compaction closeout: `docs/handover-compaction-2026-07-15.md`

Use the ledgers to find authoritative closeouts and policy documents. Use the
immutable snapshot only for full historical reconstruction, retired workflow
details, or provenance not yet represented in a dedicated closeout.

## 10. Updating This Handover

Update this live file whenever current authority, baton state, protected
boundaries, active acceptance, or next work changes. Put chronological detail
in the appropriate topic ledger or sprint closeout rather than expanding the
live file indefinitely.

Before ending a material session:

1. run relevant checks and `git diff --check`;
2. update active acceptance and the Current Baton;
3. commit intentional changes;
4. align and push `master` plus `handoff/current`; and
5. verify origin refs and a clean integration worktree; and
6. send the non-PHI Pushover closeout ping with
   `scripts/notify_sprint_closeout.py`, stating whether the sprint engine is
   continuing or paused and the concrete next work or pause reason. If delivery
   fails, report that explicitly in the in-thread closeout.

The user can say **"update the handover doc"** at any time to trigger a live
baton refresh.

---

*Compacted 2026-07-15 after LC4R8. Full predecessor integrity is enforced by
`tests/test_agents_handover_archive.py`.*
