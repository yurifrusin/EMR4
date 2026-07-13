# LC2 Corpus Factory and Independent Adjudication — Tranche Contract

Role: Routine Delegated Executor (Ariadne)
Resource: `deepseek-pro-routine-coordinator` / high
Model: `deepseek-v4-pro` / high
Leverage reason: LC2 freezes the provenance-tier ontology, promotion rules, and
independent-adjudication framework. Incorrect allocation would contaminate the
entire corpus pipeline (LC3 evaluator, LC4 holdout, LC5 live-model shadow).
Settings fingerprint:
`sha256:20e82ee5251321c4987158176b29f8c780ba5debc2c515592c320e869be418d5`

## Direction-Dialogue Disposition

Skipped. The approved product direction is LC2 per
`docs/bernie-language-coverage-implementation-plan.md`. The LC2 direction and
authority boundary are unambiguous: no architecture dispute, policy change, or
material sprint-size disagreement exists. Sol is the protected orchestrator/
integrator and final acceptance owner; this routine owns the sprint
decomposition and allocation within the accepted lane boundaries.

## Boundary

**LC2 is a pure-Python/domain-layer and strict-JSON-fixture sprint with zero
surface-mutation authority.**

- No provider calls, no live prompts, no provider adapter work.
- No route wiring, no HTTP interception changes, no GraphQL mutations.
- No database writes, no appointment/audit mutation.
- No diary write authority, no confirmation authority.
- No historical-trove access, no H15/H-series runtime imports.
- No memory/RAG/GraphRAG access.
- No deployment/release/external-client changes.
- No download, dataset content, licence acceptance, or cost for external
  task-dialogue sources.
- No PHI in synthetic-diary receptionist elicitation.
- T3.1-T3.4 shadow-evaluation scaffolding preserved unchanged.
- T3.5 DeepSeek/Gemini provider adapters, live provider calls, historical diary
  access, confirmation changes, and write authority remain closed.
- The existing interpretation-harness runtime gate remains `blocked`.
- `ReceptionScenarioSpec`, `language_normalization.py`, and
  `bernie_coverage_lattice.py` from LC1 are read-only canonical inputs;
  their schemas and dimension enumerations may be referenced but not
  mutated. DW1 must **not** add provenance fields to or otherwise modify
  `scenario_spec.py`. Instead, DW1 defines a strict `CorpusCandidate`
  / evidence wrapper type that wraps a `ReceptionScenarioSpec` without
  changing the LC1 schema.

## Lane Cleanliness and Availability

| Lane | Status | Worktree | Action |
|---|---|---|---|
| Claude CLI | Unavailable | `claude/current` — subscription cancelled after 2026-07-13 | Stand down |
| Antigravity CLI | Available when probed | `antigravity/current` — clean at last check, `agy.exe` reachable; required probe before dispatch | Allocate as independent adversarial lane; probe availability as required gate |
| DeepSeek via Claude Code bare | Reachable | Disposable worktrees from current master | Allocate two `deepseek-v4-flash`/high lanes |
| Deep Code (fallback) | Reachable | Zero active managed slots; TTY required | Fallback only — not allocated unless bare-mode transport fails after recorded remediation |

DeepSeek Flash lane count: 0 active, 0 complete/idle, 0 to close.
Two fresh lanes are allocated but not yet spawned/dispatched.

## Antigravity Decision

**Antigravity Gemini Flash is selected** with a distinct, non-overlapping
independent adversarial generation surface. Its ownership:

- Generates adversarial probe cases (prompt-injection, authority bypass,
  confirmation-circumvention, unsafe-instruction, and tier-escalation attacks)
  that exercise the factory promotion rules and quarantine queue.
- Independently reviews DW2 DeepSeek-generated candidate fixtures for
  independence violations, schema compliance, and semantic drift from
  Gold sources. Gemini may independently review DW2 DeepSeek candidates
  because the reviewer model differs from the generator model.
- Antigravity's **own** generated adversarial probes cannot be certified by
  Gemini; they remain `silver/pending` or quarantine until independent Sol
  acceptance. Gemini acting as generator cannot also be judge.
- Produces committed adversarial fixtures and a review artifact.
- Availability is treated as a required probe: the `agy.exe` CLI must
  produce a tangible repo artifact before its review is accepted;
  stdout-only output is not sufficient evidence per the known `agy`
  non-TTY capture quirk.

## DeepSeek Lane Count

**Two DeepSeek Flash lanes** where ownership is truly separable:

| Lane | Worker | Role | Model | Branch |
|---|---|---|---|---|
| DW1 | DeepSeek Flash | Implementation owner — corpus factory core (tiers, promotion, quarantine, registry, wrapper) | `deepseek-v4-flash`/high | `codex/lc2-dw1-corpus-factory-core` |
| DW2 | DeepSeek Flash | Implementation owner — candidate generators (paraphrase, minimal-pair, ambiguity, correction, adversarial from Gold) | `deepseek-v4-flash`/high | `codex/lc2-dw2-candidate-generators` |
| AG | Antigravity Gemini Flash | Independent adversarial review — probe generation, independence audit, tier-escalation attacks | `gemini-flash-3.5`/medium | `antigravity/lc2-adversarial-corpus-review` |

DW1 and DW2 may proceed in parallel (disjoint file ownership). AG must wait for
DW1 and DW2 to submit their artifacts, then run adversarial probes against both.

**Corpus authorship rule:** No model certifies its own corpus. DW2 generates
Silver candidates from LC1 Gold seeds; DW1 validates them against the
factory schema deterministically; AG provides independent adversarial evidence.
Corpus authority remains with Sol, the protected orchestrator/integrator;
model review is veto evidence only. DW1 deterministic checks validate shape
and policy only (schema conformance, authority boundaries, provenance
completeness), not semantics.

## Assignments

### DW1 — Corpus Factory Core

