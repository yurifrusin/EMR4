# Sprint R30 Adversarial Review: Deterministic Synthetic Replay Consumer

**Reviewer:** Codex/DeepSeek Flash adversarial lane
**Target:** Proposed R30 deterministic synthetic replay consumer over the R29 action grammar
**Review date:** 2026-07-06
**Mode:** source-safe plan-gate review; no R30 implementation exists yet — challenging design assumptions before code is written

**Sources read:**
- `app/services/diary/action_grammar.py` (R29 grammar foundation)
- `tests/test_diary_action_grammar.py` (R29 grammar tests)
- `docs/receptionist_review_r29.md` (R29 acceptance criteria)
- `orchestration/agent_inbox/codex/plan-claude-claude-r28-fable-full-trove-readiness-review.md` (Fable ordering)
- `tests/bernie_scenarios/replay.py` (existing scenario replay engine)
- `tests/bernie_scenarios/test_scenario_replay.py` (existing replay harness)
- `tests/bernie_scenarios/loader.py` (scenario loader)
- `tests/fixtures/bernie_scenarios/` (corpus fixtures)
- `tests/test_h_series_profile_consistency.py` (H-series validation)
- `docs/h-series-profile-schema.md` (profile contract)
- `docs/adversarial/r29_action_grammar_adversarial_review.md` (prior adversarial pattern)
- `docs/adversarial/h_series_profile_consumption_review_r27.md` (prior consumption review)
- `orchestration/parallel_workstreams.md` (active board)

---

## 0. Current-State Baseline (Pre-R30)

The existing replay harness (`tests/bernie_scenarios/replay.py`) operates at the **backend route level** over the slot-search pipeline:

| Component | What it tests | Authority gate |
|---|---|---|
| `ReplayContext` | Executes normalize/search/select/confirm turns against live API routes | `_install_forbidden_ai_provider_guard` monkeypatches the AI provider to raise `AssertionError` |
| `run_scenario` | Asserts status codes, response fields, DB row counts for Appointment and AppointmentAuditLog | `appointment_written`/`audit_written` comparison; `forbidden_outcomes` list |
| `test_scenario_replay` | Parametrized across YAML scenario fixtures | Monkeypatch + DB count arithmetic |

The R29 grammar foundation (`action_grammar.py`) is deliberately **disconnected** from this replay harness. It defines a typed verb vocabulary, consistency invariants, and an `action_verb_for_envelope` bridge — but it has no routes, no dispatch, no write authority, and no scenario fixtures.

**Key invariant:** every existing scenario replay turn maps to a live backend HTTP endpoint. The grammar is not wired into any endpoint.

---

## 1. Tautology Risk: Grammar Reads Its Own Definition

### Risk 1.1: Replay consumer that only validates grammar table completeness

The R29 grammar already has an `assert_grammar_consistency()` function that statically checks:
- Every `DiaryActionVerb` has exactly one descriptor in `DIARY_ACTION_GRAMMAR`
- Confirm-tier descriptors have non-None `confirm_affordance_notes`
- Mutating verbs have `requires_staff_confirmation=True`
- Implemented confirm-tier verbs reference existing `DiaryConfirmAction` entries
- Planned-not-implemented verbs have empty `confirm_actions`
- Read-only/meta verbs are not mutating
- `capability_name` resolves in `BERNIE_CAPABILITY_REGISTRY`

A replay consumer that loads the grammar table and re-asserts these same invariants is **tautological** — it validates authoring discipline, not runtime behaviour. The R29 tests already cover this.

**Pre-merge gate:** The replay consumer must test something the grammar tests and consistency checker do not. Examples of valid non-tautological assertions: serialization roundtrips, load-save symmetry, enumeration stability across import paths. Examples of tautological assertions: re-checking descriptor field values, re-confirming the verb set matches the enum.

### Risk 1.2: Synthetic fixture authored from grammar table

If the R30 implementation defines synthetic fixtures whose expected outcomes are derived from reading grammar table fields, the replay can never discover a discrepancy — the fixture author and the grammar author are the same authority.

