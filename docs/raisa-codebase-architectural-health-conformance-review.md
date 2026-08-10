# EMR4 codebase architectural-health and conformance review

Date: 2026-08-11

Reviewed source: `95ce6b75723d57e672858619c3621d4a273c1f34`

Decision: `accepted_with_bounded_corrective_successor`

## Executive result

The architecture remains directionally sound. The live API still has the
right authority shape: GraphQL is a scoped read plane; canonical mutations are
REST/OpenAPI commands; events are signals that trigger fresh reads; model and
product descendants are default-off; and accepted Context Fabric durability
work remains unapplied and unmounted. No P0 finding or current patient/clinical
authority breach was found.

The review did find two P1 conformance defects that should be corrected before
starting AES-C0: the authoritative handover contained one stale next-work row,
and the protected-branch Python workflow can pass without compiling or testing
the declared Python 3.11 application surface. The latter is demonstrated by a
tracked, non-mounted historical module containing Python-3.12-style f-string
syntax while Ruff is configured for Python 3.11. A focused API Spine suite also
reproduced one P2 historical-contract failure after the practitioner directory
evolved.

The stale handover row is corrected in this closeout. The remaining P1/P2
verification and lifecycle defects form one narrow, provider-free conformance-
repair tranche. That repair is the next safe action under standing authority;
it is not a broad refactor and does not delay the strategic containment
direction beyond the minimum necessary correction.

## Method

The review reconstructed the mounted FastAPI route set, actual GraphQL schema,
default-off configuration gates, accepted-unmounted Context Fabric and Bureau
artifacts, API Spine decision history, verification workflows and source hot
spots. It traced read, appointment command, event consequence and future Bureau
paths against the API Spine and the model-required deterministic-authority
doctrine.

Deterministic checks included:

- 79 focused API Spine and practitioner-directory tests passing before the one
  reproduced historical inventory failure;
- 22/22 repository-maintenance and GraphQL shell/hardening tests passing;
- whole-`app` Ruff inspection under the repository's `py311` target, which
  found the target-incompatible syntax and 33 removable unused imports; and
- `git diff --check` passing.

No provider, external retrieval, product/patient data, runtime gate, database
behavior harness, command, migration, deployment or protected ref was opened.

## Healthy invariants confirmed

1. `app/graphql/schema.py` defines Query-only health and practice practitioner
   reads. Runtime tests at
   `tests/test_practitioner_directory_graphql_runtime_shell.py:34` and
   `tests/test_practitioner_directory_graphql_contract_hardening.py:41` reject
   Mutation/Subscription and unexpected fields.
2. Practitioner GraphQL reuses the same scoped read service as REST; resolver
   tests cover authentication, pagination, sensitive-field absence and cross-
   practice non-disclosure.
3. Appointment writes require mutating roles. Canonical confirmation paths
   claim durable idempotency, validate, audit and read back state.
4. Committed events remain typed signals and the runtime defaults off.
5. Rayleen A4/A5, Reception One product context and Davida B4 have separate
   default-off settings and practice/secret gates in `app/config.py:95` through
   `app/config.py:131`.
6. The development fixture router is both `ENVIRONMENT=dev`-gated and
   authenticated (`app/routers/bernie_dev.py:31` and
   `app/routers/bernie_dev.py:272`).
7. Context Fabric database evidence remains an unmounted proof; no migration,
   watcher, source or operational persistence was inferred from artifact
   presence.

## Findings

### P1-01 — Protected Python checks do not enforce the declared application target

The Python workflow selects Python 3.11 at
`.github/workflows/python-security.yml:24`, but its only correctness-like step
runs `verify_repository.py --profile ci-lint` at line 32. That profile runs
Ruff on the hand-maintained `RUFF_PATHS` list and a historical-data leakage
lint; it does not compile the application or run the focused test profile
(`scripts/verify_repository.py:95` through `scripts/verify_repository.py:145`).