**Scope:**
1. Define `ProvenanceTier` (`gold`, `silver`, `bronze`), `AdjudicationState`
   (`adjudicated`, `pending`, `quarantine`), and `ScenarioFamily` enumerations
   as standalone domain types in a new `app/services/bernie/corpus_tier.py`.
2. Define deterministic promotion rules:
   - Gold → Silver: Only Gold scenarios may seed Silver generation; Silver
     cases require independent adjudication before promotion scoring.
   - Silver → Gold: Silver cases require an independent model or human
     adjudicator who did not generate the case; the adjudicator must confirm
     schema validity and semantic equivalence to the source Gold contract.
   - Bronze → Silver: Bronze material requires explicit independent
     adjudication of its semantics before promotion; a Bronze case may propose
     a scenario family but cannot enter promotion scoring until its semantics
     are independently adjudicated.
   - Quarantine: Any case with disagreement between generator and judge, invalid
     evidence, authority-boundary violation, or schema non-compliance is placed
     in quarantine without silent promotion.
3. Define a `CandidateRegistry` schema (JSON-only, no imports, no downloads):
   - A declarative schema for describing external task-dialogue candidates
     (source name, licence status, linguistic forms present, estimated count,
     access posture) without importing or downloading any content.
   - The registry is an allowlist-based descriptor only: no dataset content, no
     licence acceptance, no cost.
   - Registry entries record whether a source has been evaluated and the
     decision (eligible, ineligible-licence, ineligible-cost, unevaluated).