| Anti-pattern | Why it is tautological |
|---|---|
| Fixture expects `desc.mutating == True` for verb `create` | Duplicates the grammar table entry |
| Fixture expects `implemented` verb to have non-empty `confirm_actions` | Already checked by `assert_grammar_consistency()` |
| Fixture uses `get_verb_descriptor(verb).tier` to decide whether the replay should succeed | Lets the grammar define its own pass/fail |

**Pre-merge gate:** Synthetic fixture expected outcomes must be **hand-authored**, not derived from grammar table fields at test-load time. The grammar and the fixture must be independent authorities so a fixture can fail when the grammar changes subtly.

### Risk 1.3: Assertions that grammar field exists, not that it does something

A replay that asserts `desc.confirm_affordance_notes is not None` at import time already passes via the consistency checker. A replay that asserts the *contents* of `confirm_affordance_notes` contain `"evaluate_confirm_affordance"` tests documentation diligence, not runtime dispatch correctness.

**Pre-merge gate:** If the replay consumer asserts against `confirm_affordance_notes`, the assertion must test that the notes **could guide a caller** to the correct gate — not merely that the string is non-empty or mentions a known word.

---

## 2. Hidden Write Authority: Grammar-Led Dispatch

### Risk 2.1: Replay consumer creates a verb-to-endpoint mapping

The R29 grammar explicitly has no routes, no dispatch, and no write authority. A replay consumer that maps grammar verbs to backend endpoints (e.g., `create -> POST /api/v1/appointments/proposals/create`) creates a **new dispatch layer** that bypasses the careful route-level authorization, session binding, and proposal-turn sequencing in the existing appointment router.

| What the existing replay does | What grammar-led dispatch could miss |
|---|---|
| Calls exact HTTP endpoint with auth header | Might skip route-level middleware (auth, practice scoping) |
| Uses the normalized slot-search pipeline | Might invent its own "resolve grammar verb -> confirm endpoint" shortcut |
| Encodes `writes_authorized` as a `Literal[False]` type in envelopes | Grammar-led dispatch might use the verb's `mutating` boolean directly |

**Pre-merge gate:** The replay consumer must call the same HTTP endpoints the existing scenario replay calls. It must not define its own dispatch table that maps grammar verbs to backend write endpoints. Any grammar-verb-to-route mapping must live in the backend router layer, not in the replay consumer.

### Risk 2.2: `mutating` boolean used as authorization signal

The grammar table has a `mutating: bool` field on each descriptor. If the replay consumer reads `desc.mutating` and uses it to decide whether to send a write request, it has created a **grammar-driven authority decision** — the grammar's metadata becomes a routing concern.

**Attack scenario:** A future sprint adds a new confirm-tier verb with `mutating=True`. The replay consumer auto-discovers it and sends a write request before the backend has a signed confirm endpoint for that verb. The request hits a catch-all or a partially-implemented route, producing a 500 or (worse) a confused state.

**Pre-merge gate:** The replay consumer must not dispatch write requests based on `desc.mutating`. It must only dispatch reads for verbs in a static, manually enumerated **allowed-for-replay** set. Write verbs must require explicit approval — same as how the scenario YAML `forbidden_outcomes` mechanism gates per-scenario write expectations.

### Risk 2.3: `action_verb_for_envelope` bridge used as a dispatch decoder

The grammar provides `action_verb_for_envelope(action_name: str) -> Optional[DiaryActionVerb]` which maps free-string envelope action names to canonical verbs. If the replay consumer reads an envelope's `action_name`, feeds it through this bridge, and then dispatches based on the returned verb, it has created a **string-to-authority** path: any envelope with a matching `action_name` string becomes a valid replay action, even if the envelope was never intended for replay.

**Pre-merge gate:** If the replay consumer uses `action_verb_for_envelope`, it must validate that the source envelope is from an approved replay fixture, not from arbitrary backend traffic. Add an explicit "replay-authorized envelope source" tag or fixture metadata field.