The allowlist includes routers and selected service paths but excludes the
whole `app/services/bernie` tree except `session.py` and `session_store.py`
(`scripts/verify_repository.py:21` through `scripts/verify_repository.py:45`).
`tests/test_repository_maintenance.py:55` currently locks that blanket
exclusion in as an invariant.

Whole-application Ruff inspection under `target-version = "py311"`
(`pyproject.toml:19`) found invalid Python-3.11 f-string quoting at
`app/services/bernie/lc4v4d4_composed_evidence.py:572` through line 589. The
module is sealed historical evaluation machinery and is not imported by the
mounted product, so this is not a current runtime outage. It nevertheless
proves that protected checks can accept tracked application-namespace source
that is incompatible with the declared target.

Required correction: replace the unsafe blanket omission with an explicit
source-state manifest or narrowly enumerated protected exclusions; compile and
Ruff-check every `mounted_current`, `mounted_default_off` and maintained
`accepted_unmounted` Python source under Python 3.11 in CI; run a bounded
correctness test profile on pull requests. Historical holdout material must
remain closed and must not be inspected merely to broaden coverage.

### P1-02 — Authoritative handover contained a stale execution instruction

Before this review, `AGENTS.md:31` still named parse/catalogue source
`2f0047cd...` and directed behavior rebind/attempt 016, while `AGENTS.md:46`
recorded accepted attempt 048 and line 47 correctly named this review next.
Because mandatory rehydration treats the live file as authoritative, the stale
row could have caused a closed database experiment to be repeated or its
protected evidence boundary to be misunderstood.

Correction: this closeout rewrites the Required Git relation row to the actual
reviewed task head and protected refs. The repository fitness set should add an
exact cross-row baton-consistency check so contradictory current/next state
cannot be committed.

### P2-01 — API Spine history lacks a canonical supersession index

`docs/api-spine/external-router-read-model-gap-inventory.md:28` still says the
practitioner directory has no route. The later readiness review records the
implemented route at
`docs/api-spine/practitioner-directory-post-implementation-readiness-review.md:11`,
and current code mounts it at `app/routers/practice.py:14`; the GraphQL resolver
also now exists.

The historical test still defines the practitioner surface as a `route_gap`
and omits `app/routers/practice.py` from its route search
(`tests/test_api_spine_external_read_model_gap_inventory.py:19` and lines
173-186). Its SDL fragment assertion at lines 159-170 also drifted when
pagination arguments were added. The focused review run therefore stopped at
one reproducible failure after 79 passes.

Required correction: preserve the historical packet, but mark it superseded
through a canonical API Spine lifecycle index and convert its current-state
assertions into historical-byte or monotonic-transition assertions. Add a
machine-readable current surface/status index as the sole input to current-
state conformance tests.

### P2-02 — Appointment responsibilities have accumulated in one change hotspot

`app/routers/appointments.py` is 8,658 lines with 36 route decorators, 189
top-level functions and 33 imports. It combines ordinary reads, raw
compatibility CRUD, canonical proposal/confirm commands, audit/idempotency,
Bernie session behavior, interpretation, slot search, product-context planning,
committed-event behavior and Rayleen descendants.

The paths are individually gated, but the concentration increases review
surface, import side effects and the chance that a change in one lane affects
another. It also makes state classification harder because current, legacy and
default-off functions share one module.

Required correction: do not perform a broad rewrite. Before the next material
appointment feature, freeze route-family characterization tests and extract one
family at a time behind stable service interfaces. Start with legacy raw
compatibility and model/default-off route families, leaving the canonical
command kernel and public paths behaviorally unchanged.

### P2-03 — Legacy interpreter fallback can conflict with the model-required doctrine

The legacy interpreter provider defaults disabled, and the runtime gate rejects
live provider configuration. However,
`bernie_booking_interpreter_fallback_to_deterministic` defaults true at
`app/config.py:90`, and provider exceptions produce a
`deterministic_fallback` result at
`app/services/bernie_booking_interpreter.py:459` through line 472. Ordinary UI
shows provider metadata only in debug mode (`docs/diary/diary.js:2247`).