4. **Bounded no-import external-source evaluation (allocated within DW1):**
   Evaluate at least three well-known task-dialogue corpus candidates with
   **no dataset download, content, licence acceptance, eligibility claim, or
   cost.** Each registry entry must include only:
   - Official-source URL (primary, verifiable)
   - Declared licence metadata (verbatim from the source, no interpretation)
   - Linguistic-form capability labels (task-dialogue forms present per the
     source's own documentation)
   - A conservative `candidate_only` / `requires_licence_review` decision;
     no candidate may be marked `eligible` without independent licence review
     beyond DW1.
   Protected Sol will independently verify primary-source metadata before
   acceptance. DW1 may not claim a source is eligible, accepted, or licensed
   for use.
5. Define generator/judge identity recording: every generated candidate must
   carry `generator_identity`, `judge_identity`, and a rule that
   `generator_identity != judge_identity` for any candidate promoted beyond
   Bronze. The factory validates this at promotion time.
6. Define the quarantine queue as a deterministic set of rejection reasons and
   a fail-closed validator that rejects on:
   - Generator == judge (self-certification)
   - Invalid schema (missing required fields from `ReceptionScenarioSpec`)
   - Authority-boundary violation (claims write authority, provider authority,
     or confirmation authority in scenario fields that must be null)
   - Source-span evidence mismatch (spans do not match original utterance text)
   - Missing provenance metadata
   - Unsafe instruction fragments (adversarial payloads that passed generation
     but fail quarantine checks)
7. Define a strict `CorpusCandidate` evidence wrapper type around
   `ReceptionScenarioSpec` that carries all mandatory provenance fields
   (`provenance`, `adjudication`, `family`, `generator_identity`,
   `judge_identity`, `generation_timestamp`, `source_scenario_id` for
   Silver, `promotion_history`) without mutating the LC1 canonical
   `ReceptionScenarioSpec` schema. The wrapper type is the unit of
   transport between workers; `ReceptionScenarioSpec` instances are
   embedded, not subclassed.
8. Define deterministic temporal-relation and coordinate-source preservation
   rules: generators must preserve original utterances, LC1 source coordinates,
   explicit temporal relations, deterministic clinic clocks, and scenario
   authority boundaries from the source Gold scenario unless the transformation
   is explicitly designed to change a specific field. Every derived candidate
   must record a stable derivation ID/hash that reproduces from source seeds.

**File ownership:**
- New `app/services/bernie/corpus_tier.py` — `ProvenanceTier`,
  `AdjudicationState`, `ScenarioFamily`, `QuarantineReason`, promotion rules,
  `CandidateRegistry` schema, `CorpusCandidate` wrapper, `GeneratorIdentity`,
  `JudgeIdentity`, self-certification guard, quarantine validator
- New `tests/test_bernie_corpus_tier.py` — unit tests for all tier transitions,
  promotion/rejection cases, quarantine triggers, self-certification guard,
  schema validation, authority-boundary rejection, registry descriptor
  validation
- New `tests/fixtures/bernie_corpus_tier/` — factory test fixtures:
  `valid_gold_seed.json`, `valid_silver_candidate.json`,
  `self_certified_reject.json`, `quarantine_schema_invalid.json`,
  `quarantine_authority_breach.json`,
  `registry_evaluation_candidates.json` (3+ candidates, URL + licence +
  linguistic-form labels + conservative decision only)
- Must **not** write to `app/services/bernie/scenario_spec.py`
- New `docs/bernie-lc2-provenance-rules.md` — human-readable provenance and
  promotion rule reference

**Must not touch:** `app/services/bernie/candidate_generators.py` (DW2),
`app/services/bernie/scenario_spec.py`, `app/services/bernie/language_normalization.py`,
`scripts/bernie_coverage_lattice.py`, routes, schemas, migrations, T3 tests,
existing LC1 fixtures (read-only).

### DW2 — Candidate Generators

**Scope:**
1. Build bounded, reproducible candidate generators as pure Python functions
   that consume a Gold `ReceptionScenarioSpec` JSON fixture and produce
   candidate families:
   - **Paraphrase generator**: Preserves semantics; changes surface wording,
     filler, politeness, and punctuation variants. Each output must have
     identical `normalized_values`, `temporal_relation`, entity semantics, and
     expected outcomes to the source Gold.
   - **Minimal-pair generator**: Changes exactly one semantic field
     (`temporal_relation`, practitioner, patient, date, duration, or dialogue
     form) in a controlled direction. Produces pairs where only the changed
     field differs; all other fields match the source.
   - **Ambiguity generator**: Removes a disambiguating element (temporal
     operator, entity name, duration) to produce scenarios where
     `action_semantics: "ambiguous"` and the expected outcome is
     `clarification_required`.
   - **Correction generator**: Produces two-turn dialogue where turn 2
     corrects exactly one field from turn 1. The correction must supersede only
     the corrected field; all other fields remain from turn 1.
   - **Adversarial generator**: Produces unsafe-instruction, authority-bypass,
     and confirmation-circumvention variants derived from Gold scenarios. These
     must have `action_semantics: "prohibited"` and expected outcomes that
     refuse the unsafe instruction.
2. **Bounded output: exactly 15 candidates** — three candidates for each of
   the five generator families, derived from named LC1 Gold seeds (see fixture
   manifest below). No `30+` or open-ended fixture target.
3. Candidate fixture manifest (single directory, one JSON per family):
   - `tests/fixtures/bernie_corpus_candidates/paraphrase_family.json` — 3
     paraphrase candidates from a named Gold seed
   - `tests/fixtures/bernie_corpus_candidates/minimal_pair_family.json` — 3
     minimal-pair candidates from a named Gold seed
   - `tests/fixtures/bernie_corpus_candidates/ambiguity_family.json` — 3
     ambiguity candidates from a named Gold seed
   - `tests/fixtures/bernie_corpus_candidates/correction_family.json` — 3
     correction candidates from a named Gold seed
   - `tests/fixtures/bernie_corpus_candidates/adversarial_family.json` — 3
     adversarial candidates from a named Gold seed
   Each family file is a JSON array of `CorpusCandidate` wrapper records.
4. Every generated candidate must:
   - Preserve the original utterance and LC1 source coordinates from the source
     Gold scenario (annotated with generation metadata). Exact original
     source-span text must be preserved byte-for-byte.
   - Carry `provenance: "silver"`, `adjudication: "pending"`, and
     `generator_identity: "deepseek-flash-dw2"`.
   - Reference its source Gold `scenario_id` in a `source_scenario_id` field.
   - Leave `judge_identity` unset until independent adjudication (DW2 must
     never set `judge_identity` on its own candidates).
   - Record `generation_timestamp` in ISO-8601 and a stable derivation ID/hash
     reproducible from source seed + generation parameters.
   - Be deterministically reproducible: given the same Gold seed and generation
     parameters, the same candidate must be produced (use fixed random seeds
     or deterministic templates with bounded counts).
5. Define synthetic-diary receptionist elicitation without PHI:
   - Pure templated utterances over synthetic patient/practitioner/location
     names drawn from a committed allowlist fixture.
   - No real patient data, no PHI-bearing fields, no external provider calls.
   - Elicitation templates cover everyday receptionist phrasing: availability
     queries, booking requests, reschedule/cancel requests, check-in,
     handoff, and clarification exchanges.
6. Define a deterministic candidate validator that checks each generated
   candidate against the `ReceptionScenarioSpec` schema before writing.

**File ownership:**
- New `app/services/bernie/candidate_generators.py` — paraphrase, minimal-pair,
  ambiguity, correction, adversarial generators; deterministic validation;
  synthetic elicitation templates; synthetic name allowlist
- New `tests/test_bernie_candidate_generators.py` — unit tests for each
  generator type, reproducibility, schema compliance, semantic preservation
  (paraphrase), field-isolation (minimal-pair), ambiguity detection,
  correction supersession, adversarial safety
- New `tests/fixtures/bernie_corpus_candidates/` — exactly 5 family files
  (see manifest above) each containing exactly 3 candidates
- New `docs/bernie-lc2-candidate-generation.md` — generator reference,
  reproducibility contract, bounded counts, synthetic elicitation policy

**Must not touch:** `app/services/bernie/corpus_tier.py` (DW1),
`app/services/bernie/scenario_spec.py` (read-only; may read, may not write),
`app/services/bernie/language_normalization.py`, routes, schemas, migrations,
T3 tests, existing LC1 fixtures (read-only seeds).

### AG — Independent Adversarial Review

**Scope:**
1. Generate adversarial probe cases that exercise:
   - Self-certification bypass (candidate where generator == judge)
   - Tier-escalation attacks (Bronze candidate masquerading as Gold)
   - Authority-boundary violations (candidate claiming confirmation or write
     authority)
   - Schema non-compliance (missing required fields, invalid temporal relations,
     malformed source spans)
   - Semantic drift attacks (paraphrase that silently changes temporal relation
     or entity)
   - Quarantine bypass attempts (invalid evidence promoted without review)
2. **Bounded AG probe count:** AG produces exactly 6 adversarial probe fixture
   files, one per attack class listed above. Each file contains a single
   representative probe case. The probes are committed in the Antigravity
   disposable worktree only.
3. Review DW1 factory schema for:
   - Promotion-rule completeness (every possible tier transition is defined)
   - Quarantine-trigger coverage (every rejection class has a test)
   - Self-certification guard correctness (no edge case allows generator==judge
     promotion)
4. **Independently** review DW2 generated candidates (Gemini reviews
   DeepSeek output — distinct model identities):
   - Independence violations (any candidate where generator is also judge)
   - Schema compliance (every generated candidate passes deterministic
     validation)
   - Semantic preservation (paraphrase candidates preserve all semantic fields)
   - Field isolation (minimal-pair candidates change only the intended field)
   - Adversarial safety (adversarial candidates are correctly classified as
     prohibited and produce refusal outcomes)
5. AG's **own** generated adversarial probes cannot be certified by Gemini
   and remain `silver/pending` or quarantine until independent Sol acceptance.
   Gemini acting as generator cannot also be judge for those probes. DW1
   deterministic checks validate AG probe shape and policy conformance only,
   not semantics.
6. Produce committed artifacts on the Antigravity worktree branch
   `antigravity/lc2-adversarial-corpus-review`.

**File ownership:**
- New `tests/fixtures/bernie_corpus_adversarial/` (placed in Antigravity
  disposable worktree, integrated to staging by Sol):
  `adversarial_probes_tier_escalation.json`,
  `adversarial_probes_self_certification.json`,
  `adversarial_probes_authority_breach.json`,
  `adversarial_probes_schema_violation.json`,
  `adversarial_probes_semantic_drift.json`,
  `adversarial_probes_quarantine_bypass.json`
- New `orchestration/agent_inbox/codex/review-antigravity-lc2-adversarial-corpus-review.md`
  — review artifact with findings, pass/fail decisions, and concrete evidence
- New `docs/adversarial/lc2_independent_review.md` — bounded adversarial review
  record

**Must not touch:** Any `app/` code, DW1 or DW2 files, routes, schemas,
migrations, T3 tests, existing LC1 fixtures.

AG is a generate-and-review lane with distinct file ownership. Its generated
adversarial cases are validated by DW1's factory schema (deterministic, shape
and policy only), not by AG itself. Its review of DW2 candidates provides
independent evidence (different model identity); it does not certify or
promote those candidates.

