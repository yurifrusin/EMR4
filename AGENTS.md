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

Use a fresh chat context for each named tranche by default. The new context must
repeat this full rehydration before acting; prior-chat memory never substitutes
for the five sources. Durable decisions that must survive the handoff belong in
this file and the active plan/evidence documents. The outgoing tranche must name
its exact result, artifacts, unresolved gates, next tranche, and reasoning level.

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
| Active product track | Yuri accepted the strategic transition review and paused the provider lane without retry. Stages 1 and 2 passed the local synthetic provider-free appointment-create vertical and its durable authority/security foundation through protected PRs 36-39. Yuri then accepted a strategic product north star: make routine Diary work possible without scanning a grid or entering a form by making *bernie* the conversational twin of the living Diary, while FastAPI/PostgreSQL remains authoritative. This reshapes the Stage 3 decision but does not authorize Stage 3 execution |
| Active acceptance | `docs/bernie-stage2-durable-authority-recovery-security-plan.md`, `docs/security/bernie-stage2-threat-model-delta.md`, `orchestration/agent_inbox/codex/bernie-stage2-plan-sol-review.md`, `orchestration/agent_inbox/codex/bernie-stage2-durable-authority-rehydration-receipt.json`, `orchestration/agent_inbox/codex/bernie-stage2-durable-authority-preplan-receipt.json`, `orchestration/agent_inbox/codex/bernie-stage1-tranche-d-extra-high-sol-acceptance.md`, `orchestration/agent_inbox/codex/bernie-stage1-regression-harness-maintenance-sol-acceptance.md`, `docs/bernie-stage1-regression-harness-maintenance-plan.md`, `orchestration/agent_inbox/codex/bernie-stage1-tranche-d-sol-acceptance.md`, `docs/bernie-stage1-provider-free-supervised-booking-acceptance-plan.md`, `orchestration/agent_inbox/codex/bernie-stage1-acceptance-plan-sol-review.md`, `docs/bernie-current-strategic-transition-review.md`, `orchestration/agent_inbox/codex/lc4v10-sol-acceptance.md`, `docs/bernie-lc4v10-fresh-certification-closeout.md`, `orchestration/agent_inbox/codex/security-hardening-final-purple-acceptance.md`, `docs/security/secure-sdlc-red-blue-diary-hardening-closeout-2026-07-17.md`, `docs/bernie-post-certification-transition-review.md`, `orchestration/agent_inbox/codex/appointment-call-quarantine-pilot-sol-acceptance.md`, `docs/bernie-appointment-call-quarantine-pilot-closeout.md`, `docs/bernie-synthetic-silver-v2-anchor-contract.md`, `docs/bernie-synthetic-silver-v2-closeout.md`, `orchestration/agent_inbox/antigravity/synthetic-silver-v2-final-review.md`, `orchestration/agent_inbox/codex/synthetic-silver-v2-sol-acceptance.md`, `docs/bernie-t3r1-synthetic-shadow-refresh.md`, `docs/bernie-t3r1-synthetic-shadow-baseline.json`, `orchestration/agent_inbox/codex/t3r1-synthetic-shadow-refresh-sol-acceptance.md`, `docs/bernie-t3r2-synthetic-live-comparison-approval.json`, `docs/bernie-t3r3-three-lane-transport-preflight-closeout.md`, `docs/bernie-t3r4-pragmatic-live-comparison-approval.json`, `docs/bernie-t3r4-pragmatic-live-comparison-report.json`, `docs/bernie-t3r4-pragmatic-live-comparison-closeout.md`, `orchestration/agent_inbox/codex/t3r4-pragmatic-live-comparison-sol-acceptance.md`, `docs/bernie-t3r5-vertex-au-feasibility-and-entitlement-design.md`, `docs/bernie-t3r5-vertex-au-readiness-report.json`, `docs/bernie-t3r5-vertex-au-feasibility-closeout.md`, `orchestration/agent_inbox/codex/t3r5-vertex-au-feasibility-sol-acceptance.md`, `docs/bernie-t3r6-us-synthetic-development-policy.md`, `docs/bernie-t3r6-us-synthetic-development-report.json`, `docs/bernie-t3r6-us-synthetic-development-closeout.md`, `orchestration/agent_inbox/codex/t3r6-us-synthetic-development-sol-acceptance.md`, `docs/bernie-t3r7-vertex-sydney-live-report.json`, `docs/bernie-t3r7-vertex-sydney-live-closeout.md`, and `orchestration/agent_inbox/codex/t3r7-vertex-sydney-live-sol-acceptance.md` |
| Stage 2 acceptance | `orchestration/agent_inbox/codex/bernie-stage2-durable-authority-sol-acceptance.md`, `docs/bernie-stage2-durable-authority-recovery-security-closeout.md`, `orchestration/agent_inbox/codex/bernie-stage2-durable-authority-restored-preintegration-receipt.json`, and `orchestration/agent_inbox/codex/bernie-stage2-durable-authority-preacceptance-receipt.json` |
| Product north star | `orchestration/agent_inbox/codex/bernie-conversational-diary-north-star-sol-review.md`, `docs/bernie-conversational-diary-north-star.md`, `docs/bernie-stage3-conversational-diary-decision.md`, `docs/bernie-stage2-technical-workflow-retrospective.md`, `orchestration/agent_inbox/codex/bernie-conversational-diary-north-star-rehydration-receipt.json`, `orchestration/agent_inbox/codex/bernie-conversational-diary-north-star-preplan-receipt.json`, and `orchestration/agent_inbox/codex/bernie-conversational-diary-north-star-preacceptance-receipt.json` |
| Current result | Stage 2 remains final `stage2_pass`. The accepted strategic direction is the death of the Diary as an interaction burden, not as an authoritative system. The reshaped Stage 3 hypothesis is whether reception staff can safely obtain answers and complete the supported appointment-create task conversationally without using the grid. Repository review recommends opt-in auto-merge under unchanged strict protections, a separate pinned Ruff/tooling tranche rather than an ad-hoc install, and Sol-first adaptive single-thread ownership for tightly coupled work. No repository setting, dependency, participant, voice, provider, PII, production, deployment, release, new action, or Stage 3 authority moved |
| Next implementation | Remain paused pending Yuri's Stage 3 decision on participants, synthetic task/comparison protocol, acceptance thresholds, typed-first versus any later explicit push-to-talk modality, observation retention, and evidence-only versus bounded correction authority. Do not begin Stage 3, ambient listening, or any provider, protected, historical, PII, production, deployment, release, additional action, GraphQL mutation, production-role/encryption, retention-scheduler, or autonomous-confirmation work |

