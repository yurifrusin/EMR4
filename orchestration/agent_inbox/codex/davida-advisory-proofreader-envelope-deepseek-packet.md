# Davida advisory proofreader envelope — DeepSeek worker packet

Source head: `b957ed7623310206cf5f4970e1eb91241c73ef6f`

Worktree: `C:\Users\sarashera\EMR4-worktrees\davida-advisory-proofreader-envelope`

Branch: `codex/davida-advisory-proofreader-envelope`

Model/transport: exact DeepSeek V4 Flash/high through Claude Code `--bare`.
No fallback is authorised.

## Mandatory source pass

Read `AGENTS.md` completely and state the exact five rehydration sources. Read
the EMR4 API Steward skill and its review checklist completely. Read this
packet, the accepted Bernie/Davida seam, Davida boundary and pure-read plans,
designs, threat deltas, contracts and closeouts, plus only the exact accepted
context implementation named below. Verify exact branch/source and a clean
worktree before editing.

Yuri has clarified the continuous-tranche protocol: after a successful
continuing Pushover closeout, the conductor starts the next already-authorised
tranche immediately. That grants no additional product, data, provider, Git or
deployment authority to this worker.

## Task

Implement Davida tranche 2 as a provider-free, unmounted and unoccupied typed
interpretation/proofreader envelope. It consumes one already accepted authored-
synthetic `PracticeAdministrationContextFrame`, admits exactly the two advisory
operations, and releases only a strict structured, deterministically grounded,
non-authoritative advisory draft.

Candidate input contains selectors only—never caller/model-authored prose,
counts, claims or values. The deterministic proofreader constructs every
released field from the accepted context. There is no model/provider call,
memory, database, network, clock read, route, GraphQL field, proposal, apply,
confirmation or write.

## Owned files

- `app/schemas/practice_administration_advisory.py`
- `app/services/practice/practice_administration_advisory_proofreader.py`
- `docs/davida-provider-free-practice-administration-advisory-plan.md`
- `docs/davida-provider-free-practice-administration-advisory-design.md`
- `docs/security/davida-provider-free-practice-administration-advisory-threat-model-delta.md`
- `orchestration/continuity/davida-provider-free-practice-administration-advisory/advisory-contract.json`
- `orchestration/continuity/davida-provider-free-practice-administration-advisory/advisory-contract.schema.json`
- `scripts/davida_provider_free_practice_administration_advisory_acceptance.py`
- `tests/test_davida_provider_free_practice_administration_advisory.py`

The acceptance script may write evidence only when root later invokes it with
an explicit output path:
`orchestration/continuity/davida-provider-free-practice-administration-advisory/provider-free-unoccupied-evidence.json`.
Do not create or commit that evidence now.

Do not edit any other path. Especially forbidden: `AGENTS.md`, all accepted
parent artifacts, `app/schemas/practice_administration.py`,
`app/services/practice/active_location_directory_read.py`,
`app/services/practice/practice_administration_context_desk.py`, `app/main.py`,
routers, GraphQL, models, migrations, auth, API Spine/manifests, `docs/diary/**`,
`docs/branding/**`, Diary-lane paths, workflows, harness settings,
Continuity/Compass global maps, protected evidence and refs.

## Frozen envelope contract

- Closed operation type contains exactly `ADVISORY_EXPLAIN_DIRECTORY` and
  `ADVISORY_SUMMARIZE_DIRECTORY`. Every accepted parent proposal operation,
  apply/confirmation/write code and unknown operation is unavailable and fails
  closed.
- Strict extra-forbid, frozen candidate envelopes bind the exact context schema
  v1, `practice_ref`, `principal_ref`, `correlation_id`, `content_revision`,
  `authority_class=advisory`, and literal-false `writes_authorized`,
  `proposal_authorized` and `confirmation_authorized` fields.
- Explain requires exactly one `subject_kind` (`practitioner` or `location`) and
  one opaque `subject_ref`. Summary admits no target, caller-supplied count,
  prose, template, claim, fact value or open selector.