## Ownership Boundaries

```
DW1 (corpus factory core)          DW2 (candidate generators)
├─ app/services/bernie/             ├─ app/services/bernie/
│  corpus_tier.py (NEW)             │  candidate_generators.py (NEW)
├─ tests/test_bernie_corpus_tier.py ├─ tests/test_bernie_candidate_generators.py
├─ tests/fixtures/bernie_corpus_tier├─ tests/fixtures/bernie_corpus_candidates/
├─ docs/bernie-lc2-provenance-rules ├─ docs/bernie-lc2-candidate-generation.md
│                                   │
│  READ-ONLY (shared):              │  READ-ONLY (shared):
│  app/services/bernie/             │  app/services/bernie/
│    scenario_spec.py               │    scenario_spec.py
│    language_normalization.py      │    language_normalization.py
│  scripts/bernie_coverage_lattice  │  tests/fixtures/bernie_scenario_spec/
│  tests/fixtures/bernie_scenario_  │
│    spec/ (3 Gold fixtures)        │
│                                   │
│                 AG (independent adversarial)
│                 ├─ tests/fixtures/bernie_corpus_adversarial/
│                 ├─ orchestration/agent_inbox/codex/
│                 │  review-antigravity-lc2-adversarial-corpus-review.md
│                 └─ docs/adversarial/lc2_independent_review.md
```

No file is owned by more than one worker. The LC1 Gold fixtures and shared
modules (`scenario_spec.py`, `language_normalization.py`,
`bernie_coverage_lattice.py`) are read-only canonical inputs to all lanes.
DW1 must **not** add provenance fields to `scenario_spec.py`; the
`CorpusCandidate` wrapper type is the sole provenance carrier. DW2 must not
write to `scenario_spec.py`.

## Ordered Dependencies

```
DW1 (corpus factory core) ──┐
                              ├──> AG (independent adversarial review)
DW2 (candidate generators) ──┘
                                │
                                v
                            Sol acceptance → integration
```

DW1 and DW2 are parallel (disjoint file ownership). AG must wait for both DW1
and DW2 to submit their artifacts, then run adversarial probes against the
combined surface.

## Verification Plan

### Pre-dispatch (Sol verifies before dispatching any worker)

```powershell
# 1. LC1 foundation is intact
.venv\Scripts\python.exe -m pytest tests/test_bernie_scenario_spec.py -q
.venv\Scripts\python.exe -m pytest tests/test_bernie_coverage_lattice.py -q

# 2. Three Gold fixtures validate
.venv\Scripts\python.exe -m pytest tests/test_bernie_scenario_spec.py -q -k "seed"

# 3. Coverage lattice reports correctly
.venv\Scripts\python.exe scripts/bernie_coverage_lattice.py

# 4. T3.1-T3.4 unchanged
.venv\Scripts\python.exe -m pytest tests/test_bernie_shadow_eval_contract.py tests/test_bernie_shadow_corpus.py tests/test_bernie_shadow_runner.py tests/test_bernie_shadow_live_gate.py -q

# 5. Readiness gate still blocked
.venv\Scripts\python.exe scripts/bernie_interpretation_readiness_check.py
# Expected: runtime_or_provider_wiring_ready=false, raw_trove_access_ready=false,
#           runtime_gate_decision=blocked, sprint_engine_state=continuing
```

### DW1 acceptance (corpus factory core)

```powershell
# 6. Corpus tier module imports cleanly (no provider, route, DB deps)
.venv\Scripts\python.exe -c "from app.services.bernie.corpus_tier import ProvenanceTier, AdjudicationState, ScenarioFamily, CorpusCandidate; print('OK')"

# 7. Promotion rules: Gold->Silver, Silver->Gold, Bronze->Silver, quarantine all tested
.venv\Scripts\python.exe -m pytest tests/test_bernie_corpus_tier.py -q -k "promotion"

# 8. Self-certification guard: generator==judge -> quarantine
.venv\Scripts\python.exe -m pytest tests/test_bernie_corpus_tier.py -q -k "self_cert"

# 9. Quarantine triggers: schema_invalid, authority_breach, evidence_mismatch
.venv\Scripts\python.exe -m pytest tests/test_bernie_corpus_tier.py -q -k "quarantine"

# 10. Candidate registry schema validates; registry evaluation has 3+ candidates
#     with primary-source URLs and conservative decisions
.venv\Scripts\python.exe -m pytest tests/test_bernie_corpus_tier.py -q -k "registry"

# 11. CorpusCandidate wrapper validates, wraps ReceptionScenarioSpec without mutation
.venv\Scripts\python.exe -m pytest tests/test_bernie_corpus_tier.py -q -k "wrapper"

# 12. All factory tests pass
.venv\Scripts\python.exe -m pytest tests/test_bernie_corpus_tier.py -q

# 13. Existing LC1 tests still pass (scenario_spec.py is untouched)
.venv\Scripts\python.exe -m pytest tests/test_bernie_scenario_spec.py -q
.venv\Scripts\python.exe scripts/bernie_coverage_lattice.py
```