### Compact historical evaluation and transition state

The detailed language-evaluation chronology is indexed in
`docs/handover-ledgers/bernie-language-evaluation.md`; the active acceptance
documents in the Current Baton remain authoritative. The compact facts needed
for present decisions are:

- LC4V6-V9 are consumed and sealed historical certification attempts. V9D1
  found 7 extraction and 14 policy gaps, repaired only reproduced ordinary
  development patient-grammar causes, passed its focused/broader gates, and
  received a fresh Gemini pass. See `lc4v9d1-sol-acceptance.md`.
- LC4R10 completed the ordinary-development reconciliation at semantic counts
  `880/814/672/154/330/835`, safety 1,152/1,152, and zero variance over
  2,304 samples. No independently supported parser gap remains.
- LC4V10 fresh certification passed with `certification_pass`: complete and every dimension 576/576,
  safety 576/576, and zero variance. The authoritative
  records are `orchestration/agent_inbox/codex/lc4v10-sol-acceptance.md` and
  `docs/bernie-lc4v10-fresh-certification-closeout.md`. No V11 is needed or authorized; the standing fresh-version cycle is complete.
- Synthetic Silver v2 completed with 96 coherent anchors, 192/192 accepted
  candidates complete over two observations, safety 384/384, and zero variance.
  It remains frozen ordinary-development evidence, not real-world, Gold,
  protected-holdout, provider/runtime, production, or write evidence.
- T3R1 proved only provider-free projection plumbing. T3R2-T3R4 produced bounded
  synthetic comparison/preflight evidence without selecting a production
  provider. T3R5-T3R6 remain no-call/readiness policy evidence. T3R7 consumed
  11/48 exact Sydney synthetic calls and stopped without retry on its first
  schema-invalid response; unused calls carry no authority.
- The provider lane remains paused. The T3R6 US synthetic-development policy
  begins no earlier than 2026-10-16 but grants no continuing call, prompt,
  cost, runtime, PII, production, or write authority. Australian production/PII
  review remains no earlier than 2027 unless Yuri changes that policy.
- The post-certification security transition, protected holdout history,
  appointment-call provenance stop, historical-diary limits, synthetic corpus
  lineage, exact hashes, worker failures/recoveries, and provider observations
  remain available through the Current Baton documents and topic ledgers. They
  are historical context and do not broaden current authority.
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

### Worker-lane economy rule

Dispatch is an optimization, not a default. Sol keeps a task when its execution
is serial, stateful, tightly coupled to a disposable runtime/database, or small
enough that writing the worker packet plus monitoring, review, and recovery is
likely to cost as much as direct completion. This includes short live-browser
acceptance sequences whose scenarios share one mutable synthetic database.

Use DeepSeek Flash through Claude Code `--bare` when a stable, separable packet
can own a mechanical script, focused tests, fixture regeneration, or contained
repair and can return one durable artifact without acceptance judgment. Use
Gemini Flash primarily for a fresh independent veto or a genuinely separable
peer check, not as a second conductor for routine execution. A dispatch should
normally save at least one meaningful implementation/test cycle or supply
independence required by acceptance; otherwise Sol executes locally. Never
split a serial acceptance run merely to maximize worker utilization.