---

## 3. Accidental H-Series / Full-Trove Semantic Promotion

### Risk 3.1: H-series profiles loaded as replay fixtures

The R28 Fable packet says: "H-series profiles may guard isolation invariants only, per R27 rules." The R27 review says: "Do not use these fixtures as provider prompt content" and "neutral event classes must not be passed into Bernie replay."

If the R30 replay consumer loads YAML fixtures from a directory that could be confused with H-series profiles, or if it uses `discover_scenarios()` on a broad glob that includes non-scenario fixtures, it risks loading neutral aggregate data as executable replay input.

| Misuse | Consequence |
|---|---|
| `discover_scenarios(path)` with too-broad glob | H-series YAML loaded as replay scenario; replay asserts "no_structural_change" as a valid action |
| Replay fixture format that looks like H-series profile | Future reader assumes H-series data is executable replay input |
| Profile `source_docs` field used as replay step | Replay attempts to "execute" a doc reference as a backend turn |

**Pre-merge gate:** The replay consumer fixture directory must be distinct from `tests/fixtures/h_series_profiles/`. The loader must reject any fixture whose `profile_kind` or `schema_version` fields match H-series profile conventions. Add a loader guard: `if fixture.get("profile_kind") == "h_series_neutral_profile": raise ValueError("H-series profiles are not executable replay fixtures")`.

### Risk 3.2: Neutral event classes appear in replay fixture design

If the synthetic replay grammar or fixture schema uses vocabulary like `no_structural_change`, `small_content_delta`, `time_grid_delta`, or `large_unexplained_delta` as transition labels, it cross-contaminates the neutral H-series event model with the native diary action grammar.

**Pre-merge gate:** Zero H-series event class names in replay fixture schema, grammar consumption tests, or replay result vocabulary. Use only the existing `DiaryActionVerb` names and backend outcome terminology. The grammar's `test_no_h_series_references_in_grammar_vocabulary` test should be extended to include replay consumer modules.

### Risk 3.3: Replay consumer claims to validate diary "shape" from aggregate expectations

A replay consumer that accepts aggregate expectations (e.g., "expect 3 no-change transitions and 2 small-delta transitions in this replay") creates a **bridge from aggregate evidence to semantic test logic** — exactly what the H15 gate is designed to prevent. This is semantically equivalent to promoting neutral H-series buckets into expected test outcomes.

**Pre-merge gate:** The replay consumer must only accept **deterministic per-turn outcomes** (status code, field values, DB row count delta), never aggregate transition-class expectations. Aggregate acceptance criteria belong in H-series validation, not in grammar replay.

---

## 4. Weak No-Write Assertions

### Risk 4.1: Monkeypatch-only AI provider guard is insufficient

The existing replay harness uses `_install_forbidden_ai_provider_guard` which raises `AssertionError` if any turn calls the AI provider. This is a strong guard for the existing scenario replay because the replay is testing the backend proposal pipeline, and the only external write vector is through the AI provider.

But a grammar-level replay consumer has a broader attack surface. Grammar verbs describe clinical actions. If the replay consumer accidentally creates a code path that calls `app.services.diary.envelopes.DiaryActionConfirmation` directly (without going through the route), the monkeypatch guard does not catch it — the guard only blocks the AI provider, not grammar-to-envelope shortcuts.

| Guard | Catches AI provider calls | Catches grammar-to-envelope shortcuts |
|---|---|---|
| `_install_forbidden_ai_provider_guard` | Yes | No |
| `appointment_written` DB count check | Yes (indirectly) | Yes (if shortcut creates DB rows) |
| Grammar-internal dispatch assertion | No | Only if explicitly written |

**Pre-merge gate:** The replay consumer must include both:
1. The existing `_install_forbidden_ai_provider_guard` (or equivalent) — prevents provider calls.
2. A DB row count assertion (before/after) for every replay — prevents silent writes through any path.