### DW2 acceptance (candidate generators)

```powershell
# 14. Generator module imports cleanly (no provider, route, DB deps)
.venv\Scripts\python.exe -c "from app.services.bernie.candidate_generators import generate_paraphrase_candidates; print('OK')"

# 15. Paraphrase generation: semantic preservation, bounded count (exactly 3), reproducibility
.venv\Scripts\python.exe -m pytest tests/test_bernie_candidate_generators.py -q -k "paraphrase"

# 16. Minimal-pair generation: exactly one field changes, bounded count (exactly 3)
.venv\Scripts\python.exe -m pytest tests/test_bernie_candidate_generators.py -q -k "minimal_pair"

# 17. Ambiguity generation: produces ambiguous semantics, clarification expected (exactly 3)
.venv\Scripts\python.exe -m pytest tests/test_bernie_candidate_generators.py -q -k "ambiguity"

# 18. Correction generation: two-turn, exactly one field corrected (exactly 3)
.venv\Scripts\python.exe -m pytest tests/test_bernie_candidate_generators.py -q -k "correction"

# 19. Adversarial generation: prohibited semantics, refusal outcomes (exactly 3)
.venv\Scripts\python.exe -m pytest tests/test_bernie_candidate_generators.py -q -k "adversarial"

# 20. Synthetic elicitation: no PHI, pure templated utterances
.venv\Scripts\python.exe -m pytest tests/test_bernie_candidate_generators.py -q -k "elicitation"

# 21. Reproducibility: same seed + params -> identical output, stable derivation IDs/hashes
.venv\Scripts\python.exe -m pytest tests/test_bernie_candidate_generators.py -q -k "reproducible"

# 22. All generator tests pass; exactly 15 candidates across 5 family files
.venv\Scripts\python.exe -m pytest tests/test_bernie_candidate_generators.py -q

# 23. Generated fixtures validate against ReceptionScenarioSpec via CorpusCandidate wrapper
.venv\Scripts\python.exe -m pytest tests/test_bernie_scenario_spec.py -q -k "candidate"

# 24. Exact original/source-span preservation verified byte-for-byte
.venv\Scripts\python.exe -m pytest tests/test_bernie_candidate_generators.py -q -k "source_span"

# 25. No generator imports corpus_tier.py (DW2 must not depend on DW1 internals)
# (Verified by test or static check)
```

### AG acceptance (independent adversarial review)

```powershell
# 26. Adversarial probes exercise factory promotion rules (exactly 6 probes)
.venv\Scripts\python.exe -m pytest tests/test_bernie_corpus_tier.py -q -k "adversarial_probe"

# 27. Self-certification bypass attempts all rejected
.venv\Scripts\python.exe -m pytest tests/test_bernie_corpus_tier.py -q -k "self_cert"

# 28. Tier-escalation attacks all quarantined
.venv\Scripts\python.exe -m pytest tests/test_bernie_corpus_tier.py -q -k "escalation"

# 29. Authority-boundary violations all rejected
.venv\Scripts\python.exe -m pytest tests/test_bernie_corpus_tier.py -q -k "authority_breach"

# 30. AG review artifact exists and documents Gemini≠generator independence
# File: orchestration/agent_inbox/codex/review-antigravity-lc2-adversarial-corpus-review.md

# 31. AG adversarial fixtures exist and validate (all pending, none adjudicated)
.venv\Scripts\python.exe -m pytest tests/test_bernie_corpus_tier.py -q -k "fixture"
```

### End-to-end integration (Sol after DW1 + DW2 + AG)

```powershell
# 32. Full corpus test suite passes
.venv\Scripts\python.exe -m pytest tests/test_bernie_corpus_tier.py tests/test_bernie_candidate_generators.py -q

# 33. LC1 foundation intact (scenario_spec.py untouched)
.venv\Scripts\python.exe -m pytest tests/test_bernie_scenario_spec.py tests/test_bernie_coverage_lattice.py -q

# 34. T3.1-T3.4 unchanged
.venv\Scripts\python.exe -m pytest tests/test_bernie_shadow_eval_contract.py tests/test_bernie_shadow_corpus.py tests/test_bernie_shadow_runner.py tests/test_bernie_shadow_live_gate.py -q

# 35. No provider, route, DB, or write-authority imports in new modules
# (Verified by static import check)
.venv\Scripts\python.exe -c "
import ast, sys
forbidden = {'fastapi', 'sqlalchemy', 'asyncio', 'httpx', 'requests', 'openai', 'google.generativeai', 'vertexai'}
for mod_name in ['app.services.bernie.corpus_tier', 'app.services.bernie.candidate_generators']:
    with open(mod_name.replace('.', '/') + '.py') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(alias.name.startswith(f) for f in forbidden):
                    print(f'FORBIDDEN IMPORT in {mod_name}: {alias.name}')
                    sys.exit(1)
        elif isinstance(node, ast.ImportFrom):
            if node.module and any(node.module.startswith(f) for f in forbidden):
                print(f'FORBIDDEN IMPORT in {mod_name}: {node.module}')
                sys.exit(1)
print('Import check passed')
"

# 36. Readiness gate still blocked
.venv\Scripts\python.exe scripts/bernie_interpretation_readiness_check.py

# 37. Registry primary-source citations independently verifiable by Sol
# (Sol inspects registry_evaluation_candidates.json for official URLs,
#  verbatim licence strings, conservative decisions, no eligibility claims)
```

## Fallback Reasons

Claude Code bare mode is the primary transport. On a lane failure, retry the
same bare-mode lane with recorded remediation before considering DeepCode for
that lane. Do not switch a healthy lane merely to make transports match.
DeepCode remains fallback-only.