Native subagents follow the same rule. Sol may use them for parallel read-only
analysis, independent reproduction, or separable implementation/test artifacts
when their packet is bounded and their expected leverage exceeds briefing,
monitoring, review, and correction cost. They do not receive acceptance,
integration, baton, or protected-ref authority.

### Reasoning-level and closeout rule

Reasoning level follows decision risk; it is not a ceremonial Git gate. Sol at
High may plan and execute a frozen bounded tranche, review its own complete
evidence, integrate, commit, push through the normal protected-branch workflow,
advance the baton after acceptance, and send closeout notification. A second
Sol Extra High pass is not required merely because the implementation or
execution was performed at High.

Pause and use Extra High before:

- freezing or materially revising acceptance meaning, architecture, authority
  allocation, product policy, or user-visible behaviour;
- choosing among material privacy, protected-evidence, provider/cloud,
  production, release, migration, durable-session, security, licence, cost, or
  data-retention alternatives;
- overriding a failed gate, reconciling contradictory or incomplete evidence,
  accepting a conceptual recovery, or making a claim broader than the frozen
  evidence directly supports; or
- any point where the active plan or Yuri explicitly requires Extra High for a
  named material decision.

High remains sufficient for mechanical corrections already permitted by a
frozen plan, focused tests, deterministic harness/Playwright work, evidence
packaging, routine review, and check-gated Git closeout when no item above is
triggered. A fresh tranche chat is a context-hygiene rule, not a requirement to
change reasoning level or agent identity.

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

The provider-experimentation lane is paused by Yuri without T3R7 retry. T3.1-T3.4 remain intact and blocked by default. The dedicated T3R4 and T3R7 synthetic evaluation exceptions are consumed and closed. T3R5 remains historical no-call evidence. T3R6 authorizes a US synthetic-development policy from 2026-10-16 but no continuing provider call, prompt transmission, cost acceptance, runtime, PII, or production authority. T3.5 adapters, further live calls/external prompts, raw-response persistence, provider-executed tools, promotion claims, and runtime wiring remain deferred.

### Historical diary material

Raw historical diary files may contain PHI. Keep them local and ignored under
`local_data/historical-diary-trove/`. Do not commit them, transmit them to an
external model/provider, retrieve from them at runtime, or fine-tune on them.
H15 approval is limited to the exact bounded payload in
`docs/historical-diary-trove-h15-approved-gate.json`; it does not authorize
broad-trove processing or product/runtime access.

### Product authority

Bernie may explain, clarify, read bounded context, and propose. The backend owns
identity, availability, conflicts, confirmation, writes, and audit. Do not open
API/database/GraphQL/UI/deployment/memory/RAG/write authority unless explicitly
authorized. Stage 1 permits only its local synthetic Diary/FastAPI/PostgreSQL
path: proposals do not mutate; staff confirms; the existing REST command may
create exactly one appointment, audit, idempotency result, and typed receipt.

## 6. User Decision Boundaries

Continue autonomously through ordinary development-only analysis,
implementation, tests, review, recovery, documentation, commit, and push. The
completed fresh-certification and v2 authorizations grant no V11, synthetic v3,
or frozen-v2 refinement. Yuri's 2026-07-18 Stage 1 authorization permits only
the tranches and confirmed synthetic appointment-create path in its frozen plan;
it begins read-only and returns to Yuri for any material fork. Pause before:

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

### Browser automation and evidence

Acceptance depends on the exercised path and interception boundary, not on
whether the browser is driven interactively or by a script. A task-scoped
Playwright script is equivalent to interactive browser control when it drives a
real browser through the ordinary UI, makes real non-intercepted calls to the
intended local or deployed backend, and records the required screenshots,
sanitized outcomes, and backend/database readback. Prefer a Playwright script
for repeatable multi-scenario acceptance when selectors and fixtures are stable;
interactive browser control remains useful for exploration and visual diagnosis.

The evidence label remains strict:

- no API interception or mocked transport, real local UI/backend/database:
  `live_local_browser_backend_postgres`;
- direct real local HTTP/backend/database support without a browser:
  `live_local_backend_postgres`;
- `page.route(...)`, fixture responses, mocked APIs, or equivalent interception:
  `route_intercepted_browser`.

Do not call route-intercepted evidence live. Do not let a Playwright script
bypass explicit staff confirmation, call internal page functions as a substitute
for the visible UI action, or fabricate receipt/readback evidence. For protected-
safe work, scripts must use the active exact-path and exact-node allowlist and
must not introduce repository-wide discovery. Browser processes and PostgreSQL-
loading pytest processes remain serial when they share mutable runtime state.

### Git and handoff

- Sprint 156 status/delete confirm client header emission is the accepted historical closeout marker.
- Preserve unrelated user changes in a dirty tree.
- Workers commit only to disposable/task branches and do not push protected
  refs.
- Sol High may commit and push its own accepted bounded work; Git authority does
  not require an additional Extra High pass. An accurately labelled partial
  result may be committed to a task branch/PR, but protected integration, baton
  movement, and a final product-stage claim wait for the applicable acceptance
  gates.
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