- The proofreader alone emits a strict structured draft with
  `authority_label=model_interpretation`,
  `evidence_mode=provider_free_unoccupied_authored_synthetic`,
  `status=advisory_only`,
  `presentation=structured_fields_only_no_html_or_markdown`, one closed fixed
  template code, payload copied/derived from exact context rows, grounding
  paths/digest, and exact context binding.
- The released authority ceiling sets command, confirmation, proposal, apply,
  write, provider, memory, database, network, event and model-to-database fields
  to literal false. No human-confirmation, signed-command, arbitrary text or
  mutating release shape exists.
- Result is an exact discriminated released/rejected union. Both carry a
  candidate hash, context revision and one closed verdict/reason.
  `repair_performed=false` and `retry_authorized=false`. A released draft is
  present only on exact pass; rejection has no partial payload.

## Frozen proofreader order

1. Require a bounded canonical raw candidate and exact operation allowlist;
   proposal/apply/unknown operations terminate before interpretation.
2. Strict candidate schema and extra-field admission.
3. Validate the accepted `PracticeAdministrationContextFrame`, exact blocked
   sources, authority ceiling and labels; independently recompute the accepted
   SHA-256 content revision without changing the parent algorithm.
4. Require exact practice/principal/correlation/revision equality.
5. Require caller-supplied timezone-aware `evaluated_at` in the half-open range
   `[observed_at, expires_at)`; never read system time.
6. Require the literal-false candidate authority ceiling.
7. For explain, resolve the subject ref exactly once in the declared frame/kind;
   if a practitioner has a default-location ref, require it resolves to one
   active supplied location.
8. For summary, derive counts from actual row lengths; for explain, derive exact
   fields from the matched row. Candidate-supplied fact values are impossible.
9. Compute canonical candidate/grounding hashes and atomically release the one
   structured draft.

No repair, inference, retry, lookup, generated prose, partial release or
mutation of the supplied context is permitted.

## Deterministic acceptance

Exercise positive empty/non-empty summary, practitioner explain with and
without role/default location, location explain and repeated byte/hash
determinism. Validate the exact machine contract against its schema and mutate
every nested authority/shape-bearing field to prove fail-closed admission.

Adversarial cases must include all four accepted parent proposal operation
codes, apply/unknown/missing operation, extra free-text/provider/memory/DB/
network/clock/write fields, true authority flags, scope/correlation/revision
mismatch, tampered context row with old revision, altered blocked source/source
label/active-only/authority ceiling, naive/before-observed/at-expiry time,
missing/duplicate/wrong-kind target, dangling default-location ref,
over-bounded/noncanonical input and impossible partial release. AST/static
checks prove no SQLAlchemy/model/database/requests/httpx/socket/provider/memory
imports and no `now`, `utcnow` or `time` call.

Evidence persists only exact label, case/verdict counts, booleans and hashes—no
names, refs, rows, prompts, DSN or raw candidates. Evidence label is exactly
`provider_free_unoccupied_authored_synthetic`. Proposed terminal result:
`provider_free_practice_administration_advisory_proofreader_pass`.

## API Spine

This is a non-authoritative context-to-advisory transform only. GraphQL remains
read-only and unused by the proofreader. REST command plane is unused. There is
no event or manifest change. No idempotency/audit command fields are appropriate
because there is no mutation or external effect. The older prototype Davida
charter is not broadened; mounting or charter alignment is a later decision.

## Verification and commit

Do not run repository pytest or PostgreSQL; root owns the serial test lease. You
may run Ruff, py_compile, schema validation, direct import-free/pure-function
checks and diff hygiene. Commit only the nine owned files with explicit
`git add -- <path...>`. Verify the cached list is exact and contains no
`docs/branding/`. Never use `git add -A` or `git add .`. Do not fetch, merge,
rebase, switch or push.

At most one later mechanical repair is eligible. Any change to operation
vocabulary, authority meaning, arbitrary prose, parent context contract,
provider/model occupancy, route, database or command boundary is conceptual and
must return immediately to Sol.

Return the five-source statement, exact commit/files/checks/blockers and finish
with exactly one terminal `DECISION: pass` or `DECISION: revision_required`.