| Scenario | Fallback |
|---|---|
| DW1 DeepSeek bare-mode transport fails | Retry DW1 bare-mode with recorded remediation. If retry also fails, switch DW1 to Deep Code TUI fallback with durable packet artifact; record transport change and remediation log |
| DW2 DeepSeek bare-mode transport fails | Retry DW2 bare-mode with recorded remediation. If retry also fails, switch DW2 to Deep Code TUI fallback. Do **not** switch DW1 if it succeeded bare-mode; cross-checks are deterministic, not transport-dependent |
| Antigravity `agy.exe` unavailable or produces no durable artifact | Stand down AG; Sol runs adversarial probe fixture validation locally and records reduced-independence posture; this is a known risk given the `agy` non-TTY stdout capture quirk |
| DeepSeek API quota exhausted mid-sprint | Serialize DW1 → DW2; Sol executes the remaining lane locally with the same deterministic acceptance checks; record the substitution |
| AG submits only stdout without a committed artifact | Reject AG lane; Sol records the probe failure and runs adversarial checks locally; mark independence as reduced |

## Independence Labels

| Surface | Independence Posture |
|---|---|
| DW1 factory schema validation | Deterministic (Python schema validation, no model involved) — validates shape and policy only, not semantics; independent of all models |
| DW2 candidate generation | Model-generated (`deepseek-flash-dw2`) — not independent; requires external adjudication |
| DW2 candidate schema validation | Deterministic (via `ReceptionScenarioSpec` Pydantic model) — independent of DW2 model |
| AG adversarial probe generation | Model-generated (`gemini-flash-3.5-ag`) — not independent; probes remain `silver/pending` or quarantine until independent Sol acceptance |
| AG review of DW2 candidates | Independent review surface (Gemini reviews DeepSeek output; distinct model identities) — `generator_identity != judge_identity` satisfied |
| DW1 review of AG probes | Deterministic shape/policy validation (factory rejects or quarantines by rule, not semantic certification) — independent of AG model |
| Sol final acceptance | Protected orchestrator/integrator — owns corpus authority; model evidence is advisory only; Sol alone changes `adjudication` from `pending` to `adjudicated` |

**Key constraint:** DW2 must never set `judge_identity` on its own candidates.
AG must never promote or certify its own adversarial probes. The factory
(DW1, deterministic) validates shape and policy only — it does not semantically
certify any candidate. No worker or generator may mark its own cases
adjudicated or Gold. Actual generated cases remain `silver/pending` (or
quarantine) unless an independent judge record exists. Sol is the only
authority that can change `adjudication` from `pending` to `adjudicated`.

## Unfilled Obligations

1. **Independent model judge**: No separate model judge is allocated in this
   sprint. The deterministic factory (DW1) validates schema and promotion
   rules (shape and policy only, not semantics); AG provides independent
   adversarial review evidence (Gemini ≠ DeepSeek, distinct model identities).
   A true independent model judge (e.g., a distinct instance that semantically
   reviews generated candidates and sets `judge_identity`) is deferred to LC3
   or a later sprint when multi-model evaluation infrastructure is built.
   **Mitigation**: The factory's deterministic validation plus AG's adversarial
   review provide sufficient independence for the initial corpus; no candidate
   is promoted to `adjudicated` without Sol acceptance. The `judge_identity`
   field remains unset on all DW2 candidates and on all AG probe candidates.

2. **Historical-diary Bronze discovery**: Bronze-tier material from the
   historical diary trove is not generated. The H15 semantic-gate payload
   authorizes only one bounded local prototype; broad trove mining for Bronze
   candidates remains blocked by the existing H-series gates and the Fable R28
   review verdict.

3. **Coverage lattice refresh with Silver candidates**: The coverage lattice
   script (`bernie_coverage_lattice.py`) currently reads only
   `tests/fixtures/bernie_scenario_spec/`. Silver/Bronze candidates in new
   directories are not yet counted in the gap report. A multi-directory
   lattice refresh is deferred to LC3.

4. **Full independent LLM verifier**: The operating model's risk-triggered
   independent verifier is not triggered for this sprint (see risk/API-spine
   classification below). If a trigger condition emerges during execution
   (resource limit exception, authority drift signal), the verifier must be
   invoked before integration.

## Workspace-Receipt Requirements

Before any worker is dispatched, the Sol orchestrator/integrator preflight
receipt must confirm:

| Requirement | Expected Value |
|---|---|
| Target worktree | `C:\Users\sarashera\EMR4-worktrees\lc2-staging` |
| Target branch | `codex/lc2-staging` |
| Worktree cleanliness | Clean (no uncommitted changes, no stale worker artifacts) |
| HEAD relation to `handoff/current` | Matches or has recorded divergence |
| Realignment | Executed from target worktree (not integration worktree) |
| Settings fingerprint | `sha256:20e82ee5251321c4987158176b29f8c780ba5debc2c515592c320e869be418d5` |
| Preflight decision | `passed` |

The receipt is required at: new-session, post-compaction, pre-plan, and
pre-dispatch continuation events. Unknown context without a fresh receipt
cannot proceed to planning, dispatch, or integration.

## Exact Acceptance Criteria

### Must-pass (rejection if any fails)

1. `ProvenanceTier`, `AdjudicationState`, `ScenarioFamily`, and `CorpusCandidate`
   wrapper imported from `app/services/bernie/corpus_tier.py`.
2. `CorpusCandidate` wraps `ReceptionScenarioSpec` without mutating the LC1
   schema; `scenario_spec.py` is untouched.
3. Promotion function: `promote_candidate(candidate, judge_identity) -> PromotionResult`
   — returns `promoted` with new tier only when judge ≠ generator and all
   schema/authority checks pass; returns `quarantine(reason)` otherwise.
4. Quarantine triggers: self-certification (generator == judge), schema
   invalid (Pydantic validation failure via embedded `ReceptionScenarioSpec`),
   authority breach (write/confirm/provider fields non-null where prohibited),
   evidence mismatch (spans do not match original text), missing provenance
   fields. Every quarantine must include an explicit `QuarantineReason`.
5. Candidate registry schema validates; `registry_evaluation_candidates.json`
   contains at least 3 well-known task-dialogue corpus candidates with
   official-source URL, verbatim declared licence metadata, linguistic-form
   capability labels, and conservative `candidate_only` /
   `requires_licence_review` decision. No entry claims eligibility, licence
   acceptance, dataset content, or cost assessment.