### Risk 4.2: Read-only verbs asserted as "no write" without DB check

A replay over read-only grammar verbs (`slot_search`, `explain_schedule`, `handoff`) that asserts "no write" using only the monkeypatch guard would miss a write that happens through a non-provider code path (e.g., an audit log entry written during envelope serialization, a session state update, a cache-warming trigger).

**Evidence:** The existing `replay.py` already verifies DB row counts before/after with `appointment_written` and `audit_written` checks. The new replay consumer must replicate this.

**Pre-merge gate:** Every replay turn must include a DB row count delta check, not just a "no provider called" assertion. Read-only verb replays must assert that both Appointment and AppointmentAuditLog row counts are unchanged (unless the audit log is expected for read actions).

### Risk 4.3: `no_writes_authorized` fixture flag without enforcement

If the replay consumer introduces a `no_writes_authorized: true` field in the fixture metadata, but does not enforce it at runtime (e.g., the fixture declares no writes but the replay engine still calls confirm endpoints), the declaration becomes a documentation assertion with no backend enforcement.

**Pre-merge gate:** Any `no_writes_authorized` fixture field must be enforced at runtime — the replay engine must fail the turn if any write occurs. Do not accept unenforced metadata assertions. Follow the existing `forbidden_outcomes` pattern: a list of strings that the engine actively checks.

---

## 5. Overfitting to Grammar Table Fields

### Risk 5.1: Replay consumer iterates `DIARY_ACTION_GRAMMAR.items()` for fixture generation

A consumer that auto-discovers verbs by iterating the grammar dictionary creates an **implicit coupling**: adding a new verb to the grammar automatically adds it to the replay surface, possibly before the backend has implemented the corresponding route.

```python
# Anti-pattern — auto-discovery
for verb, desc in DIARY_ACTION_GRAMMAR.items():
    if desc.implemented:
        replay_fixtures.append(make_fixture(verb))
```

This pattern would automatically create replay fixtures for `status_change` and `create` (which are implemented) but also for `check_in`, `waiting_area_move`, and `link_patient` (which have `implemented=False` but the `if desc.implemented` guard filters them). The risk is subtler: new grammar verbs added in a future sprint would auto-appear in the replay fixture set without explicit review.

**Pre-merge gate:** The replay fixture list must be **hand-authored**, not generated by iterating `DIARY_ACTION_GRAMMAR`. Each replay fixture must explicitly name the verb and turn sequence. If auto-discovery is used for convenience, it must be restricted to a `ReplayFixtureRegistry` that requires explicit registration of each verb+action pair, not implicit enumeration.

### Risk 5.2: Field-by-field assertion against descriptor structure

A replay consumer that asserts `desc.verb == DiaryActionVerb.create` or `desc.tier == BernieCapabilityTier.confirm` by reading grammar descriptor fields is testing that the grammar says what it says. This is already checked by `assert_grammar_consistency()`.

**Pre-merge gate:** Replay consumer assertions must target **runtime behaviour**, not grammar table structure. Valid assertions: "calling `action_verb_for_envelope("create")` returns `DiaryActionVerb.create`" (test the bridge), "serializing a DiaryActionConfirmation with action_name='create' roundtrips through the envelope validator" (test envelope integration). Invalid assertion: "the grammar table entry for create has `tier == BernieCapabilityTier.confirm`" (duplicates static consistency test).

### Risk 5.3: Confirm affordance gate tested only against grammar notes, not against `evaluate_confirm_affordance`

The R29 golden confirm-affordance-block test (`test_confirm_affordance_blocks_grammar_action`) is a strong integration test. A replay consumer that asserts the same gate by reading `confirm_affordance_notes` and checking for the string `"evaluate_confirm_affordance"` is weaker — it tests documentation, not runtime gating.

**Pre-merge gate:** Any confirm-affordance assertion in the replay consumer must call `evaluate_confirm_affordance()` with session state, not merely parse `confirm_affordance_notes`. The existing R29 golden test pattern should be reused or extended, not replaced with a text-scanner.

