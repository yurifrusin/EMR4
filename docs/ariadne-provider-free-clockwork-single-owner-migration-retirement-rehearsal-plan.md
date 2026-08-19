# Ariadne provider-free clockwork single-owner migration and retirement rehearsal plan

**Frozen:** 2026-08-19
**Reasoning level:** Extra High
**Operation:** `ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal`
**Source anchor:** machine-resolved full Git object ID from the exact task `HEAD`
**Protected refs:** local/origin `master` and local/origin `handoff/current` remain `2e34bdad732fdab32fbf778280b3d3c70d66d602`

## Decision and objective

Yuri selected the recommended bounded migration-and-retirement rehearsal after accepting the private-shadow reducer at exact candidate `a0bb86b78bfc011066142740c82d5c25cab7b9c8`. This tranche must prove or reject that one clockwork transaction can become the sole writer for a complete repository-local governance generation without producing a second live control plane.

The rehearsal imports the exact current canonical controls as a read-only generation-zero oracle, derives one representative clean closeout from a narrow human-authored intent manifest, compares every derived projection, atomically promotes a clockwork-owned generation in an isolated canonical mirror, rejects legacy and stale writers, proves crash safety at every publication step, and proves byte-exact rollback. Actual canonical files remain unchanged by the rehearsal engine.

## Authority ceiling

Authorized:

- provider-free repository-local implementation and tests;
- read-only use of the exact current canonical graph, Compass, latch, error register, pattern report and Current Baton fields as the oracle;
- one isolated canonical-mirror root owned by this tranche;
- pure composition of the accepted transactional-closeout and governance-clockwork reducers;
- an exclusive lease, immutable generations, atomic current-generation pointer, writer-retirement map, fault injection and rollback;
- deterministic evidence, a fresh Gemini 3.7 Flash/high read-only veto after admission, task-branch commits and task-branch push;
- a non-PHI Yuri summary and Pushover closeout notification.

Not authorized:

- mutation, deletion or retirement of the actual canonical controls, historical updater scripts, accepted evidence or tests;
- a long-term dual control plane or two accepted writers for any mirror surface;
- caller-supplied Git object IDs, counts, revisions, output paths, peer links or derived statuses;
- DeepSeek, occupied HMR, Claude Code fallback or any provider call before the optional Gemini veto;
- product, practice, route, schema, OpenAPI, GraphQL, database, client, patient, clinical or protected data change;
- production runtime, deployment, release, Pages or protected-ref movement.

## The single reading

The only mutable human-authored input is a versioned closeout intent containing irreducible narrative and authority:

- operation ID, title and timestamp;
- accepted node authority, claim scope, evidence paths, unresolved gates and human decisions;
- journey/current-position narrative;
- next operation objective and authority source;
- explicit command names selected from the contract allowlist.

The clockwork must derive and reject caller attempts to supply:

- full source commit and all protected-ref readings;
- Continuity and Compass revisions, node coordinates and current-position binding;
- register revision, incident population, latest incident and pattern aggregates;
- Current Baton numeric/result/next fields;
- latch transition counters and source binding;
- transaction, generation, lease, journal, ownership and projection digests;
- all output locations.

A clean-closeout tick creates no incident and leaves the error register and pattern report byte-identical. A corrected-failure tick is out of scope for this tranche but remains covered by the accepted private-shadow reducer.

## Ownership state machine

The mirror has exactly three states:

1. `legacy_oracle`: generation zero is a byte snapshot of current canonical inputs; legacy controls are oracle-only and the clockwork has no publication authority.
2. `clockwork_active`: exact comparison has passed; one exclusive lease atomically promotes an immutable generation; every maintained surface is owned by `clockwork`; legacy writers are `retired_in_mirror` and any attempted write fails closed.
3. `rolled_back`: the same lease atomically selects generation zero after its complete digest is revalidated. No files are copied back and no mixed generation is possible.

The accepted final rehearsal state is `clockwork_active`. Rollback is exercised on a disposable clone and the active pointer is then restored only through another validated lease-bound transition.

## Maintained surfaces

One generation owns these exact logical surfaces:

1. Continuity graph;
2. Compass JSON;
3. Compass Markdown reading;
4. active-operation latch;
5. agent-error register;
6. recurrence pattern report;
7. typed Current Baton reading;
8. typed closeout command manifest;
9. transaction journal and generation metadata;
10. ownership/retirement map.

The existing engines remain pure libraries and cease to be publication writers inside the mirror. The new composition layer is the only mirror publisher.

## Frozen implementation package