6. Five generator types each produce exactly 3 candidates from named Gold
   seed(s) — total exactly 15 DW2 candidates across 5 family manifest files.
7. Paraphrase candidates preserve all semantic fields (identical
   `normalized_values`, `temporal_relation`, entity semantics, expected
   outcomes) and exact original source-span text byte-for-byte.
8. Minimal-pair candidates change exactly one semantic field.
9. Adversarial candidates have `action_semantics: "prohibited"` and expected
   outcomes that refuse the unsafe instruction.
10. All generated candidates pass `ReceptionScenarioSpec` schema validation
    (via `CorpusCandidate` wrapper).
11. All generated candidates carry required provenance metadata:
    `provenance: "silver"`, `adjudication: "pending"`, `generator_identity`,
    `judge_identity` (unset or set by an independent judge), `family`,
    `generation_timestamp`, `source_scenario_id`, `promotion_history`.
12. Generator reproducibility: same Gold seed + parameters → identical output
    (deterministic bounded counts, stable derivation IDs/hashes).
13. Synthetic elicitation templates contain no PHI (no real patient names, no
    real identifiers; only committed synthetic allowlist values).
14. Zero provider, route, database, or write-authority imports in
    `corpus_tier.py` and `candidate_generators.py`.
15. AG adversarial probes exist as exactly 6 committed JSON fixtures (one per
    attack class) and exercise all quarantine trigger classes. All AG probes
    remain `silver/pending` or quarantine — none adjudicated.
16. AG review artifact documents each finding with concrete evidence and
    confirms `generator_identity != judge_identity` for every reviewed
    candidate.
17. LC1 foundation tests pass unchanged (`scenario_spec.py` untouched;
    T3.1-T3.4 pass; coverage lattice reports correctly).
18. Interpretation-harness readiness gate remains `blocked`.
19. `git diff --check` passes (no whitespace errors).

### Rejection conditions

- Any generated candidate carries `judge_identity` set by its own generator
  (`generator_identity == judge_identity`).
- Any candidate with `provenance: "gold"` was generated by a model (Gold is
  human/Sol-authored only).
- Any worker or generator marks its own cases adjudicated or Gold.
- Any generator, validator, or registry module imports `fastapi`, `sqlalchemy`,
  `httpx`, `requests`, `openai`, `google.generativeai`, or any provider/route/
  database module.
- Any candidate fixture contains real patient data, PHI, or non-synthetic
  identifiers.
- Any DW1 or DW2 file touches a file owned by the other lane.
- DW1 modifies `scenario_spec.py` in any way.
- The AG review artifact claims to certify or promote candidates rather than
  providing independent adversarial evidence.
- T3.5 provider adapters or live-provider code is referenced, imported, or
  modified.
- The interpretation-harness runtime gate changes from `blocked`.
- Any registry entry claims a source is eligible, licence-accepted, or licensed
  for use.

## Proposed Staging Integration Order

1. **Pre-dispatch**: Sol runs pre-dispatch checks, confirms workspace receipt
   `passed`, verifies Antigravity availability via `agy.exe` probe, confirms
   DeepSeek bare-mode transport reachable. Two DeepSeek Flash lanes are
   allocated but not yet dispatched.
2. **Parallel dispatch**: DW1 and DW2 dispatched simultaneously to separate
   disposable worktrees. Both use DeepSeek Flash via Claude Code bare mode.
   Workers make candidate commits **only in disposable worktrees** and never
   push branches.
3. **DW1 submit**: Factory core committed in disposable worktree
   `codex/lc2-dw1-corpus-factory-core`. Sol reviews artifact, runs DW1
   acceptance checks.
4. **DW2 submit**: Candidate generators and initial corpus committed in
   disposable worktree `codex/lc2-dw2-candidate-generators`. Sol reviews
   artifact, runs DW2 acceptance checks.
5. **AG dispatch**: After both DW1 and DW2 artifacts are accepted, AG is
   dispatched with the combined surface. AG runs adversarial probes, generates
   probe fixtures, and produces review artifact. AG commits **only in
   disposable worktree** `antigravity/lc2-adversarial-corpus-review` and
   never pushes.
6. **AG submit**: Adversarial fixtures and review artifact committed in
   Antigravity disposable worktree. Sol reviews, integrates AG fixtures
   into staging.
7. **Sol integration**: Combined acceptance — all DW1, DW2, AG checks pass.
   **Sol alone** integrates all artifacts into a single staging commit on
   `codex/lc2-staging`. Sol alone pushes branches and integrates protected
   master. Runs full test suite. Records integration in
   `orchestration/integration_log.md`.
8. **Staging closeout**: Sol updates `AGENTS.md` with LC2 closeout notes,
   records the coverage lattice delta, and prepares the integration manifest.

All pytest processes that use the repository conftest (shared PostgreSQL
schema) must run serially. Parallel execution is allowed only for import-free
static checks, filesystem-only checks, and independent checks that do not
load the repository conftest.

## Risk / API-Spine Classification

| Dimension | Classification | Rationale |
|---|---|---|
| API-spine impact | **None** | No new routes, no GraphQL, no commands, no events, no schema changes to existing API models |
| Security surface | **None** | No auth changes, no new endpoints, no external data ingestion |
| Write authority | **None** | No database writes, no appointment/audit mutation, no confirmation authority |
| Provider surface | **None** | No provider calls, no live prompts, no provider adapter changes |
| Deployment risk | **None** | No deployment, release, or external-client changes |
| Data risk | **Low** | Synthetic data only; no PHI, no real patient identifiers; no external dataset download or content |
| Licence/cost risk | **Low** | Registry evaluation is URL + declared licence metadata only (no acceptance, no cost); provider calls remain closed |
| Regression risk | **Low** | LC1 scenario_spec.py is untouched; T3.1-T3.4 unchanged; CorpusCandidate wrapper is additive |
| Independence risk | **Medium** | No separate model semantic judge allocated; mitigated by deterministic factory shape/policy validation + AG independent adversarial review (Gemini ≠ DeepSeek) + Sol acceptance gate |
| Transport risk | **Low** | DeepSeek bare-mode is primary with retry + remediation; Deep Code TUI fallback-only; Antigravity probe required |