---

## 6. Replay Harness Drift

### Risk 6.1: Grammar replay uses different turn semantics than existing scenario replay

The existing scenario replay has exactly four turn types: `normalize`, `search`, `select`, `confirm`. These map to the slot-search pipeline. A grammar-level replay consumer introduces new turn types (e.g., `propose_grammar_verb`, `resolve_grammar_action`, `apply_grammar_outcome`) that diverge from the battle-tested replay harness.

| Dimension | Existing replay | Grammar replay risk |
|---|---|---|
| Turn types | normalize, search, select, confirm | New: propose_create, propose_move, confirm_create, etc. |
| Auth | Route-level Bearer token | May skip route auth if dispatching internally |
| DB assertions | Before/after row counts for Appointment and AuditLog | May only check grammar-level outcomes |
| Provider guard | `_install_forbidden_ai_provider_guard` | May use weaker `monkeypatch` or no guard |
| Fixture format | YAML with action/input/expect/structure | New format may diverge |
| Error handling | `AssertionError` from provider leads to test failure | May silently swallow dispatch errors |

**Pre-merge gate:** The grammar replay consumer must either:
1. Extend the existing scenario replay harness (same `ReplayContext`, same turn semantics, same DB assertions, same provider guard), or
2. Document in a DRIFT.md or equivalent why divergence is necessary, with explicit cross-reference to which existing invariants are preserved.

### Risk 6.2: Two replay harnesses with overlapping scope

If the grammar replay consumer lives alongside the existing scenario replay, future sprints may add fixture YAML to the wrong directory, or run the wrong test file, or fix a bug in one harness but not the other.

| What could drift | Consequence |
|---|---|
| A fixture added to `tests/fixtures/bernie_scenarios/` but the grammar replay only checks `tests/fixtures/grammar_replay/` | Scenario corpus grows without grammar coverage |
| The existing replay adds a new turn type (e.g., `fetch_slots`) but the grammar replay doesn't know about it | Grammar replay misses a route that consumes grammar verbs |
| The grammar replay has a `forbidden_outcomes` check that is subtly different from the existing one | Same fixture passes in one harness, fails in the other |

**Pre-merge gate:** The grammar replay consumer must define a clear ownership boundary. Either:
- A: The grammar replay **replaces** the fixture format for all grammar-verb-related fixtures, and the old scenario format is deprecated for grammar verbs.
- B: The grammar replay uses the exact same fixture format and loader, and only adds grammar-specific assertion helpers.

Recommend option B for minimal drift.

### Risk 6.3: `_install_forbidden_ai_provider_guard` not inherited

The existing harness's `_install_forbidden_ai_provider_guard` monkeypatches `app.services.ai.service._get_default_provider`. A grammar replay consumer that does not call this guard creates an **unprotected replay path** that could silently call AI providers during grammar resolution.

**Pre-merge gate:** The grammar replay consumer must install the AI provider guard before executing any turn. Make it an explicit initialisation step, not a caller responsibility.

---

## 7. Bernie Facade Re-Export Consistency

The R29 grammar has a Bernie facade at `app/services/bernie/action_grammar.py` that re-exports identical objects. The R29 tests verify identity.

### Risk 7.1: Non-uniform import path

A replay consumer that imports grammar objects from the Bernie facade path (e.g., `from app.services.bernie.action_grammar import DiaryActionVerb`) must receive the same objects as importing from the canonical path. If the replay consumer only checks one path, a facade drift would go undetected until a separate import test fails.

**Pre-merge gate:** The replay consumer must import grammar objects from the canonical path (`app.services.diary.action_grammar`), not from the Bernie facade. Use `app.services.bernie` only for tests that explicitly validate facade consistency (as the R29 tests do).

### Risk 7.2: Fixture loader under Bernie facade

If a future sprint adds a grammar-related fixture loader under `app/services/bernie/`, that loader could re-export grammar objects through the facade to fixture consumers, creating a dependency chain that is harder to audit.