This is not an active provider or authority exposure. It is a latent semantic
hazard because the accepted model-required doctrine says no new intelligent
projection is released when the provider is unavailable
(`docs/emr4-model-required-deterministic-authority-bureau-architecture.md:212`)
and no fallback may be presented as equivalent intelligence.

Required correction: before any legacy or successor model-required route can
be enabled, a fitness check must require fallback false or require an explicit
non-intelligent/degraded result that cannot progress through intelligent
proofreading or confirmation. AES-C0 should make this distinction part of the
capability manifest rather than trusting UI metadata.

### P3-01 — The master plan mixes current, superseded and aspirational views

The current section correctly names the native Diary and the next containment
direction, but the main architecture diagram still labels the reception Diary
as Word/co-authoring at `implementation_plan.md:693`, and the Phase 2 table
still presents the SharePoint `.docx` design at line 1029 before a later note
marks it historical at lines 1038-1040. Similar long chronological sections
make accepted-unmounted Context Fabric work easy to misread as current runtime.

Recommendation: keep the history, but generate the plan's current architecture
summary from the same source-state manifest as the fitness tests. Historical
and aspirational diagrams should carry visible status labels.

## Repository-owned fitness functions

The review recommends the following small, executable architecture suite:

1. **Source-state manifest:** every application/API/worker/database entry point
   is classified as mounted current, mounted default-off, accepted unmounted,
   future or retired, with owner, evidence and gate.
2. **Mounted-route inventory:** snapshot public method/path/route-family and
   fail when a new mutation, provider, tool or external route lacks a boundary
   classification.
3. **GraphQL read-only contract:** inspect the actual runtime schema and reject
   Mutation/Subscription, command-like fields or forbidden imports.
4. **Command-family matrix:** every canonical mutation proves authentication,
   role/practice scope, idempotency, confirmation where required, audit and
   deterministic readback.
5. **Event contract:** events declare `command_authority: false`, contain no
   direct identifiers/free text beyond their approved schema and trigger fresh
   authorized reads.
6. **Default-off/model-required contract:** all provider, product-context,
   Rayleen command and Davida command descendants fail closed by default; a
   model-required capability cannot admit deterministic fallback as equivalent
   intelligence.
7. **Python target and source-state compilation:** on Python 3.11, compile and
   Ruff-check all maintained non-protected source selected by the explicit
   state manifest. Protected holdouts remain excluded by exact path and reason.
8. **Baton consistency:** AGENTS current result, required Git relation, next
   implementation, Continuity position and Compass position must agree.
9. **Lifecycle supersession:** current-state indexes may reference historical
   packets, but no historical gap/status assertion can override a later
   implemented and accepted state.
10. **Hotspot signal:** report, rather than initially fail, modules above 2,000
    lines or route modules with more than 20 endpoints; require a decomposition
    note when they receive material new behavior.

## Review cadence

- Run the executable fitness suite on every pull request.
- Run a bounded architectural-health pulse after every five to eight material
  tranches or seven active development days, whichever comes first.
- Run a deeper composition review every four to six weeks and before a major
  integration such as product Context Fabric admission, occupied Bureau tools,
  a new command family or a new clinical/data authority boundary.
- Trigger an immediate pulse after a protected-boundary incident, recurring CI
  bypass, cross-surface transaction defect or major provider/runtime change.

This cadence is deliberately lighter than constant redesign. It converts the
working compass-harness into frequent mechanical feedback while reserving
human architectural attention for material composition changes.

## Next safe sequence

1. Execute one bounded conformance-repair tranche covering P1-01, the remaining
   P2-01 current-state test drift, and the new baton/lifecycle fitness checks.
   Preserve historical evidence and exact holdout boundaries; do not refactor
   product behavior.
2. Begin AES-C0 architecture and contract with the source-state, no-fallback,
   route-classification and command-separation fitness functions as acceptance
   constraints.
3. Schedule the appointments hotspot decomposition as incremental maintenance
   before the next material feature is added to that module, not as a blocking
   rewrite of the containment programme.

No user decision fork is present. The narrow repair strengthens the selected
architecture and may proceed under the recorded standing uninterrupted-
development authority.