**Independent final LLM verifier: NOT triggered.** No trigger condition is met:
no new security/write/deployment/release authority, no orchestrator-integrator
material disagreement, no ambiguous mandate or scope boundary, no resource
limit exception, and no prior authority or ownership drift signal. If a
trigger condition emerges during execution, the verifier must be invoked
before integration.

## Expected Candidate Fixtures and Reports at Closeout

### DW1 deliverables

| Artifact | Path | Description |
|---|---|---|
| Corpus tier module | `app/services/bernie/corpus_tier.py` | Provenance tiers, promotion rules, quarantine, registry, CorpusCandidate wrapper |
| Tier tests | `tests/test_bernie_corpus_tier.py` | All promotion/rejection/quarantine/wrapper unit tests |
| Factory fixtures | `tests/fixtures/bernie_corpus_tier/valid_gold_seed.json` | Valid Gold seed for promotion testing |
| | `tests/fixtures/bernie_corpus_tier/valid_silver_candidate.json` | Valid Silver candidate (CorpusCandidate wrapper) |
| | `tests/fixtures/bernie_corpus_tier/self_certified_reject.json` | Self-certification rejection case |
| | `tests/fixtures/bernie_corpus_tier/quarantine_schema_invalid.json` | Schema-invalid quarantine case |
| | `tests/fixtures/bernie_corpus_tier/quarantine_authority_breach.json` | Authority-breach quarantine case |
| | `tests/fixtures/bernie_corpus_tier/registry_evaluation_candidates.json` | 3+ candidates: URL, licence metadata, linguistic-form labels, conservative decision only |
| Provenance rules doc | `docs/bernie-lc2-provenance-rules.md` | Human-readable reference |

### DW2 deliverables

| Artifact | Path | Description |
|---|---|---|
| Candidate generators module | `app/services/bernie/candidate_generators.py` | All five generator types + elicitation templates |
| Generator tests | `tests/test_bernie_candidate_generators.py` | Per-generator unit tests |
| Candidate fixtures (exactly 15) | `tests/fixtures/bernie_corpus_candidates/paraphrase_family.json` | 3 paraphrase candidates from a named Gold seed |
| | `tests/fixtures/bernie_corpus_candidates/minimal_pair_family.json` | 3 minimal-pair candidates from a named Gold seed |
| | `tests/fixtures/bernie_corpus_candidates/ambiguity_family.json` | 3 ambiguity candidates from a named Gold seed |
| | `tests/fixtures/bernie_corpus_candidates/correction_family.json` | 3 correction candidates from a named Gold seed |
| | `tests/fixtures/bernie_corpus_candidates/adversarial_family.json` | 3 adversarial candidates from a named Gold seed |
| Generator reference | `docs/bernie-lc2-candidate-generation.md` | Generator specification, reproducibility contract, family manifest |

### AG deliverables (exactly 6 probes)

| Artifact | Path | Description |
|---|---|---|
| Adversarial probe fixtures | `tests/fixtures/bernie_corpus_adversarial/adversarial_probes_tier_escalation.json` | Tier-escalation attack probe |
| | `tests/fixtures/bernie_corpus_adversarial/adversarial_probes_self_certification.json` | Self-certification bypass probe |
| | `tests/fixtures/bernie_corpus_adversarial/adversarial_probes_authority_breach.json` | Authority-breach probe |
| | `tests/fixtures/bernie_corpus_adversarial/adversarial_probes_schema_violation.json` | Schema-violation probe |
| | `tests/fixtures/bernie_corpus_adversarial/adversarial_probes_semantic_drift.json` | Semantic-drift probe |
| | `tests/fixtures/bernie_corpus_adversarial/adversarial_probes_quarantine_bypass.json` | Quarantine-bypass probe |
| Review artifact | `orchestration/agent_inbox/codex/review-antigravity-lc2-adversarial-corpus-review.md` | Independent review with findings and evidence |
| Adversarial review record | `docs/adversarial/lc2_independent_review.md` | Bounded review record |

### Integration deliverables (routine evidence)

| Artifact | Path | Description |
|---|---|---|
| Tranche contract | `orchestration/agent_inbox/codex/lc2-corpus-factory-tranche-contract.md` | This document (sole committed tranche evidence) |
| Integration manifest | `orchestration/integration_log.md` | Integration outcome record (to be committed at closeout) |
| AGENTS.md update | `AGENTS.md` | LC2 closeout notes |

Worker packets, receipts, transcripts, and intermediate dispatch artifacts are
ignored local artifacts under `local_data/ariadne-lc2/`. They are not committed
deliverables and are not produced under `orchestration/agent_inbox/deepcode/`
or `orchestration/agent_inbox/antigravity/`. The tranche contract, later
integration manifest, and closeout are the routine evidence. Candidate
fixtures, code, and docs remain ordinary product artifacts.

## Sprint-Engine State

**Sprint engine continuing.** LC2 is a bounded pure-Python/domain-layer and
strict-JSON-fixture sprint with no provider, route, database, write-authority,
external-client, or data-ingestion surface. Claude is unavailable (subscription
cancelled after 2026-07-13); Antigravity Gemini Flash is allocated as an
independent adversarial review lane with a required availability probe; two
DeepSeek Flash lanes are allocated but not yet spawned/dispatched — they
provide implementation coverage with separable file ownership. Sol, as
protected orchestrator/integrator, owns architecture, final acceptance, and
protected master integration. No user decision is required unless work would
broaden historical-trove access, send sensitive data to a provider, accept
material licensing/cost terms, open live-provider calls, or change diary
write authority — none of which are in scope.