**Pre-merge gate:** Do not add grammar fixture loaders under `app/services/bernie/`. Keep fixture loading in `tests/bernie_scenarios/loader.py` or a new `tests/grammar_replay/` module.

---

## 8. Concrete Attack Vectors (For Ariadne's Merge Gate)

### Vector A: Grammar replay creates new fixture directory without naming guard

```python
# New directory: tests/fixtures/grammar_replay/
# Fixture files use a new format that resembles neither bernie_scenarios nor h_series_profiles
```

This creates three fixture directories with potentially overlapping filename conventions.

**Mitigation:** If a new directory is needed, prefix all filenames with `grammar_replay_` and add a loader guard: `if not path.name.startswith("grammar_replay_"): raise ValueError()`.

### Vector B: Replay consumer asserts grammar-table field type at runtime

```python
desc = get_verb_descriptor(DiaryActionVerb.create)
assert isinstance(desc.confirm_actions, tuple)  # type-level assertion, already enforced by dataclass
```

This is a type-level assertion that Python's type system already enforces at dataclass construction time.

### Vector C: Propose-tier verbs tested without checking ProposalSession table

The grammar's propose-tier verbs should not create backend writes. But if the grammar testing reveals that `slot_search` incidentally creates a session state row, the no-write assertion is only as strong as the set of DB tables being checked.

**Mitigation:** Extend the DB assertion schema to include ProposalSession or any table that proposal-tier grammar consumption could touch.

### Vector D: Grammar replay uses `importlib` to discover grammar verbs

```python
import importlib
grammar_module = importlib.import_module("app.services.diary.action_grammar")
```

Dynamic import-based discovery of grammar symbols bypasses the explicit `__all__` list and static import checks.

**Mitigation:** Only import grammar objects through explicit `from ... import` statements, not `importlib`.

### Vector E: Synthetic replay fixture filename accidentally matches H-series naming

A fixture named `no_slot_change.yaml` in `tests/fixtures/grammar_replay/` could be confused with a future H-series profile.

**Mitigation:** Use a `grammar_replay_` prefix on all fixture filenames, and explicitly disallow bare words that match H-series terminology in fixture filenames.

---

## 9. Positive Design Requirements

| Requirement | Must include | Must not include |
|---|---|---|
| Turn dispatch | Calls exact HTTP endpoints with route-level auth | Grammar-to-endpoint dispatch table |
| Fixture format | Same format as existing bernie_scenarios (or documented extension) | New format without drift cross-reference |
| Provider guard | `_install_forbidden_ai_provider_guard` or equivalent | Weaker or absent guard |
| DB assertions | Before/after row counts for Appointment and AppointmentAuditLog | Grammar-only assertions |
| Confirm-affordance testing | Calls `evaluate_confirm_affordance()` with real session state | Text-scanning `confirm_affordance_notes` |
| Fixture list | Hand-authored fixture list (or explicit registration) | Auto-discovery by iterating `DIARY_ACTION_GRAMMAR` |
| H-series isolation | Distinct fixture directory; loader rejects H-series profile metadata | Cross-loading H-series YAML as replay fixtures |
| No-write enforcement | Runtime-enforced `forbidden_outcomes` (existing pattern) | Unenforced fixture metadata declarations |
| Import path | Canonical `app.services.diary.action_grammar` | Bernie facade path for non-facade tests |
| Schema version | Grammar replay fixtures pinned to a `replay_schema_version` | Orphan fixtures without version tracking |

---

## 10. Adversarial Questions for Ariadne

1. Should the R30 replay consumer reuse the existing `tests/bernie_scenarios/replay.py` and `test_scenario_replay.py` harness (extending `KNOWN_ACTIONS` and `KNOWN_FORBIDDEN_OUTCOMES`), or create a new grammar-specific harness with documented drift? If new, who maintains both harnesses when backend routes change?