- `orchestration_harness/governance_migration.py`
- `scripts/ariadne_provider_free_clockwork_single_owner_migration_retirement_rehearsal.py`
- `orchestration/continuity/ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal/contract.json`
- `orchestration/continuity/ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal/closeout-intent.json`
- `tests/test_ariadne_provider_free_clockwork_single_owner_migration_retirement_rehearsal.py`
- compatibility retirement assertions in `tests/test_ariadne_provider_free_clockwork_governance_projection_consolidation_repair.py` and `tests/test_current_baton_consistency.py`;
- deterministic evidence, report and one inspectable canonical-mirror generation under the same topic root;
- plan, threat-model delta, closeout, Sol acceptance, paired Yuri summary, Continuity updater and its focused test.

The combined implementation, runner, contract, intent and focused rehearsal test must remain at or below **950 physical lines** before generated evidence. Any overage is `revision_required`, not a budget waiver. Existing accepted reducers must be composed rather than copied.

The two existing compatibility files are outside that new-package ceiling because they are not new maintained mechanism surfaces. Their exact diff is reported separately; the accepted predecessor package must remain at its original 850-line ceiling.

## Deterministic acceptance gates

All gates are mandatory:

1. Fresh five-source Ariadne receipt passes and names the five authority sources exactly.
2. The active latch passes and the task/protected refs match the frozen hashes.
3. Contract and intent reject unknown keys and every caller-authored derived binding.
4. Generation zero is byte-identical to every selected current canonical oracle input.
5. The pure clockwork generation matches the independent accepted reducer outputs for Continuity, Compass and latch; clean register and pattern outputs are byte-identical to their inputs.
6. All ten maintained surfaces have exactly one owner after cutover; zero surfaces have a legacy and clockwork writer simultaneously.
7. Legacy-writer, wrong-writer, stale-lease, stale-generation, wrong-source, abbreviated-OID, wrong-protected-ref and path-escape attempts fail before publication.
8. Fault injection before and after every generation-file write and before pointer replacement leaves the previous complete generation selected, no partial generation and no leaked lease. An injected post-replacement exception must be classified as committed and expose only the complete new generation.
9. A disposable rollback selects the exact generation-zero digest; restore selects the exact clockwork generation digest.
10. The representative fault-free closeout requires zero manual derived-field edits and zero corrective reruns.
11. The controls make AER-0643 through AER-0651 either impossible to represent or fail before publication: bounded latch prose, Compass fixture derivation, immutable replay source, exact line reading, current pytest-node discovery/whole-file fallback, aggregate/membership generation, structured accessor use and yielding-session completion.
12. All 13 immutable predecessor probes and all 9 surrounding probes remain passing with no coverage loss.
13. Construction retries are reported separately from the projected steady-state closeout; no amortisation or timing claim is accepted.
14. Focused, latch, register, Compass, transactional-closeout and governance-clockwork suites pass.
15. Fresh Gemini 3.7 Flash/high returns a read-only pass on the exact clean candidate and command packet.
16. `git diff --cached --check`, explicit-path staging, clean tracked handoff, task-origin alignment and unchanged protected refs pass.

## Efficacy decision rule

The rehearsal passes only if it proves exclusive ownership and prevents every observed post-review closeout rerun class while reducing a representative closeout to one intent validation plus one atomic promotion. Build cost is recorded honestly. Passing does **not** itself activate the engine against canonical repository files; it supports a separately explicit live-adoption decision. Failure freezes the mechanism as research evidence and the existing controls remain authoritative.

## Parallelism assessment

- **DeepSeek:** declined. The transaction is provider-free and serial; native Harness work remains behind the stock-headless-to-custom-runner HMR boot proof and Claude Code is not a fallback.
- **Gemini:** reserved for one fresh 3.7 Flash/high exact-candidate read-only veto after deterministic admission.
- **Native subagents:** declined under current developer policy and because lease, ownership, promotion and rollback form one inseparable serial boundary.

Reassess at plan freeze, exact comparison, cutover/rollback completion, pre-verifier admission, closeout and before any future canonical adoption.

## Closeout

Closeout must state pass or rejection, exact reviewed 40-character source, exact generation and bundle digests, construction reruns, projected steady-state reruns, ownership count, fault coverage, rollback result, line budget, unresolved gates and the precise next authority boundary. It must update Continuity/Compass through the existing accepted updater path, update the latch, write the paired lay/technical Yuri summary, send the usual non-PHI Pushover notification, stage explicit paths only, commit and push only the task branch.
