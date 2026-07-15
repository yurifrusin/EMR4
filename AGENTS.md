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
| Active product track | Bernie language coverage repair after accepted LC4R8 |
| Active acceptance | `orchestration/agent_inbox/codex/lc4r8-sol-acceptance.md` |
| Current result | Exit counts `0/0/11/53/40`; status `blocked_pending_generator_repair_and_contract_reconciliation` |
| Next implementation | LC4R9: frozen 11-case generator-backed audit-vocabulary repair |

### LC4R8 accepted state

LC1-LC4 and LC4R1-LC4R8 are complete. The current development semantic counts
are `880/814/628/101/300/782`; safety is 1,152/1,152; variance is zero over
2,304 samples.

LC4R8 established:

- 53 clarification records all have upstream semantic-contract defects;
  zero are ready for a material clarification-policy choice;
- 51 replay/contract records split into 11 audit-vocabulary-only, 11
  clarification-tool/contract conflicts, 28 creation/replay-policy conflicts,
  one negated-surface/create-contract conflict, and zero genuine replay
  integration defects;
- only the frozen 11-case audit-vocabulary subset is authorized for LC4R9;
- no parser remediation is currently authorized.

Sol's recovered focused suite passed 88/88. Gemini returned `DECISION: pass` on
exact reviewed source head `1824de50`. The expanded clean preservation gate
completed with 1,595 passes, one expected xfail, and one established skip over
1,597 selected nodes. It excluded the documented pre-existing interpretation
runtime-isolation baseline plus three historical exact-report nodes. See the
acceptance document for exact provenance and hashes.

### Next sequence

1. Preserve this compact-handover maintenance as a standalone verified commit.
2. Plan LC4R9 against the exact 11-case selection from LC4R8.
3. Change the source generator/contract, never generated fixtures in place.
4. Freeze and independently review the exact regenerated delta.
5. Recompute development-only evidence once and define the LC4R exit gate.
6. Keep corpus reconciliation separate from parser remediation.

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

### Protected holdout v1

Protected holdout v1 remains sealed. Do not open, enumerate, list, search,
import, run, regenerate, evaluate, hash-check, infer labels from, or tune
against any protected fixture, support module, seal, receipt, or report. A
historical metadata-enumeration incident does not authorize reuse.

Before future certification, Yuri must approve either a new holdout version or
an explicit reuse policy. Development work uses only ordinary development,
Silver/pending, synthetic, or otherwise explicitly authorized evidence.

### T3 and providers

T3.1-T3.4 remain intact and blocked by default. T3.5 provider adapters, live
provider calls, external prompts, raw-response persistence, provider-executed
tools, promotion claims, and runtime wiring remain deferred.

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
Pause before:

- a material clarification-policy or product-behaviour choice;
- holdout reuse or creation of a new holdout version;
- live-provider calls, T3.5 activation, or sensitive-data transmission;
- historical-trove scope expansion beyond an approved payload;
- material licence or cost acceptance;
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

- Preserve unrelated user changes in a dirty tree.
- Workers commit only to disposable/task branches and do not push protected
  refs.
- Sol reviews and integrates, then advances `master` and `handoff/current`.
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
5. verify origin refs and a clean integration worktree.

The user can say **"update the handover doc"** at any time to trigger a live
baton refresh.

---

*Compacted 2026-07-15 after LC4R8. Full predecessor integrity is enforced by
`tests/test_agents_handover_archive.py`.*