2. The existing `forbidden_outcomes` list includes `"provider_called"`, `"appointment_written"`, and `"audit_written"`. Should grammar replay add `"grammar_to_confirm_shortcut"` as a new forbidden outcome — an assertion that no turn bypassed the route-level confirm gate by invoking a grammar verb's confirm action directly?

3. Who adds DB assertion coverage for grammar-replay tables beyond Appointment and AppointmentAuditLog (e.g., ProposalSession, SessionState, DiaryActionLog tables)? Each new table added to the assertion scope is a maintenance burden that must be kept in sync with migrations.

4. The R29 `test_no_h_series_references_in_grammar_vocabulary` test scans `app/services/diary/action_grammar.py` for forbidden fragments. Should this test be extended to cover any new R30 replay consumer modules (`tests/grammar_replay/*.py`, `app/services/diary/replay/*.py`)?

5. Should the grammar replay consumer assert that turn execution **never** imports or calls `action_verb_for_envelope()` with a free-string envelope that came from raw backend traffic (not from an approved fixture)? This guards against the bridge becoming a dispatch decoder.

6. If a future sprint adds a new confirm-tier verb with `implemented=True`, should the R30 replay consumer auto-detect it (tautology risk) or require a manual update to the fixture list (maintenance burden)? Where is the right trade-off?

7. The existing scenario replay computes `appt_written = appt_after > appt_before`. A delete verb (cancel) should reduce row count. Does the replay consumer's write assertion account for deletions, or does it only assert no-new-rows? Should cancellations assert `appt_after < appt_before`?

---

## 11. Verdict

**Pre-implementation gate: do not implement the R30 replay consumer until these pre-merge gates are satisfied by the design.**

### Pre-Merge Gates

| Gate | Description | Verification |
|---|---|---|
| G1 | Replay fixture list is hand-authored, not auto-discovered from grammar table | Inspect fixture list in PR |
| G2 | Every replay turn calls actual HTTP endpoints with route-level auth | Code review of dispatch layer |
| G3 | `_install_forbidden_ai_provider_guard` installed before any turn | Code review |
| G4 | Every turn has before/after DB row count assertions for Appointment and AppointmentAuditLog | Test code review |
| G5 | Zero H-series event class names in replay fixture schema or test code | Automated scan (extend R29 forbidden-fragments test) |
| G6 | Replay fixture directory is distinct from `tests/fixtures/h_series_profiles/` | Directory layout review |
| G7 | Replay fixture loader rejects fixture with `profile_kind == "h_series_neutral_profile"` | Test code review |
| G8 | Confirm-affordance assertions call `evaluate_confirm_affordance()`, not text-scanning notes | Test code review |
| G9 | Replay consumer imports grammar objects from canonical path, not Bernie facade | Import review |
| G10 | No `importlib` dynamic introspection of grammar module | Code review |
| G11 | Existing `test_no_h_series_references_in_grammar_vocabulary` extended to cover new replay modules | PR inspection |
| G12 | Read-only verb replays assert zero DB row changes (unless audit logging is expected for reads) | Test code review |
| G13 | Cancel verb replay asserts `appt_after < appt_before` (decrement), not `appt_after == appt_before` | Test logic review |
| G14 | Fixture filenames prefixed `grammar_replay_` (if new directory); avoid H-series terminology | Filename review |

### Vectors Requiring Explicit Decision Before Code

| Decision | Options | Recommended |
|---|---|---|
| Single harness or separate grammar harness? | (A) Extend existing replay, (B) New grammar replay with documented drift | A — extend existing |
| DB assertion table scope | (1) Only Appointment + AuditLog (existing), (2) Add ProposalSession | 1 initially, expand per-verb |
| Grammar fixture directory | (1) `tests/fixtures/bernie_scenarios/` with naming prefix, (2) New `tests/fixtures/grammar_replay/` | 1 — existing directory, `grammar_replay_` prefix |

---

*This review is source-safe: no raw trove filenames, PHI, patient/staff identifiers, exact timestamps, document text, or semantic appointment labels are disclosed. All findings are derived from committed source code and review artifacts only.*
